"""One definition of every domain's data model → Mermaid erDiagrams (for .md) and EventCatalog
entities (domains/<domain>/entities/<Entity>/index.mdx)."""
import json, os, sys

# property: (name, type, required, description, extra)  extra: refs=Entity (one), many=Entity, enum=[...]
def P(name, type_, desc, req=True, **extra):
    return dict(name=name, type=type_, required=req, description=desc, **extra)

STATUSES = ["placed", "confirmed", "rejected", "onHold", "readyForShipment", "shipped", "delivered", "completed", "cancelled"]

MODELS = {
 "order": {
  "built": "Built (process-api-order 1.2.0). The order is kept in Salesforce, the system of record.",
  "entities": [
   dict(id="Order", name="Order", aggregateRoot=True, identifier="orderId",
        summary="The order across its lifecycle: a state machine, with payment status as a separate dimension.",
        properties=[P("orderId", "string", "Order id, assigned by Salesforce (OrderNumber), e.g. 4711. Business key orderid."),
                    P("customerId", "string", "The customer (Salesforce Account). Business key customerid.", refs="Account"),
                    P("channel", "string", "Where it was placed.", enum=["salesforce", "webshop", "agent"]),
                    P("status", "string", "Lifecycle status (state machine).", enum=STATUSES),
                    P("paymentStatus", "string", "Separate from status: shipped can be unpaid.", enum=["unpaid", "invoiced", "paid"]),
                    P("orderLines", "array", "The products ordered.", many="OrderLine"),
                    P("totalAmount", "Money", "Sum of the lines.", refs="Money"),
                    P("deliveryAddress", "DeliveryAddress", "Where it goes.", refs="DeliveryAddress"),
                    P("requestedDeliveryDate", "date", "Requested delivery date.", req=False),
                    P("holdReason", "string", "Why it is on hold, when it is.", req=False),
                    P("cancellationReason", "string", "Why it was cancelled (soft delete).", req=False),
                    P("references", "OrderReferences", "Where the order lives in the other domains' systems.", req=False, refs="OrderReferences"),
                    P("timeline", "array", "Every business fact about the order, from every domain.", many="OrderMilestone"),
                    P("createdAt", "date-time", "Placed at, UTC."), P("updatedAt", "date-time", "Last change, UTC.")]),
   dict(id="OrderReferences", name="Order References", summary="Value object: the order's documents in the other domains, recorded from their facts; OrderCancelled names them so each domain undoes its part.",
        properties=[P("erpOrderNumber", "string", "SAP sales order.", req=False, refs="SalesOrder"), P("invoiceNumber", "string", "SAP invoice.", req=False, refs="Invoice"),
                    P("creditNoteNumber", "string", "SAP credit note.", req=False, refs="CreditNote"),
                    P("reservationId", "string", "WMS reservation.", req=False, refs="StockReservation"), P("warehouseId", "string", "Warehouse.", req=False),
                    P("shipmentId", "string", "3PL shipment.", req=False, refs="Shipment"), P("trackingNumber", "string", "Tracking number.", req=False),
                    P("partnerId", "string", "3PL partner.", req=False)]),
   dict(id="OrderMilestone", name="Order Milestone", summary="One business fact about the order, from any domain: the order's timeline.",
        properties=[P("fact", "string", "The fact, e.g. SalesOrderAccepted."), P("domain", "string", "Who published it.", enum=["order", "finance", "supply", "logistics"]),
                    P("occurredAt", "date-time", "When the order domain recorded it, UTC.")]),
   dict(id="OrderLine", name="Order Line", summary="One product in an order; line numbers are assigned by the order domain.",
        properties=[P("lineNumber", "integer", "Position in the order."), P("productId", "string", "The product.", refs="Product"),
                    P("quantity", "integer", "Units ordered."), P("unitPrice", "Money", "Price per unit.", refs="Money")]),
   dict(id="DeliveryAddress", name="Delivery Address", summary="Value object: where an order or shipment is delivered.",
        properties=[P("street", "string", "Street and number."), P("postalCode", "string", "Postal code."),
                    P("city", "string", "City."), P("countryCode", "string", "ISO 3166-1 alpha-2.")]),
   dict(id="Money", name="Money", summary="Value object: an amount in one currency.",
        properties=[P("value", "number", "The amount."), P("currency", "string", "ISO 4217, e.g. EUR.")]),
  ]},
 "sales": {
  "built": "Order, OrderItem, Account and Product are simulated in Cosmos DB (backend-systems, system-api-salesforce 1.1.0); Opportunity is not simulated yet.",
  "entities": [
   dict(id="Account", name="Account", aggregateRoot=True, identifier="AccountId", summary="A customer, e.g. ACME. Its id is the platform's customerid.",
        properties=[P("AccountNumber", "string", "Account number, e.g. ACME. Business key customerid."), P("Name", "string", "Customer name."),
                    P("Industry", "string", "Industry.", req=False), P("ShippingCity", "string", "Shipping address, flattened (also Street, PostalCode, CountryCode)."),
                    P("CurrencyIsoCode", "string", "The customer's currency.")]),
   dict(id="Opportunity", name="Opportunity", summary="A deal with an account; closed-won is where an order starts.",
        properties=[P("OpportunityId", "string", "Opportunity id."), P("AccountId", "string", "The account.", refs="Account"),
                    P("StageName", "string", "Sales stage.", enum=["Prospecting", "Negotiation", "Closed Won", "Closed Lost"]),
                    P("Amount", "number", "Expected value."), P("CloseDate", "date", "Expected or actual close.")]),
   dict(id="SalesforceOrder", name="Order (Salesforce)", aggregateRoot=True, identifier="OrderNumber",
        summary="Salesforce's Order record: the system of record of every order. Salesforce naming: PascalCase and __c custom fields.",
        properties=[P("id", "string", "Record id, e.g. 801Ad0000004711AAA."), P("OrderNumber", "string", "Auto-number, e.g. 4711: the platform's orderid."),
                    P("AccountId", "string", "The customer.", refs="Account"), P("OpportunityId", "string", "The deal it came from.", req=False, refs="Opportunity"),
                    P("Status", "string", "Salesforce's own status.", enum=["Draft", "Activated", "Cancelled"]),
                    P("Order_Status__c", "string", "The order domain's status."), P("Payment_Status__c", "string", "unpaid, invoiced, paid."),
                    P("Channel__c", "string", "salesforce, webshop, agent."), P("OrderItems", "array", "The lines.", many="SalesforceOrderItem"),
                    P("CurrencyIsoCode", "string", "ISO 4217."), P("TotalAmount", "number", "Computed by Salesforce."),
                    P("ShippingStreet", "string", "Address, flattened (also PostalCode, City, CountryCode)."),
                    P("Requested_Delivery_Date__c", "date", "Requested delivery date.", req=False),
                    P("Idempotency_Key__c", "string", "Key of the request that created it.", req=False),
                    P("ERP_Order_Number__c", "string", "References: SAP sales order (also Invoice_Number__c, Reservation_Id__c, Shipment_Id__c, ...).", req=False),
                    P("Order_Milestones__r", "array", "Related list: the order's timeline (Fact__c, Domain__c, Occurred_At__c).", req=False),
                    P("CreatedDate", "date-time", "UTC."), P("LastModifiedDate", "date-time", "UTC.")]),
   dict(id="SalesforceOrderItem", name="Order Item (Salesforce)", summary="An OrderItem of a Salesforce Order.",
        properties=[P("OrderItemNumber", "integer", "Line number."), P("Product2Id", "string", "The product.", refs="Product"),
                    P("Quantity", "integer", "Units."), P("UnitPrice", "number", "Price per unit, in the order's currency.")]),
   dict(id="Product", name="Product", summary="Salesforce Product2: what can be sold, e.g. SKU-1042. Its id is used by every domain.",
        properties=[P("ProductCode", "string", "Product code, e.g. SKU-1042: the productId of every domain."), P("Name", "string", "Product name."),
                    P("Family", "string", "Product family.", req=False), P("StandardPrice", "number", "List price (standard price book)."),
                    P("IsActive", "boolean", "For sale.")]),
  ]},
 "finance": {
  "built": "Built (system-api-sap 1.2.0, finance-intake 1.1.0). Kept in the simulated SAP, in SAP's own tables (VBAK, VBRK).",
  "entities": [
   dict(id="SalesOrder", name="Sales Order (SAP)", aggregateRoot=True, identifier="erpOrderNumber",
        summary="The ERP's copy of an order, after credit and availability checks: accepted or refused.",
        properties=[P("erpOrderNumber", "string", "SAP sales order number, e.g. 8000043217."), P("orderId", "string", "The order. Business key orderid.", refs="Order"),
                    P("customerId", "string", "The customer. Business key customerid.", refs="Account"),
                    P("status", "string", "Outcome of the checks.", enum=["accepted", "refused"]),
                    P("refusalReason", "string", "Why it was refused.", req=False), P("netValue", "Money", "Order value.", refs="Money"),
                    P("cancelledAt", "date-time", "Cancelled (soft delete), UTC.", req=False), P("cancellationReason", "string", "Why.", req=False)]),
   dict(id="Invoice", name="Invoice", aggregateRoot=True, identifier="invoiceNumber", summary="What the customer is billed for one sales order.",
        properties=[P("invoiceNumber", "string", "Invoice number."), P("erpOrderNumber", "string", "The sales order.", refs="SalesOrder"),
                    P("amount", "Money", "Amount due.", refs="Money"), P("issuedAt", "date-time", "UTC."), P("dueDate", "date", "Payment due."),
                    P("status", "string", "Open until fully paid.", enum=["open", "paid"]),
                    P("creditNoteNumber", "string", "The credit note that reversed it; it can no longer be paid.", req=False, refs="CreditNote")]),
   dict(id="CreditNote", name="Credit Note", identifier="creditNoteNumber", summary="Reverses an invoice when its sales order is cancelled (SAP credit memo, billing type G2).",
        properties=[P("creditNoteNumber", "string", "Credit memo number, e.g. 70004711."), P("invoiceNumber", "string", "The reversed invoice.", refs="Invoice"),
                    P("amount", "Money", "Amount credited.", refs="Money"), P("issuedAt", "date-time", "UTC.")]),
   dict(id="Payment", name="Payment", summary="Money received against an invoice.",
        properties=[P("paymentId", "string", "Payment id."), P("invoiceNumber", "string", "The invoice.", refs="Invoice"),
                    P("amount", "Money", "Amount received.", refs="Money"), P("receivedAt", "date-time", "UTC.")]),
  ]},
 "supply": {
  "built": "Built (system-api-wms 1.1.0, supply-intake 1.1.0). Kept in the simulated WMS.",
  "entities": [
   dict(id="Warehouse", name="Warehouse", summary="Where stock is kept.",
        properties=[P("warehouseId", "string", "Warehouse id: BRU-1."), P("name", "string", "Name."), P("countryCode", "string", "ISO 3166-1 alpha-2.")]),
   dict(id="StockItem", name="Stock Item", summary="Stock of one product in one warehouse.",
        properties=[P("productId", "string", "The product.", refs="Product"), P("warehouseId", "string", "The warehouse.", refs="Warehouse"),
                    P("onHand", "integer", "Units in the warehouse."), P("reserved", "integer", "Units reserved for orders.")]),
   dict(id="StockReservation", name="Stock Reservation", aggregateRoot=True, identifier="reservationId", summary="Stock set aside for one order.",
        properties=[P("reservationId", "string", "Reservation id."), P("orderId", "string", "The order. Business key orderid.", refs="Order"),
                    P("warehouseId", "string", "Where it is reserved.", refs="Warehouse"),
                    P("lines", "array", "What is reserved.", many="ReservationLine"),
                    P("lifecycleStatus", "string", "Reserved, or released when the order is cancelled.", enum=["reserved", "released"]),
                    P("reservedAt", "date-time", "UTC."), P("releasedAt", "date-time", "UTC.", req=False)]),
   dict(id="ReservationLine", name="Reservation Line", summary="One product of a reservation.",
        properties=[P("productId", "string", "The product.", refs="Product"), P("quantity", "integer", "Units reserved.")]),
  ]},
 "logistics": {
  "built": "Built (system-api-3pl 1.1.0, logistics-intake 1.1.0, experience-api-partner 1.0.0). Kept by the simulated partner speedy-3pl.",
  "entities": [
   dict(id="Partner", name="Partner (3PL)", identifier="partnerId", summary="A third-party logistics partner and the API version it speaks.",
        properties=[P("partnerId", "string", "Partner id. Business key partnerid."), P("name", "string", "Name."),
                    P("apiVersion", "string", "Version of the partner's shipment API the mapping targets, e.g. 2.4.")]),
   dict(id="Shipment", name="Shipment", aggregateRoot=True, identifier="shipmentId", summary="The delivery of one order by a 3PL partner.",
        properties=[P("shipmentId", "string", "Shipment id."), P("orderId", "string", "The order. Business key orderid.", refs="Order"),
                    P("partnerId", "string", "Who delivers. Business key partnerid.", refs="Partner"),
                    P("reservationId", "string", "The stock it ships.", refs="StockReservation"),
                    P("lines", "array", "What is shipped.", many="ShipmentLine"),
                    P("deliveryAddress", "DeliveryAddress", "Where it goes.", refs="DeliveryAddress"),
                    P("status", "string", "Lifecycle: booked; the partner reports the pick-up (dispatched) and the delivery; cancelled until picked up.",
                      enum=["booked", "dispatched", "delivered", "cancelled"]),
                    P("trackingNumber", "string", "The partner's tracking number."), P("bookedAt", "date-time", "UTC."),
                    P("dispatchedAt", "date-time", "UTC.", req=False), P("deliveredAt", "date-time", "UTC.", req=False),
                    P("cancelledAt", "date-time", "UTC.", req=False)]),
   dict(id="ShipmentLine", name="Shipment Line", summary="One product of a shipment.",
        properties=[P("productId", "string", "The product.", refs="Product"), P("quantity", "integer", "Units.")]),
  ]},
 "platform": {
  "built": "Built (contracts envelope 1.1.0). The business keys tie every domain's facts together.",
  "entities": [
   dict(id="CloudEvent", name="Event (envelope)", aggregateRoot=True, identifier="id",
        summary="Every event on the platform: a CloudEvent with a correlation id and business keys (contracts envelope 1.1.0).",
        properties=[P("id", "string", "Unique per event."), P("source", "string", "Who published it, e.g. /process-api-order/1.0.0."),
                    P("type", "string", "The fact, e.g. com.acme.order.placed."), P("time", "date-time", "When it happened, UTC."),
                    P("correlationid", "string", "The business journey, e.g. ord-4711."),
                    P("customerid", "string", "Business key: the customer.", req=False, refs="Account"),
                    P("orderid", "string", "Business key: the order.", req=False, refs="Order"),
                    P("partnerid", "string", "Business key: the partner.", req=False, refs="Partner"),
                    P("componentid", "string", "Business key: the API or flow, e.g. logistics-intake.", req=False),
                    P("data", "object", "The payload: owned by the producer.")]),
  ]},
}
DOMAIN_OF = {e["id"]: d for d, m in MODELS.items() for e in m["entities"]}

def er_type(p):
    t = p["type"]
    return {"date-time": "datetime", "array": "list"}.get(t, t.replace("-", ""))

def mermaid(domains, external=True):
    """erDiagram of the given domains; entities of other domains they reference appear as stubs."""
    lines = ["erDiagram"]
    shown = {e["id"] for d in domains for e in MODELS[d]["entities"]}
    rels, stubs = [], set()
    for d in domains:
        for e in MODELS[d]["entities"]:
            lines.append(f"    {e['id']} {{")
            for p in e["properties"]:
                key = "PK" if p["name"] == e.get("identifier") else ("FK" if "refs" in p and p["type"] == "string" else "")
                lines.append(f"        {er_type(p) if 'many' not in p else 'list'} {p['name']}{' ' + key if key else ''}")
            lines.append("    }")
            for p in e["properties"]:
                if "many" in p:
                    rels.append(f'    {e["id"]} ||--|{{ {p["many"]} : "{p["name"]}"')
                elif "refs" in p:
                    target = p["refs"]
                    if target in ("Money", "DeliveryAddress") and target not in shown:
                        continue  # value objects of the order domain: shown in its own diagram
                    card = "||--||" if target in ("Money", "DeliveryAddress") else ("}o--o|" if not p["required"] else "}o--||")
                    rels.append(f'    {e["id"]} {card} {target} : "{p["name"]}"')
                    if target not in shown:
                        stubs.add(target)
    if external:
        for s in sorted(stubs):
            lines.append(f'    {s} {{\n        string see_{DOMAIN_OF[s]}_domain\n    }}')
    return "\n".join(lines + rels)

def entity_mdx(domain, e):
    props = []
    for p in e["properties"]:
        q = {k: p[k] for k in ("name", "type", "required", "description")}
        if "enum" in p: q["enum"] = p["enum"]
        if "refs" in p: q["references"] = p["refs"]; q["relationType"] = "references"
        if "many" in p: q["type"] = "array"; q["items"] = {"type": p["many"]}; q["references"] = p["many"]; q["relationType"] = "hasMany"
        props.append(q)
    import yaml
    front = {"id": e["id"], "name": e["name"], "version": "1.0.0", "summary": e["summary"], "owners": [f"{domain}-team"]}
    if e.get("aggregateRoot"): front["aggregateRoot"] = True
    if e.get("identifier"): front["identifier"] = e["identifier"]
    front["properties"] = props
    body = f"\n## Overview\n\n{e['summary']}\n\n{MODELS[domain]['built']}\n\n<EntityPropertiesTable />\n"
    return "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=110) + "---\n" + body

if __name__ == "__main__":
    out = sys.argv[1]
    for d, m in MODELS.items():
        for e in m["entities"]:
            path = os.path.join(out, "domains", d, "entities", e["id"])
            os.makedirs(path, exist_ok=True)
            open(os.path.join(path, "index.mdx"), "w").write(entity_mdx(d, e))
        open(os.path.join(out, f"{d}.mmd"), "w").write(mermaid([d]))
    open(os.path.join(out, "all.mmd"), "w").write(mermaid(list(MODELS)))
    print(json.dumps({d: [e["id"] for e in m["entities"]] for d, m in MODELS.items()}))
