# ZEROSHIKI Reasoning OS

**Version:** v0.5.0  
**Status:** Draft / Reference Specification  
**Codename:** `KATA Conformance Core`

ZEROSHIKI Reasoning OS is a traceable reasoning architecture that converts experience into reusable **Reasoning KATA**, evaluates when those KATA should be used, evolves them from evidence, orchestrates multiple KATA, and preserves their meaning across implementations through explicit interfaces and conformance rules.

> Do not remember every thought.  
> Preserve the KATA that can recreate it.
>
> Do not reason deeply by default.  
> Breathe computation according to need.
>
> Do not evolve from success alone.  
> Evolve from traceable evidence.

---

## 1. What is ZEROSHIKI Reasoning OS?

ZEROSHIKI Reasoning OS is not a new foundation model.

It is a structural layer for managing reusable reasoning behavior.

Its core question is:

> Can an AI learn a reasoning form in the same way that a human retains the structure of riding a bicycle, playing an instrument, or practicing a martial-arts KATA?

Instead of storing every reasoning episode indefinitely, ZEROSHIKI OS converts experience into a smaller reusable structure:

```text
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
Applicability
    ↓
Computational Breathing
    ↓
Selection
    ↓
Orchestration
    ↓
Execution
    ↓
New Trace
    ↓
KATA Evolution
    ↺
```

The purpose is not infinite memory.

The purpose is:

> **Memory Compression by Structure.**

---

## 2. What does “ZEROSHIKI” mean?

ZEROSHIKI does not mean zero intelligence.

It means returning to a minimal structural baseline and activating only what is necessary.

```text
ZERO
=
Minimum necessary structure
+
No unnecessary reasoning
+
No unnecessary execution
+
No unnecessary assumption
```

The system attempts to avoid two opposite failures:

```text
Too little structure
→ unstable reasoning

Too much structure
→ rigid and expensive reasoning
```

ZEROSHIKI therefore aims for:

> **A strong core with deliberate structural margin.**

---

## 3. Evolution from v0.1 to v0.5

| Version | Layer | Core Question |
|---|---|---|
| v0.1 | Memory | How can reusable reasoning form be preserved? |
| v0.2 | Judgment | When is a KATA actually applicable? |
| v0.3 | Lineage | Where did a KATA come from and how mature is it? |
| v0.4 | Orchestration | Which KATA should be selected and combined? |
| v0.5 | Conformance | Can the KATA preserve meaning across implementations? |

In simplified form:

```text
v0.1
Remember the KATA.

      ↓

v0.2
Know when not to use it.

      ↓

v0.3
Know where it came from.

      ↓

v0.4
Know how to combine it.

      ↓

v0.5
Know whether another system
can safely understand and use it.
```

---

# 4. Architecture

```text
                     Experience
                         │
                         ↓
                       Trace
                         │
                         ↓
                 Causal Validation
                         │
                         ↓
                 Pattern Extraction
                         │
                         ↓
                 ┌───────────────┐
                 │ Reasoning KATA│
                 └───────┬───────┘
                         │
                 Applicability Gate
                         │
              ┌──────────┴──────────┐
              │                     │
            reuse                escalate
              │                     │
              ↓                     ↓
      Computational Breathing      Deep
              │
              ↓
        KATA Selection
              │
       ┌──────┴───────┐
       │              │
    Single         Composite
     KATA             KATA
       │              │
       │        Orchestration Plan
       │              │
       │        KATA → Handoff → KATA
       │              │
       └──────┬───────┘
              ↓
           Execution
              │
              ↓
           New Trace
              │
              ↓
        KATA Evolution
              │
              ↺

──────────────── Interoperability Layer ────────────────

KATA
 ↓
Interface Contract
 ↓
Compatibility Assessment
 ↓
Conformance Assessment
 ↓
Package Manifest
```

---

# 5. Core Record Types

ZEROSHIKI Reasoning OS v0.5 defines 19 schema types.

## v0.1 — Reasoning Core

### `ReasoningKATA`

Reusable reasoning structure.

Defines:

- activation conditions,
- reasoning steps,
- validation criteria,
- failure boundaries,
- origin traces,
- compute policy,
- lineage,
- maturity,
- composition.

### `TraceRecord`

Auditable execution record.

Stores:

```text
Input
→ Applied structure
→ Observable execution evidence
→ Validation
→ Outcome
→ Resource metrics
```

A TraceRecord does **not** require private hidden chain-of-thought.

### `CausalValidation`

Evaluates whether a KATA or reasoning step materially contributed to an outcome.

Supported methods include:

- leave-one-out,
- step ablation,
- KATA ablation,
- alternative KATA comparison,
- manual review.

### `BreathingProfile`

Defines computational breathing policy.

```text
rest
  ↓
minimal compute

kata
  ↓
bounded reusable reasoning

deep
  ↓
extended reasoning
```

### `KataEvolutionRecord`

Records evidence-backed and reversible KATA evolution.

---

# 6. v0.2 — Applicability Layer

### `FailureBoundary`

Explicitly defines situations in which a KATA should not be reused.

Examples:

- missing evidence,
- domain mismatch,
- causal uncertainty,
- stale information,
- safety constraint.

### `ApplicabilityAssessment`

Evaluates whether a specific KATA may be reused for a specific input.

Possible decisions:

```text
reuse
escalate
reject
```

The fundamental rule is:

> **Boundary Overrides Similarity.**

A 0.99 similarity score does not override a matched failure boundary.

---

# 7. v0.3 — Lineage and Maturity

### `KataLineage`

Records how one KATA emerged from others.

Supported derivation types include:

```text
root
refinement
specialization
generalization
composition
fork
```

### `KataComposition`

Defines a composite reasoning structure built from multiple KATA.

Composition includes:

- components,
- execution order,
- conflict policy,
- merge policy,
- fallback policy.

### `KataMaturityAssessment`

Measures evidence-backed KATA maturity.

```text
K0 — Experimental
K1 — Observed
K2 — Repeated
K3 — Causally Validated
K4 — Cross-Context Validated
K5 — Stable
```

Maturity cannot be assigned solely from success count.

---

# 8. v0.4 — KATA Orchestration

### `KataSelectionRequest`

Defines:

- candidate KATA,
- objective,
- compute constraints,
- minimum maturity,
- maximum selected KATA count.

### `KataSelectionDecision`

Records how candidates were evaluated and which KATA were selected.

Selection follows the structural order:

```text
Applicability
    ↓
Failure Boundary
    ↓
Evidence
    ↓
Maturity
    ↓
Efficiency
    ↓
Selection
```

Similarity alone is insufficient.

### `KataOrchestrationPlan`

Transforms selected KATA into an executable graph.

Supported strategies:

```text
sequential
parallel
gated
hybrid
```

Stage dependency graphs MUST remain acyclic.

### `KataHandoffRecord`

Defines auditable transfer between two KATA stages.

A handoff is based on:

```text
Output Contract
      ↓
Handoff
      ↓
Input Contract
```

rather than unrestricted sharing of internal reasoning state.

---

# 9. v0.5 — Conformance and Interoperability

### `ZEROSHIKIPackageManifest`

Declares what a ZEROSHIKI implementation supports.

It identifies:

- specification version,
- implementation,
- supported record types,
- conformance profiles,
- extension namespaces.

### `ConformanceProfile`

Defines what must be satisfied before an implementation or KATA can claim conformance.

A profile specifies:

- required records,
- required checks,
- required invariants,
- compatibility policy,
- extension policy.

### `KataInterfaceContract`

Defines the portable interface of a KATA.

```text
Inputs
Preconditions
     ↓
   KATA
     ↓
Outputs
Postconditions
Failure Signals
Trace
```

### `KataConformanceAssessment`

Evaluates a KATA against a declared conformance profile.

Conformance MUST be evidence-backed.

### `KataInteroperabilityAssessment`

Determines whether the output of one KATA can safely become the input of another.

It evaluates:

- required input coverage,
- field type compatibility,
- KATA/interface version compatibility,
- Trace preservation.

The core rule is:

> **Compatibility Before Handoff.**

---

# 10. Core Invariants

ZEROSHIKI Reasoning OS v0.5 defines the following structural invariants.

## Reasoning and Trace

### Z1 — No KATA Without Trace

A reusable KATA MUST have traceable origin evidence.

### Z2 — No Evolution Without Validation

Successful output alone MUST NOT justify KATA evolution.

### Z3 — No Deep Reasoning Without Need

Implementations SHOULD use the lowest sufficient reasoning level.

### Z4 — No Reuse Without Applicability Assessment

A KATA MUST be evaluated before reuse.

### Z5 — Boundary Overrides Similarity

Failure boundaries take precedence over similarity scores.

### Z6 — No Causal Support Below Threshold

Insufficient causal effect MUST NOT be reported as supported.

### Z7 — Every Execution Produces a Trace

KATA and orchestrated execution MUST remain auditable.

### Z8 — Evolution Must Be Reversible

KATA evolution MUST preserve rollback lineage.

---

## Lineage and Maturity

### Z9 — No Derivative Without Lineage

Derivative KATA MUST preserve ancestry.

### Z10 — Lineage Must Be Acyclic

A KATA MUST NOT become its own ancestor.

### Z11 — No Composition Without Conflict Policy

Composite reasoning requires explicit conflict behavior.

### Z12 — No Maturity Without Evidence

KATA maturity MUST be supported by evidence.

---

## Selection and Orchestration

### Z13 — Applicability Before Ranking

Applicability is evaluated before ranking.

### Z14 — Boundary Before Score

A blocked KATA cannot win by score.

### Z15 — No Selection Without Evidence

Selected KATA require evidence-backed evaluation.

### Z16 — Lowest Sufficient KATA Set

The smallest sufficient KATA set SHOULD be preferred.

### Z17 — No Orchestration Without Conflict Policy

Multi-KATA execution requires defined conflict behavior.

### Z18 — No Handoff Without Contract

Cross-KATA transfer requires an input/output contract.

### Z19 — Maturity Does Not Override Inapplicability

A K5 KATA can still be inappropriate.

### Z20 — Every Orchestration Produces Trace

Composite execution remains traceable.

---

## Conformance and Interoperability

### Z21 — No Conformance Without Profile

Conformance MUST identify the profile being evaluated.

### Z22 — No Portable KATA Without Interface

Portable KATA require explicit interface contracts.

### Z23 — Consumer Requirements Must Be Satisfied

Required consumer inputs MUST be available before handoff.

### Z24 — Compatibility Before Handoff

Interoperability MUST be evaluated before cross-KATA transfer.

### Z25 — Version Mismatch Must Be Explicit

Version mismatch MUST NOT be silently ignored.

### Z26 — Extensions Must Not Rewrite Core Semantics

Extensions MAY add capability but MUST NOT redefine Core meaning.

### Z27 — Conformance Requires Evidence

Self-declaration alone is insufficient for conformance.

### Z28 — Interoperability Must Remain Traceable

Transformations and cross-KATA transfers MUST preserve auditability.

---

# 11. Repository Structure

```text
zeroshiki-reasoning-os/
├── .github/
│   └── workflows/
│       └── validate.yml
│
├── README.md
├── SPEC.md
├── CHANGELOG.md
│
├── schemas/
│   ├── reasoning-kata.schema.json
│   ├── trace-record.schema.json
│   ├── causal-validation.schema.json
│   ├── breathing-profile.schema.json
│   ├── kata-evolution-record.schema.json
│   ├── failure-boundary.schema.json
│   ├── applicability-assessment.schema.json
│   ├── kata-lineage.schema.json
│   ├── kata-composition.schema.json
│   ├── kata-maturity-assessment.schema.json
│   ├── kata-selection-request.schema.json
│   ├── kata-selection-decision.schema.json
│   ├── kata-orchestration-plan.schema.json
│   ├── kata-handoff-record.schema.json
│   ├── zeroshiki-package-manifest.schema.json
│   ├── conformance-profile.schema.json
│   ├── kata-interface-contract.schema.json
│   ├── kata-conformance-assessment.schema.json
│   └── kata-interoperability-assessment.schema.json
│
├── examples/
│   ├── pass/
│   └── fail/
│
└── scripts/
    └── validate_examples.py
```

---

# 12. Validation

Install dependencies:

```bash
python -m pip install jsonschema pyyaml
```

Run:

```bash
python scripts/validate_examples.py
```

Expected final result:

```text
=== Summary ===
[validation-ok]
```

GitHub Actions can run the same validation automatically on:

```text
push
pull_request
workflow_dispatch
```

A conforming example repository SHOULD:

1. accept every document in `examples/pass/`;
2. reject every document in `examples/fail/`;
3. pass JSON Schema validation;
4. pass local semantic validation;
5. pass cross-record reference validation;
6. preserve KATA lineage consistency;
7. preserve applicability and maturity constraints;
8. preserve orchestration DAG integrity;
9. validate handoff contracts;
10. validate declared interoperability relationships.

---

# 13. Schema Validation vs Semantic Validation

JSON Schema handles structural validity.

Example:

```text
Does the field exist?
Is the type correct?
Is the value inside the allowed enum?
```

The Python validator handles semantic validity.

Example:

```text
Does the referenced KATA exist?

Does this ApplicabilityAssessment
actually target that KATA?

Does a K3 assessment really have
causal evidence?

Does the orchestration graph contain a cycle?

Does the consumer interface receive
all required inputs?

Does a "compatible" decision agree
with derived compatibility?
```

ZEROSHIKI therefore distinguishes:

```text
Syntax
  ≠
Meaning
```

Both are required.

---

# 14. Reasoning Privacy

ZEROSHIKI Reasoning OS does not require storage or disclosure of private hidden chain-of-thought.

A conforming Trace SHOULD preserve auditable information such as:

```text
input summary
decision
applied KATA
observable actions
validation evidence
causal evidence
output
resource metrics
```

The objective is:

> Preserve enough evidence to reproduce and audit useful reasoning behavior without requiring unrestricted internal reasoning transcripts.

---

# 15. Computational Breathing

ZEROSHIKI does not assume that deeper reasoning is always better.

```text
Level 0 — Rest
Known / cached / direct
        ↓
minimal compute

Level 1 — KATA
Reusable known reasoning form
        ↓
bounded compute

Level 2 — Deep
Novel / uncertain / conflicting
        ↓
extended compute
```

The architecture therefore treats computation as something to regulate rather than maximize.

> **Do not think maximally.  
> Think sufficiently.**

---

# 16. External KATA

ZEROSHIKI v0.5 permits references to KATA that are not stored inside the local repository.

This allows:

```text
Implementation A
     ↓
KATA Interface

Implementation B
     ↓
KATA Interface

Implementation C
```

to interoperate without requiring a single centralized KATA registry.

Where an external KATA is referenced, implementations SHOULD preserve:

- KATA ID,
- version,
- interface identity,
- provenance information,
- interoperability evidence.

---

# 17. Extensions

ZEROSHIKI Core is designed to support later extension profiles.

Possible future profiles include:

```text
Agent Skills Binding
MCP Binding
Zero Authority Profile
Cryptographic Trace Profile
Distributed KATA Registry
Royalty / Attribution Profile
Edge Computational Breathing
Federated KATA Exchange
```

Extensions MAY add new functionality.

They MUST NOT silently redefine existing ZEROSHIKI Core semantics.

---

# 18. Non-Goals of v0.5

ZEROSHIKI Reasoning OS v0.5 does not attempt to standardize:

- foundation-model architecture,
- model weights,
- hidden chain-of-thought,
- autonomous self-modification,
- universal semantic ontology,
- distributed consensus,
- payment settlement,
- cryptographic immutability,
- a centralized KATA marketplace,
- a mandatory agent framework,
- a mandatory transport protocol.

These may be implemented separately or defined through extension profiles.

---

# 19. v0.5 Completion Boundary

v0.5 represents the first complete architectural cycle.

```text
Experience
    ↓
Trace
    ↓
KATA
    ↓
Applicability
    ↓
Lineage
    ↓
Maturity
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
```

Future versions should extend this architecture rather than destabilize its core.

---

# 20. Core Philosophy

ZEROSHIKI Reasoning OS is based on three principles.

### Preserve structure, not every thought.

```text
Experience
→ Trace
→ Pattern
→ KATA
```

### Use only the computation that is necessary.

```text
Rest
→ KATA
→ Deep
```

### Evolve only from evidence.

```text
Execution
→ Trace
→ Validation
→ Evolution
```

In one sentence:

> **Experience → Trace → KATA → Breathing → Execution → Evolution.**

And in its v0.5 portable form:

> **Traceable KATA, applied with restraint, evolved by evidence, and exchanged through explicit contracts.**

---

## License

The specification does not prescribe a license.

Repository maintainers should define the applicable license in a `LICENSE` file before distribution.
