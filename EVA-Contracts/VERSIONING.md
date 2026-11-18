# EVA Contracts Versioning Policy

## 1. Versioning Standard

EVA Contracts uses Semantic Versioning.

Format: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes.
- MINOR: Backward-compatible additions.
- PATCH: Non-breaking corrections.

## 2. Independent Versioning

Each contract is versioned independently.

Examples:

- Node Registration: 1.0.0
- Node Capabilities: 1.1.0
- Node Telemetry: 1.0.2
- Event Envelope: 1.0.0

Updating one contract does not require updating all others.

## 3. Breaking Changes

The following changes require a MAJOR version:

- Removing existing fields.
- Renaming existing fields.
- Changing field types.
- Changing required fields.
- Changing the meaning of existing fields.
- Changing existing enum values incompatibly.

## 4. Compatible Changes

The following changes may use a MINOR version:

- Adding optional fields.
- Adding new event types.
- Adding new independent contracts.
- Extending supported capabilities.

Compatibility must be verified against existing consumers.

## 5. Patch Changes

PATCH versions are used for:

- Documentation corrections.
- Metadata corrections.
- Non-breaking schema corrections.

## 6. Compatibility

EVA Core and EVA Agent may use different contract versions.

Receiving components must support:

- Version identification.
- Compatibility checks.
- Receiving-side adapters.
- Graceful rejection of unsupported versions.

## 7. Published Contracts

Released contract versions are immutable.

Changes to a released contract require a new version.

## 8. Validation

Every contract change must pass:

- JSON syntax validation.
- JSON Schema validation.
- Example message validation.
- Compatibility checks.