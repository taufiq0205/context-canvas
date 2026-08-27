#!/usr/bin/env python3
"""Execute prepared Phase 1 packages through DeepSeek's Responses API."""

import argparse
import datetime
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

import context_policy


API_URL = "https://api.deepseek.com/responses"


def env_value(path, name):
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.removeprefix("export ").strip() == name:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if not value:
                raise ValueError(f"{name} is empty")
            return value
    raise ValueError(f"{name} is missing")


def post_response(api_key, prompt):
    payload = {
        "model": context_policy.PINNED_MODEL_ID,
        "input": prompt,
        **context_policy.PINNED_SETTINGS,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 3:
                detail = error.read(500).decode(errors="replace")
                raise RuntimeError(f"DeepSeek HTTP {error.code}: {detail}") from None
        except urllib.error.URLError as error:
            if attempt == 3:
                raise RuntimeError(f"DeepSeek request failed: {error.reason}") from None
        time.sleep(2 ** attempt)


def response_text(response):
    parts = [
        content["text"]
        for item in response.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
        if content.get("type") == "output_text"
    ]
    text = "".join(parts).strip()
    if response.get("status") != "completed" or not text:
        raise ValueError("DeepSeek response is incomplete or empty")
    return text


def receipt_from_envelope(envelope):
    response = envelope["response"]
    text = response_text(response)
    created = datetime.datetime.fromtimestamp(response["created_at"], datetime.timezone.utc)
    return {
        "package_id": envelope["package_id"],
        "prompt_sha256": envelope["prompt_sha256"],
        "answer_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "provider_response_id": response["id"],
        "model_id": response["model"],
        "settings": context_policy.PINNED_SETTINGS,
        "tokenizer_id": context_policy.PINNED_TOKENIZER_ID,
        "input_tokens": response["usage"]["input_tokens"],
        "completed_at": created.isoformat().replace("+00:00", "Z"),
    }


def execute(packages_path, output, env_path, limit=None):
    api_key = env_value(env_path, "DEEPSEEK_API_KEY")
    packages = context_policy.read_jsonl(packages_path)
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "provider-responses"
    raw_dir.mkdir(exist_ok=True)
    answers_path = output / "answers.jsonl"
    receipts_path = output / "receipts.jsonl"
    answers = context_policy.read_jsonl(answers_path) if answers_path.exists() else []
    receipts = context_policy.read_jsonl(receipts_path) if receipts_path.exists() else []
    completed = {row["package_id"] for row in answers}
    if completed != {row["package_id"] for row in receipts}:
        raise ValueError("answer and receipt checkpoints disagree")
    pending = [row for row in packages if row["package_id"] not in completed]
    if limit is not None:
        pending = pending[:limit]
    for index, package in enumerate(pending, 1):
        started = time.monotonic()
        response = post_response(api_key, package["prompt"])
        elapsed_ms = round((time.monotonic() - started) * 1000)
        text = response_text(response)
        envelope = {
            "package_id": package["package_id"],
            "prompt_sha256": package["prompt_sha256"],
            "elapsed_ms": elapsed_ms,
            "response": response,
        }
        (raw_dir / f"{package['package_id']}.json").write_text(
            json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        receipt = receipt_from_envelope(envelope)
        answer = {
            "package_id": package["package_id"],
            "text": text,
            "answer_sha256": receipt["answer_sha256"],
            "prompt_sha256": package["prompt_sha256"],
            "model_id": receipt["model_id"],
            "settings": context_policy.PINNED_SETTINGS,
            "tokenizer_id": context_policy.PINNED_TOKENIZER_ID,
            "input_tokens": receipt["input_tokens"],
            "elapsed_ms": elapsed_ms,
            "manual_actions": 0,
        }
        answers.append(answer)
        receipts.append(receipt)
        answers_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in answers))
        receipts_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in receipts))
        print(f"completed {len(completed) + index}/{len(packages)}")


def verify(raw_dir, response_id):
    envelopes = (
        [json.loads(path.read_text(encoding="utf-8")) for path in raw_dir.glob("*.json")]
        if raw_dir.is_dir()
        else context_policy.read_jsonl(raw_dir)
    )
    for envelope in envelopes:
        if envelope["response"].get("id") == response_id:
            print(json.dumps(receipt_from_envelope(envelope), sort_keys=True))
            return
    raise ValueError("provider response ID not found")


def freeze_evidence(raw_dir, output):
    envelopes = [json.loads(path.read_text(encoding="utf-8")) for path in raw_dir.glob("*.json")]
    if len(envelopes) != context_policy.PACKAGE_COUNT:
        raise ValueError(f"exactly {context_policy.PACKAGE_COUNT} provider responses are required")
    envelopes.sort(key=lambda row: row["package_id"])
    context_policy.write_jsonl(output, envelopes)


def freeze_result(prepared, execution, scored_report, artifact_dir, report_path):
    artifact_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(prepared / "key.jsonl", artifact_dir / "scoring-key.jsonl")
    shutil.copyfile(execution / "answers.jsonl", artifact_dir / "answers.jsonl")
    shutil.copyfile(execution / "receipts.jsonl", artifact_dir / "receipts.jsonl")
    evidence_path = artifact_dir / "provider-evidence.jsonl"
    if evidence_path.exists():
        evidence_path.unlink()
    freeze_evidence(execution / "provider-responses", evidence_path)
    report = json.loads(scored_report.read_text(encoding="utf-8"))
    report.update(
        {
            "answer_artifact_limitation": "Only sanitized answer text and execution metrics are frozen.",
            "execution_receipts_limitation": (
                "DeepSeek's API is stateless; sanitized response envelopes are frozen as execution evidence."
            ),
        }
    )
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    root = Path(__file__).resolve().parent
    files = {
        "scenarios.json": root / "scenarios.json",
        "selections.json": root / "selections.json",
        "scoring-key.jsonl": artifact_dir / "scoring-key.jsonl",
        "answers.jsonl": artifact_dir / "answers.jsonl",
        "receipts.jsonl": artifact_dir / "receipts.jsonl",
        "provider-evidence.jsonl": evidence_path,
        "report.json": report_path,
    }
    manifest = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "packages_sha256": context_policy.sha256_file(prepared / "packages.jsonl"),
        "files": {name: context_policy.sha256_file(path) for name, path in files.items()},
    }
    manifest_path = artifact_dir / "checksums.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(context_policy.sha256_file(manifest_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    execute_parser = commands.add_parser("execute")
    execute_parser.add_argument("--packages", type=Path, required=True)
    execute_parser.add_argument("--output", type=Path, required=True)
    execute_parser.add_argument("--env", type=Path, default=Path(".env.dev"))
    execute_parser.add_argument("--limit", type=int)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--responses", type=Path, required=True)
    verify_parser.add_argument("response_id")
    freeze_parser = commands.add_parser("freeze-evidence")
    freeze_parser.add_argument("--responses", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    result_parser = commands.add_parser("freeze-result")
    result_parser.add_argument("--prepared", type=Path, required=True)
    result_parser.add_argument("--execution", type=Path, required=True)
    result_parser.add_argument("--scored-report", type=Path, required=True)
    result_parser.add_argument("--artifacts", type=Path, required=True)
    result_parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "execute":
        execute(args.packages, args.output, args.env, args.limit)
    elif args.command == "verify":
        verify(args.responses, args.response_id)
    elif args.command == "freeze-evidence":
        freeze_evidence(args.responses, args.output)
    else:
        freeze_result(args.prepared, args.execution, args.scored_report, args.artifacts, args.report)


if __name__ == "__main__":
    main()
