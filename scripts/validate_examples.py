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
    "reasoning_kata":
        SCHEMA_DIR / "reasoning-kata.schema.json",

    "trace_record":
        SCHEMA_DIR / "trace-record.schema.json",

    "causal_validation":
        SCHEMA_DIR / "causal-validation.schema.json",

    "breathing_profile":
        SCHEMA_DIR / "breathing-profile.schema.json",

    "kata_evolution_record":
        SCHEMA_DIR / "kata-evolution-record.schema.json",

    "failure_boundary":
        SCHEMA_DIR / "failure-boundary.schema.json",

    "applicability_assessment":
        SCHEMA_DIR / "applicability-assessment.schema.json",
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


def local_semantic_errors(
    instance: dict[str, Any],
) -> list[str]:

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

        if (
            created_at
            and updated_at
            and updated_at < created_at
        ):
            errors.append(
                "updated_at must not be earlier than created_at"
            )

    elif record_type == "trace_record":

        mode = instance.get("execution_mode")
        kata_id = instance.get("applied_kata_id")

        assessment_id = instance.get(
            "applicability_assessment_id"
        )

        if mode == "kata":

            if not kata_id:
                errors.append(
                    "execution_mode 'kata' "
                    "requires applied_kata_id"
                )

            if not assessment_id:
                errors.append(
                    "execution_mode 'kata' requires "
                    "applicability_assessment_id"
                )

        if mode in {"direct", "deep"}:

            if kata_id is not None:
                errors.append(
                    f"execution_mode {mode!r} must not "
                    "declare applied_kata_id"
                )

            if assessment_id is not None:
                errors.append(
                    f"execution_mode {mode!r} must not declare "
                    "applicability_assessment_id"
                )

    elif record_type == "causal_validation":

        method = instance.get("method")
        conclusion = instance.get("conclusion")
        intervention = instance.get("intervention", {})

        if method == "not_run":

            if conclusion != "not_tested":
                errors.append(
                    "method 'not_run' requires "
                    "conclusion 'not_tested'"
                )

            if intervention.get("kind") != "none":
                errors.append(
                    "method 'not_run' requires "
                    "intervention.kind 'none'"
                )

        baseline = instance.get("baseline_score")

        intervention_score = instance.get(
            "intervention_score"
        )

        delta = instance.get("effect_delta")

        threshold = instance.get(
            "minimum_effect_threshold"
        )

        if (
            baseline is not None
            and intervention_score is not None
            and delta is not None
        ):

            expected = (
                baseline - intervention_score
            )

            if not math.isclose(
                delta,
                expected,
                abs_tol=1e-6,
            ):
                errors.append(
                    "effect_delta must equal "
                    "baseline_score - intervention_score"
                )

        if conclusion == "supported":

            if method == "not_run":
                errors.append(
                    "supported conclusion cannot "
                    "use method 'not_run'"
                )

            if delta is None:
                errors.append(
                    "supported conclusion "
                    "requires effect_delta"
                )

            elif (
                threshold is not None
                and delta < threshold
            ):
                errors.append(
                    "supported conclusion requires "
                    "effect_delta >= "
                    "minimum_effect_threshold"
                )

    elif record_type == "breathing_profile":

        level = instance.get("level")

        budget = instance.get(
            "reasoning_budget_class"
        )

        mapping = {
            "rest": "minimal",
            "kata": "bounded",
            "deep": "extended",
        }

        expected = mapping.get(level)

        if (
            expected
            and budget != expected
        ):
            errors.append(
                f"level {level!r} requires "
                f"reasoning_budget_class "
                f"{expected!r}"
            )

    elif record_type == "applicability_assessment":

        score = instance.get(
            "intent_match_score"
        )

        threshold = instance.get(
            "minimum_match_score"
        )

        conditions = instance.get(
            "required_conditions",
            [],
        )

        decision = instance.get("decision")

        selected = instance.get(
            "selected_breathing_level"
        )

        expected_level = {
            "reuse": "kata",
            "escalate": "deep",
            "reject": "none",
        }.get(decision)

        if (
            expected_level
            and selected != expected_level
        ):
            errors.append(
                f"decision {decision!r} requires "
                f"selected_breathing_level "
                f"{expected_level!r}"
            )

        if decision == "reuse":

            if (
                score is not None
                and threshold is not None
                and score < threshold
            ):
                errors.append(
                    "reuse decision requires "
                    "intent_match_score >= "
                    "minimum_match_score"
                )

            if any(
                not condition.get("met", False)
                for condition in conditions
            ):
                errors.append(
                    "reuse decision requires all "
                    "required_conditions to be met"
                )

    elif record_type == "kata_evolution_record":

        from_version = instance.get(
            "from_version"
        )

        to_version = instance.get(
            "to_version"
        )

        rollback = instance.get(
            "rollback_target_version"
        )

        if from_version == to_version:
            errors.append(
                "from_version and to_version "
                "must differ"
            )

        if rollback != from_version:
            errors.append(
                "rollback_target_version must "
                "equal from_version in v0.2"
            )

    return errors


def build_registry(
    records: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:

    registry = {
        record_type: {}
        for record_type in SCHEMA_BY_RECORD_TYPE
    }

    id_fields = {
        "reasoning_kata": "kata_id",
        "trace_record": "trace_id",
        "causal_validation": "validation_id",
        "breathing_profile": "profile_id",
        "kata_evolution_record": "evolution_id",
        "failure_boundary": "boundary_id",
        "applicability_assessment": "assessment_id",
    }

    for record in records:

        record_type = record["record_type"]

        key = record.get(
            id_fields[record_type]
        )

        if key:
            registry[record_type][key] = record

    return registry


def cross_semantic_errors(
    instance: dict[str, Any],
    registry: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:

    record_type = instance.get("record_type")
    errors: list[str] = []

    if record_type == "reasoning_kata":

        for boundary_id in instance.get(
            "failure_boundary_ids",
            [],
        ):
            if boundary_id not in registry[
                "failure_boundary"
            ]:
                errors.append(
                    f"unknown failure_boundary_id "
                    f"{boundary_id!r}"
                )

    elif record_type == "applicability_assessment":

        kata_id = instance.get("kata_id")

        kata = registry[
            "reasoning_kata"
        ].get(kata_id)

        if kata is None:
            errors.append(
                f"unknown kata_id {kata_id!r}"
            )
            return errors

        expected_threshold = (
            kata["applicability_policy"]
            ["minimum_match_score"]
        )

        actual_threshold = instance.get(
            "minimum_match_score"
        )

        if not math.isclose(
            actual_threshold,
            expected_threshold,
            abs_tol=1e-9,
        ):
            errors.append(
                "minimum_match_score must "
                "match the KATA applicability policy"
            )

        configured = set(
            kata.get(
                "failure_boundary_ids",
                [],
            )
        )

        checked = {
            check["boundary_id"]
            for check
            in instance.get(
                "boundary_checks",
                [],
            )
        }

        if configured != checked:
            errors.append(
                "boundary_checks must cover "
                "exactly the KATA "
                "failure_boundary_ids"
            )

        actions: list[str] = []

        for check in instance.get(
            "boundary_checks",
            [],
        ):

            if not check["matched"]:
                continue

            boundary = registry[
                "failure_boundary"
            ].get(
                check["boundary_id"]
            )

            if boundary:
                actions.append(
                    boundary["on_match"]
                )

        decision = instance.get(
            "decision"
        )

        if "fail_closed" in actions:

            if decision != "reject":
                errors.append(
                    "matched fail_closed boundary "
                    "requires decision 'reject'"
                )

        elif "reject_reuse" in actions:

            if decision == "reuse":
                errors.append(
                    "matched reject_reuse boundary "
                    "forbids decision 'reuse'"
                )

        elif "escalate_to_deep" in actions:

            if decision == "reuse":
                errors.append(
                    "matched escalate_to_deep boundary "
                    "forbids decision 'reuse'"
                )

    elif record_type == "trace_record":

        if instance.get(
            "execution_mode"
        ) == "kata":

            kata_id = instance.get(
                "applied_kata_id"
            )

            assessment_id = instance.get(
                "applicability_assessment_id"
            )

            assessment = registry[
                "applicability_assessment"
            ].get(
                assessment_id
            )

            if (
                assessment is not None
                and assessment["kata_id"] != kata_id
            ):
                errors.append(
                    "applicability assessment "
                    "targets a different KATA"
                )

            if (
                assessment is not None
                and assessment["decision"] != "reuse"
            ):
                errors.append(
                    "KATA execution requires "
                    "applicability decision 'reuse'"
                )

    return errors


def iter_examples(
    directory: Path,
) -> list[Path]:

    return sorted([
        *directory.glob("*.yaml"),
        *directory.glob("*.yml"),
    ])


def load_instance(
    path: Path,
) -> dict[str, Any]:

    instance = load_yaml(path)

    if not isinstance(instance, dict):
        raise ValueError(
            "document root must be a mapping"
        )

    return instance


def main() -> int:

    print(
        "=== ZEROSHIKI Reasoning OS "
        "v0.2 Validation ==="
    )

    schemas = {}

    for (
        record_type,
        path,
    ) in SCHEMA_BY_RECORD_TYPE.items():

        schema = load_json(path)

        Draft202012Validator.check_schema(
            schema
        )

        schemas[record_type] = schema

        print(
            f"schema [{record_type}]: "
            f"{path.relative_to(ROOT)}"
        )

    pass_records = []

    for path in iter_examples(PASS_DIR):

        instance = load_instance(path)

        if (
            not schema_errors(
                instance,
                schemas,
            )
            and not local_semantic_errors(
                instance
            )
        ):
            pass_records.append(instance)

    registry = build_registry(
        pass_records
    )

    print("\n[pass examples]\n")

    pass_failed = False

    for path in iter_examples(PASS_DIR):

        print(
            f"- {path.relative_to(ROOT)}"
        )

        instance = load_instance(path)

        s_errors = schema_errors(
            instance,
            schemas,
        )

        if s_errors:

            pass_failed = True
            print("  [schema-error]")

            for error in s_errors:
                print(f"    - {error}")

            continue

        print("  [schema-ok]")

        sem_errors = (
            local_semantic_errors(instance)
            + cross_semantic_errors(
                instance,
                registry,
            )
        )

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

        print(
            f"- {path.relative_to(ROOT)}"
        )

        instance = load_instance(path)

        s_errors = schema_errors(
            instance,
            schemas,
        )

        if s_errors:

            print(
                "  [expected-schema-failure]"
            )

            for error in s_errors:
                print(f"    - {error}")

            continue

        temp_registry = build_registry(
            pass_records + [instance]
        )

        sem_errors = (
            local_semantic_errors(instance)
            + cross_semantic_errors(
                instance,
                temp_registry,
            )
        )

        if sem_errors:

            print(
                "  [expected-semantic-failure]"
            )

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
