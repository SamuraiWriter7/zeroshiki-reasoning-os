# Changelog

All notable changes to **ZEROSHIKI Reasoning OS** are documented in this file.

The project follows semantic versioning for specification releases where practical.

---

## [0.5.0] - 2026-08-15

### Codename

`KATA Conformance Core`

### Added

- Added `ZEROSHIKIPackageManifest`.
- Added `ConformanceProfile`.
- Added `KataInterfaceContract`.
- Added `KataConformanceAssessment`.
- Added `KataInteroperabilityAssessment`.
- Added package-level capability declarations.
- Added explicit KATA input/output interfaces.
- Added KATA preconditions and postconditions.
- Added explicit KATA failure signals.
- Added profile-based conformance evaluation.
- Added evidence-backed conformance decisions.
- Added producer-to-consumer field mappings.
- Added required consumer-input validation.
- Added interface field-type compatibility validation.
- Added KATA/interface version consistency checks.
- Added Trace-preservation requirements for interoperability.
- Added compatibility validation before KATA handoff.
- Added conformance profile references from package manifests.
- Added extension namespaces.
- Added compatibility policies:
  - `exact`
  - `compatible_minor`
  - `declared_mapping`
- Added v0.5 cross-record semantic validation.
- Expanded validator support to 19 schema types.

### Changed

- All v0.5 records now use:

  ```text
  schema_version: 0.5.0

  Cross-KATA handoff now requires compatibility evidence.
Portable KATA are expected to expose an explicit KataInterfaceContract.
Conformance assessments must reference a declared ConformanceProfile.
A conformant result requires all profile-required checks to pass.
An incompatible interoperability result must correspond to an actual derived compatibility failure.
Package manifests must support record types required by their declared conformance profiles.
Interface contracts may reference external KATA, but locally available KATA versions must match.
Extensions may extend ZEROSHIKI Core but must not redefine Core semantics.
Core Invariants Added
Z21 — No Conformance Without Profile
Z22 — No Portable KATA Without Interface
Z23 — Consumer Requirements Must Be Satisfied
Z24 — Compatibility Before Handoff
Z25 — Version Mismatch Must Be Explicit
Z26 — Extensions Must Not Rewrite Core Semantics
Z27 — Conformance Requires Evidence
Z28 — Interoperability Must Remain Traceable
Milestone

v0.5 establishes the first complete ZEROSHIKI Reasoning OS architectural cycle:

Experience
→ Trace
→ KATA
→ Applicability
→ Lineage
→ Maturity
→ Selection
→ Orchestration
→ Interface
→ Interoperability
→ Conformance

v0.5 is intended as the first major specification-completion boundary before extension profiles and external bindings.

[0.4.0] - 2026-08-14
Codename

KATA Orchestration Core

Added
Added KataSelectionRequest.
Added KataSelectionDecision.
Added KataOrchestrationPlan.
Added KataHandoffRecord.
Added candidate KATA evaluation.
Added evidence-gated KATA selection.
Added selection objectives:
accuracy
latency
compute efficiency
safety
balanced
Added selection constraints:
maximum selected KATA count,
minimum maturity,
maximum compute level.
Added orchestration execution strategies:
sequential,
parallel,
gated,
hybrid.
Added stage dependency definitions.
Added orchestration dependency-graph validation.
Added KATA handoff contracts.
Added stage input and output contracts.
Added orchestration conflict policies.
Added orchestration fallback policies.
Added orchestrated execution mode to TraceRecord.
Added selection and orchestration references to execution traces.
Changed
KATA selection is performed after applicability evaluation.
Failure boundaries take precedence over ranking.
Boundary-blocked KATA cannot be selected.
Maturity does not override applicability failure.
Orchestration stage graphs must remain acyclic.
Multi-KATA execution must preserve explicit handoff contracts.
ReasoningKATA references:
lineage,
composition,
maturity assessment.
Core Invariants Added
Z13 — Applicability Before Ranking
Z14 — Boundary Before Score
Z15 — No Selection Without Evidence
Z16 — Lowest Sufficient KATA Set
Z17 — No Orchestration Without Conflict Policy
Z18 — No Handoff Without Contract
Z19 — Maturity Does Not Override Inapplicability
Z20 — Every Orchestration Produces Trace
[0.3.0] - 2026-08-13
Codename

KATA Lineage Core

Added
Added KataLineage.
Added KataComposition.
Added KataMaturityAssessment.
Added explicit KATA parent relationships.
Added explicit root KATA relationships.
Added KATA generation depth.
Added derivation types:
root,
refinement,
specialization,
generalization,
composition,
fork.
Added inherited and introduced step tracking.
Added composite KATA definitions.
Added composition execution strategies.
Added composition conflict policies.
Added composition merge policies.
Added KATA maturity levels:
K0 Experimental,
K1 Observed,
K2 Repeated,
K3 Causally Validated,
K4 Cross-Context Validated,
K5 Stable.
Added evidence-gated maturity promotion.
Added maturity retain and demote operations.
Added local self-parent validation.
Added local lineage-cycle detection.
Added self-recursive composition rejection.
Added causal-evidence requirements for K3 and above.
Added cross-context requirements for K4 and above.
Added regression-stability requirement for K5.
Changed
Parent relationships were moved out of the ReasoningKATA body into KataLineage.
KATA lineage, composition, and maturity became independent auditable records.
ReasoningKATA may reference a KataComposition.
KATA maturity is no longer treated as an informal status label.
Maturity transitions are checked against evidence and previous maturity level.
Core Invariants Added
Z9 — No Derivative Without Lineage
Z10 — Lineage Must Be Acyclic
Z11 — No Composition Without Conflict Policy
Z12 — No Maturity Without Evidence
[0.2.0] - 2026-08-13
Codename

KATA Gate

Added
Added ApplicabilityAssessment.
Added FailureBoundary.
Added explicit KATA applicability decisions:
reuse,
escalate,
reject.
Added minimum_match_score.
Added required-condition validation.
Added structured failure-boundary checks.
Added boundary precedence over similarity.
Added structured intervention definitions to causal validation.
Added minimum causal-effect thresholds.
Added applicability references to KATA execution traces.
Added applicability evidence to KATA evolution records.
Added cross-record semantic validation.
Changed
ReasoningKATA now references failure boundaries by ID.
KATA reuse now requires applicability evaluation.
CausalValidation distinguishes:
baseline score,
intervention score,
effect delta,
minimum effect threshold.
A supported causal conclusion requires sufficient observed effect.
Deep reasoning became the standard escalation path for unresolved KATA applicability.
KATA execution cannot proceed when its applicability decision is not reuse.
Core Invariants Added / Refined
Z4 — No Reuse Without Applicability Assessment
Z5 — Boundary Overrides Similarity
Z6 — No Causal Support Below Threshold
Structural Transition

v0.2 changed the architecture from:

Find similar KATA
→ Reuse

to:

Find candidate KATA
→ Check applicability
→ Check boundaries
→ Reuse / Escalate / Reject
[0.1.0] - 2026-08-13
Codename

Pranayama-KATA Core

Added
Initial public ZEROSHIKI Reasoning OS specification.

Defined the Grand Loop:

Experience
    ↓
Trace
    ↓
Causal Validation
    ↓
Pattern Extraction
    ↓
Reasoning KATA
    ↓
Computational Breathing
    ↓
Adaptive Reuse
    ↓
Execution
    ↓
New Trace
    ↓
KATA Evolution
    ↺
Added ReasoningKATA.
Added TraceRecord.
Added CausalValidation.
Added BreathingProfile.
Added KataEvolutionRecord.
Added JSON Schema validation.
Added semantic example validation.
Added pass examples.
Added intentionally invalid fail examples.
Added computational breathing levels:
rest,
kata,
deep.
Added compute budget classes:
minimal,
bounded,
extended.
Added cache policies.
Added reversible KATA evolution.
Added causal-effect delta validation.
Added Trace-based KATA origin requirements.
Added GitHub Actions validation workflow.
Design Decisions
Reasoning traces are represented as auditable decision evidence rather than mandatory hidden chain-of-thought.
Compute levels are logical policy classes rather than universal token counts.
Cache policy and observed cache outcome are represented separately.
KATA evolution is versioned and reversible.
JSON Schema validates structure.
Python semantic validation enforces relationships that cannot be expressed reliably through isolated schemas.
Initial Core Invariants
Z1 — No KATA Without Trace
Z2 — No Evolution Without Validation
Z3 — No Deep Reasoning Without Need
Z4 — No Reuse Without Applicability Check
Z5 — No Causal Claim Without Validation Method
Z6 — Every Execution Produces a Trace
Z7 — Evolution Must Be Reversible
Initial Principle

Do not remember every thought. Preserve the KATA that can recreate it.

Do not reason deeply by default. Breathe computation according to need.

Do not evolve from success alone. Evolve from traceable evidence.

Architectural Progression

The first five ZEROSHIKI Reasoning OS releases form one continuous progression.

v0.1
Experience
   ↓
Trace
   ↓
Reasoning KATA


v0.2
Reasoning KATA
   ↓
Applicability Gate


v0.3
KATA
   ↓
Lineage
   ↓
Maturity


v0.4
Candidate KATA
   ↓
Selection
   ↓
Orchestration
   ↓
Handoff


v0.5
Interface
   ↓
Interoperability
   ↓
Conformance

The resulting v0.5 architecture is:

Experience
    ↓
Trace
    ↓
Causal Evidence
    ↓
Reasoning KATA
    ↓
Applicability
    ↓
Lineage / Maturity
    ↓
Selection
    ↓
Orchestration
    ↓
Interface
    ↓
Interoperability
    ↓
Conformance
    ↓
Portable Reasoning System
v0.5 Milestone Statement

ZEROSHIKI Reasoning OS v0.5 completes the first specification cycle.

The architecture now defines not only how a reusable reasoning form is created, but also:

where it came from,
when it should be used,
when it should not be used,
how mature it is,
how multiple KATA are selected,
how KATA are composed,
how execution is orchestrated,
how outputs are handed to another KATA,
how interfaces are declared,
how compatibility is evaluated,
how conformance is demonstrated.

The specification therefore moves from:

Reusable Reasoning

to:

Traceable, Evolvable, Orchestratable, and Portable Reasoning.
