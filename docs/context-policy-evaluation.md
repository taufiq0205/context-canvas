# Context-policy evaluation harness

This implements only ADR 0002: eight redacted workflow scenarios × two policies × three runs = 48 blinded prompts. It does not build a canvas or provide a provider/IDE integration.

## Evidence and registration

`scenarios.json` contains two scenarios each for stale, conflicting, irrelevant, and adversarial context. The scenarios are anonymized paraphrases of the eight private Phase 1 workflow records. `selections.json` is the separate record of the selected context; it contains no expected or forbidden scoring data. Each record includes `selection_kind` (`user_explicit`, `workflow_observed`, or `inferred`), redacted task/session/run provenance, selected source artifact/version pairs, and a recorded date. The user explicitly confirmed all eight committed selections on 2026-08-27.

Some recorded workflows have no task, session, run, or subagent provenance. The fixtures retain that limitation as `not recorded in source` or `redacted from committed fixture`; no multi-agent provenance is invented. Private source files remain ignored and are never part of a commit.

Every generated source block includes task, run, artifact, and version fields. Source text is non-authoritative data. Explicit packages use only the source IDs in `selections.json`; automatic retrieval searches every non-deleted source version in the SQLite workspace except the destination task and does not use graph edges as a filter.

The prepared SQLite workspace contains the minimal `tasks`, `context_edges`, `versions`, `selections`, and immutable `handoff_snapshots` records, plus the FTS5 `sources` table. Snapshot updates and deletes fail.

## Prepare

Use one fresh output directory. The command below uses `whitespace-v1` only as a deterministic preflight counter; scored `input_tokens` use DeepSeek's provider-reported count and must stay within the pre-registered ceiling.

```bash
RUN_ROOT=$(mktemp -d)
python3 context_policy.py prepare \
  --output "$RUN_ROOT/prepared" \
  --token-counter-command "python3 -c 'import sys; print(len(sys.stdin.read().split()))'" \
  --tokenizer-id deepseek-v4-flash-provider-input-v1
```

The command creates `packages.jsonl`, `key.jsonl`, `answers.template.jsonl`, and `corpus.sqlite3`. Keep `key.jsonl` private from scoring. If explicit content exceeds its ceiling, preparation stops and writes `validation.json` with `actual_tokens`, `token_ceiling`, and `excess_tokens`; it never truncates or summarizes.

## Execute

Send every row in `packages.jsonl` to the same pinned model and settings, without exposing `key.jsonl` to the model. The frozen Phase 1 execution used `deepseek-v4-flash`, thinking disabled, temperature `0`, and a 64-token output ceiling:

```json
{"package_id":"...","text":"...","model_id":"deepseek-v4-flash","settings":{"max_output_tokens":64,"reasoning":{"effort":"none"},"temperature":0},"tokenizer_id":"deepseek-v4-flash-provider-input-v1","input_tokens":123,"elapsed_ms":456,"manual_actions":0}
```

`input_tokens` is the model/provider-reported input count, not the `whitespace-v1` preflight estimate. The model ID, settings, provider-input tokenizer ID, and token ceiling must not vary across the 48 rows. `manual_actions` is zero for this scripted run.

Also record one sanitized provider receipt per response, separately from the answer rows:

```json
{"package_id":"...","prompt_sha256":"...","answer_sha256":"...","provider_response_id":"...","model_id":"deepseek-v4-flash","settings":{"max_output_tokens":64,"reasoning":{"effort":"none"},"temperature":0},"tokenizer_id":"deepseek-v4-flash-provider-input-v1","input_tokens":123,"completed_at":"2026-08-27T00:00:00Z"}
```

The receipt hash binds to the exact prepared prompt and answer text. Scoring requires exactly 48 unique, internally matching receipts plus captured provider response evidence. Supply credentials only through the ignored `.env.dev`; never place them in arguments or artifacts. Caller-authored receipt rows alone never validate execution. DeepSeek's Responses API is stateless, so the sanitized response envelopes are frozen for offline verification.

Unit-test receipts are synthetic binding doubles only; they are not committed or presented as provider execution evidence.

The frozen artifact under `results/phase-1-context-policy/` contains the scoring key, 48 sanitized answer rows, 48 receipts, and 48 sanitized provider response envelopes.

## Score

```bash
python3 context_policy.py score \
  --key "$RUN_ROOT/prepared/key.jsonl" \
  --answers "$RUN_ROOT/prepared/answers.jsonl" \
  --receipts "$RUN_ROOT/prepared/receipts.jsonl" \
  --receipt-verifier-command "python3 deepseek_run.py verify --responses results/phase-1-context-policy/provider-evidence.jsonl" \
  --output "$RUN_ROOT/prepared/report.json"
```

Scoring requires exactly 48 unique answers and exactly 48 matching, independently verified provider receipts. Correctness is a 2-of-3 majority per scenario and condition. Any forbidden or stale fact in any of the three runs fails that scenario. The gate passes only when explicit selection prevents at least two automatic-retrieval scenario failures and adds none. `valid_for_gate` is also false unless all eight selection records are `user_explicit`; it is false for the word-count dry run, inconsistent model/settings/tokenizer records, incomplete calls, missing or unverified receipts, or provider-reported input tokens above the shared ceiling.

The committed result artifact contains sanitized answer text, provider evidence, validation status, pinned execution metadata, hashes, and aggregate metrics, but no prompts, source text, private paths, credentials, or workflow identifiers. The run is valid, but the gate failed because explicit selection prevented no automatic failures. Canvas work remains blocked.

## v2 registration

Issue #5 uses `scenarios-v2.json`, a small overlay over the immutable `scenarios.json`. It changes only the eight destination questions and adds a JSON answer envelope; source evidence, expected/forbidden scoring values, and `selections.json` remain bound to the canonical fixtures. The model sees neutral destination questions and is told to return exactly `{"answer":"..."}`. Scoring parses that field and ignores no longer relevant envelope text.

Prepare v2 with the same preflight counter and pinned provider-input tokenizer:

```bash
RUN_ROOT=$(mktemp -d)
python3 context_policy.py prepare \
  --scenarios scenarios-v2.json \
  --selections selections.json \
  --output "$RUN_ROOT/prepared" \
  --token-counter-command "python3 -c 'import sys; print(len(sys.stdin.read().split()))'" \
  --tokenizer-id deepseek-v4-flash-provider-input-v1
```

Preparation stops unless `validation.json` proves destination-answer hiding, unchanged confirmed selections and source evidence, differing explicit/automatic packages, unchanged v1 checksums, and 48 unique packages. Keep the scoring key private from execution. Execute the packages through the same pinned DeepSeek runner, score with independently verified receipts, and freeze to `results/phase-1-context-policy-v2/` using `deepseek_run.py freeze-result --scenarios scenarios-v2.json`. Reproduce with:

```bash
python3 context_policy.py reproduce --artifacts results/phase-1-context-policy-v2
```

The ADR threshold is unchanged: canvas work is unblocked only when v2 is valid and explicit selection prevents at least two automatic scenario failures without adding any primary failures. A valid negative v2 result is terminal evidence for this experiment.

## Offline reproduction

Run this exact offline command from the repository root:

```bash
python3 context_policy.py reproduce --artifacts results/phase-1-context-policy
```

It verifies the trusted checksum manifest, regenerates the packages/key, validates all answer and provider-evidence bindings, rescoring every answer, and emits the exact committed report.
