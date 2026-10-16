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
- **Azure**, region Belgium Central (West Europe as fallback per service).
- **Consumption tiers only.** Hard ceiling of **€10/month**, enforced by a
  budget and a kill switch ([ADR 0003](docs/adr/0003-azure-consumption-with-cost-cap.md)).
- **API-led and composable** ([ADR 0004](docs/adr/0004-api-led-composable.md)).
- **Contracts on everything**, documented in EventCatalog
  ([ADR 0005](docs/adr/0005-contracts-everywhere-eventcatalog.md)), following
  the **adidas API guidelines** ([ADR 0008](docs/adr/0008-adidas-api-guidelines.md)).
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
| 3 | Contract tooling: linting, breaking-change checks, EventCatalog | ⏳ |
| 4 | Platform core (Bicep): API Management, Event Grid, Service Bus, App Insights, Key Vault | ⏳ |
| 5 | First vertical slice: Salesforce System API → Order Process API → `OrderCreated`, one trace | ⏳ |
| 6 | SAP, WMS, 3PL System APIs and the Fulfilment Process API | ⏳ |
| 7 | Experience APIs | ⏳ |
| 8 | The v2.4 break: faulty `stock-to-3pl` mapping, dead letters arrive | ⏳ |

## Phase 2 — Intelligence domain

Tap, ingest, understand, remember, reason, expose (MCP). Planned after phase 1;
cost decisions per service.

## Architecture (phase 1)

| Layer | Building blocks | Azure service |
|---|---|---|
| Gateway | All APIs exposed through one gateway | API Management (Consumption) |
| Experience | Customer Service, Partner (3PL), Webshop | API Management (+ thin Functions) |
| Process | Order, Fulfilment | Logic Apps (Consumption) |
| System | Salesforce, SAP, WMS, 3PL | Functions (Flex Consumption, Python) |
| Events | Business events between domains | Event Grid → Service Bus Basic queue per subscriber (with DLQ) |
| Backends | Simulated Salesforce, SAP, WMS and 3PL, each with its own database (ADR 0007) | Cosmos DB serverless, one account per system + Functions (3PL partner API) |
| Observability | One trace per journey | Application Insights + Log Analytics |
| Secrets & identity | No secrets in code | Key Vault, managed identities |
| Catalog | Domains, services, events, contracts, owners | EventCatalog on Static Web Apps (Free) |

**Regions** (verified 2026-10-16): everything in **Belgium Central**, except
API Management (Consumption tier not offered there) and Static Web Apps
(not offered there), which run in **West Europe**.

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
        catalog["EventCatalog<br/>Static Web Apps Free"]
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
| integration-platform | Platform team | ⏳ step 4 |
| [contracts](https://github.com/azure-intelligence-domain/contracts) | Platform team | ✅ envelope v1.0.0 |
| eventcatalog | Platform team | ⏳ step 3 |
| template-api | Platform team | ⏳ step 5 |
| backend-systems | Outside world | ⏳ step 5 |
| system-api-salesforce, -sap, -wms, -3pl | Domain teams | ⏳ steps 5–6 |
| process-api-order, -fulfilment | Domain teams | ⏳ steps 5–6 |
| experience-api-customer-service, -partner, -webshop | Channel teams | ⏳ step 7 |
| intelligence-domain | Intelligence team | ⏳ phase 2 |

How they relate: see [ADR 0006](docs/adr/0006-repository-per-ownership-boundary.md).
