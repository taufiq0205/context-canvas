# Context-policy evaluation harness

Implements only the two-condition gate in [ADR 0002](adr/0002-stage-policy-before-canvas.md): eight scenarios × two policies × three runs = 48 blinded prompts. It does not call a model or build a canvas.

## Prepare

For a local dry run:

```bash
python3 context_policy.py prepare --output /tmp/context-policy-dry-run
```

For a gate-valid run, provide a pinned model tokenizer command that reads prompt text from stdin and prints one integer:

```bash
python3 context_policy.py prepare \
  --output /tmp/context-policy-run \
  --token-counter-command './count_tokens' \
  --tokenizer-id '<model-id>:<tokenizer-version>'
```

Send each row in `packages.jsonl` to the same pinned model at temperature 0. Do not expose `key.jsonl` to a human scorer. Record one `answers.jsonl` row per package:

```json
{"package_id":"...","text":"...","model_id":"...","settings":{"temperature":0},"input_tokens":123,"elapsed_ms":456,"manual_actions":0}
```

## Score

```bash
python3 context_policy.py score \
  --key /tmp/context-policy-run/key.jsonl \
  --answers /tmp/context-policy-run/answers.jsonl \
  --output /tmp/context-policy-run/report.json
```

The gate passes only when explicit selection prevents at least two automatic-retrieval scenario failures and adds none. Correctness uses majority across three runs; any forbidden or stale emission fails that scenario. `valid_for_gate` is false for the word-count dry run or when provider-reported input tokens exceed the shared ceiling.

The bundled scenarios are redacted fixtures derived from decisions recorded in this project's ADRs and `CONTEXT.md`, with synthetic stale, conflicting, irrelevant, and adversarial distractors.
