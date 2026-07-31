# Collection and Role Maturity Model

Use this scorecard when you plan role work or when you assess readiness for a customer deliverable or Validated Content submission.

## Levels

| Level | Name | Intent |
|-------|------|--------|
| **Bronze** | Functional | Works for a known use case; basic documentation |
| **Silver** | Tested | CI-covered Molecule scenario; lint clean |
| **Gold** | Release-ready | Changelog, examples, EE path understood, documentation complete |
| **Platinum** | Validation-ready | Meets Red Hat Validated Content expectations |

## Role Scorecard

| Criterion | Bronze | Silver | Gold | Platinum |
|-----------|:------:|:------:|:----:|:--------:|
| `tasks/`, `meta/main.yml`, and `README.md` present | Yes | Yes | Yes | Yes |
| `defaults/` with role-prefixed variables | Yes | Yes | Yes | Yes |
| README matches `docs/templates/role_readme_format_template.md` | | Yes | Yes | Yes |
| `verify_readme.py` passes | | Yes | Yes | Yes |
| Scenario under `extensions/molecule/` | | Yes | Yes | Yes |
| Scenario exercises a happy path and at least one negative or cleanup path | | | Yes | Yes |
| `meta/argument_specs.yml` for public inputs | | | Yes | Yes |
| Example playbook in the README matches actual variables | | | Yes | Yes |
| Changelog fragments for consumer-facing changes | | | Yes | Yes |
| Security scripts clean for the role | | | Yes | Yes |
| Idempotent on re-run (Molecule verify) | | | Yes | Yes |
| Supported platforms and prerequisites documented | | | Yes | Yes |
| Production `ansible-lint` profile clean without role excludes | | | | Yes |
| CI evidence and maintainability suitable for Partner Engineering review | | | | Yes |
| Customer-facing release notes and support matrix entry | | | | Yes |

## Collection Scorecard (`infra.ado`)

| Criterion | Bronze | Silver | Gold | Platinum |
|-----------|:------:|:------:|:----:|:--------:|
| Builds with `ansible-galaxy collection build` | Yes | Yes | Yes | Yes |
| Pull request gate: lint, Molecule, and changelog | | Yes | Yes | Yes |
| Semantic Versioning and antsibull-changelog | | Yes | Yes | Yes |
| GitHub Release and Galaxy publish path documented | | | Yes | Yes |
| EE build story (`aap_build_ee` or sibling EE repository) | | | Yes | Yes |
| README and security checks required, not informational | | | | Yes |
| Consistent role metadata (`company`, `license`, SPDX) | | | | Yes |
| Argument specifications on all public roles | | | | Yes |
| Galaxy importer or Automation Hub import validated | | | | Yes |

## How ADO Uses This Model

- **Default merge bar today:** approximately Silver for touched roles (lint and Molecule coverage through the pull request gate).
- **Customer deliverable bar:** Gold.
- **Validated Content submission bar:** Platinum.

Track gaps in [Gap Analysis](../appendices/gap-analysis.md).
