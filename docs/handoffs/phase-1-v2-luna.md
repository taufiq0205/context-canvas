# Luna handoff: Phase 1 v2 context-policy gate

## Objective

Implement [Issue #5](https://github.com/taufiq0205/context-canvas/issues/5) and continue until the canvas is either legitimately unblocked or a valid negative v2 result requires stopping.

## Start

1. Work on `phase-1-context-policy`; pull its latest remote commit.
2. Read Issue #5, `CONTEXT.md`, ADR 0002, `docs/context-policy-evaluation.md`, and the frozen v1 report.
3. Run v1 reproduction and tests before editing. Completion: both pass and v1 hashes are recorded for later comparison.
4. Use `$diagnosing-bugs` for the v1 non-discrimination, `$ponytail full` for implementation, then `$code-review` against `main`.

## Fixed evidence

- V1 is immutable: `results/phase-1-context-policy/` and `results/phase-1-context-policy.json`.
- V1 was a valid 48-call DeepSeek run: `valid_for_gate: true`, `gate_passed: false`, 0 automatic failures prevented, 0 explicit failures added.
- Root defect: destination instructions revealed expected answers; whole-response exact scoring was also brittle.
- The user explicitly confirmed all eight selections on 2026-08-27.
- Reuse the same source evidence, source artifact/version pairs, and selected source IDs. Changes to those require fresh user confirmation.
- `.env.dev` contains `DEEPSEEK_API_KEY` and is ignored. Access it only through the runner; keep its value out of output, commits, and prompts.

## Execution

1. Pre-register neutral v2 tasks and structured answer-field scoring exactly as Issue #5 specifies. Completion: static tests prove no expected/forbidden answer leaks through titles/instructions and v1 files remain byte-identical.
2. Prepare v2 packages without exposing the scoring key to the model. Completion: 48 unique packages, unchanged 8 × 2 × 3 design, and differing explicit/automatic context packages.
3. Make one API smoke call. Continue only when model/settings/token accounting and receipt binding match the registration.
4. Execute the remaining calls with checkpoints, freeze v2 under `results/phase-1-context-policy-v2/`, and reproduce it offline.
5. Run tests, compilation, `git diff --check`, and a secret/privacy scan. Preserve `docs/private/` and unrelated working-tree changes.
6. Run `$code-review`, fix valid high/medium findings, commit, and push only `phase-1-context-policy`.

## Stop conditions

- If v2 has `valid_for_gate: true` and `gate_passed: true`, document that ADR 0002 unblocks canvas work, update Issue #1/#5, and stop before implementing canvas.
- If v2 is valid but negative, preserve it, document why canvas remains blocked, update Issue #5, and stop. Treat this as evidence; do not tune the gate or create v3.
- If execution is invalid, repair only the tooling defect and resume the same pre-registered v2. Changes to evidence, selections, model, or threshold require user approval.

## Deliverable

Return the branch commit, pushed remote state, review result, exact v2 metrics, reproduction command, and one sentence stating whether canvas work is unblocked.
