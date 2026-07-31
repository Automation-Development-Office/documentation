# Architecture Diagrams

Render these Mermaid diagrams on GitHub or in any Mermaid-capable viewer. The same flows appear in the handbook as plain-text diagrams.

## Delivery Pipeline

```mermaid
flowchart TD
  dev[Developer] --> gh[GitHub ado]
  gh --> gha[GitHub Actions]
  gha --> col[Collection tarball]
  gha --> ee[EE image]
  col --> hub[Automation Hub or Galaxy]
  ee --> hub
  hub --> aap[Ansible Automation Platform controller]
  aap --> nodes[Execution nodes]
  nodes --> infra[Managed infrastructure]
```

## Pull Request Gate

```mermaid
flowchart LR
  pr[Pull request] --> lint[ansible-lint]
  pr --> mol[Molecule matrix]
  pr --> cl[Changelog]
  lint --> gate[Pull request gate]
  mol --> gate
  cl --> gate
  gate --> merge[Merge to main]
```

## Role Versus Collection Decision

See [Collection Versus Role Decisions](../templates/collection-decision.md).
