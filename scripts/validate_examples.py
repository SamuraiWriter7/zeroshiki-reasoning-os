#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


# ======================================================================
# Paths
# ======================================================================

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"


# ======================================================================
# Schema Registry
# ======================================================================

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

    "kata_selection_request":
        SCHEMA_DIR / "kata-selection-request.schema.json",

    "kata_selection_decision":
        SCHEMA_DIR / "kata-selection-decision.schema.json",

    "kata_orchestration_plan":
        SCHEMA_DIR / "kata-orchestration-plan.schema.json",

    "kata_handoff_record":
        SCHEMA_DIR / "kata-handoff-record.schema.json",

    "zeroshiki_package_manifest":
        SCHEMA_DIR / "zeroshiki-package-manifest.schema.json",

    "conformance_profile":
        SCHEMA_DIR / "conformance-profile.schema.json",

    "kata_interface_contract":
        SCHEMA_DIR / "kata-interface-contract.schema.json",

    "kata_conformance_assessment":
        SCHEMA_DIR / "kata-conformance-assessment.schema.json",

    "kata_interoperability_assessment":
        SCHEMA_DIR / "kata-interoperability-assessment.schema.json",
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
    "kata_selection_request": "request_id",
    "kata_selection_decision": "decision_id",
    "kata_orchestration_plan": "plan_id",
    "kata_handoff_record": "handoff_id",
    "zeroshiki_package_manifest": "manifest_id",
    "conformance_profile": "profile_id",
    "kata_interface_contract": "interface_id",
    "kata_conformance_assessment": "assessment_id",
    "kata_interoperability_assessment": "assessment_id",
}


MATURITY_RANK = {
    "K0": 0,
    "K1": 1,
    "K2": 2,
    "K3": 3,
    "K4": 4,
    "K5": 5,
}


COMPUTE_LEVEL_RANK = {
    "none": -1,
    "rest": 0,
    "kata": 1,
    "deep": 2,
}


# ======================================================================
# Loading
# ======================================================================

def load_json(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def load_yaml(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return yaml.safe_load(handle)


def load_instance(
    path: Path,
) -> dict[str, Any]:

    instance = load_yaml(path)

    if not isinstance(instance, dict):
        raise ValueError(
            "document root must be a mapping/object"
        )

    return instance


def iter_examples(
    directory: Path,
) -> list[Path]:

    return sorted([
        *directory.glob("*.yaml"),
        *directory.glob("*.yml"),
    ])


# ======================================================================
# Utility
# ======================================================================

def format_path(
    error_path: Any,
) -> str:

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


def kata_ref_set(
    refs: list[dict[str, Any]],
) -> set[tuple[str, str]]:

    return {
        kata_ref_key(ref)
        for ref in refs
    }


def field_type_compatible(
    producer_type: str,
    consumer_type: str,
) -> bool:

    if producer_type == "any":
        return True

    if consumer_type == "any":
        return True

    return producer_type == consumer_type


# ======================================================================
# JSON Schema Validation
# ======================================================================

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


# ======================================================================
# Generic Graph Validation
# ======================================================================

def dependency_graph_has_cycle(
    graph: dict[str, set[str]],
) -> bool:

    visited: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> bool:

        if node in active:
            return True

        if node in visited:
            return False

        visited.add(node)
        active.add(node)

        for dependency in graph.get(
            node,
            set(),
        ):
            if visit(dependency):
                return True

        active.remove(node)

        return False

    return any(
        visit(node)
        for node in graph
    )


# ======================================================================
# Local Semantic Validation
# ======================================================================

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

        applicability_id = instance.get(
            "applicability_assessment_id"
        )

        selection_id = instance.get(
            "selection_decision_id"
        )

        orchestration_id = instance.get(
            "orchestration_plan_id"
        )

        if mode == "direct":

            if kata_id is not None:
                errors.append(
                    "direct execution must not "
                    "declare applied_kata_id"
                )

            if applicability_id is not None:
                errors.append(
                    "direct execution must not declare "
                    "applicability_assessment_id"
                )

            if selection_id is not None:
                errors.append(
                    "direct execution must not declare "
                    "selection_decision_id"
                )

            if orchestration_id is not None:
                errors.append(
                    "direct execution must not declare "
                    "orchestration_plan_id"
                )

        elif mode == "kata":

            if not kata_id:
                errors.append(
                    "execution_mode 'kata' requires "
                    "applied_kata_id"
                )

            if not applicability_id:
                errors.append(
                    "execution_mode 'kata' requires "
                    "applicability_assessment_id"
                )

            if orchestration_id is not None:
                errors.append(
                    "single KATA execution must not "
                    "declare orchestration_plan_id"
                )

        elif mode == "orchestrated":

            if kata_id is not None:
                errors.append(
                    "orchestrated execution must not "
                    "declare applied_kata_id"
                )

            if applicability_id is not None:
                errors.append(
                    "orchestrated execution must not "
                    "declare applicability_assessment_id"
                )

            if not selection_id:
                errors.append(
                    "orchestrated execution requires "
                    "selection_decision_id"
                )

            if not orchestration_id:
                errors.append(
                    "orchestrated execution requires "
                    "orchestration_plan_id"
                )

        elif mode == "deep":

            if kata_id is not None:
                errors.append(
                    "deep execution must not declare "
                    "applied_kata_id"
                )

            if applicability_id is not None:
                errors.append(
                    "deep execution must not declare "
                    "applicability_assessment_id"
                )

            if orchestration_id is not None:
                errors.append(
                    "deep execution must not declare "
                    "orchestration_plan_id"
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
                    "baseline_score - intervention_score "
                    f"(expected {expected_delta:.6f}, "
                    f"got {delta:.6f})"
                )

        if conclusion == "supported":

            if method == "not_run":
                errors.append(
                    "supported conclusion cannot "
                    "use method 'not_run'"
                )

            if delta is None:
                errors.append(
                    "supported conclusion requires "
                    "effect_delta"
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

        expected_budget = {
            "rest": "minimal",
            "kata": "bounded",
            "deep": "extended",
        }.get(level)

        if (
            expected_budget is not None
            and budget != expected_budget
        ):
            errors.append(
                f"level {level!r} requires "
                f"reasoning_budget_class "
                f"{expected_budget!r}"
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
            and selected_level != expected_level
        ):
            errors.append(
                f"decision {decision!r} requires "
                f"selected_breathing_level "
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
                "boundary_id values must be unique"
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
                "from_version and to_version "
                "must differ"
            )

        if rollback != from_version:
            errors.append(
                "rollback_target_version must "
                "equal from_version in v0.5"
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

        action = instance.get(
            "on_match"
        )

        if (
            severity == "warning"
            and action == "fail_closed"
        ):
            errors.append(
                "warning boundary must not "
                "use fail_closed"
            )


    # ------------------------------------------------------------------
    # KataLineage
    # ------------------------------------------------------------------

    elif record_type == "kata_lineage":

        target_key = kata_ref_key(
            instance[
                "kata_ref"
            ]
        )

        parents = instance.get(
            "parent_kata_refs",
            [],
        )

        parent_keys = [
            kata_ref_key(parent)
            for parent in parents
        ]

        if (
            len(parent_keys)
            != len(set(parent_keys))
        ):
            errors.append(
                "parent_kata_refs must be unique"
            )

        if target_key in set(
            parent_keys
        ):
            errors.append(
                "KATA must not reference itself "
                "as a parent"
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
                "root_kata_refs must be unique"
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
                    "root KATA must not declare "
                    "parent_kata_refs"
                )

            if generation != 0:
                errors.append(
                    "root KATA requires generation 0"
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

        if inherited & introduced:
            errors.append(
                "step IDs must not appear "
                "in both inherited_step_ids "
                "and introduced_step_ids"
            )


    # ------------------------------------------------------------------
    # KataComposition
    # ------------------------------------------------------------------

    elif record_type == "kata_composition":

        output_key = kata_ref_key(
            instance[
                "output_kata_ref"
            ]
        )

        components = instance.get(
            "components",
            [],
        )

        component_keys = [
            kata_ref_key(
                component[
                    "kata_ref"
                ]
            )
            for component in components
        ]

        if output_key in component_keys:
            errors.append(
                "output KATA must not appear "
                "as its own component"
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
                "composition requires at least "
                "one required component"
            )


    # ------------------------------------------------------------------
    # KataMaturityAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_maturity_assessment":

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
                    f"{level} requires observed "
                    "execution evidence"
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
                    f"{level} requires repeated "
                    "execution evidence"
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
                    f"{level} requires supported "
                    "causal validation"
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

        if previous_level is None:

            if level != "K0":
                errors.append(
                    "initial maturity assessment "
                    "without previous_level "
                    "must start at K0"
                )

            if decision != "retain":
                errors.append(
                    "initial K0 assessment must "
                    "use decision 'retain'"
                )

        else:

            previous_rank = MATURITY_RANK[
                previous_level
            ]

            current_rank = MATURITY_RANK[
                level
            ]

            if (
                decision == "promote"
                and current_rank <= previous_rank
            ):
                errors.append(
                    "promote decision requires "
                    "a higher maturity level"
                )

            elif (
                decision == "retain"
                and current_rank != previous_rank
            ):
                errors.append(
                    "retain decision requires "
                    "the same maturity level"
                )

            elif (
                decision == "demote"
                and current_rank >= previous_rank
            ):
                errors.append(
                    "demote decision requires "
                    "a lower maturity level"
                )


    # ------------------------------------------------------------------
    # KataSelectionRequest
    # ------------------------------------------------------------------

    elif record_type == "kata_selection_request":

        candidates = instance.get(
            "candidate_kata_refs",
            [],
        )

        candidate_keys = [
            kata_ref_key(ref)
            for ref in candidates
        ]

        if (
            len(candidate_keys)
            != len(set(candidate_keys))
        ):
            errors.append(
                "candidate_kata_refs must be unique"
            )

        constraints = instance.get(
            "constraints",
            {},
        )

        max_selected = constraints.get(
            "max_selected_katas"
        )

        if (
            max_selected is not None
            and candidates
            and max_selected > len(candidates)
        ):
            errors.append(
                "max_selected_katas must not exceed "
                "the number of candidate KATAs"
            )


    # ------------------------------------------------------------------
    # KataSelectionDecision
    # ------------------------------------------------------------------

    elif record_type == "kata_selection_decision":

        evaluations = instance.get(
            "candidate_evaluations",
            [],
        )

        evaluation_keys = [
            kata_ref_key(
                evaluation[
                    "kata_ref"
                ]
            )
            for evaluation in evaluations
        ]

        if (
            len(evaluation_keys)
            != len(set(evaluation_keys))
        ):
            errors.append(
                "candidate_evaluations must contain "
                "unique KATA references"
            )

        selected_refs = instance.get(
            "selected_kata_refs",
            [],
        )

        selected_keys = [
            kata_ref_key(ref)
            for ref in selected_refs
        ]

        if (
            len(selected_keys)
            != len(set(selected_keys))
        ):
            errors.append(
                "selected_kata_refs must be unique"
            )

        evaluation_map = {
            kata_ref_key(
                evaluation[
                    "kata_ref"
                ]
            ): evaluation
            for evaluation in evaluations
        }

        for selected_key in selected_keys:

            evaluation = evaluation_map.get(
                selected_key
            )

            if evaluation is None:
                errors.append(
                    "selected KATA must appear "
                    "in candidate_evaluations"
                )
                continue

            if not evaluation[
                "eligible"
            ]:
                errors.append(
                    "selected KATA must be eligible"
                )

            if evaluation[
                "boundary_blocked"
            ]:
                errors.append(
                    "boundary-blocked KATA "
                    "must not be selected"
                )

        for evaluation in evaluations:

            eligible = evaluation[
                "eligible"
            ]

            blocked = evaluation[
                "boundary_blocked"
            ]

            rank = evaluation.get(
                "rank"
            )

            exclusion = evaluation.get(
                "exclusion_reason"
            )

            if eligible and blocked:
                errors.append(
                    "boundary-blocked candidate "
                    "cannot be eligible"
                )

            if eligible and rank is None:
                errors.append(
                    "eligible candidate requires rank"
                )

            if (
                not eligible
                and exclusion is None
            ):
                errors.append(
                    "ineligible candidate requires "
                    "exclusion_reason"
                )

        decision = instance.get(
            "decision"
        )

        breathing = instance.get(
            "selected_breathing_level"
        )

        selected_count = len(
            selected_keys
        )

        if decision == "single":

            if selected_count != 1:
                errors.append(
                    "single decision requires "
                    "exactly one selected KATA"
                )

            if breathing != "kata":
                errors.append(
                    "single decision requires "
                    "selected_breathing_level 'kata'"
                )

        elif decision == "composed":

            if selected_count < 1:
                errors.append(
                    "composed decision requires "
                    "at least one selected KATA"
                )

            if breathing != "kata":
                errors.append(
                    "composed decision requires "
                    "selected_breathing_level 'kata'"
                )

        elif decision == "escalate":

            if selected_count != 0:
                errors.append(
                    "escalate decision must not "
                    "select a KATA"
                )

            if breathing != "deep":
                errors.append(
                    "escalate decision requires "
                    "selected_breathing_level 'deep'"
                )

        elif decision == "reject":

            if selected_count != 0:
                errors.append(
                    "reject decision must not "
                    "select a KATA"
                )

            if breathing != "none":
                errors.append(
                    "reject decision requires "
                    "selected_breathing_level 'none'"
                )


    # ------------------------------------------------------------------
    # KataOrchestrationPlan
    # ------------------------------------------------------------------

    elif record_type == "kata_orchestration_plan":

        stages = instance.get(
            "stages",
            [],
        )

        stage_ids = [
            stage["stage_id"]
            for stage in stages
        ]

        if (
            len(stage_ids)
            != len(set(stage_ids))
        ):
            errors.append(
                "stage_id values must be unique"
            )

        stage_id_set = set(
            stage_ids
        )

        stage_kata_keys = [
            kata_ref_key(
                stage[
                    "kata_ref"
                ]
            )
            for stage in stages
        ]

        if (
            len(stage_kata_keys)
            != len(set(stage_kata_keys))
        ):
            errors.append(
                "orchestration stages must not "
                "repeat the same KATA/version"
            )

        graph: dict[
            str,
            set[str],
        ] = {}

        for stage in stages:

            stage_id = stage[
                "stage_id"
            ]

            dependencies = set(
                stage.get(
                    "depends_on",
                    [],
                )
            )

            graph[
                stage_id
            ] = dependencies

            if stage_id in dependencies:
                errors.append(
                    "stage must not depend on itself"
                )

            for dependency in dependencies:

                if dependency not in stage_id_set:
                    errors.append(
                        f"unknown dependency "
                        f"{dependency!r}"
                    )

        valid_graph = {
            stage_id: {
                dependency
                for dependency in dependencies
                if dependency in stage_id_set
            }
            for (
                stage_id,
                dependencies,
            ) in graph.items()
        }

        if dependency_graph_has_cycle(
            valid_graph
        ):
            errors.append(
                "orchestration stage dependency "
                "graph must be acyclic"
            )

        strategy = instance.get(
            "execution_strategy"
        )

        if strategy != "parallel":

            orders = [
                stage["order"]
                for stage in stages
            ]

            if (
                len(orders)
                != len(set(orders))
            ):
                errors.append(
                    "non-parallel orchestration "
                    "requires unique stage order values"
                )


    # ------------------------------------------------------------------
    # KataHandoffRecord
    # ------------------------------------------------------------------

    elif record_type == "kata_handoff_record":

        provided = set(
            instance.get(
                "provided_fields",
                [],
            )
        )

        required = set(
            instance.get(
                "required_fields",
                [],
            )
        )

        status = instance.get(
            "validation_status"
        )

        if (
            status == "pass"
            and not required.issubset(
                provided
            )
        ):
            errors.append(
                "handoff marked pass but "
                "required fields are missing"
            )

        if (
            instance.get(
                "from_stage_id"
            )
            == instance.get(
                "to_stage_id"
            )
        ):
            errors.append(
                "handoff source and destination "
                "stages must differ"
            )

        if (
            instance.get(
                "from_kata_id"
            )
            == instance.get(
                "to_kata_id"
            )
        ):
            errors.append(
                "handoff source and destination "
                "KATAs must differ"
            )


    # ------------------------------------------------------------------
    # ZEROSHIKI PackageManifest
    # ------------------------------------------------------------------

    elif record_type == "zeroshiki_package_manifest":

        supported = instance.get(
            "supported_record_types",
            [],
        )

        if len(
            supported
        ) != len(set(supported)):
            errors.append(
                "supported_record_types must be unique"
            )

        profile_ids = instance.get(
            "conformance_profile_ids",
            [],
        )

        if len(
            profile_ids
        ) != len(set(profile_ids)):
            errors.append(
                "conformance_profile_ids must be unique"
            )

        namespaces = instance.get(
            "extension_namespaces",
            [],
        )

        if len(
            namespaces
        ) != len(set(namespaces)):
            errors.append(
                "extension_namespaces must be unique"
            )


    # ------------------------------------------------------------------
    # ConformanceProfile
    # ------------------------------------------------------------------

    elif record_type == "conformance_profile":

        record_types = instance.get(
            "required_record_types",
            [],
        )

        for required_type in record_types:

            if (
                required_type
                not in SCHEMA_BY_RECORD_TYPE
            ):
                errors.append(
                    "unknown required_record_type "
                    f"{required_type!r}"
                )


    # ------------------------------------------------------------------
    # KataInterfaceContract
    # ------------------------------------------------------------------

    elif record_type == "kata_interface_contract":

        input_names = [
            field["name"]
            for field in instance.get(
                "inputs",
                [],
            )
        ]

        output_names = [
            field["name"]
            for field in instance.get(
                "outputs",
                [],
            )
        ]

        if (
            len(input_names)
            != len(set(input_names))
        ):
            errors.append(
                "interface input field names "
                "must be unique"
            )

        if (
            len(output_names)
            != len(set(output_names))
        ):
            errors.append(
                "interface output field names "
                "must be unique"
            )


    # ------------------------------------------------------------------
    # KataConformanceAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_conformance_assessment":

        checks = instance.get(
            "checks",
            [],
        )

        check_ids = [
            check["check_id"]
            for check in checks
        ]

        if (
            len(check_ids)
            != len(set(check_ids))
        ):
            errors.append(
                "conformance check_id values "
                "must be unique"
            )

        result = instance.get(
            "result"
        )

        if result == "conformant":

            if any(
                check[
                    "status"
                ] == "fail"
                for check in checks
            ):
                errors.append(
                    "conformant result must not "
                    "contain failed checks"
                )


    # ------------------------------------------------------------------
    # KataInteroperabilityAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_interoperability_assessment":

        producer_key = kata_ref_key(
            instance[
                "producer_kata_ref"
            ]
        )

        consumer_key = kata_ref_key(
            instance[
                "consumer_kata_ref"
            ]
        )

        if producer_key == consumer_key:
            errors.append(
                "producer and consumer KATAs "
                "must differ"
            )

        mappings = instance.get(
            "field_mappings",
            [],
        )

        producer_outputs = [
            mapping[
                "producer_output"
            ]
            for mapping in mappings
        ]

        consumer_inputs = [
            mapping[
                "consumer_input"
            ]
            for mapping in mappings
        ]

        if (
            len(producer_outputs)
            != len(set(producer_outputs))
        ):
            errors.append(
                "producer_output mappings "
                "must be unique"
            )

        if (
            len(consumer_inputs)
            != len(set(consumer_inputs))
        ):
            errors.append(
                "consumer_input mappings "
                "must be unique"
            )

        checks = instance.get(
            "compatibility_checks",
            {},
        )

        if (
            instance.get("decision")
            == "compatible"
            and not all(
                checks.values()
            )
        ):
            errors.append(
                "compatible decision requires "
                "all compatibility checks to pass"
            )

    return errors


# ======================================================================
# Registry
# ======================================================================

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

        id_field = (
            ID_FIELD_BY_RECORD_TYPE.get(
                record_type
            )
        )

        if id_field is None:
            continue

        record_id = record.get(
            id_field
        )

        if record_id:
            registry[
                record_type
            ][
                str(record_id)
            ] = record

    return registry


def registry_integrity_errors(
    records: list[dict[str, Any]],
) -> list[str]:

    errors: list[str] = []

    seen: dict[
        tuple[str, str],
        int,
    ] = {}

    for record in records:

        record_type = record.get(
            "record_type"
        )

        id_field = (
            ID_FIELD_BY_RECORD_TYPE.get(
                record_type
            )
        )

        if id_field is None:
            continue

        record_id = record.get(
            id_field
        )

        if record_id is None:
            continue

        key = (
            record_type,
            str(record_id),
        )

        seen[key] = (
            seen.get(
                key,
                0,
            )
            + 1
        )

    for (
        record_type,
        record_id,
    ), count in seen.items():

        if count > 1:
            errors.append(
                f"duplicate {record_type} id "
                f"{record_id!r}"
            )

    return errors


# ======================================================================
# Lineage Helpers
# ======================================================================

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
            lineage[
                "kata_ref"
            ]
        )

        result[
            key
        ] = lineage

    return result


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
        instance[
            "kata_ref"
        ]
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

        visited.add(
            key
        )

        active.add(
            key
        )

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

                if visit(
                    parent_key
                ):
                    return True

        active.remove(
            key
        )

        return False

    return visit(
        start_key
    )


# ======================================================================
# Interface Helpers
# ======================================================================

def interface_field_map(
    interface: dict[str, Any],
    key: str,
) -> dict[str, dict[str, Any]]:

    return {
        field["name"]: field
        for field in interface.get(
            key,
            [],
        )
    }


def matching_interoperability_assessments(
    registry: dict[
        str,
        dict[str, dict[str, Any]],
    ],
    producer_ref: dict[str, Any],
    consumer_ref: dict[str, Any],
) -> list[dict[str, Any]]:

    producer_key = kata_ref_key(
        producer_ref
    )

    consumer_key = kata_ref_key(
        consumer_ref
    )

    matches = []

    for assessment in registry[
        "kata_interoperability_assessment"
    ].values():

        if (
            kata_ref_key(
                assessment[
                    "producer_kata_ref"
                ]
            )
            == producer_key
            and kata_ref_key(
                assessment[
                    "consumer_kata_ref"
                ]
            )
            == consumer_key
        ):
            matches.append(
                assessment
            )

    return matches


# ======================================================================
# Cross-Record Semantic Validation
# ======================================================================

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

        breathing_profile_id = instance.get(
            "breathing_profile_id"
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

        for validation_id in instance.get(
            "causal_validation_ids",
            [],
        ):

            validation = registry[
                "causal_validation"
            ].get(
                validation_id
            )

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

        lineage_id = instance.get(
            "lineage_id"
        )

        lineage = registry[
            "kata_lineage"
        ].get(
            lineage_id
        )

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
                lineage_ref[
                    "kata_id"
                ] != kata_id
                or lineage_ref[
                    "version"
                ] != version
            ):
                errors.append(
                    "lineage record targets "
                    "a different KATA/version"
                )

        maturity_id = instance.get(
            "maturity_assessment_id"
        )

        maturity = registry[
            "kata_maturity_assessment"
        ].get(
            maturity_id
        )

        if maturity is None:
            errors.append(
                "unknown maturity_assessment_id "
                f"{maturity_id!r}"
            )

        else:

            maturity_ref = maturity[
                "kata_ref"
            ]

            if (
                maturity_ref[
                    "kata_id"
                ] != kata_id
                or maturity_ref[
                    "version"
                ] != version
            ):
                errors.append(
                    "maturity assessment targets "
                    "a different KATA/version"
                )

        composition_id = instance.get(
            "composition_id"
        )

        if composition_id is not None:

            composition = registry[
                "kata_composition"
            ].get(
                composition_id
            )

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
                    output_ref[
                        "kata_id"
                    ] != kata_id
                    or output_ref[
                        "version"
                    ] != version
                ):
                    errors.append(
                        "composition output targets "
                        "a different KATA/version"
                    )


    # ------------------------------------------------------------------
    # ApplicabilityAssessment
    # ------------------------------------------------------------------

    elif record_type == "applicability_assessment":

        kata_id = instance.get(
            "kata_id"
        )

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_id
        )

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
                "minimum_match_score must match "
                "the KATA applicability policy"
            )

        if (
            instance.get(
                "decision"
            ) == "reuse"
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
                    "reuse decision requires all "
                    "required_conditions to be met"
                )

        configured = set(
            kata.get(
                "failure_boundary_ids",
                [],
            )
        )

        checked = {
            check[
                "boundary_id"
            ]
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

        matched_actions = []

        for check in instance.get(
            "boundary_checks",
            [],
        ):

            boundary_id = check[
                "boundary_id"
            ]

            boundary = registry[
                "failure_boundary"
            ].get(
                boundary_id
            )

            if boundary is None:
                errors.append(
                    "unknown boundary_id "
                    f"{boundary_id!r}"
                )
                continue

            if check[
                "matched"
            ]:
                matched_actions.append(
                    boundary[
                        "on_match"
                    ]
                )

        decision = instance.get(
            "decision"
        )

        if "fail_closed" in matched_actions:

            if decision != "reject":
                errors.append(
                    "matched fail_closed boundary "
                    "requires decision 'reject'"
                )

        elif "reject_reuse" in matched_actions:

            if decision == "reuse":
                errors.append(
                    "matched reject_reuse boundary "
                    "forbids decision 'reuse'"
                )

        elif (
            "escalate_to_deep"
            in matched_actions
        ):

            if decision != "escalate":
                errors.append(
                    "matched escalate_to_deep boundary "
                    "requires decision 'escalate'"
                )


    # ------------------------------------------------------------------
    # TraceRecord
    # ------------------------------------------------------------------

    elif record_type == "trace_record":

        mode = instance.get(
            "execution_mode"
        )

        if mode == "kata":

            kata_id = instance.get(
                "applied_kata_id"
            )

            assessment_id = instance.get(
                "applicability_assessment_id"
            )

            kata = registry[
                "reasoning_kata"
            ].get(
                kata_id
            )

            if kata is None:
                errors.append(
                    "unknown applied_kata_id "
                    f"{kata_id!r}"
                )

            assessment = registry[
                "applicability_assessment"
            ].get(
                assessment_id
            )

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
                        "applicability decision 'reuse'"
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

        elif mode == "orchestrated":

            selection_id = instance.get(
                "selection_decision_id"
            )

            plan_id = instance.get(
                "orchestration_plan_id"
            )

            selection = registry[
                "kata_selection_decision"
            ].get(
                selection_id
            )

            if selection is None:
                errors.append(
                    "unknown selection_decision_id "
                    f"{selection_id!r}"
                )

            elif (
                selection[
                    "decision"
                ]
                != "composed"
            ):
                errors.append(
                    "orchestrated execution requires "
                    "selection decision 'composed'"
                )

            plan = registry[
                "kata_orchestration_plan"
            ].get(
                plan_id
            )

            if plan is None:
                errors.append(
                    "unknown orchestration_plan_id "
                    f"{plan_id!r}"
                )

            elif (
                plan[
                    "selection_decision_id"
                ]
                != selection_id
            ):
                errors.append(
                    "orchestration plan references "
                    "a different selection decision"
                )


    # ------------------------------------------------------------------
    # KataEvolutionRecord
    # ------------------------------------------------------------------

    elif record_type == "kata_evolution_record":

        kata_id = instance.get(
            "kata_id"
        )

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_id
        )

        if (
            kata is not None
            and kata[
                "version"
            ] != instance[
                "to_version"
            ]
        ):
            errors.append(
                "to_version must match "
                "the current KATA version"
            )


    # ------------------------------------------------------------------
    # KataLineage
    # ------------------------------------------------------------------

    elif record_type == "kata_lineage":

        if lineage_has_cycle(
            instance,
            registry,
        ):
            errors.append(
                "KATA lineage graph "
                "must be acyclic"
            )

        kata_ref = instance[
            "kata_ref"
        ]

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_ref[
                "kata_id"
            ]
        )

        if kata is not None:

            if (
                kata[
                    "version"
                ]
                != kata_ref[
                    "version"
                ]
            ):
                errors.append(
                    "lineage kata_ref version "
                    "does not match "
                    "ReasoningKATA version"
                )

            if (
                kata.get(
                    "lineage_id"
                )
                != instance[
                    "lineage_id"
                ]
            ):
                errors.append(
                    "ReasoningKATA lineage_id "
                    "does not reference "
                    "this lineage record"
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
            output_ref[
                "kata_id"
            ]
        )

        if kata is not None:

            if (
                kata[
                    "version"
                ]
                != output_ref[
                    "version"
                ]
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
                    "ReasoningKATA composition_id "
                    "does not reference "
                    "this composition"
                )


    # ------------------------------------------------------------------
    # KataMaturityAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_maturity_assessment":

        kata_ref = instance[
            "kata_ref"
        ]

        kata_id = kata_ref[
            "kata_id"
        ]

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_id
        )

        if kata is not None:

            if (
                kata[
                    "version"
                ]
                != kata_ref[
                    "version"
                ]
            ):
                errors.append(
                    "maturity assessment version "
                    "does not match "
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
            ].get(
                validation_id
            )

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
                instance[
                    "level"
                ]
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
                    f"{instance['level']} requires "
                    "supported causal validation records"
                )


    # ------------------------------------------------------------------
    # KataSelectionDecision
    # ------------------------------------------------------------------

    elif record_type == "kata_selection_decision":

        request_id = instance[
            "request_id"
        ]

        request = registry[
            "kata_selection_request"
        ].get(
            request_id
        )

        if request is None:
            errors.append(
                "unknown kata selection request "
                f"{request_id!r}"
            )
            return errors

        requested_candidates = kata_ref_set(
            request[
                "candidate_kata_refs"
            ]
        )

        evaluated_candidates = {
            kata_ref_key(
                evaluation[
                    "kata_ref"
                ]
            )
            for evaluation
            in instance[
                "candidate_evaluations"
            ]
        }

        if (
            requested_candidates
            != evaluated_candidates
        ):
            errors.append(
                "candidate_evaluations must cover "
                "exactly the candidate KATAs "
                "from the selection request"
            )

        selected = kata_ref_set(
            instance.get(
                "selected_kata_refs",
                [],
            )
        )

        max_selected = request[
            "constraints"
        ][
            "max_selected_katas"
        ]

        if (
            len(selected)
            > max_selected
        ):
            errors.append(
                "selected KATA count exceeds "
                "max_selected_katas"
            )

        minimum_maturity = request[
            "constraints"
        ].get(
            "minimum_maturity_level"
        )

        evaluation_map = {
            kata_ref_key(
                evaluation[
                    "kata_ref"
                ]
            ): evaluation
            for evaluation
            in instance[
                "candidate_evaluations"
            ]
        }

        for key in selected:

            evaluation = evaluation_map.get(
                key
            )

            if evaluation is None:
                continue

            applicability_id = evaluation.get(
                "applicability_assessment_id"
            )

            if applicability_id is None:
                errors.append(
                    "selected KATA requires "
                    "applicability_assessment_id"
                )

            else:

                applicability = registry[
                    "applicability_assessment"
                ].get(
                    applicability_id
                )

                if applicability is None:
                    errors.append(
                        "unknown "
                        "applicability_assessment_id "
                        f"{applicability_id!r}"
                    )

                elif (
                    applicability[
                        "decision"
                    ]
                    != "reuse"
                ):
                    errors.append(
                        "selected KATA requires "
                        "applicability decision 'reuse'"
                    )

            maturity_id = evaluation.get(
                "maturity_assessment_id"
            )

            if maturity_id is None:
                errors.append(
                    "selected KATA requires "
                    "maturity_assessment_id"
                )

            else:

                maturity = registry[
                    "kata_maturity_assessment"
                ].get(
                    maturity_id
                )

                if maturity is None:
                    errors.append(
                        "unknown maturity_assessment_id "
                        f"{maturity_id!r}"
                    )

                else:

                    maturity_key = kata_ref_key(
                        maturity[
                            "kata_ref"
                        ]
                    )

                    if maturity_key != key:
                        errors.append(
                            "maturity assessment "
                            "targets a different "
                            "candidate KATA/version"
                        )

                    if minimum_maturity is not None:

                        if (
                            MATURITY_RANK[
                                maturity[
                                    "level"
                                ]
                            ]
                            < MATURITY_RANK[
                                minimum_maturity
                            ]
                        ):
                            errors.append(
                                "selected KATA does not "
                                "meet minimum maturity "
                                f"{minimum_maturity}"
                            )


    # ------------------------------------------------------------------
    # KataOrchestrationPlan
    # ------------------------------------------------------------------

    elif record_type == "kata_orchestration_plan":

        decision_id = instance[
            "selection_decision_id"
        ]

        decision = registry[
            "kata_selection_decision"
        ].get(
            decision_id
        )

        if decision is None:
            errors.append(
                "unknown selection_decision_id "
                f"{decision_id!r}"
            )

        elif (
            decision[
                "decision"
            ]
            != "composed"
        ):
            errors.append(
                "orchestration plan requires "
                "selection decision 'composed'"
            )

        composition_id = instance.get(
            "source_composition_id"
        )

        if composition_id is not None:

            composition = registry[
                "kata_composition"
            ].get(
                composition_id
            )

            if composition is None:
                errors.append(
                    "unknown source_composition_id "
                    f"{composition_id!r}"
                )

            else:

                if (
                    instance[
                        "execution_strategy"
                    ]
                    != composition[
                        "execution_strategy"
                    ]
                ):
                    errors.append(
                        "orchestration strategy must "
                        "match source composition"
                    )

                if (
                    instance[
                        "conflict_policy"
                    ]
                    != composition[
                        "conflict_policy"
                    ]
                ):
                    errors.append(
                        "orchestration conflict_policy "
                        "must match source composition"
                    )

                if (
                    instance[
                        "fallback_policy"
                    ]
                    != composition[
                        "fallback_policy"
                    ]
                ):
                    errors.append(
                        "orchestration fallback_policy "
                        "must match source composition"
                    )

                stage_refs = {
                    kata_ref_key(
                        stage[
                            "kata_ref"
                        ]
                    )
                    for stage
                    in instance[
                        "stages"
                    ]
                }

                component_refs = {
                    kata_ref_key(
                        component[
                            "kata_ref"
                        ]
                    )
                    for component
                    in composition[
                        "components"
                    ]
                }

                if stage_refs != component_refs:
                    errors.append(
                        "orchestration stages must cover "
                        "exactly the source composition "
                        "components"
                    )


    # ------------------------------------------------------------------
    # KataHandoffRecord
    # ------------------------------------------------------------------

    elif record_type == "kata_handoff_record":

        plan_id = instance[
            "plan_id"
        ]

        plan = registry[
            "kata_orchestration_plan"
        ].get(
            plan_id
        )

        if plan is None:
            errors.append(
                "unknown orchestration plan "
                f"{plan_id!r}"
            )
            return errors

        stages = {
            stage[
                "stage_id"
            ]: stage
            for stage
            in plan[
                "stages"
            ]
        }

        from_stage_id = instance[
            "from_stage_id"
        ]

        to_stage_id = instance[
            "to_stage_id"
        ]

        from_stage = stages.get(
            from_stage_id
        )

        to_stage = stages.get(
            to_stage_id
        )

        if from_stage is None:
            errors.append(
                "unknown from_stage_id "
                f"{from_stage_id!r}"
            )

        if to_stage is None:
            errors.append(
                "unknown to_stage_id "
                f"{to_stage_id!r}"
            )

        if (
            from_stage is None
            or to_stage is None
        ):
            return errors

        if (
            from_stage[
                "kata_ref"
            ][
                "kata_id"
            ]
            != instance[
                "from_kata_id"
            ]
        ):
            errors.append(
                "from_kata_id does not match "
                "the source orchestration stage"
            )

        if (
            to_stage[
                "kata_ref"
            ][
                "kata_id"
            ]
            != instance[
                "to_kata_id"
            ]
        ):
            errors.append(
                "to_kata_id does not match "
                "the destination orchestration stage"
            )

        if (
            from_stage_id
            not in to_stage.get(
                "depends_on",
                [],
            )
        ):
            errors.append(
                "handoff destination stage must "
                "depend on the source stage"
            )

        provided = set(
            instance.get(
                "provided_fields",
                [],
            )
        )

        required = set(
            instance.get(
                "required_fields",
                [],
            )
        )

        source_outputs = set(
            from_stage.get(
                "output_contract",
                [],
            )
        )

        destination_inputs = set(
            to_stage.get(
                "input_contract",
                [],
            )
        )

        if not provided.issubset(
            source_outputs
        ):
            errors.append(
                "handoff provided_fields must be "
                "declared by source output_contract"
            )

        if required != destination_inputs:
            errors.append(
                "handoff required_fields must match "
                "destination input_contract"
            )

        # v0.5:
        # Compatibility Before Handoff

        matching = (
            matching_interoperability_assessments(
                registry,
                from_stage[
                    "kata_ref"
                ],
                to_stage[
                    "kata_ref"
                ],
            )
        )

        compatible = [
            assessment
            for assessment in matching
            if assessment.get(
                "decision"
            ) == "compatible"
        ]

        if not compatible:
            errors.append(
                "handoff requires a compatible "
                "KataInteroperabilityAssessment"
            )


    # ------------------------------------------------------------------
    # ZEROSHIKI PackageManifest
    # ------------------------------------------------------------------

    elif record_type == "zeroshiki_package_manifest":

        supported = set(
            instance[
                "supported_record_types"
            ]
        )

        for record_name in supported:

            if (
                record_name
                not in SCHEMA_BY_RECORD_TYPE
            ):
                errors.append(
                    "manifest declares unknown "
                    "record type "
                    f"{record_name!r}"
                )

        for profile_id in instance[
            "conformance_profile_ids"
        ]:

            profile = registry[
                "conformance_profile"
            ].get(
                profile_id
            )

            if profile is None:
                errors.append(
                    "unknown conformance_profile_id "
                    f"{profile_id!r}"
                )
                continue

            required = set(
                profile[
                    "required_record_types"
                ]
            )

            missing = (
                required
                - supported
            )

            if missing:
                errors.append(
                    "manifest does not support "
                    "profile-required record types: "
                    + ", ".join(
                        sorted(
                            missing
                        )
                    )
                )


    # ------------------------------------------------------------------
    # ConformanceProfile
    # ------------------------------------------------------------------

    elif record_type == "conformance_profile":

        for record_name in instance[
            "required_record_types"
        ]:

            if (
                record_name
                not in SCHEMA_BY_RECORD_TYPE
            ):
                errors.append(
                    "unknown profile-required "
                    "record type "
                    f"{record_name!r}"
                )


    # ------------------------------------------------------------------
    # KataInterfaceContract
    # ------------------------------------------------------------------

    elif record_type == "kata_interface_contract":

        kata_ref = instance[
            "kata_ref"
        ]

        kata = registry[
            "reasoning_kata"
        ].get(
            kata_ref[
                "kata_id"
            ]
        )

        # External KATA references are permitted.
        # If the KATA exists locally, the version
        # MUST agree with the contract.

        if (
            kata is not None
            and kata[
                "version"
            ] != kata_ref[
                "version"
            ]
        ):
            errors.append(
                "interface contract KATA version "
                "does not match local ReasoningKATA"
            )


    # ------------------------------------------------------------------
    # KataConformanceAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_conformance_assessment":

        profile_id = instance[
            "profile_id"
        ]

        profile = registry[
            "conformance_profile"
        ].get(
            profile_id
        )

        if profile is None:
            errors.append(
                "unknown conformance profile "
                f"{profile_id!r}"
            )
            return errors

        interface_id = instance[
            "interface_id"
        ]

        interface = registry[
            "kata_interface_contract"
        ].get(
            interface_id
        )

        if interface is None:
            errors.append(
                "unknown interface_id "
                f"{interface_id!r}"
            )

        else:

            if (
                kata_ref_key(
                    interface[
                        "kata_ref"
                    ]
                )
                != kata_ref_key(
                    instance[
                        "kata_ref"
                    ]
                )
            ):
                errors.append(
                    "interface contract targets "
                    "a different KATA/version"
                )

        required_checks = set(
            profile[
                "required_checks"
            ]
        )

        observed_checks = {
            check[
                "check_id"
            ]: check
            for check
            in instance[
                "checks"
            ]
        }

        for check_id in required_checks:

            check = observed_checks.get(
                check_id
            )

            if check is None:
                errors.append(
                    "missing required conformance "
                    f"check {check_id!r}"
                )

            elif (
                instance[
                    "result"
                ]
                == "conformant"
                and check[
                    "status"
                ]
                != "pass"
            ):
                errors.append(
                    "conformant result requires all "
                    "required checks to pass"
                )

        if (
            instance[
                "result"
            ]
            == "non_conformant"
        ):

            failing_required = any(
                (
                    check_id
                    not in observed_checks
                )
                or (
                    observed_checks[
                        check_id
                    ][
                        "status"
                    ]
                    != "pass"
                )
                for check_id
                in required_checks
            )

            if not failing_required:
                errors.append(
                    "non_conformant result requires "
                    "at least one failed or missing "
                    "required check"
                )


    # ------------------------------------------------------------------
    # KataInteroperabilityAssessment
    # ------------------------------------------------------------------

    elif record_type == "kata_interoperability_assessment":

        producer_interface_id = instance[
            "producer_interface_id"
        ]

        consumer_interface_id = instance[
            "consumer_interface_id"
        ]

        producer_interface = registry[
            "kata_interface_contract"
        ].get(
            producer_interface_id
        )

        consumer_interface = registry[
            "kata_interface_contract"
        ].get(
            consumer_interface_id
        )

        if producer_interface is None:
            errors.append(
                "unknown producer_interface_id "
                f"{producer_interface_id!r}"
            )

        if consumer_interface is None:
            errors.append(
                "unknown consumer_interface_id "
                f"{consumer_interface_id!r}"
            )

        if (
            producer_interface is None
            or consumer_interface is None
        ):
            return errors

        producer_ref = instance[
            "producer_kata_ref"
        ]

        consumer_ref = instance[
            "consumer_kata_ref"
        ]

        version_compatible = True

        if (
            kata_ref_key(
                producer_interface[
                    "kata_ref"
                ]
            )
            != kata_ref_key(
                producer_ref
            )
        ):
            errors.append(
                "producer interface targets "
                "a different KATA/version"
            )

            version_compatible = False

        if (
            kata_ref_key(
                consumer_interface[
                    "kata_ref"
                ]
            )
            != kata_ref_key(
                consumer_ref
            )
        ):
            errors.append(
                "consumer interface targets "
                "a different KATA/version"
            )

            version_compatible = False

        producer_outputs = (
            interface_field_map(
                producer_interface,
                "outputs",
            )
        )

        consumer_inputs = (
            interface_field_map(
                consumer_interface,
                "inputs",
            )
        )

        mappings = instance.get(
            "field_mappings",
            [],
        )

        mapped_consumer_inputs = set()

        mapping_type_compatible = True

        mapping_names_valid = True

        for mapping in mappings:

            producer_name = mapping[
                "producer_output"
            ]

            consumer_name = mapping[
                "consumer_input"
            ]

            producer_field = (
                producer_outputs.get(
                    producer_name
                )
            )

            consumer_field = (
                consumer_inputs.get(
                    consumer_name
                )
            )

            if producer_field is None:
                errors.append(
                    "field mapping references "
                    "unknown producer output "
                    f"{producer_name!r}"
                )

                mapping_names_valid = False

            if consumer_field is None:
                errors.append(
                    "field mapping references "
                    "unknown consumer input "
                    f"{consumer_name!r}"
                )

                mapping_names_valid = False

            if (
                producer_field is None
                or consumer_field is None
            ):
                mapping_type_compatible = False
                continue

            mapped_consumer_inputs.add(
                consumer_name
            )

            if not field_type_compatible(
                producer_field[
                    "field_type"
                ],
                consumer_field[
                    "field_type"
                ],
            ):
                mapping_type_compatible = False

        required_consumer_inputs = {
            name
            for (
                name,
                field,
            ) in consumer_inputs.items()
            if field[
                "required"
            ]
        }

        required_inputs_satisfied = (
            required_consumer_inputs
            .issubset(
                mapped_consumer_inputs
            )
        )

        type_compatible = (
            mapping_names_valid
            and mapping_type_compatible
        )

        trace_preserved = (
            producer_interface.get(
                "trace_required"
            )
            is True
            and consumer_interface.get(
                "trace_required"
            )
            is True
            and bool(
                instance.get(
                    "evidence_trace_ids"
                )
            )
        )

        declared = instance[
            "compatibility_checks"
        ]

        derived = {
            "required_inputs_satisfied":
                required_inputs_satisfied,

            "type_compatible":
                type_compatible,

            "version_compatible":
                version_compatible,

            "trace_preserved":
                trace_preserved,
        }

        for key, value in derived.items():

            if declared[
                key
            ] != value:
                errors.append(
                    f"compatibility check "
                    f"{key!r} does not match "
                    f"derived value {value!r}"
                )

        all_compatible = all(
            derived.values()
        )

        if (
            instance[
                "decision"
            ]
            == "compatible"
            and not all_compatible
        ):
            errors.append(
                "compatible decision requires "
                "all derived compatibility "
                "checks to pass"
            )

        if (
            instance[
                "decision"
            ]
            == "incompatible"
            and all_compatible
        ):
            errors.append(
                "incompatible decision requires "
                "at least one compatibility failure"
            )

    return errors


# ======================================================================
# Pass Record Collection
# ======================================================================

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

        records.append(
            instance
        )

    return records


# ======================================================================
# Main
# ======================================================================

def main() -> int:

    print(
        "=== ZEROSHIKI Reasoning OS "
        "v0.5 Validation ==="
    )

    schemas: dict[
        str,
        dict[str, Any],
    ] = {}


    # ------------------------------------------------------------------
    # Load Schemas
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

            schema = load_json(
                path
            )

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


    # ------------------------------------------------------------------
    # Load Example Paths
    # ------------------------------------------------------------------

    pass_paths = iter_examples(
        PASS_DIR
    )

    fail_paths = iter_examples(
        FAIL_DIR
    )


    # ------------------------------------------------------------------
    # Build Registry
    # ------------------------------------------------------------------

    pass_records = (
        collect_locally_valid_records(
            pass_paths,
            schemas,
        )
    )

    registry = build_registry(
        pass_records
    )

    registry_errors = (
        registry_integrity_errors(
            pass_records
        )
    )


    # ------------------------------------------------------------------
    # Pass Examples
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

        semantic_errors = (
            local_semantic_errors(
                instance
            )
            + cross_semantic_errors(
                instance,
                registry,
            )
        )

        if semantic_errors:

            pass_failed = True

            print(
                "  [semantic-error]"
            )

            for error in semantic_errors:
                print(
                    f"    - {error}"
                )

        else:

            print(
                "  [semantic-ok]"
            )


    # ------------------------------------------------------------------
    # Registry Integrity
    # ------------------------------------------------------------------

    if registry_errors:

        pass_failed = True

        print(
            "\n[registry integrity]\n"
        )

        for error in registry_errors:
            print(
                f"- {error}"
            )


    # ------------------------------------------------------------------
    # Fail Examples
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

        temp_records = (
            pass_records
            + [instance]
        )

        temp_registry = build_registry(
            temp_records
        )

        semantic_errors = (
            local_semantic_errors(
                instance
            )
            + cross_semantic_errors(
                instance,
                temp_registry,
            )
        )

        if semantic_errors:

            print(
                "  [expected-semantic-failure]"
            )

            for error in semantic_errors:
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

    if (
        pass_failed
        or fail_failed
    ):

        print(
            "[validation-failed]"
        )

        return 1

    print(
        "[validation-ok]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
