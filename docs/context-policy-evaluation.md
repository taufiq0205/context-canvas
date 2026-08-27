# Context-policy evaluation harness

This implements only ADR 0002: eight redacted workflow scenarios × two policies × three runs = 48 blinded prompts. It does not build a canvas or provide a provider/IDE integration.

## Evidence and registration

`scenarios.json` contains two scenarios each for stale, conflicting, irrelevant, and adversarial context. The scenarios are anonymized paraphrases of the eight private Phase 1 workflow records. `selections.json` is the separate record of the context selected in each observed workflow; it contains no expected or forbidden scoring data. Each record includes `selection_kind` (`user_explicit`, `workflow_observed`, or `inferred`), redacted task/session/run provenance, selected source artifact/version pairs, and a recorded date. The committed records are `workflow_observed`; no user confirmation is available, so they cannot validate the explicit-policy gate.

Some recorded workflows have no task, session, run, or subagent provenance. The fixtures retain that limitation as `not recorded in source` or `redacted from committed fixture`; no multi-agent provenance is invented. Private source files remain ignored and are never part of a commit.

Every generated source block includes task, run, artifact, and version fields. Source text is non-authoritative data. Explicit packages use only the source IDs in `selections.json`; automatic retrieval searches every non-deleted source version in the SQLite workspace except the destination task and does not use graph edges as a filter.

The prepared SQLite workspace contains the minimal `tasks`, `context_edges`, `versions`, `selections`, and immutable `handoff_snapshots` records, plus the FTS5 `sources` table. Snapshot updates and deletes fail.

## Prepare

Use one fresh output directory. The command below uses `whitespace-v1` only as a deterministic preflight counter; scored `input_tokens` use the pinned `gpt-5.6-sol-provider-input-v1` model-input tokenizer and must stay within the pre-registered ceiling.

```bash
RUN_ROOT=$(mktemp -d)
python3 context_policy.py prepare \
  --output "$RUN_ROOT/prepared" \
  --token-counter-command "python3 -c 'import sys; print(len(sys.stdin.read().split()))'" \
  --tokenizer-id gpt-5.6-sol-provider-input-v1
```

The command creates `packages.jsonl`, `key.jsonl`, `answers.template.jsonl`, and `corpus.sqlite3`. Keep `key.jsonl` private from scoring. If explicit content exceeds its ceiling, preparation stops and writes `validation.json` with `actual_tokens`, `token_ceiling`, and `excess_tokens`; it never truncates or summarizes.

## Execute

Send every row in `packages.jsonl` to the same pinned model and settings, without exposing `key.jsonl` to the model or scorer. The Phase 1 execution used `gpt-5.6-sol`, reasoning effort `low`, temperature `0`, and `gpt-5.6-sol-provider-input-v1`; record one answer row per package:

```json
{"package_id":"...","text":"...","model_id":"gpt-5.6-sol","settings":{"reasoning_effort":"low","temperature":0},"tokenizer_id":"gpt-5.6-sol-provider-input-v1","input_tokens":123,"elapsed_ms":456,"manual_actions":0}
```

`input_tokens` is the model/provider-reported input count, not the `whitespace-v1` preflight estimate. The model ID, settings, provider-input tokenizer ID, and token ceiling must not vary across the 48 rows. `manual_actions` is zero for this scripted run.

Also record one sanitized provider receipt per response, separately from the answer rows:

```json
{"package_id":"...","prompt_sha256":"...","answer_sha256":"...","provider_response_id":"...","model_id":"gpt-5.6-sol","settings":{"reasoning_effort":"low","temperature":0},"tokenizer_id":"gpt-5.6-sol-provider-input-v1","input_tokens":123,"completed_at":"2026-08-27T00:00:00Z"}
```

The receipt hash binds to the exact prepared prompt and answer text. Scoring requires exactly 48 unique, internally matching receipts; answer metadata alone never validates execution. The committed fixture has no genuine provider receipts, so its gate remains invalid.

Unit-test receipts are synthetic binding doubles only; they are not committed or presented as provider execution evidence.

The frozen artifact under `results/phase-1-context-policy/` contains the scoring key and 48 outcome-only sanitized answer rows. Raw answer text and answer hashes were not available in the checkout, so each row records `answer_status: "answer_text_unavailable"` and `answer_sha256: null`; this is a limitation marker, not fabricated provider evidence.

## Score

```bash
python3 context_policy.py score \
  --key "$RUN_ROOT/prepared/key.jsonl" \
  --answers "$RUN_ROOT/prepared/answers.jsonl" \
  --receipts "$RUN_ROOT/prepared/receipts.jsonl" \
  --output "$RUN_ROOT/prepared/report.json"
```

Scoring requires exactly 48 unique answers and exactly 48 matching provider receipts. Correctness is a 2-of-3 majority per scenario and condition. Any forbidden or stale fact in any of the three runs fails that scenario. The gate passes only when explicit selection prevents at least two automatic-retrieval scenario failures and adds none. `valid_for_gate` is also false unless all eight selection records are `user_explicit`; it is false for the word-count dry run, inconsistent model/settings/tokenizer records, incomplete calls, missing or inconsistent receipts, or provider-reported input tokens above the shared ceiling.

The committed result artifact is sanitized: it contains validation status, pinned execution metadata, scenario-level outcomes, hashes, and aggregate metrics, but no prompts, source text, answer text, private paths, credentials, or linkable workflow identifiers. A passing result is not a market or canvas-usability claim; canvas work remains blocked unless both `valid_for_gate` and `gate_passed` are true.

## Offline reproduction

Run this exact offline command from the repository root:

```bash
python3 context_policy.py reproduce --artifacts results/phase-1-context-policy
```

It regenerates the blinded packages and scoring key, verifies SHA-256 checksums for the scenarios, selections, packages, scoring key, sanitized answers, and report, validates the frozen outcomes, and emits the exact committed report. Any tampering fails verification before output.
