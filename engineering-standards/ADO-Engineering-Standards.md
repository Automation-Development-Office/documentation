<p align="center">
  <img src="assets/ado-logo.png" alt="Ansible Automation Development Office" width="180" />
</p>

# ADO Engineering Standards

**Developing Enterprise Ansible Collections**

| Field | Value |
|-------|--------|
| Organization | Automation Development Office (ADO) |
| Collection | `infra.ado` |
| Handbook version | 1.1.3 |
| Style basis | [Red Hat Technical Writing Style Guide](https://stylepedia.net/) |
| Audience | ADO engineers, contributors, and release engineers |
| Handbook repository | [Automation-Development-Office/documentation](https://github.com/Automation-Development-Office/documentation) |
| Collection repository | [Automation-Development-Office/ado](https://github.com/Automation-Development-Office/ado) |
| Related procedure guide | [Developers Guide](https://github.com/Automation-Development-Office/ado/blob/main/.github/Developers%20_Guide.md) |

This handbook describes how ADO develops and maintains the `infra.ado` Ansible collection. Use it with the Developers Guide in the collection repository: this handbook sets policy; the Developers Guide documents workflow mechanics.

---

# Part I. Foundations

## Purpose of This Handbook

This handbook is the authoritative reference for ADO engineering practices for `infra.ado`. It is based on practices already present in the collection repository and states requirements where the project previously relied on convention alone.

This handbook is not a guide for submitting content to the Red Hat Validated Content program. Validation readiness is covered in a later chapter. After you read Parts I and II, you can clone the collection repository and contribute changes that meet ADO standards.

## About the Automation Development Office

The Automation Development Office develops reusable automation for Ansible Automation Platform environments. ADO provides tested, documented collections and execution environments that support consistent automation of enterprise infrastructure, including Ansible Automation Platform, OpenShift, Red Hat Enterprise Linux, Satellite, identity services, and related tooling.

The primary deliverable of the collection repository is the Ansible collection `infra.ado`.

## Requirement Words

This handbook uses the following words in the sense defined by the Red Hat Technical Writing Style Guide:

| Word | Meaning |
|------|---------|
| **must** | A requirement. You are required to do this. |
| **should** | A strong recommendation. Follow it unless you document a justified exception. |
| **can** / **might** | An optional or conditional action. |

Labels in this handbook:

- **Current standard** — Behavior that the collection repository already implements or enforces.
- **Recommended standard** — An ADO roadmap item that improves consistency or validation readiness but is not fully enforced yet.

## Guiding Principles

### Automate Repeatable Work

If you can automate a task safely and repeatedly, you should add that automation to the collection instead of relying on undocumented knowledge.

### Keep Each Role Focused

Each role must have a clear scope, for example `ocp_namespace`, `rhel_cron`, or `aap_build_ee`. If a role mixes unrelated concerns, you must split it.

### Design for Reuse

Write roles so that another team can consume them from Automation Hub or from a collection tarball without reading the implementation.

### Require Idempotence

When you run a role again with the same inputs, the end state should remain the same. Molecule verify stages should assert this where practical.

### Test Before You Merge

If a change alters automation behavior, it must pass the pull request gate: lint, Molecule, and changelog rules. See the testing and CI/CD chapters.

### Treat Documentation as Deliverable Content

A feature is complete only when the role README describes how to use it, and when a changelog fragment is present if project rules require one.

### Optimize for the Consumer

Prefer clear install paths, variable names, examples, and upgrade notes. Prefer predictable patterns over clever ones.

### Never Commit Secrets

You must not commit passwords, API keys, vault contents, customer data, or environment-specific secrets in issues, pull requests, or the repository. This rule is also stated in the ADO Code of Conduct addendum.

## Glossary

| Term | Definition |
|------|------------|
| Collection | Installable Ansible content unit defined by `galaxy.yml` (`infra.ado`) |
| Role | Reusable automation unit under `roles/` |
| Plugin | Module, filter, lookup, or similar content under `plugins/` (not used in this collection today) |
| Execution environment (EE) | Container image that Ansible Automation Platform uses to run jobs |
| Molecule scenario | Integration test under `extensions/molecule/<name>/` |
| Fragment | antsibull-changelog YAML file under `changelogs/fragments/` |
| Pull request gate | Jobs in `main.yml` that must succeed before merge |
| Validated Content | Red Hat program that reviews collections as recommended automation patterns |
| Published content | Content that is available on Automation Hub or Galaxy without implying validation |
| Certified content | Content at a higher support and certification tier than Validated Content |

---

# Part II. Engineering Standards

## Collection Architecture

### Collection Identity

| Field | Value |
|-------|--------|
| Namespace | `infra` |
| Name | `ado` |
| Version source of truth | `galaxy.yml` (`version`). CI can override only `version` from a Git tag at build time. |
| License | GPL-3.0-or-later |
| Ansible requirement | `requires_ansible: ">=2.16.0"` in `meta/runtime.yml` |
| Runtime dependencies | `dependencies: {}` in `galaxy.yml` |

**Current standard:** Runtime collections come from the execution environment or container so that offline tarball installs do not resolve Galaxy dependencies at install time.

### Capability Areas

Role name prefixes map to domains as follows:

| Prefix | Domain |
|--------|--------|
| `aap_`, `install_aap`, `bootstrap_` | Ansible Automation Platform, EE builds, bootstrap pipelines |
| `ocp_` | OpenShift platform and operators |
| `idm_`, `rhbk_` | Identity (Identity Management and Red Hat build of Keycloak) |
| `rhel_`, `satellite_` | Red Hat Enterprise Linux and Satellite |
| `grafana_`, `elastic`, `kafka_`, `gitlab_`, `jira` | Observability and DevOps tooling |
| `install_*` | Multi-step application installs |
| `vm_` | Image management |

### Choosing a Role or a Collection

For the decision procedure, see [Collection Versus Role Decisions](templates/collection-decision.md).

**Current standard:** Prefer a new role in `infra.ado` for platform-adjacent automation.

**Recommended standard:** Split into another collection only when release cadence, EE contents, or Validated Content scope clearly diverge.

## Repository Layout

The collection repository uses the following top-level layout:

```text
ado/
├── galaxy.yml
├── README.md
├── CHANGELOG.rst
├── meta/runtime.yml
├── roles/
├── extensions/molecule/
├── extensions/eda/
├── changelogs/fragments/
├── collections/requirements.yml
├── scripts/
├── docs/
│   └── templates/role_readme_format_template.md
├── tests/
└── .github/workflows/
```

Engineering standards for ADO live in this documentation repository under `engineering-standards/`.

You must place new integration tests under `extensions/molecule/` in the collection repository. Do not rely only on `roles/<role>/molecule/`.

### AI-Assisted Contributions

`AGENTS.md` in the collection repository requires contributors and agents to follow the ansible-creator [agents.md](https://raw.githubusercontent.com/ansible/ansible-creator/refs/heads/main/docs/agents.md) practices. Human reviewers remain accountable for correctness, secrets handling, and changelog accuracy.

## Role Development

### Required Role Contents

Every role must contain the following files:

| Path | Requirement |
|------|-------------|
| `README.md` | Present. The README should match `docs/templates/role_readme_format_template.md`. |
| `tasks/` | At least `main.yml` |
| `meta/main.yml` | Present, with ADO `galaxy_info` defaults |

Every role should contain the following files:

| Path | Notes |
|------|-------|
| `defaults/main.yml` | Role-prefixed variables |
| `handlers/main.yml` | Can be empty |
| `vars/main.yml` | Role constants |
| `meta/argument_specs.yml` | Recommended standard for public inputs (currently used in 5 of 90 roles) |

For a copyable skeleton, see [New Role Skeleton](templates/new-role.md).

### Role Metadata

Use the following values in `meta/main.yml`:

- `company: Automation Development Office`
- `license: GPL-3.0-or-later`
- `min_ansible_version: "2.16.0"`

YAML files should begin with the following comment:

```yaml
# SPDX-License-Identifier: GPL-3.0-or-later
```

You must not use the invalid SPDX identifier `GPL-3.0-or-later-0`. That incorrect form exists in parts of the tree today; see the gap analysis.

### Variable Naming

- Public variables must use the `<role_name>_` prefix. `ansible-lint` enforces `var-naming[no-role-prefix]` unless you add a justified `noqa`.
- README variable tables must match the names that `tasks/` and `defaults/` actually use.
- **Recommended standard:** Declare inputs in `meta/argument_specs.yml`. Use `roles/aap_build_ee` as the reference implementation.

### Task Style

- Modules must use fully qualified collection names (FQCN), for example `ansible.builtin.copy` or `kubernetes.core.k8s`.
- Task `name` values should be descriptive phrases in title case.
- Prefer modules over `shell` or `command` unless no suitable module exists. If you use `shell` or `command`, document why and keep the task idempotent.

### Vendored Content

You can exclude content that is vendored from upstream, for example `aap_ocp_install_upstream` from `infra.aap_utilities`, from local lint when you include an explicit comment that cites the upstream version. ADO wrapper roles should remain thin and documented.

## Documentation Standards

### Role README Files

Role README files should follow this section order from `docs/templates/role_readme_format_template.md`:

1. Title (`# Role: infra.ado.<name>`)
2. Role Author
3. Role Requirements
4. Role Variables
5. Role Usage
6. Role Molecule Testing
7. Role Structure

Validate a README with the following command:

```bash
python scripts/verify_readme.py roles/<role>/README.md
```

**Current standard:** CI runs this check as informational (`continue-on-error`).

**Recommended standard:** Require the check on pull requests that touch role README files or add roles.

### Molecule Instructions in README Files

The Molecule section must document scenarios under `extensions/molecule/`. Example:

```bash
cd extensions
molecule test -s integration_<role>
```

You must not instruct readers to run `cd roles/<role> && molecule test` unless that path is intentionally maintained and discovered by CI. CI discovers scenarios only under `extensions/molecule/`.

### Collection README

The root `README.md` in the collection repository must remain the entry point for collection purpose, role index, requirements, and high-level testing notes.

## Testing Standards

### Molecule

- Canonical scenarios live in `extensions/molecule/<scenario>/`.
- Shared helpers live in `extensions/molecule/utils/`.
- `extensions/molecule/pr_exclude.txt` lists scenarios that pull request CI skips. You can still run those scenarios with `workflow_dispatch`. Heavy OpenShift and `install_*` scenarios are typically excluded from pull requests because of cost or secrets.
- Scenarios should include converge and verify stages, and destroy when needed.

### ansible-lint

Configuration lives in `.ansible-lint`.

- `mock_roles` lists all `infra.ado.*` roles.
- `mock_modules` documents the third-party FQCN surface.
- Broad `exclude_paths` settings focus lint on tasks, handlers, and templates more than on defaults and vars.

You must fix lint failures before merge. The pull request gate requires the lint job to succeed. For internal `continue-on-error` details, see the Developers Guide.

### ansible-test and tox

`tests/integration` and `tests/unit` provide ansible-test scaffolding. `tox-ansible.ini` skips obsolete Python and ansible-core lines to match the 2.16 floor.

**Recommended standard:** Add real integration targets when you add plugins. Remove stub `roles/*/tests/test.yml` files that imply coverage they do not provide, or replace them with real tests.

### Pre-commit Hooks

Before you push, you should run the following command:

```bash
pre-commit run --all-files
```

Hooks include merge-conflict and symlink checks, trailing whitespace fixes, Prettier, isort, Black, flake8, and a block on direct commits to `main`.

## CI/CD Standards

### Workflows

| Workflow | Purpose |
|----------|---------|
| `main.yml` | Primary pull request gate, build, and tag pre-release |
| `tests.yml` | Secondary checks in the ansible-content-actions style |
| `security-check.yml` | Security scripts (informational) |
| `release.yml` | Official GitHub Release, changelog, and tarball |
| `publish-galaxy.yml` | Manual Galaxy publish |
| `open-changelog-pr.yml` | Changelog pull request recovery |

### Pull Request Gate

The following checks are required for merge on pull requests (`main.yml`):

1. Ansible Lint
2. Discover Molecule Scenarios (must find at least one scenario)
3. Molecule matrix
4. Changelog (unless the `skip-changelog` label is applied)

The README format check and the security check are not required today.

**Recommended standard:** Make the README and security checks required after the false-positive rate is acceptable. Consolidate overlapping jobs between `main.yml` and `tests.yml`.

### Branch Policy

You must not commit directly to `main`. The pre-commit `no-commit-to-branch` hook blocks those commits. Submit changes through pull requests.

---

# Part III. Release Engineering

## Changelog and Versioning

### Changelog Fragments

- For consumer-visible changes, you must add a YAML fragment under `changelogs/fragments/`.
- In ordinary pull requests, you must not edit `CHANGELOG.rst` or `changelogs/changelog.yaml`.
- Release pull requests can update those compiled files when `antsibull-changelog` produces them.

Trivial non-user-facing edits can be exempt. Follow the Developers Guide and the changelog rule in the collection repository.

### Semantic Versions

- Tags should use Semantic Versioning, for example `1.2.0` or `v1.2.0`.
- `scripts/validate_release_version.py` rejects malformed versions, for example an extra numeric segment before `-rc`.
- The artifact name is `infra-ado-<version>.tar.gz`.

### Release Flow

The current release flow is as follows:

1. Merge changes to `main` through a pull request.
2. Push a version tag.
3. CI creates or updates a GitHub pre-release with a changelog preview.
4. Publish an official GitHub Release.
5. `release.yml` runs `antsibull-changelog release`, attaches the collection tarball, and opens a changelog pull request to `main`.
6. Merge the changelog pull request.
7. Run **Publish to Ansible Galaxy** with `workflow_dispatch`. This step is manual and uses the `release` GitHub Environment and `ANSIBLE_GALAXY_API_KEY`.

## Execution Environments

### Building Execution Environments in the Collection

The `infra.ado.aap_build_ee` role does the following:

- Renders `execution-environment.yml` and requirements files from defaults and templates.
- Runs `ansible-builder` against a base image that you supply.
- Exposes typed inputs through `meta/argument_specs.yml`.

Treat this role as the reference implementation for argument specifications.

Playbook runtime collection dependencies should be satisfied by the execution environment, consistent with empty `dependencies` in `galaxy.yml`.

### Related Roles

- `aap_configuration` dispatches to `infra.aap_configuration`.
- `aap_ocp_install` and the upstream vendored role install Ansible Automation Platform on OpenShift.
- `install_aap` provides an alternate install path.

Development containers (`.devcontainer`, `devfile.yaml`) use community Ansible development tooling images. Those images are not substitutes for customer execution environments.

---

# Part IV. Operations

## Security

You must do the following:

- Run `scripts/security_checks.py` on touched roles before review. When relevant, also run `scripts/security_data_exposure_scan.py`.
- Avoid `shell` with untrusted input. Avoid copying credentials into templates that you commit.
- Treat CI logs as potentially sensitive. Do not echo secrets.

**Current standard:** The security workflow is informational.

**Recommended standard:** Block merge on high findings for role changes.

## Code Review

Reviewers should verify the following items:

1. The change matches the pull request type checklist.
2. Variable prefixes and README content are accurate.
3. Molecule scenarios are updated when behavior changes.
4. A changelog fragment is present, or the skip label is justified.
5. No secrets are included.
6. Breaking changes are called out.
7. For new roles, the team discussed the design, and `verify_readme.py` passed.

Feature tasks use acceptance criteria in `.github/ISSUE_TEMPLATE/feature_task.yml`.

## Validation Readiness

The Red Hat Validated Content program evaluates a collection as a product: lint and sanity results, CI evidence, documentation completeness, design quality, security, and functional proof.

Use [Validation Readiness Checklist](checklists/validation-readiness.md) and target Platinum on the [Collection and Role Maturity Model](checklists/maturity-model.md).

| Tier | Question answered |
|------|-------------------|
| Published | Is the content available? |
| Validated | Does Red Hat treat the content as a recommended pattern? |
| Certified | Is the content a supported certified integration? |

## Customer Deliverables

A customer-facing delivery should include the following items:

1. Collection tarball (`infra-ado-<version>.tar.gz`)
2. Matching execution environment image, or EE build inputs
3. Collection and role documentation
4. Example playbooks
5. Release notes or a changelog excerpt
6. Support and compatibility matrix (Ansible, platforms, Ansible Automation Platform version)

## Reference Architecture

The following flow shows how ADO artifacts reach managed infrastructure:

```text
Developer
    |
    v
GitHub (ado)
    |
    v
GitHub Actions
    |--------------|
    v              v
Collection      EE image
tarball         (registry)
    |              |
    +------+-------+
           v
 Automation Hub or Galaxy
           v
 Ansible Automation Platform controller
           v
 Execution nodes (EE)
           v
 Managed infrastructure
```

When bootstrap tools or UI surfaces outside the collection repository are part of a customer delivery, link them from the customer runbook.

## Maturity Model

See [Collection and Role Maturity Model](checklists/maturity-model.md).

| Level | Expectation |
|-------|-------------|
| Bronze | Locally functional only. Insufficient for merging new roles. |
| Silver | Default pull request merge bar. |
| Gold | Customer deliverable bar. |
| Platinum | Validated Content bar. |

---

# Appendixes

## Quick Command Card

```bash
ansible-lint
python scripts/verify_readme.py roles/<role>/README.md
python3 scripts/security_checks.py roles/<role>
python3 scripts/validate_changelog.py --ref main
pre-commit run --all-files
cd extensions && molecule test -s <scenario>
```

## Related Documents

| Document | Location |
|----------|----------|
| Developers Guide | [ado Developers Guide](https://github.com/Automation-Development-Office/ado/blob/main/.github/Developers%20_Guide.md) |
| Pull request template | [ado PR template](https://github.com/Automation-Development-Office/ado/blob/main/.github/pull_request_template.md) |
| Code of Conduct | [ado CODE_OF_CONDUCT.md](https://github.com/Automation-Development-Office/ado/blob/main/CODE_OF_CONDUCT.md) |
| Role README template | [ado role README template](https://github.com/Automation-Development-Office/ado/blob/main/docs/templates/role_readme_format_template.md) |
| Changelog rule | [ado changelog rule](https://github.com/Automation-Development-Office/ado/blob/main/.cursor/rules/changelog-fragments.mdc) |
| Gap analysis | [appendices/gap-analysis.md](appendices/gap-analysis.md) |

## Document Control

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-07-31 | Initial handbook based on `infra.ado` repository practices |
| 1.1.0 | 2026-07-31 | Revised for Red Hat Technical Writing Style Guide |
| 1.1.1 | 2026-07-31 | Moved handbook into Automation-Development-Office/documentation |
| 1.1.2 | 2026-07-31 | Added Ansible Automation Development Office logo to package branding |
| 1.1.3 | 2026-07-31 | Fixed root README links to files under engineering-standards/ |

When you change engineering policy, update this handbook through a pull request in this documentation repository. Pair tooling changes in `ado` when required. Add a changelog fragment in `ado` when the process change is consumer-facing for collection users.
