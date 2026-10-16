# AI Intelligence Domain — demo

A demo of the talk **"AI as a new architectural domain"**
(Nordic APIs Summit 2026, Axel Vuylsteke — The Value Hub), built on Azure.

> Every system knows its part. None knows the story.
> Your integration platform already sees every hand-off.

The demo replays one business journey, **ACME's order 4711**, through an
integration platform (Salesforce → SAP → Warehouse → 3PL). Later, an
**Intelligence domain** subscribes to everything the platform sees and answers
questions no single system can answer, such as *"Where is ACME's order
4711?"*, with cited evidence.

## Scope

- **Demo / reference only.** Not production.
- **Azure**, region Belgium Central (France Central as fallback per service).
- **Consumption tiers only.** Hard ceiling of **€10/month**, enforced by a
  budget and a kill switch ([ADR 0003](docs/adr/0003-azure-consumption-with-cost-cap.md)).
- **API-led and composable** ([ADR 0004](docs/adr/0004-api-led-composable.md)).
- **Contracts on everything**, documented in EventCatalog
  ([ADR 0005](docs/adr/0005-contracts-everywhere-eventcatalog.md)), following
  the **adidas API guidelines** ([ADR 0008](docs/adr/0008-adidas-api-guidelines.md)).
- **Tap by default**: every event, gateway mutation, agent action, deployment and trace can
  reach the Intelligence domain; nobody can opt out ([ADR 0011](docs/adr/0011-tap-by-default.md)).
- **A separate gateway for AI agents**, with an Entra identity per agent and every call
  audited ([ADR 0012](docs/adr/0012-agent-gateway.md)).
- **One repository per ownership boundary** in the GitHub organisation
  [azure-intelligence-domain](https://github.com/azure-intelligence-domain)
  ([ADR 0006](docs/adr/0006-repository-per-ownership-boundary.md)).

## Phase 1 — Integration platform

*No solid platform? No intelligence!*

| Step | What | Status |
|---|---|---|
| 0 | Repo structure, rules, decision log | ✅ |
| 1 | Foundation: Azure subscription, budget + kill switch ([guardrails](https://github.com/azure-intelligence-domain/azure-landing-zone/tree/main/guardrails)), GitHub organisation, OIDC deploy identity ([bootstrap](https://github.com/azure-intelligence-domain/azure-landing-zone/tree/main/bootstrap)) | ✅ |
| 2 | Envelope contract: CloudEvents + `correlationid`, `customerid`, `orderid` ([contracts](https://github.com/azure-intelligence-domain/contracts)) | ✅ |
| 3 | Contract tooling: linting, breaking-change checks, [EventCatalog](https://azure-intelligence-domain.github.io/eventcatalog/) | ✅ |
| 4 | Platform core: API Management, Event Grid, Service Bus, App Insights ([integration-platform](https://github.com/azure-intelligence-domain/integration-platform), [ADR 0010](docs/adr/0010-platform-core.md)) | ✅ |
| 4b | Tap by default and the agent gateway ([ADR 0011](docs/adr/0011-tap-by-default.md), [ADR 0012](docs/adr/0012-agent-gateway.md)) | ✅ |
| 5a | Order domain design: business events (Event Storming), commands and queries, BPMN flows ([process-api-order](https://github.com/azure-intelligence-domain/process-api-order), [ADR 0013](docs/adr/0013-order-domain.md)) | ✅ |
| 5b | Order domain implementation: Order Process API, Salesforce System API, source system, order topic, tapped queries | ⏳ |
| 6 | SAP, WMS, 3PL System APIs and the Fulfilment Process API | ⏳ |
| 7 | Experience APIs | ⏳ |
| 8 | The v2.4 break: faulty `stock-to-3pl` mapping, dead letters arrive | ⏳ |

## Phase 2 — Intelligence domain

Tap, ingest, understand, remember, reason, expose (MCP). Planned after phase 1;
cost decisions per service.

## Architecture (phase 1)

[![Solution design](docs/architecture/solution-design.svg)](docs/architecture/)


| Layer | Building blocks | Azure service |
|---|---|---|
| Gateways | People and websites: `apim-intplat-demo`. AI agents: `apim-intplat-agents` (Entra token per agent) | API Management (Consumption), France Central |
| Tap | Every topic, gateway mutation, agent action, deployment and trace, kept for the Intelligence domain | Event Grid tap subscriptions + Log Analytics export → `sttapintplatdemo` (`rg-intplat-tap`, never deleted) |
| Experience | Customer Service, Partner (3PL), Webshop | API Management (+ thin Functions) |
| Process | Order, Fulfilment | Logic Apps (Consumption) |
| System | Salesforce, SAP, WMS, 3PL | Functions (Flex Consumption, Python) |
| Events | Business events between domains | Event Grid → Service Bus Basic queue per subscriber (with DLQ) |
| Backends | Simulated Salesforce, SAP, WMS and 3PL, each with its own database (ADR 0007) | Cosmos DB serverless, one account per system + Functions (3PL partner API) |
| Observability | One trace per journey | Application Insights + Log Analytics |
| Secrets & identity | No secrets in code | Managed identities; Key Vault with the first real secret ([ADR 0010](docs/adr/0010-platform-core.md)) |
| Catalog | Domains, services, events, contracts, owners | EventCatalog, generated from released contracts, on a storage static website ([ADR 0009](docs/adr/0009-eventcatalog-generated-from-contracts.md)) |

**Regions** (verified 2026-10-16): everything in **Belgium Central**, except
API Management (Consumption tier not offered there), which runs in **France
Central**. West Europe does not accept new customers for this subscription.

### API-led layers

Every call between layers goes through API Management. Hand-offs between
domains are events.

```mermaid
flowchart TB
    consumers(["Consumers<br/>webshop · support · partners · agents"])
    apim{{"API Management<br/>Consumption tier"}}

    subgraph experience["Experience layer · APIM + thin Functions"]
        direction LR
        exp_cs["Customer Service API"]
        exp_partner["Partner 3PL API"]
        exp_web["Webshop API"]
    end

    subgraph process["Process layer · Logic Apps Consumption"]
        direction LR
        proc_order["Order Process API"]
        proc_fulfil["Fulfilment Process API"]
    end

    subgraph events["Events"]
        eg[["Event Grid topics<br/>CloudEvents 1.0"]]
        sbq[("Service Bus Basic<br/>queue per subscriber + DLQ")]
    end

    subgraph system["System layer · Functions Flex Consumption"]
        sys_sf["Salesforce System API"]
        sys_sap["SAP System API"]
        sys_wms["WMS System API"]
        sys_3pl["3PL System API"]
    end

    subgraph backends["Backends"]
        sf["Salesforce<br/>mock or Developer Edition"]
        sap["SAP mock"]
        wms["WMS mock"]
        tpl["3PL mock<br/>strict schema"]
    end

    subgraph shared["Cross-cutting"]
        appi["Application Insights<br/>one trace per journey"]
        kv["Key Vault + managed identities"]
        catalog["EventCatalog<br/>generated from contracts"]
    end

    consumers --> apim --> experience
    experience --> process
    process -- "publish" --> eg --> sbq -- "subscribe" --> process
    process --> system
    sys_sf --> sf
    sys_sap --> sap
    sys_wms --> wms
    sys_3pl --> tpl
```

### The ACME 4711 journey

What the platform sees for one order. After deployment v2.4 of
`stock-to-3pl`, the 3PL rejects the shipment request and it lands in the
dead-letter queue.

```mermaid
sequenceDiagram
    autonumber
    participant SF as Salesforce
    participant OP as Order Process API
    participant EG as Event Grid
    participant FP as Fulfilment Process API
    participant SAP as SAP System API
    participant WMS as WMS System API
    participant TPL as 3PL System API
    participant DLQ as Dead-letter queue

    Note over SF,DLQ: correlationid ord-4711 · customerid ACME · orderid 4711 on every hop
    SF->>OP: Opportunity closed-won, create order 4711
    OP->>EG: OrderCreated
    EG->>FP: OrderCreated
    FP->>SAP: Create sales order
    SAP-->>FP: Confirmed
    FP->>EG: OrderConfirmed
    FP->>WMS: Reserve stock
    WMS-->>FP: Reserved
    FP->>EG: StockReserved
    FP->>TPL: ShipmentRequest via stock-to-3pl v2.4
    TPL-->>FP: 400 schema mismatch
    FP->>DLQ: Dead-lettered with reason
    Note over FP,DLQ: 12 orders worth €84k, ACME is one of them
```

## Repositories

| Repository | Owner | Status |
|---|---|---|
| [ai-intelligence-domain](https://github.com/azure-intelligence-domain/ai-intelligence-domain) | Architecture | ✅ this repository |
| [azure-landing-zone](https://github.com/azure-intelligence-domain/azure-landing-zone) | Platform team | ✅ guardrails + OIDC pipeline |
| [integration-platform](https://github.com/azure-intelligence-domain/integration-platform) | Platform team | ✅ v1.1.0: two gateways, events, queues, tracing, tap |
| [contracts](https://github.com/azure-intelligence-domain/contracts) | Platform team | ✅ v1.2.0: envelope 1.1.0, rules, contract check |
| [eventcatalog](https://github.com/azure-intelligence-domain/eventcatalog) | Platform team | ✅ [GitHub Pages](https://azure-intelligence-domain.github.io/eventcatalog/) · [Azure](https://stcatalogxyxd4f2znqkqy.z50.web.core.windows.net) |
| template-api | Platform team | ⏳ step 5 |
| backend-systems | Outside world | ⏳ step 5 |
| system-api-salesforce, -sap, -wms, -3pl | Domain teams | ⏳ steps 5–6 |
| [process-api-order](https://github.com/azure-intelligence-domain/process-api-order) | Order team | ✅ v0.1.0: design (contracts, BPMN) |
| process-api-fulfilment | Domain teams | ⏳ step 6 |
| experience-api-customer-service, -partner, -webshop | Channel teams | ⏳ step 7 |
| intelligence-domain | Intelligence team | ⏳ phase 2 |

How they relate: see [ADR 0006](docs/adr/0006-repository-per-ownership-boundary.md).
