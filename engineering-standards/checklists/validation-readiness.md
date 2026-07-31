# Validation Readiness Checklist

Complete this checklist before you propose `infra.ado`, or a focused subset of roles, for the Red Hat Validated Content program. Validation reviews the collection as a product: code, documentation, tests, CI, security, and customer experience.

## Content Tiers

| Tier | Meaning |
|------|---------|
| **Published** | Importable and available. Quality and support belong to the publisher. |
| **Validated** | Reviewed by Red Hat as a recommended automation pattern. This tier is not the same support bar as Certified. |
| **Certified** | Partner or integration certification with subscription support expectations. |

ADO day-to-day work targets high-quality published content under `infra.*`. Validated Content is an optional uplift.

## Evidence Pack

### Technical Quality

- [ ] `ansible-lint` production profile passes without role-level ignores for submitted content.
- [ ] `ansible-test` sanity, or an equivalent tox-ansible path, is documented and green.
- [ ] Galaxy metadata in `galaxy.yml` is complete and accurate.
- [ ] Semantic Versioning is followed. Invalid tags are not used for release.
- [ ] Fully qualified collection names are used everywhere. Variables use role prefixes.

### CI/CD and Maintainability

- [ ] Automated CI runs on every pull request for lint and integration tests.
- [ ] Every public role or plugin is exercised at least once in CI.
- [ ] Branch protection and required checks are documented.
- [ ] The release path from tag to artifact to Automation Hub or Galaxy is documented.

### Documentation

- [ ] Collection README covers purpose, install, requirements, and examples.
- [ ] Every role covers requirements, variables, examples, limitations, and platforms.
- [ ] Changelog or release notes are available for consumers.
- [ ] Support and ownership contacts are populated in `MAINTAINERS`.

### Design

- [ ] Workflows are idempotent.
- [ ] Collection scope is clear. Unrelated domains are partitioned or justified.
- [ ] Defaults are safe. No hardcoded secrets are present.
- [ ] Failures are clear. Privilege escalation is intentional and documented.

### Security

- [ ] No secrets appear in Git history for submitted paths.
- [ ] The dependency and supply-chain story for EE images is documented.
- [ ] `scripts/security_checks.py` and the data-exposure scan are clean.

### Functional Proof

- [ ] Molecule or equivalent tests demonstrate intended outcomes.
- [ ] Supported platforms are listed and tested.
- [ ] The execution environment used for runtime dependencies matches what customers receive.

## ADO-Specific Notes

**Current standard:** The pull request gate enforces lint, Molecule, and changelog checks. README format and security scans are informational.

**Recommended standard before validation:** Make README and security checks required. Remove SPDX and `galaxy_info` drift. Adopt `argument_specs.yml` on all submitted roles. Consolidate duplicate CI workflows. Run galaxy-importer. Ensure Molecule README instructions match the `extensions/molecule/` layout.

See [Collection and Role Maturity Model](maturity-model.md) (Platinum) and [Gap Analysis](../appendices/gap-analysis.md).
