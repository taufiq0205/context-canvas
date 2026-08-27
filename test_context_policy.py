import json
import tempfile
import unittest
from pathlib import Path

import context_policy


class ContextPolicyTest(unittest.TestCase):
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
            context_policy.prepare(
                Path("scenarios.json"), output, context_policy.word_count, context_policy.PINNED_TOKENIZER_ID
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

            report = context_policy.score(output / "key.jsonl", output / "answers.jsonl")

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


if __name__ == "__main__":
    unittest.main()
