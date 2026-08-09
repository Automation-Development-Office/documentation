# ADO release and deployment status

_Generated automatically for [`Automation-Development-Office`](https://github.com/Automation-Development-Office). Last refresh: `2026-08-09T06:35:03Z`._

This page tracks **released** versions (GitHub Releases) and **deployed / published channel** versions from [`deployments.yml`](deployments.yml), which the nightly workflow auto-fills from GHCR and configured sources.

## Product board

| Product | Latest stable | Published | Artifact | Latest prerelease | Deployed (prod) | Deployed (stage) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [infra.ado collection](https://github.com/Automation-Development-Office/ado) | [1.1.0](https://github.com/Automation-Development-Office/ado/releases/tag/1.1.0) | 2026-08-07 | infra.ado:1.1.0 | — | `1.1.0` (2026-08-07) · _github_release:stable_ | — | Published to Ansible Galaxy from GitHub Releases. |
| [ADO Execution Environment](https://github.com/Automation-Development-Office/ado-ee) | [1.1.0](https://github.com/Automation-Development-Office/ado-ee/releases/tag/1.1.0) | 2026-08-07 | ghcr.io/automation-development-office/ado-ee:1.1.0 | — | `1.1.0` (2026-08-09) · _ghcr:latest_ | — | Container image; often tracks the latest infra.ado collection. |
| [ADO Preflight UI](https://github.com/Automation-Development-Office/ado-preflight-ui) | [1.1.0](https://github.com/Automation-Development-Office/ado-preflight-ui/releases/tag/1.1.0) | 2026-07-23 | ghcr.io/automation-development-office/ado-preflight-ui:1.1.0 | [1.1.10-CCP](https://github.com/Automation-Development-Office/ado-preflight-ui/releases/tag/1.1.10-CCP) | `1.1.10-CCP` (2026-08-09) · _ghcr:latest_ | `1.1.10-CCP` (2026-07-24) · _ghcr_prerelease_ | Stable releases and CCP prereleases are listed separately. |

## How this is maintained

| Piece | Role |
| --- | --- |
| [`products.yml`](products.yml) | Repos on the board + `deploy_channels` discovery rules |
| [`deployments.yml`](deployments.yml) | Auto-filled channel pins (override with `manual: true`) |
| [`versions.json`](versions.json) | Machine-readable snapshot |
| [`../scripts/generate_release_status.py`](../scripts/generate_release_status.py) | Discovers pins and regenerates this page |
| `.github/workflows/update-release-status.yml` | Nightly + on-demand refresh |

### What “deployed” means today

| Product | `prod` source | `stage` source |
| --- | --- | --- |
| infra.ado | Newest stable GitHub Release (Galaxy not publicly queryable yet) | Newest GitHub prerelease |
| ado-ee | GHCR `:latest` resolved to a version tag by digest | Newest prerelease tag present in GHCR |
| ado-preflight-ui | GHCR `:latest` resolved to a version tag by digest | Newest prerelease tag present in GHCR |

This is a **published artifact channel**, not a live OpenShift/AAP inventory. When cluster or Automation Hub APIs are available, add a channel type and point `deploy_channels` at them.

### Refresh locally

```bash
pip install pyyaml
export GITHUB_TOKEN=$(gh auth token)  # needed for GHCR pull on private packages
python3 scripts/generate_release_status.py
```

### Hold a pin manually

```yaml
ado-ee:
  prod:
    manual: true
    version: "1.0.1"
    updated_at: "2026-08-01T12:00:00Z"
    notes: Held back for soak testing
```

## Source repositories

- [infra.ado collection](https://github.com/Automation-Development-Office/ado) — [releases](https://github.com/Automation-Development-Office/ado/releases)
- [ADO Execution Environment](https://github.com/Automation-Development-Office/ado-ee) — [releases](https://github.com/Automation-Development-Office/ado-ee/releases)
- [ADO Preflight UI](https://github.com/Automation-Development-Office/ado-preflight-ui) — [releases](https://github.com/Automation-Development-Office/ado-preflight-ui/releases)
