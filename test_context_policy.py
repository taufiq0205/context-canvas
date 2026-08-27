import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import context_policy


class ContextPolicyTest(unittest.TestCase):
    def _selection_payload(self):
        return json.loads(Path("selections.json").read_text(encoding="utf-8"))

    def _write_selection_payload(self, directory, payload):
        path = Path(directory) / "selections.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _answers(self, key):
        scenarios = {row["id"]: row for row in context_policy.load_scenarios(Path("scenarios.json"))}
        return [
            {
                "package_id": row["package_id"],
                "text": scenarios[row["scenario_id"]]["expected"][0],
                "model_id": context_policy.PINNED_MODEL_ID,
                "settings": context_policy.PINNED_SETTINGS,
                "tokenizer_id": context_policy.PINNED_TOKENIZER_ID,
                "input_tokens": 1,
                "elapsed_ms": 1,
                "manual_actions": 0,
            }
            for row in key
        ]

    def _receipts(self, key, answers):
        # Test-only doubles exercise binding; they are not provider evidence.
        return [
            {
                "package_id": package["package_id"],
                "prompt_sha256": package["prompt_sha256"],
                "answer_sha256": hashlib.sha256(answer["text"].encode()).hexdigest(),
                "provider_response_id": f"test-response-{index}",
                "model_id": answer["model_id"],
                "settings": answer["settings"],
                "tokenizer_id": answer["tokenizer_id"],
                "input_tokens": answer["input_tokens"],
                "completed_at": "2026-08-27T00:00:00Z",
            }
            for index, (package, answer) in enumerate(zip(key, answers))
        ]

    def test_answer_validation_rejects_boolean_metrics(self):
        with self.assertRaises(ValueError):
            context_policy.validate_answer(
                {
                    "package_id": "id",
                    "text": "answer",
                    "model_id": "model-version",
                    "settings": {"temperature": 0},
                    "tokenizer_id": "tokenizer-version",
                    "input_tokens": True,
                    "elapsed_ms": 1,
                    "manual_actions": 0,
                }
            )

    def test_prepare_builds_blinded_48_run_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation"
            context_policy.prepare(Path("scenarios.json"), output, context_policy.word_count, "words")

            packages = context_policy.read_jsonl(output / "packages.jsonl")
            key = context_policy.read_jsonl(output / "key.jsonl")

            self.assertEqual(48, len(packages))
            self.assertEqual(48, len({row["package_id"] for row in packages}))
            self.assertNotIn("condition", packages[0])
            self.assertEqual(64, len(packages[0]["prompt_sha256"]))
            self.assertEqual({"automatic", "explicit"}, {row["condition"] for row in key})
            self.assertTrue((output / "corpus.sqlite3").exists())
            connection = context_policy.sqlite3.connect(output / "corpus.sqlite3")
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'trigger')"
                )
            }
            self.assertTrue({"tasks", "context_edges", "selections", "versions", "handoff_snapshots"} <= tables)
            self.assertEqual(48, connection.execute("SELECT COUNT(*) FROM handoff_snapshots").fetchone()[0])
            with self.assertRaises(context_policy.sqlite3.IntegrityError):
                connection.execute("DELETE FROM handoff_snapshots")
            connection.close()

    def test_explicit_package_excludes_unselected_context(self):
        scenarios = context_policy.load_scenarios(Path("scenarios.json"))
        scenario = scenarios[0]
        scenario["selected_source_ids"] = context_policy.load_selections(
            Path("selections.json"), scenarios
        )[scenario["id"]]["selected_source_ids"]
        prompt, selected = context_policy.build_prompt(
            scenario, "explicit", scenario["sources"], context_policy.word_count
        )

        self.assertEqual(scenario["selected_source_ids"], selected)
        for source in scenario["sources"]:
            if source["id"] in selected:
                self.assertIn(source["text"], prompt)
            else:
                self.assertNotIn(source["text"], prompt)
        self.assertIn("task", prompt)
        self.assertNotIn("session", prompt)

    def test_selection_requires_provenance_fields(self):
        payload = self._selection_payload()
        del payload["selections"][0]["provenance"]
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_selection_payload(directory, payload)
            with self.assertRaises(ValueError):
                context_policy.load_selections(path, context_policy.load_scenarios(Path("scenarios.json")))

    def test_selection_rejects_scoring_data_and_unknown_source(self):
        scenarios = context_policy.load_scenarios(Path("scenarios.json"))
        payload = self._selection_payload()
        payload["selections"][0]["expected"] = ["must not be here"]
        payload["selections"][1]["selected_source_ids"] = ["unknown-source"]
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_selection_payload(directory, payload)
            with self.assertRaises(ValueError):
                context_policy.load_selections(path, scenarios)

    def test_inferred_selection_cannot_validate_gate(self):
        payload = self._selection_payload()
        payload["selections"][0]["selection_kind"] = "inferred"
        with tempfile.TemporaryDirectory() as directory:
            selection_path = self._write_selection_payload(directory, payload)
            output = Path(directory) / "evaluation"
            context_policy.prepare(
                Path("scenarios.json"),
                output,
                context_policy.word_count,
                context_policy.PINNED_TOKENIZER_ID,
                selection_path,
            )
            key = context_policy.read_jsonl(output / "key.jsonl")
            context_policy.write_jsonl(output / "answers.jsonl", self._answers(key))
            report = context_policy.score(
                output / "key.jsonl", output / "answers.jsonl", selections_path=selection_path
            )
            self.assertFalse(report["valid_for_gate"])
            self.assertFalse(report["validation"]["all_selections_user_explicit"])

    def test_answers_without_receipts_cannot_validate_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            selections = self._selection_payload()
            for selection in selections["selections"]:
                selection["selection_kind"] = "user_explicit"
            selection_path = self._write_selection_payload(directory, selections)
            output = Path(directory) / "evaluation"
            context_policy.prepare(
                Path("scenarios.json"),
                output,
                context_policy.word_count,
                context_policy.PINNED_TOKENIZER_ID,
                selection_path,
            )
            key = context_policy.read_jsonl(output / "key.jsonl")
            context_policy.write_jsonl(output / "answers.jsonl", self._answers(key))

            report = context_policy.score(
                output / "key.jsonl", output / "answers.jsonl", selections_path=selection_path
            )

            self.assertFalse(report["valid_for_gate"])
            self.assertFalse(report["validation"]["matching_provider_receipts"])

    def test_key_selection_metadata_cannot_override_canonical_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            selections = self._selection_payload()
            for selection in selections["selections"]:
                selection["selection_kind"] = "user_explicit"
            selection_path = self._write_selection_payload(directory, selections)
            output = Path(directory) / "evaluation"
            context_policy.prepare(
                Path("scenarios.json"),
                output,
                context_policy.word_count,
                context_policy.PINNED_TOKENIZER_ID,
                selection_path,
            )
            key_path = output / "key.jsonl"
            key = context_policy.read_jsonl(key_path)
            key[0]["selection_kind"] = "workflow_observed"
            key_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in key))
            answers = self._answers(key)
            answers_path = output / "answers.jsonl"
            context_policy.write_jsonl(answers_path, answers)
            receipts_path = Path(directory) / "receipts.jsonl"
            context_policy.write_jsonl(receipts_path, self._receipts(key, answers))

            report = context_policy.score(key_path, answers_path, receipts_path, selection_path)

            self.assertFalse(report["valid_for_gate"])
            self.assertFalse(report["validation"]["key_selection_metadata_matches"])

    def test_explicit_over_budget_reports_excess(self):
        scenario = {
            "id": "budget-check",
            "title": "A title",
            "instructions": "Answer",
            "token_ceiling": 1,
            "selected_source_ids": ["source"],
        }
        source = {
            "id": "source",
            "label": "Evidence",
            "text": "Some evidence",
            "provenance": {
                "task_id": "task",
                "run_id": "run",
                "artifact_id": "artifact",
                "version": "version",
            },
        }
        with self.assertRaises(context_policy.TokenBudgetError) as raised:
            context_policy.build_prompt(scenario, "explicit", [source], context_policy.word_count)
        self.assertGreater(raised.exception.excess_tokens, 0)
        self.assertIn("by", str(raised.exception))

    def test_gate_passes_when_explicit_prevents_two_automatic_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation"
            selections = self._selection_payload()
            for selection in selections["selections"]:
                selection["selection_kind"] = "user_explicit"
            selection_path = self._write_selection_payload(directory, selections)
            context_policy.prepare(
                Path("scenarios.json"),
                output,
                context_policy.word_count,
                context_policy.PINNED_TOKENIZER_ID,
                selection_path,
            )
            key = context_policy.read_jsonl(output / "key.jsonl")
            scenarios = {row["id"]: row for row in context_policy.load_scenarios(Path("scenarios.json"))}
            failed = {"stale-approved-scope", "adversarial-handoff-authority"}
            answers = []
            for row in key:
                scenario = scenarios[row["scenario_id"]]
                text = scenario["expected"][0]
                if row["condition"] == "automatic" and row["scenario_id"] in failed:
                    text = "wrong " + " ".join(scenario["forbidden"])
                answers.append(
                    {
                        "package_id": row["package_id"],
                        "text": text,
                        "model_id": context_policy.PINNED_MODEL_ID,
                        "settings": context_policy.PINNED_SETTINGS,
                        "tokenizer_id": context_policy.PINNED_TOKENIZER_ID,
                        "input_tokens": 100,
                        "elapsed_ms": 1,
                        "manual_actions": 0,
                    }
                )
            context_policy.write_jsonl(output / "answers.jsonl", answers)
            receipts_path = Path(directory) / "receipts.jsonl"
            context_policy.write_jsonl(receipts_path, self._receipts(key, answers))

            report = context_policy.score(
                output / "key.jsonl", output / "answers.jsonl", receipts_path, selection_path
            )

            self.assertTrue(report["gate_passed"])
            self.assertEqual(2, report["automatic_failures_prevented"])
            self.assertTrue(report["valid_for_gate"])

    def test_dry_run_cannot_pass_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation"
            context_policy.prepare(Path("scenarios.json"), output, context_policy.word_count, "words")
            key = context_policy.read_jsonl(output / "key.jsonl")
            scenarios = {row["id"]: row for row in context_policy.load_scenarios(Path("scenarios.json"))}
            answers = [
                {
                    "package_id": row["package_id"],
                    "text": scenarios[row["scenario_id"]]["expected"][0],
                    "model_id": "test-model",
                    "settings": {"temperature": 0},
                    "tokenizer_id": "words",
                    "input_tokens": 1,
                    "elapsed_ms": 1,
                    "manual_actions": 0,
                }
                for row in key
            ]
            context_policy.write_jsonl(output / "answers.jsonl", answers)

            report = context_policy.score(output / "key.jsonl", output / "answers.jsonl")

            self.assertFalse(report["valid_for_gate"])
            self.assertFalse(report["gate_passed"])

    def test_frozen_report_reproduces_exactly(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            context_policy.reproduce(Path("results/phase-1-context-policy"))
        self.assertEqual(Path("results/phase-1-context-policy.json").read_text(), output.getvalue())

    def test_frozen_answer_tampering_fails_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "phase-1-context-policy"
            shutil.copytree("results/phase-1-context-policy", artifact)
            shutil.copy("results/phase-1-context-policy.json", artifact.with_suffix(".json"))
            answers = artifact / "answers.jsonl"
            answers.write_text(answers.read_text().replace('"correct": true', '"correct": false', 1))
            with self.assertRaises(ValueError):
                context_policy.reproduce(artifact)


if __name__ == "__main__":
    unittest.main()
