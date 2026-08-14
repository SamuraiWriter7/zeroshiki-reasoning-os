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
