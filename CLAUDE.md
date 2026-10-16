# CLAUDE.md

Azure demo of the talk "AI as a new architectural domain" (Nordic APIs Summit
2026). See README.md for the story, build order and architecture, and
`docs/adr/` for every decision.

## Ground rules (from the talk; do not break them)

1. **All hand-offs go through the platform.** Building blocks never call each
   other's implementations directly; only via API Management or events.
2. **Standardise the envelope, not the payload.** Every event is a CloudEvent
   carrying business keys (`customerid`, `orderid`, …) and a `correlationid`.
3. **The envelope is a contract.** Changes are reviewed like an API change and
   recorded in an ADR.
4. **Contracts on everything, internal included.** OpenAPI for every HTTP
   interface, AsyncAPI for every topic and queue. Contract first; no contract,
   no deploy. Every contract is versioned and has an owner.
5. **One trace per journey.** OpenTelemetry context propagates across every
   hop.
6. **Everything is cataloged** in EventCatalog (`eventcatalog` repository).
7. **All contracts follow the adidas API guidelines** (ADR 0008), enforced by
   the Spectral ruleset in the `contracts` repository. Deviations only via
   ADR 0008, each with its reason.

## Cost rules (hard)

- Monthly ceiling **€10**. Consumption / pay-per-use tiers only.
- A service with a fixed monthly fee needs its own ADR and explicit user
  approval before it is deployed.
- Never remove or weaken the budget, the kill switch or the Log Analytics
  daily cap.
- Every demo resource group is tagged `costguard=delete` (except
  `rg-intplat-guardrails`). An untagged group escapes the kill switch.

## How we work

- Build in the order of README.md. Finish and verify one step before the next.
- Basics before features: correctness, contracts and tests over polish.
- API-led and composable: one repository, one resource group, one deploy
  identity and one pipeline per building block (ADR 0006). Repositories live
  in the GitHub organisation `azure-intelligence-domain`.
- Infrastructure as code only (Bicep). No manual portal changes.
- Record every non-trivial choice as an ADR (`docs/adr/0000-template.md`).
- Diagrams in `.md` files are Mermaid (renders on GitHub). Update them in the
  same change as the thing they describe, and check they render
  (`npx -y @mermaid-js/mermaid-cli@11 -i <file>.md -o /tmp/out.md`).
- Region Belgium Central; West Europe fallback per service, noted in README.
- No secrets in the repo. CI/CD uses GitHub OIDC.
- Python 3.12+ (via `uv`). Keep code readable enough to show on a slide.
