# Cross-tenant data movement: governance checklist

Fabric makes it very easy to reach across workspace and tenant boundaries — OneLake shortcuts, cross-workspace notebook reads, `az login` into a second identity in the same terminal session. Easy access is not the same as authorized access. Treat any step that moves or references data across a tenant boundary as a decision for the data owner, not a technical convenience to reach for by default.

## What actually gets logged

- **Every sign-in** (including `az login --use-device-code` into a second tenant) is recorded in that tenant's Entra ID sign-in logs.
- **OneLake shortcuts and cross-workspace reads** go through normal Entra ID authentication/authorization and are recorded in Fabric's own audit log for the source workspace, whether or not the read "feels" like a harmless, read-only operation.
- None of this is hidden or best-effort — assume a security/compliance team can and does see it.

## Before creating a shortcut or copy that crosses a tenant boundary

Ask, and if in doubt, stop and ask the data owner or your organization's data-governance contact — do not decide this alone:

1. **Whose data is this, actually?** If it's a client/production system, "read-only" and "just a shortcut" don't change who's authorized to access it.
2. **Which tenant is the destination?** A personal Microsoft trial tenant (a `*.onmicrosoft.com` you created yourself for learning) is a different trust boundary than your employer's tenant, even if you're the one logged into both.
3. **Is the data actually anonymized/synthetic**, or does it just *look* like it might be (test-looking codes, placeholder-looking names)? Verify rather than assume — check a few real values, and if still unsure, treat it as sensitive.
4. **Is there a lower-risk way to achieve the same learning/testing goal?** Generating structurally-realistic synthetic data (matching real column names/types but with fabricated values — see [delta-tables-without-spark.md](delta-tables-without-spark.md)) is almost always sufficient for learning a pipeline's mechanics, without needing real data at all.

## If real (non-anonymized) data ends up somewhere it shouldn't

Don't try to reason your own way to "it's probably fine" — this is exactly the situation the governance/security contact exists for:

1. Remove the data from the inappropriate location immediately (delete the OneLake files/shortcut, drop the table).
2. Report it to your organization's data protection / security contact — let them assess whether it's a reportable incident and what else (other copies, backups, cached credentials) needs attention.
3. Only resume the original task once you have an approved, appropriately-scoped way to do it — usually either explicit authorization for the original location, or continuing with synthetic data instead.
