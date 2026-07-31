# Gap Analysis: Current Standards and Recommended Standards

This appendix summarizes an audit of the `ado` collection repository (`infra.ado` 1.0.3) that informed handbook version 1.1.1. Counts are approximate as of that authorship date.

## Strengths to Keep

| Area | Observation |
|------|-------------|
| Role coverage | 90 roles include README, tasks, and meta files |
| CI | Strong pull request gate: ansible-lint, Molecule discovery and matrix, changelog |
| Changelog | antsibull-changelog with clear fragment rules |
| Release | Tag to pre-release preview to official release to optional Galaxy publish |
| Documentation tooling | Canonical role README template and `verify_readme.py` |
| Execution environments | `aap_build_ee` with `argument_specs.yml` and ansible-builder templates |
| Developer experience | Developers Guide, pre-commit, devcontainer, and devfile |
| Code of Conduct | Ansible Code of Conduct plus ADO addendum for secrets, AI policy, and conventions |

## Gaps to Close

| Gap | Scale | Recommended standard |
|-----|-------|----------------------|
| Invalid SPDX `GPL-3.0-or-later-0` | About 206 files under `roles/` | All YAML files must use `GPL-3.0-or-later` |
| Copy-pasted defaults comments that mention `advanced-cluster-management` | About 24 roles | Defaults comments must name the actual role |
| README and task variable drift | Confirmed for example in `ocp_namespace` | Documented variables must match code. Prefer `argument_specs.yml`. |
| Misleading Molecule instructions in README files | Widespread | README files must point to `extensions/molecule/<scenario>` |
| Orphan in-role `molecule/` directories | 8 roles | Prefer collection-level scenarios only. Remove or synchronize orphans. |
| Stub `tests/test.yml` files | About 11 roles | Remove stubs or replace them with real ansible-test targets |
| Rare `argument_specs.yml` adoption | 5 of 90 roles | New and public roles should include argument specifications |
| `galaxy_info` company and license drift | About 11 or more roles | Normalize to ADO and `GPL-3.0-or-later` |
| `min_ansible_version` drift | 2 roles | Align to `>=2.16.0` / `"2.16.0"` |
| Incomplete `docs/roles.md` index | 89 roles missing | Generate the index or remove the stale file |
| Empty `MAINTAINERS` | 1 file | Populate ownership |
| Duplicate CI (`main.yml` and `tests.yml`) | 2 workflows | Consolidate when ready |
| Informational README and security gates | 2 or more jobs | Promote to required when noise is low |
| Sample plugin docs without a `plugins/` directory | Several RST files | Remove scaffolding or implement plugins |
| Generic bug report template | 1 file | Replace with an ADO-specific Ansible bug template |

## Priority Roadmap

1. **P0 — Consistency hygiene:** Fix SPDX identifiers, normalize `galaxy_info`, and correct Molecule README paths.
2. **P1 — Contract quality:** Add `argument_specs.yml` for high-traffic roles and fix known variable-name drift.
3. **P2 — Gate hardening:** Require README verification and security scripts on pull requests that touch roles.
4. **P3 — Platform:** Add galaxy-importer in CI, document an Automation Hub publish path, and consolidate workflows.
