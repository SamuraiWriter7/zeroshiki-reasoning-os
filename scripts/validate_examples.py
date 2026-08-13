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

    "kata_lineage":
        SCHEMA_DIR / "kata-lineage.schema.json",

    "kata_composition":
        SCHEMA_DIR / "kata-composition.schema.json",

    "kata_maturity_assessment":
        SCHEMA_DIR / "kata-maturity-assessment.schema.json",
}


ID_FIELD_BY_RECORD_TYPE = {
    "reasoning_kata": "kata_id",
    "trace_record": "trace_id",
    "causal_validation": "validation_id",
    "breathing_profile": "profile_id",
    "kata_evolution_record": "evolution_id",
    "failure_boundary": "boundary_id",
    "applicability_assessment": "assessment_id",
    "kata_lineage": "lineage_id",
    "kata_composition": "composition_id",
    "kata_maturity_assessment": "assessment_id",
}


MATURITY_RANK = {
    "K0": 0,
    "K1": 1,
    "K2": 2,
    "K3": 3,
    "K4": 4,
    "K5": 5,
}


# ----------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_instance(path: Path) -> dict[str, Any]:
    instance = load_yaml(path)

    if not isinstance(instance, dict):
        raise ValueError(
            "document root must be a mapping/object"
        )

    return instance


def iter_examples(directory: Path) -> list[Path]:
    return sorted([
        *directory.glob("*.yaml"),
        *directory.glob("*.yml"),
    ])


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------

def format_path(error_path: Any) -> str:
    parts = [
        str(part)
        for part in error_path
    ]

    return ".".join(parts) if parts else "<root>"


def kata_ref_key(
    ref: dict[str, Any],
) -> tuple[str, str]:
    return (
        ref["kata_id"],
        ref["version"],
    )


def format_kata_ref(
    ref: dict[str, Any],
) -> str:
    return (
        f"{ref['kata_id']}@"
        f"{ref['version']}"
    )


# ----------------------------------------------------------------------
# JSON Schema validation
# ----------------------------------------------------------------------

def schema_errors(
    instance: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
) -> list[str]:

    record_type = instance.get(
        "record_type"
    )

    if record_type not in schemas:
        return [
            f"unknown record_type: "
            f"{record_type!r}"
        ]

    validator = Draft202012Validator(
        schemas[record_type],
        format_checker=FormatChecker(),
    )

    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: list(error.path),
    )

    return [
        (
            f"{format_path(error.path)}: "
            f"{error.message}"
        )
        for error in errors
    ]


# ----------------------------------------------------------------------
# Local semantic validation
# ----------------------------------------------------------------------

def local_semantic_errors(
    instance: dict[str, Any],
) -> list[str]:

    record_type = instance.get(
        "record_type"
    )

    errors: list[str] = []

    # ------------------------------------------------------------------
    # ReasoningKATA
    # ------------------------------------------------------------------

    if record_type == "reasoning_kata":

        step_ids = [
            step["step_id"]
            for step
            in instance.get(
                "reasoning_steps",
                [],
            )
        ]

        if len(step_ids) != len(set(step_ids)):
            errors.append(
                "reasoning_steps: "
                "step_id values must be unique"
            )

        created_at = instance.get(
            "created_at"
        )

        updated_at = instance.get(
            "updated_at"
        )

        if (
            created_at
            and updated_at
            and updated_at < created_at
        ):
            errors.append(
                "updated_at must not be "
                "earlier than created_at"
            )

    # ------------------------------------------------------------------
    # TraceRecord
    # ------------------------------------------------------------------

    elif record_type == "trace_record":

        mode = instance.get(
            "execution_mode"
        )

        kata_id = instance.get(
            "applied_kata_id"
        )

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
                    "execution_mode 'kata' "
                    "requires "
                    "applicability_assessment_id"
                )

        elif mode in {
            "direct",
            "deep",
        }:

            if kata_id is not None:
                errors.append(
                    f"execution_mode {mode!r} "
                    "must not declare "
                    "applied_kata_id"
                )

            if assessment_id is not None:
                errors.append(
                    f"execution_mode {mode!r} "
                    "must not declare "
                    "applicability_assessment_id"
                )

        step_ids = [
            step["step_id"]
            for step
            in instance.get(
                "execution_steps",
                [],
            )
        ]

        if len(step_ids) != len(set(step_ids)):
            errors.append(
                "execution_steps: "
                "step_id values must be unique"
            )

    # ------------------------------------------------------------------
    # CausalValidation
    # ------------------------------------------------------------------

    elif record_type == "causal_validation":

        method = instance.get(
            "method"
        )

        conclusion = instance.get(
            "conclusion"
        )

        intervention = instance.get(
            "intervention",
            {},
        )

        if method == "not_run":

            if conclusion != "not_tested":
                errors.append(
                    "method 'not_run' requires "
                    "conclusion 'not_tested'"
                )

            if intervention.get(
                "kind"
            ) != "none":
                errors.append(
                    "method 'not_run' requires "
                    "intervention.kind 'none'"
                )

        baseline = instance.get(
            "baseline_score"
        )

        intervention_score = instance.get(
            "intervention_score"
        )

        delta = instance.get(
            "effect_delta"
        )

        threshold = instance.get(
            "minimum_effect_threshold"
        )

        if (
            baseline is not None
            and intervention_score is not None
            and delta is not None
        ):

            expected_delta = (
                baseline
                - intervention_score
            )

            if not math.isclose(
                delta,
                expected_delta,
                abs_tol=1e-6,
            ):
                errors.append(
                    "effect_delta must equal "
                    "baseline_score - "
                    "intervention_score "
                    f"(expected "
                    f"{expected_delta:.6f}, "
                    f"got {delta:.6f})"
                )

        if conclusion == "supported":

            if method == "not_run":
                errors.append(
                    "supported conclusion "
                    "cannot use method 'not_run'"
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
                    "supported conclusion "
                    "requires effect_delta >= "
                    "minimum_effect_threshold"
                )

    # ------------------------------------------------------------------
    # BreathingProfile
    # ------------------------------------------------------------------

    elif record_type == "breathing_profile":

        level = instance.get(
            "level"
        )

        budget = instance.get(
            "reasoning_budget_class"
        )

        recommended_budget = {
            "rest": "minimal",
            "kata": "bounded",
            "deep": "extended",
        }

        expected = (
            recommended_budget.get(level)
        )

        if (
            expected is not None
            and budget != expected
        ):
            errors.append(
                f"level {level!r} requires "
                "reasoning_budget_class "
                f"{expected!r}"
            )

    # ------------------------------------------------------------------
    # ApplicabilityAssessment
    # ------------------------------------------------------------------

    elif record_type == "applicability_assessment":

        score = instance.get(
            "intent_match_score"
        )

        threshold = instance.get(
            "minimum_match_score"
        )

        decision = instance.get(
            "decision"
        )

        selected_level = instance.get(
            "selected_breathing_level"
        )

        expected_level = {
            "reuse": "kata",
            "escalate": "deep",
            "reject": "none",
        }.get(decision)

        if (
            expected_level is not None
            and selected_level
            != expected_level
        ):
            errors.append(
                f"decision {decision!r} "
                "requires "
                "selected_breathing_level "
                f"{expected_level!r}"
            )

        if (
            decision == "reuse"
            and score is not None
            and threshold is not None
            and score < threshold
        ):
            errors.append(
                "reuse decision requires "
                "intent_match_score >= "
                "minimum_match_score"
            )

        boundary_ids = [
            check["boundary_id"]
            for check
            in instance.get(
                "boundary_checks",
                [],
            )
        ]

        if (
            len(boundary_ids)
            != len(set(boundary_ids))
        ):
            errors.append(
                "boundary_checks: "
                "boundary_id values "
                "must be unique"
            )

    # ------------------------------------------------------------------
    # KataEvolutionRecord
    # ------------------------------------------------------------------

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
                "from_version and "
                "to_version must differ"
            )

        if rollback != from_version:
            errors.append(
                "rollback_target_version "
                "must equal from_version "
                "in v0.3"
            )

        changed_steps = instance.get(
            "changed_steps",
            {},
        )

        total_changes = sum(
            len(
                changed_steps.get(
                    key,
                    [],
                )
            )
            for key in (
                "added",
                "modified",
                "removed",
            )
        )

        if total_changes == 0:
            errors.append(
                "changed_steps must contain "
                "at least one change"
            )

    # ------------------------------------------------------------------
    # FailureBoundary
    # ------------------------------------------------------------------

    elif record_type == "failure_boundary":

        severity = instance.get(
            "severity"
        )

        on_match = instance.get(
            "on_match"
        )

        if (
            severity == "warning"
            and on_match == "fail_closed"
        ):
            errors.append(
                "warning boundary must not "
                "use fail_closed"
            )

    # ------------------------------------------------------------------
    # KataLineage
    # ------------------------------------------------------------------

    elif record_type == "kata_lineage":

        kata_ref = instance[
            "kata_ref"
        ]

        self_key = kata_ref_key(
            kata_ref
        )

        parents = instance.get(
            "parent_kata_refs",
            [],
        )

        parent_keys = {
            kata_ref_key(parent)
            for parent in parents
        }

        if self_key in parent_keys:
            errors.append(
                "KATA must not reference "
                "itself as a parent"
            )

        roots = instance.get(
            "root_kata_refs",
            [],
        )

        root_keys = [
            kata_ref_key(root)
            for root in roots
        ]

        if (
            len(root_keys)
            != len(set(root_keys))
        ):
            errors.append(
                "root_kata_refs "
                "must be unique"
            )

        derivation_type = instance.get(
            "derivation_type"
        )

        generation = instance.get(
            "generation"
        )

        if derivation_type == "root":

            if parents:
                errors.append(
                    "root KATA must not "
                    "declare parent_kata_refs"
                )

            if generation != 0:
                errors.append(
                    "root KATA requires "
                    "generation 0"
                )

        else:

            if not parents:
                errors.append(
                    "non-root KATA requires "
                    "at least one parent"
                )

            if (
                generation is not None
                and generation < 1
            ):
                errors.append(
                    "non-root KATA requires "
                    "generation >= 1"
                )

        if (
            derivation_type == "composition"
            and len(parents) < 2
        ):
            errors.append(
                "composition lineage requires "
                "at least two parent KATAs"
            )

        inherited = set(
            instance.get(
                "inherited_step_ids",
                [],
            )
        )

        introduced = set(
            instance.get(
                "introduced_step_ids",
                [],
            )
        )

        overlap = (
            inherited
            & introduced
        )

        if overlap:
            errors.append(
                "step IDs must not appear "
                "in both inherited_step_ids "
                "and introduced_step_ids"
            )

    # ------------------------------------------------------------------
    # KataComposition
    # ------------------------------------------------------------------

    elif record_type == "kata_composition":

        output_ref = instance[
            "output_kata_ref"
        ]

        output_key = kata_ref_key(
            output_ref
        )

        components = instance.get(
            "components",
            [],
        )

        component_keys = [
            kata_ref_key(
                component["kata_ref"]
            )
            for component in components
        ]

        if output_key in component_keys:
            errors.append(
                "output KATA must not "
                "appear as its own component"
            )

        if (
            len(component_keys)
            != len(set(component_keys))
        ):
            errors.append(
                "composition components "
                "must be unique"
            )

        strategy = instance.get(
            "execution_strategy"
        )

        if strategy != "parallel":

            orders = [
                component["order"]
                for component in components
            ]

            if (
                len(orders)
                != len(set(orders))
            ):
                errors.append(
                    "non-parallel composition "
                    "requires unique order values"
                )

        if not any(
            component.get(
                "required",
                False,
            )
            for component in components
        ):
            errors.append(
                "composition requires "
                "at least one required component"
            )

    # ------------------------------------------------------------------
    # KataMaturityAssessment
    # ------------------------------------------------------------------

    elif (
        record_type
        == "kata_maturity_assessment"
    ):

        level = instance.get(
            "level"
        )

        previous_level = instance.get(
            "previous_level"
        )

        decision = instance.get(
            "decision"
        )

        evidence = instance.get(
            "evidence",
            {},
        )

        trace_ids = instance.get(
            "evidence_trace_ids",
            [],
        )

        causal_ids = instance.get(
            "causal_validation_ids",
            [],
        )

        context_ids = instance.get(
            "context_ids",
            [],
        )

        if level in {
            "K1",
            "K2",
            "K3",
            "K4",
            "K5",
        }:

            if not evidence.get(
                "observed_execution",
                False,
            ):
                errors.append(
                    f"{level} requires "
                    "observed execution evidence"
                )

            if not trace_ids:
                errors.append(
                    f"{level} requires at least "
                    "one evidence_trace_id"
                )

        if level in {
            "K2",
            "K3",
            "K4",
            "K5",
        }:

            if not evidence.get(
                "repeated_execution",
                False,
            ):
                errors.append(
                    f"{level} requires "
                    "repeated execution evidence"
                )

        if level in {
            "K3",
            "K4",
            "K5",
        }:

            if not evidence.get(
                "causal_validation_supported",
                False,
            ):
                errors.append(
                    f"{level} requires "
                    "supported causal validation"
                )

            if not causal_ids:
                errors.append(
                    f"{level} requires at least "
                    "one causal_validation_id"
                )

        if level in {
            "K4",
            "K5",
        }:

            if not evidence.get(
                "cross_context_validation_supported",
                False,
            ):
                errors.append(
                    f"{level} requires "
                    "cross-context validation"
                )

            if len(set(context_ids)) < 2:
                errors.append(
                    f"{level} requires at least "
                    "two distinct contexts"
                )

        if level == "K5":

            if not evidence.get(
                "regression_stable",
                False,
            ):
                errors.append(
                    "K5 requires regression "
                    "stability evidence"
                )

        # Maturity transition validation

        if previous_level is None:

            if level != "K0":
                errors.append(
                    "initial maturity assessment "
                    "without previous_level "
                    "must start at K0"
                )

            if decision != "retain":
                errors.append(
                    "initial K0 assessment "
                    "must use decision 'retain'"
                )

        else:

            previous_rank = (
                MATURITY_RANK[
                    previous_level
                ]
            )

            current_rank = (
                MATURITY_RANK[
                    level
                ]
            )

            if (
                decision == "promote"
                and current_rank
                <= previous_rank
            ):
                errors.append(
                    "promote decision requires "
                    "a higher maturity level"
                )

            elif (
                decision == "retain"
                and current_rank
                != previous_rank
            ):
                errors.append(
                    "retain decision requires "
                    "the same maturity level"
                )

            elif (
                decision == "demote"
                and current_rank
                >= previous_rank
            ):
                errors.append(
                    "demote decision requires "
                    "a lower maturity level"
                )

    return errors


# ----------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------

def build_registry(
    records: list[dict[str, Any]],
) -> dict[
    str,
    dict[str, dict[str, Any]],
]:

    registry = {
        record_type: {}
        for record_type
        in SCHEMA_BY_RECORD_TYPE
    }

    for record in records:

        record_type = record.get(
            "record_type"
        )

        if (
            record_type
            not in ID_FIELD_BY_RECORD_TYPE
        ):
            continue

        id_field = (
            ID_FIELD_BY_RECORD_TYPE[
                record_type
            ]
        )

        record_id = record.get(
            id_field
        )

        if record_id:
            registry[
                record_type
            ][record_id] = record

    return registry


# ----------------------------------------------------------------------
# Lineage graph helpers
# ----------------------------------------------------------------------

def lineage_by_kata_ref(
    registry: dict[
        str,
        dict[str, dict[str, Any]],
    ],
) -> dict[
    tuple[str, str],
    dict[str, Any],
]:

    result: dict[
        tuple[str, str],
        dict[str, Any],
    ] = {}

    for lineage in registry[
        "kata_lineage"
    ].values():

        key = kata_ref_key(
            lineage["kata_ref"]
        )

        result[key] = lineage

    return result


def lineage_target_duplicates(
    registry: dict[
        str,
        dict[str, dict[str, Any]],
    ],
) -> set[tuple[str, str]]:

    counts: dict[
        tuple[str, str],
        int,
    ] = {}

    for lineage in registry[
        "kata_lineage"
    ].values():

        key = kata_ref_key(
            lineage["kata_ref"]
        )

        counts[key] = (
            counts.get(key, 0)
            + 1
        )

    return {
        key
        for key, count
        in counts.items()
        if count > 1
    }


def lineage_has_cycle(
    instance: dict[str, Any],
    registry: dict[
        str,
        dict[str, dict[str, Any]],
    ],
) -> bool:

    lineage_map = lineage_by_kata_ref(
        registry
    )

    start_key = kata_ref_key(
        instance["kata_ref"]
    )

    visited: set[
        tuple[str, str]
    ] = set()

    active: set[
        tuple[str, str]
    ] = set()

    def visit(
        key: tuple[str, str],
    ) -> bool:

        if key in active:
            return True

        if key in visited:
            return False

        visited.add(key)
        active.add(key)

        lineage = lineage_map.get(
            key
        )

        if lineage is not None:

            for parent_ref in lineage.get(
                "parent_kata_refs",
                [],
            ):

                parent_key = kata_ref_key(
                    parent_ref
                )

                if visit(parent_key):
                    return True

        active.remove(key)

        return False

    return visit(start_key)


# ----------------------------------------------------------------------
# Cross-record semantic validation
# ----------------------------------------------------------------------

def cross_semantic_errors(
    instance: dict[str, Any],
    registry: dict[
        str,
        dict[str, dict[str, Any]],
    ],
) -> list[str]:

    record_type = instance.get(
        "record_type"
    )

    errors: list[str] = []

    # ------------------------------------------------------------------
    # ReasoningKATA
    # ------------------------------------------------------------------

    if record_type == "reasoning_kata":

        kata_id = instance[
            "kata_id"
        ]

        version = instance[
            "version"
        ]

        # Failure boundaries

        for boundary_id in instance.get(
            "failure_boundary_ids",
            [],
        ):

            if boundary_id not in registry[
                "failure_boundary"
            ]:
                errors.append(
                    "unknown failure_boundary_id "
                    f"{boundary_id!r}"
                )

        # Breathing profile

        breathing_profile_id = (
            instance.get(
                "breathing_profile_id"
            )
        )

        if (
            breathing_profile_id
            not in registry[
                "breathing_profile"
            ]
        ):
            errors.append(
                "unknown breathing_profile_id "
                f"{breathing_profile_id!r}"
            )

        # Causal validation references

        for validation_id in instance.get(
            "causal_validation_ids",
            [],
        ):

            validation = registry[
                "causal_validation"
            ].get(validation_id)

            if validation is None:
                errors.append(
                    "unknown causal_validation_id "
                    f"{validation_id!r}"
                )

                continue

            if (
                validation[
                    "target_kata_id"
                ]
                != kata_id
            ):
                errors.append(
                    f"causal validation "
                    f"{validation_id!r} "
                    "targets a different KATA"
                )

        # Lineage

        lineage_id = instance.get(
            "lineage_id"
        )

        lineage = registry[
            "kata_lineage"
        ].get(lineage_id)

        if lineage is None:
            errors.append(
                f"unknown lineage_id "
                f"{lineage_id!r}"
            )

        else:

            lineage_ref = lineage[
                "kata_ref"
            ]

            if (
                lineage_ref["kata_id"]
                != kata_id
                or lineage_ref["version"]
                != version
            ):
                errors.append(
                    "lineage record targets "
                    "a different KATA/version"
                )

        # Maturity

        maturity_id = instance.get(
            "maturity_assessment_id"
        )

        maturity = registry[
            "kata_maturity_assessment"
        ].get(maturity_id)

        if maturity is None:
            errors.append(
                "unknown "
                "maturity_assessment_id "
                f"{maturity_id!r}"
            )

        else:

            maturity_ref = maturity[
                "kata_ref"
            ]

            if (
                maturity_ref["kata_id"]
                != kata_id
                or maturity_ref["version"]
                != version
            ):
                errors.append(
                    "maturity assessment "
                    "targets a different "
                    "KATA/version"
                )

        # Composition

        composition_id = instance.get(
            "composition_id"
        )

        if composition_id is not None:

            composition = registry[
                "kata_composition"
            ].get(composition_id)

            if composition is None:
                errors.append(
                    "unknown composition_id "
                    f"{composition_id!r}"
                )

            else:

                output_ref = composition[
                    "output_kata_ref"
                ]

                if (
                    output_ref["kata_id"]
                    != kata_id
                    or output_ref["version"]
                    != version
                ):
                    errors.append(
                        "composition output "
                        "targets a different "
                        "KATA/version"
                    )

    # ------------------------------------------------------------------
    # ApplicabilityAssessment
    # ------------------------------------------------------------------

    elif (
        record_type
        == "applicability_assessment"
    ):

        kata_id = instance.get(
            "kata_id"
        )

        kata = registry[
            "reasoning_kata"
        ].get(kata_id)

        if kata is None:
            errors.append(
                f"unknown kata_id "
                f"{kata_id!r}"
            )

            return errors

        policy = kata[
            "applicability_policy"
        ]

        expected_threshold = policy[
            "minimum_match_score"
        ]

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
                "match the KATA "
                "applicability policy"
            )

        # Required conditions

        if (
            instance.get("decision")
            == "reuse"
            and policy[
                "require_all_conditions"
            ]
        ):

            if any(
                not condition.get(
                    "met",
                    False,
                )
                for condition
                in instance.get(
                    "required_conditions",
                    [],
                )
            ):
                errors.append(
                    "reuse decision requires "
                    "all required_conditions "
                    "to be met"
                )

        # Boundary coverage

        configured_boundaries = set(
            kata.get(
                "failure_boundary_ids",
                [],
            )
        )

        checked_boundaries = {
            check["boundary_id"]
            for check
            in instance.get(
                "boundary_checks",
                [],
            )
        }

        if (
            configured_boundaries
            != checked_boundaries
        ):
            errors.append(
                "boundary_checks must cover "
                "exactly the KATA "
                "failure_boundary_ids"
            )

        matched_actions: list[str] = []

        for check in instance.get(
            "boundary_checks",
            [],
        ):

            boundary_id = check[
                "boundary_id"
            ]

            boundary = registry[
                "failure_boundary"
            ].get(boundary_id)

            if boundary is None:
                errors.append(
                    "unknown boundary_id "
                    f"{boundary_id!r}"
                )

                continue

            if check["matched"]:
                matched_actions.append(
                    boundary["on_match"]
                )

        decision = instance.get(
            "decision"
        )

        if (
            "fail_closed"
            in matched_actions
        ):

            if decision != "reject":
                errors.append(
                    "matched fail_closed "
                    "boundary requires "
                    "decision 'reject'"
                )

        elif (
            "reject_reuse"
            in matched_actions
        ):

            if decision == "reuse":
                errors.append(
                    "matched reject_reuse "
                    "boundary forbids "
                    "decision 'reuse'"
                )

        elif (
            "escalate_to_deep"
            in matched_actions
        ):

            if decision != "escalate":
                errors.append(
                    "matched escalate_to_deep "
                    "boundary requires "
                    "decision 'escalate'"
                )

    # ------------------------------------------------------------------
    # TraceRecord
    # ------------------------------------------------------------------

    elif record_type == "trace_record":

        if (
            instance.get(
                "execution_mode"
            )
            == "kata"
        ):

            kata_id = instance.get(
                "applied_kata_id"
            )

            assessment_id = instance.get(
                "applicability_assessment_id"
            )

            kata = registry[
                "reasoning_kata"
            ].get(kata_id)

            if kata is None:
                errors.append(
                    f"unknown applied_kata_id "
                    f"{kata_id!r}"
                )

            assessment = registry[
                "applicability_assessment"
            ].get(assessment_id)

            if assessment is None:
                errors.append(
                    "unknown "
                    "applicability_assessment_id "
                    f"{assessment_id!r}"
                )

            else:

                if (
                    assessment[
                        "kata_id"
                    ]
                    != kata_id
                ):
                    errors.append(
                        "applicability assessment "
                        "targets a different KATA"
                    )

                if (
                    assessment[
                        "decision"
                    ]
                    != "reuse"
                ):
                    errors.append(
                        "KATA execution requires "
                        "applicability decision "
                        "'reuse'"
                    )

            if kata is not None:

                expected_profile = kata.get(
                    "breathing_profile_id"
                )

                actual_profile = instance.get(
                    "breathing_profile_id"
                )

                if (
                    actual_profile
                    != expected_profile
                ):
                    errors.append(
                        "KATA execution must use "
                        "the KATA breathing_profile_id"
                    )

    # ------------------------------------------------------------------
    # CausalValidation
    # ------------------------------------------------------------------

    elif record_type == "causal_validation":

        kata_id = instance.get(
            "target_kata_id"
        )

        kata = registry[
            "reasoning_kata"
        ].get(kata_id)

        if kata is not None:

            target_step_id = instance.get(
                "target_step_id"
            )

            if target_step_id is not None:

                valid_step_ids = {
                    step["step_id"]
                    for step
                    in kata.get(
                        "reasoning_steps",
                        [],
                    )
                }

                if (
                    target_step_id
                    not in valid_step_ids
                ):
                    errors.append(
                        "target_step_id does not "
                        "exist in target KATA"
                    )

    # ------------------------------------------------------------------
    # KataEvolutionRecord
    # ------------------------------------------------------------------

    elif (
        record_type
        == "kata_evolution_record"
    ):

        kata_id = instance.get(
            "kata_id"
        )

        kata = registry[
            "reasoning_kata"
        ].get(kata_id)

        if kata is not None:

            if (
                kata["version"]
                != instance["to_version"]
            ):
                errors.append(
                    "to_version must match "
                    "the current KATA version"
                )

        for validation_id in instance.get(
            "causal_validation_ids",
            [],
        ):

            validation = registry[
                "causal_validation"
            ].get(validation_id)

            if validation is None:
                errors.append(
                    "unknown causal_validation_id "
                    f"{validation_id!r}"
                )

                continue

            if (
                validation[
                    "target_kata_id"
                ]
                != kata_id
            ):
                errors.append(
                    f"causal validation "
                    f"{validation_id!r} "
                    "targets a different KATA"
                )

        for assessment_id in instance.get(
            "applicability_assessment_ids",
            [],
        ):

            assessment = registry[
                "applicability_assessment"
            ].get(assessment_id)

            if assessment is None:
                errors.append(
                    "unknown applicability_"
                    "assessment_id "
                    f"{assessment_id!r}"
                )

                continue

            if (
                assessment["kata_id"]
                != kata_id
            ):
                errors.append(
                    f"applicability assessment "
                    f"{assessment_id!r} "
                    "targets a different KATA"
                )

    # ------------------------------------------------------------------
    # KataLineage
    # ------------------------------------------------------------------

    elif record_type == "kata_lineage":

        kata_ref = instance[
            "kata_ref"
        ]

        target_key = kata_ref_key(
            kata_ref
        )

        duplicate_targets = (
            lineage_target_duplicates(
                registry
            )
        )

        if target_key in duplicate_targets:
            errors.append(
                "multiple KataLineage records "
                "target the same KATA/version"
            )

        if lineage_has_cycle(
            instance,
            registry,
        ):
            errors.append(
                "KATA lineage graph "
                "must be acyclic"
            )

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_ref["kata_id"]
        )

        if kata is not None:

            if (
                kata["version"]
                != kata_ref["version"]
            ):
                errors.append(
                    "lineage kata_ref version "
                    "does not match "
                    "ReasoningKATA version"
                )

            if (
                kata.get("lineage_id")
                != instance["lineage_id"]
            ):
                errors.append(
                    "ReasoningKATA lineage_id "
                    "does not reference "
                    "this lineage record"
                )

        if (
            instance.get(
                "derivation_type"
            )
            == "composition"
        ):

            composition_id = (
                kata.get(
                    "composition_id"
                )
                if kata is not None
                else None
            )

            if (
                kata is not None
                and not composition_id
            ):
                errors.append(
                    "composition lineage "
                    "requires the target KATA "
                    "to reference a composition"
                )

    # ------------------------------------------------------------------
    # KataComposition
    # ------------------------------------------------------------------

    elif record_type == "kata_composition":

        output_ref = instance[
            "output_kata_ref"
        ]

        kata = registry[
            "reasoning_kata"
        ].get(
            output_ref["kata_id"]
        )

        if kata is not None:

            if (
                kata["version"]
                != output_ref["version"]
            ):
                errors.append(
                    "composition output version "
                    "does not match "
                    "ReasoningKATA version"
                )

            if (
                kata.get(
                    "composition_id"
                )
                != instance[
                    "composition_id"
                ]
            ):
                errors.append(
                    "ReasoningKATA "
                    "composition_id does not "
                    "reference this composition"
                )

    # ------------------------------------------------------------------
    # KataMaturityAssessment
    # ------------------------------------------------------------------

    elif (
        record_type
        == "kata_maturity_assessment"
    ):

        kata_ref = instance[
            "kata_ref"
        ]

        kata_id = kata_ref[
            "kata_id"
        ]

        kata = registry[
            "reasoning_kata"
        ].get(kata_id)

        if kata is not None:

            if (
                kata["version"]
                != kata_ref["version"]
            ):
                errors.append(
                    "maturity assessment "
                    "version does not match "
                    "ReasoningKATA version"
                )

            if (
                kata.get(
                    "maturity_assessment_id"
                )
                != instance[
                    "assessment_id"
                ]
            ):
                errors.append(
                    "ReasoningKATA "
                    "maturity_assessment_id "
                    "does not reference "
                    "this assessment"
                )

        for validation_id in instance.get(
            "causal_validation_ids",
            [],
        ):

            validation = registry[
                "causal_validation"
            ].get(validation_id)

            if validation is None:
                errors.append(
                    "unknown causal_validation_id "
                    f"{validation_id!r}"
                )

                continue

            if (
                validation[
                    "target_kata_id"
                ]
                != kata_id
            ):
                errors.append(
                    f"causal validation "
                    f"{validation_id!r} "
                    "targets a different KATA"
                )

            if (
                instance["level"]
                in {
                    "K3",
                    "K4",
                    "K5",
                }
                and validation[
                    "conclusion"
                ]
                != "supported"
            ):
                errors.append(
                    f"{instance['level']} "
                    "requires supported "
                    "causal validation records"
                )

    return errors


# ----------------------------------------------------------------------
# Pass-record loading for registry
# ----------------------------------------------------------------------

def collect_locally_valid_records(
    paths: list[Path],
    schemas: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:

    records: list[
        dict[str, Any]
    ] = []

    for path in paths:

        try:
            instance = load_instance(
                path
            )

        except Exception:
            continue

        if schema_errors(
            instance,
            schemas,
        ):
            continue

        if local_semantic_errors(
            instance
        ):
            continue

        records.append(instance)

    return records


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:

    print(
        "=== ZEROSHIKI Reasoning OS "
        "v0.3 Validation ==="
    )

    schemas: dict[
        str,
        dict[str, Any],
    ] = {}

    # ------------------------------------------------------------------
    # Load and validate schemas
    # ------------------------------------------------------------------

    for (
        record_type,
        path,
    ) in SCHEMA_BY_RECORD_TYPE.items():

        if not path.exists():
            print(
                f"[fatal] missing schema: "
                f"{path.relative_to(ROOT)}"
            )

            return 1

        try:
            schema = load_json(path)

            Draft202012Validator.check_schema(
                schema
            )

        except Exception as exc:
            print(
                f"[fatal] invalid schema "
                f"{path.relative_to(ROOT)}: "
                f"{exc}"
            )

            return 1

        schemas[
            record_type
        ] = schema

        print(
            f"schema [{record_type}]: "
            f"{path.relative_to(ROOT)}"
        )

    pass_paths = iter_examples(
        PASS_DIR
    )

    fail_paths = iter_examples(
        FAIL_DIR
    )

    # Build one complete registry from every
    # schema-valid + locally-valid pass record.
    # Cross-record validation can therefore resolve
    # references independent of filename order.

    pass_records = (
        collect_locally_valid_records(
            pass_paths,
            schemas,
        )
    )

    registry = build_registry(
        pass_records
    )

    # ------------------------------------------------------------------
    # Pass examples
    # ------------------------------------------------------------------

    print(
        "\n[pass examples]\n"
    )

    pass_failed = False

    for path in pass_paths:

        print(
            f"- {path.relative_to(ROOT)}"
        )

        try:
            instance = load_instance(
                path
            )

        except Exception as exc:
            pass_failed = True

            print(
                "  [load-error]"
            )

            print(
                f"    - {exc}"
            )

            continue

        s_errors = schema_errors(
            instance,
            schemas,
        )

        if s_errors:

            pass_failed = True

            print(
                "  [schema-error]"
            )

            for error in s_errors:
                print(
                    f"    - {error}"
                )

            continue

        print(
            "  [schema-ok]"
        )

        local_errors = (
            local_semantic_errors(
                instance
            )
        )

        cross_errors = (
            cross_semantic_errors(
                instance,
                registry,
            )
        )

        semantic = (
            local_errors
            + cross_errors
        )

        if semantic:

            pass_failed = True

            print(
                "  [semantic-error]"
            )

            for error in semantic:
                print(
                    f"    - {error}"
                )

        else:

            print(
                "  [semantic-ok]"
            )

    # ------------------------------------------------------------------
    # Fail examples
    # ------------------------------------------------------------------

    print(
        "\n[fail examples]\n"
    )

    fail_failed = False

    for path in fail_paths:

        print(
            f"- {path.relative_to(ROOT)}"
        )

        try:
            instance = load_instance(
                path
            )

        except Exception as exc:

            print(
                "  [expected-load-failure]"
            )

            print(
                f"    - {exc}"
            )

            continue

        s_errors = schema_errors(
            instance,
            schemas,
        )

        if s_errors:

            print(
                "  [expected-schema-failure]"
            )

            for error in s_errors:
                print(
                    f"    - {error}"
                )

            continue

        # Add the fail instance to a temporary
        # registry so cross-record rules can test
        # intentionally invalid relationships.

        temp_records = (
            pass_records
            + [instance]
        )

        temp_registry = build_registry(
            temp_records
        )

        semantic = (
            local_semantic_errors(
                instance
            )
            + cross_semantic_errors(
                instance,
                temp_registry,
            )
        )

        if semantic:

            print(
                "  [expected-semantic-failure]"
            )

            for error in semantic:
                print(
                    f"    - {error}"
                )

        else:

            fail_failed = True

            print(
                "  [unexpected-pass]"
            )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    print(
        "\n=== Summary ==="
    )

    if pass_failed or fail_failed:

        print(
            "[validation-failed]"
        )

        return 1

    print(
        "[validation-ok]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
