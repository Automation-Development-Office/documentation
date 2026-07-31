# Collection Versus Role Decisions

Use the following decision flow when you need new automation capability:

```text
Need new automation capability
            |
            v
    Different product or domain
    than existing collection scope?
            |
     Yes ---+--- No
      |              |
      v              v
 Discuss a new     Reusable across
 collection with   playbooks or teams?
 maintainers             |
                  Yes ---+--- No
                   |              |
                   v              v
            New role in     Extend the existing
            infra.ado       role in tasks/ and
                            defaults/ if it is
                            the same concern
```

## Current Collection Boundaries

`infra.ado` intentionally spans multiple domains in one collection:

- Ansible Automation Platform and bootstrap
- OpenShift (`ocp_*`)
- Identity (Identity Management and Red Hat build of Keycloak)
- Red Hat Enterprise Linux and Satellite
- Observability and DevOps tooling

**Current standard:** Ship related platform bootstrap roles in `infra.ado` rather than creating many small collections.

**Recommended standard:** If a domain needs a separate release cadence, execution environment, or Validated Content submission, split it into a focused collection, for example `infra.ado_ocp`, with a documented migration plan. Do not split casually.
