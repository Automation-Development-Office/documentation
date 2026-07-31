# New Role Skeleton

Copy this layout into `roles/<role_name>/` in the [ado](https://github.com/Automation-Development-Office/ado) collection. Replace `<role_name>` throughout.

## Required Layout

```text
roles/<role_name>/
├── README.md                 # from docs/templates/role_readme_format_template.md
├── defaults/main.yml         # <role_name>_* variables only
├── handlers/main.yml         # can be empty with a comment
├── meta/main.yml             # company: Automation Development Office; license: GPL-3.0-or-later; min_ansible_version: "2.16.0"
├── meta/argument_specs.yml   # recommended for public inputs
├── tasks/main.yml
└── vars/main.yml             # optional constants
```

## Molecule Scenario Layout

Place scenarios at collection level:

```text
extensions/molecule/integration_<role_name>/
├── molecule.yml
├── converge.yml
├── verify.yml
├── destroy.yml
├── README.md
└── TEST.md
```

Prefer shared playbooks under `extensions/molecule/utils/playbooks/` when patterns repeat.

## Minimum `meta/main.yml`

```yaml
---
# SPDX-License-Identifier: GPL-3.0-or-later
galaxy_info:
  author: Automation Development Office
  description: <one line>
  company: Automation Development Office
  license: GPL-3.0-or-later
  min_ansible_version: "2.16.0"
  platforms: []
  galaxy_tags: []
dependencies: []
```

## `defaults/main.yml` Pattern

```yaml
---
# SPDX-License-Identifier: GPL-3.0-or-later
# defaults file for <role_name>

<role_name>_state: present
```

## Changelog

Add `changelogs/fragments/<short-name>.yml` when project rules require a fragment for the change. Follow the changelog rule and the Developers Guide in the `ado` repository.
