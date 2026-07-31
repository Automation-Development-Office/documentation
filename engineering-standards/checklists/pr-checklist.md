# Pull Request Checklist

Complete this checklist before you request review in the [ado](https://github.com/Automation-Development-Office/ado) collection. It aligns with `.github/pull_request_template.md` and the pull request gate in `.github/workflows/main.yml`.

## Scope

- [ ] You identified the change type: role, Molecule, CI, scripts, documentation, or bug fix.
- [ ] You listed the collection impact: roles and scenarios that you touched.
- [ ] For a large design change, a new role, or a breaking change, you discussed the work with maintainers before you opened the pull request.

## Local Checks

Run the following commands as applicable from the `ado` repository:

```bash
ansible-lint

python scripts/verify_readme.py roles/<role>/README.md

python3 scripts/security_checks.py roles/<role_name>

python3 scripts/validate_changelog.py --ref main

cd extensions
molecule test -s <scenario_name>
```

- [ ] `ansible-lint` is clean for the paths that you changed.
- [ ] The README format check passed for role changes.
- [ ] You reviewed security script findings.
- [ ] Relevant Molecule scenarios pass locally, or you documented why only CI will run them.
- [ ] `pre-commit run --all-files` is clean, or equivalent hooks passed.

## Changelog

- [ ] You added a fragment under `changelogs/fragments/`, or you applied the `skip-changelog` label for an exempt change.
- [ ] You did not hand-edit `CHANGELOG.rst` or `changelogs/changelog.yaml`, except in a dedicated release pull request.

## Quality

- [ ] The change includes no secrets, credentials, vault data, or environment-specific customer values.
- [ ] Variables use the `<role_name>_` prefix.
- [ ] Modules use fully qualified collection names.
- [ ] Breaking changes are documented in the fragment and in the pull request description.
- [ ] New role README files follow `docs/templates/role_readme_format_template.md`.
- [ ] Molecule scenarios live under `extensions/molecule/`, not only under `roles/<role>/molecule/`.

## Pull Request Gate

| Check | Required |
|-------|----------|
| Ansible Lint (`main.yml`) | Yes |
| Discover Molecule Scenarios (at least one) | Yes |
| Molecule matrix | Yes |
| Changelog (unless `skip-changelog`) | Yes |
| README format | Informational today |
| Security check | Informational today |

## After Merge

Maintainers should confirm whether a release tag is required and follow the Developers Guide when it is.
