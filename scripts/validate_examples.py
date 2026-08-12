#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"


SCHEMA_BY_RECORD_TYPE = {
    "reasoning_kata": SCHEMA_DIR / "reasoning-kata.schema.json",
    "trace_record": SCHEMA_DIR / "trace-record.schema.json",
    "causal_validation": SCHEMA_DIR / "causal-validation.schema.json",
    "breathing_profile": SCHEMA_DIR / "breathing-profile.schema.json",
    "kata_evolution_record": SCHEMA_DIR / "kata-evolution-record.schema.json",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def format_path(error_path: Any) -> str:
    parts = [str(part) for part in error_path]
    return ".".join(parts) if parts else "<root>"


def schema_errors(
    instance: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
) -> list[str]:
    record_type = instance.get("record_type")

    if record_type not in schemas:
        return [f"unknown record_type: {record_type!r}"]

    validator = Draft202012Validator(
        schemas[record_type],
        format_checker=FormatChecker(),
    )

    errors = sorted(
        validator.iter_errors(instance),
        key=lambda err: list(err.path),
    )

    return [
        f"{format_path(err.path)}: {err.message}"
        for err in errors
    ]


def semantic_errors(instance: dict[str, Any]) -> list[str]:
    record_type = instance.get("record_type")
    errors: list[str] = []

    if record_type == "reasoning_kata":
        step_ids = [
            step["step_id"]
            for step in instance.get("reasoning_steps", [])
        ]

        if len(step_ids) != len(set(step_ids)):
            errors.append(
                "reasoning_steps: step_id values must be unique"
            )

        created_at = instance.get("created_at")
        updated_at = instance.get("updated_at")

        if created_at and updated_at and updated_at < created_at:
            errors.append(
                "updated_at must not be earlier than created_at"
            )

    elif record_type == "trace_record":
        mode = instance.get("execution_mode")
        kata_id = instance.get("applied_kata_id")

        if mode == "kata" and not kata_id:
            errors.append(
                "execution_mode 'kata' requires applied_kata_id"
            )

        if mode == "direct" and kata_id is not None:
            errors.append(
                "execution_mode 'direct' should not declare applied_kata_id"
            )

        step_ids = [
            step["step_id"]
            for step in instance.get("execution_steps", [])
        ]

        if len(step_ids) != len(set(step_ids)):
            errors.append(
                "execution_steps: step_id values must be unique"
            )

    elif record_type == "causal_validation":
        method = instance.get("method")
        conclusion = instance.get("conclusion")

        if method == "not_run" and conclusion != "not_tested":
            errors.append(
                "method 'not_run' requires conclusion 'not_tested'"
            )

        baseline = instance.get("baseline_score")
        ablated = instance.get("ablated_score")
        delta = instance.get("contribution_delta")

        if (
            baseline is not None
            and ablated is not None
            and delta is not None
        ):
            expected = baseline - ablated

            if not math.isclose(
                delta,
                expected,
                abs_tol=1e-6,
            ):
                errors.append(
                    "contribution_delta must equal "
                    "baseline_score - ablated_score "
                    f"(expected {expected:.6f}, got {delta:.6f})"
                )

    elif record_type == "breathing_profile":
        level = instance.get("level")
        budget = instance.get("reasoning_budget_class")

        recommended = {
            "rest": "minimal",
            "kata": "bounded",
            "deep": "extended",
        }

        expected = recommended.get(level)

        if expected and budget != expected:
            errors.append(
                f"level {level!r} requires "
                f"reasoning_budget_class {expected!r} "
                "in v0.1 examples"
            )

    elif record_type == "kata_evolution_record":
        from_version = instance.get("from_version")
        to_version = instance.get("to_version")
        rollback = instance.get("rollback_target_version")

        if from_version == to_version:
            errors.append(
                "from_version and to_version must differ"
            )

        if rollback != from_version:
            errors.append(
                "rollback_target_version must equal "
                "from_version in v0.1"
            )

        changed_steps = instance.get("changed_steps", {})

        total_changes = sum(
            len(changed_steps.get(key, []))
            for key in ("added", "modified", "removed")
        )

        if total_changes == 0:
            errors.append(
                "changed_steps must contain at least one change"
            )

    return errors


def validate_file(
    path: Path,
    schemas: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str]]:
    try:
        instance = load_yaml(path)
    except Exception as exc:
        return [f"YAML parse error: {exc}"], []

    if not isinstance(instance, dict):
        return ["document root must be a mapping/object"], []

    s_errors = schema_errors(instance, schemas)

    if s_errors:
        return s_errors, []

    return [], semantic_errors(instance)


def iter_examples(directory: Path) -> list[Path]:
    return sorted([
        *directory.glob("*.yaml"),
        *directory.glob("*.yml"),
    ])


def main() -> int:
    print(
        "=== ZEROSHIKI Reasoning OS v0.1 Validation ==="
    )

    schemas: dict[str, dict[str, Any]] = {}

    for record_type, path in SCHEMA_BY_RECORD_TYPE.items():
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)

        schemas[record_type] = schema

        print(
            f"schema [{record_type}]: "
            f"{path.relative_to(ROOT)}"
        )

    print("\n[pass examples]\n")

    pass_failed = False

    for path in iter_examples(PASS_DIR):
        print(f"- {path.relative_to(ROOT)}")

        s_errors, sem_errors = validate_file(
            path,
            schemas,
        )

        if s_errors:
            pass_failed = True

            print("  [schema-error]")

            for error in s_errors:
                print(f"    - {error}")

            continue

        print("  [schema-ok]")

        if sem_errors:
            pass_failed = True

            print("  [semantic-error]")

            for error in sem_errors:
                print(f"    - {error}")
        else:
            print("  [semantic-ok]")

    print("\n[fail examples]\n")

    fail_failed = False

    for path in iter_examples(FAIL_DIR):
        print(f"- {path.relative_to(ROOT)}")

        s_errors, sem_errors = validate_file(
            path,
            schemas,
        )

        if s_errors:
            print("  [expected-schema-failure]")

            for error in s_errors:
                print(f"    - {error}")

        elif sem_errors:
            print("  [expected-semantic-failure]")

            for error in sem_errors:
                print(f"    - {error}")

        else:
            fail_failed = True
            print("  [unexpected-pass]")

    print("\n=== Summary ===")

    if pass_failed or fail_failed:
        print("[validation-failed]")
        return 1

    print("[validation-ok]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
