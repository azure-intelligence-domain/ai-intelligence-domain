# 0013 — The order domain: business events, soft deletes, tapped queries

- **Status:** accepted (design; implementation follows)
- **Date:** 2026-10-16

## Context

The first vertical slice is the order: placing it, and everything that
happens to it afterwards across Salesforce, the ERP, finance, the warehouse
and the 3PL. The demo's story (ACME's order 4711) is an order story. Events
must carry business meaning, not CRUD, and every retrieval of an order must be
visible to the Intelligence domain.

## Decision

**Order is a domain of its own** (`order`, owner `order-team`, topic
`evgt-intplat-order`). Sales keeps customers and opportunities; the order
domain owns the order's lifecycle across systems.

**Events are business facts in the past tense (Event Storming).**

| Rule | Example |
|---|---|
| Name what happened in the business | `OrderPlaced`, not `OrderCreated` (the talk's slides said OrderCreated) |
| No generic update: one event per intent | `OrderAmended`, `OrderDeliveryAddressChanged`, `OrderDeliveryRescheduled` |
| Nothing is deleted | Cancelling is a soft delete: `DELETE /orders/{orderId}` sets status `cancelled` and publishes `OrderCancelled` |
| Each domain names its own facts | Finance publishes `PaymentReceived`; the order domain's policy turns it into `OrderPaid` |
| Commands can fail, events cannot | `409 Order State Conflict` when the status does not allow a command |

**The order status is a state machine** (placed, confirmed, rejected, onHold,
readyForShipment, shipped, delivered, completed, cancelled). Payment status is
a separate dimension (unpaid, invoiced, paid).

**Queries are tapped with business keys.** Every operation declares its
business keys in the contract (`x-business-keys`, e.g. `orderid` from the
path, `customerid` from the query), so the gateway can publish every
retrieval as a query event carrying them: "ACME's order 4711 was retrieved 5
times today".

**Flows are BPMN 2.0.** The `.bpmn` files in the producing repository are the
source (editable in Camunda Modeler); EventCatalog shows them with bpmn-js
(the bpmn.io watermark stays visible, as its licence requires), and the README
has Mermaid versions for GitHub.

| Artefact | Where |
|---|---|
| Commands and queries (OpenAPI) | [`process-api-order/openapi.yaml`](https://github.com/azure-intelligence-domain/process-api-order/blob/main/openapi.yaml) |
| 15 business events (AsyncAPI) | [`process-api-order/asyncapi.yaml`](https://github.com/azure-intelligence-domain/process-api-order/blob/main/asyncapi.yaml) |
| Flows (BPMN) | [`process-api-order/docs/bpmn`](https://github.com/azure-intelligence-domain/process-api-order/tree/main/docs/bpmn) |
| Catalog | [Order domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/order/1.0.0/) |

Contracts are released as 0.x while designed; the catalog marks 0.x as draft.

## Alternatives considered

- **Order as a subdomain of Sales.** Fewer resources, but Sales would own the
  whole order-to-delivery lifecycle, which spans four other domains.
- **`POST /orders/{orderId}/cancellation`** instead of `DELETE`. More explicit
  as a resource, but `DELETE` is the HTTP verb people and agents expect; the
  reason is a query parameter.
- **Mermaid-only flows.** Render everywhere, but are not BPMN and cannot be
  edited in Camunda Modeler.

## Consequences

- The platform needs the `order` topic and gateway query events with business
  keys (platform v1.2.0).
- Policies need the finance, supply and logistics events; until those domains
  publish them, the order domain's policies have nothing to react to.
- `OrderCompleted` needs both `OrderDelivered` and `OrderPaid`, in any order.
