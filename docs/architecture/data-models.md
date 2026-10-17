# Data models per domain

Each domain owns its model and names things in its own language; nobody shares a database. What
ties the models together are the **business keys** that every event carries (`customerid`,
`orderid`, `partnerid`): that is how the Intelligence domain can join the facts of every domain into
one story ("ACME's order 4711: placed, accepted by SAP, stock reserved, stuck at the 3PL").

| Domain | Kept in | Status | Catalog |
|---|---|---|---|
| Order | process-api-order 1.2.0 (references, timeline) | Built | [Order domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/order/1.0.0) |
| Sales | Salesforce (system of record) | Order, Account, Product simulated | [Sales domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/sales/1.0.0) |
| Finance | SAP | Built | [Finance domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/finance/1.0.0) |
| Supply | WMS | Built | [Supply domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/supply/1.0.0) |
| Logistics | 3PL partner | Built | [Logistics domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/logistics/1.0.0) |
| Platform | the envelope | Built |
| Channel | none: the Experience APIs show the other domains' data | Built (ADR 0017) | [Channel domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/channel/1.0.0) | [Platform domain](https://azure-intelligence-domain.github.io/eventcatalog/docs/domains/platform/1.0.0) |

The models are defined once in [`data_models.py`](data_models.py), which writes the Mermaid diagrams
below and the entities of EventCatalog:

```bash
uv run --no-project --with pyyaml python docs/architecture/data_models.py <out>   # then copy <out>/domains into eventcatalog
```

## All domains, joined by their keys

```mermaid
erDiagram
    Order {
        string orderId PK
        string customerId FK
        string channel
        string status
        string paymentStatus
        list orderLines
        Money totalAmount
        DeliveryAddress deliveryAddress
        date requestedDeliveryDate
        string holdReason
        string cancellationReason
        OrderReferences references
        list timeline
        datetime createdAt
        datetime updatedAt
    }
    OrderReferences {
        string erpOrderNumber FK
        string invoiceNumber FK
        string creditNoteNumber FK
        string reservationId FK
        string warehouseId
        string shipmentId FK
        string trackingNumber
        string partnerId
    }
    OrderMilestone {
        string fact
        string domain
        datetime occurredAt
    }
    OrderLine {
        integer lineNumber
        string productId FK
        integer quantity
        Money unitPrice
    }
    DeliveryAddress {
        string street
        string postalCode
        string city
        string countryCode
    }
    Money {
        number value
        string currency
    }
    Account {
        string AccountNumber
        string Name
        string Industry
        string ShippingCity
        string CurrencyIsoCode
    }
    Opportunity {
        string OpportunityId
        string AccountId FK
        string StageName
        number Amount
        date CloseDate
    }
    SalesforceOrder {
        string id
        string OrderNumber PK
        string AccountId FK
        string OpportunityId FK
        string Status
        string Order_Status__c
        string Payment_Status__c
        string Channel__c
        list OrderItems
        string CurrencyIsoCode
        number TotalAmount
        string ShippingStreet
        date Requested_Delivery_Date__c
        string Idempotency_Key__c
        string ERP_Order_Number__c
        list Order_Milestones__r
        datetime CreatedDate
        datetime LastModifiedDate
    }
    SalesforceOrderItem {
        integer OrderItemNumber
        string Product2Id FK
        integer Quantity
        number UnitPrice
    }
    Product {
        string ProductCode
        string Name
        string Family
        number StandardPrice
        boolean IsActive
    }
    SalesOrder {
        string erpOrderNumber PK
        string orderId FK
        string customerId FK
        string status
        string refusalReason
        Money netValue
        datetime cancelledAt
        string cancellationReason
    }
    Invoice {
        string invoiceNumber PK
        string erpOrderNumber FK
        Money amount
        datetime issuedAt
        date dueDate
        string status
        string creditNoteNumber FK
    }
    CreditNote {
        string creditNoteNumber PK
        string invoiceNumber FK
        Money amount
        datetime issuedAt
    }
    Payment {
        string paymentId
        string invoiceNumber FK
        Money amount
        datetime receivedAt
    }
    Warehouse {
        string warehouseId
        string name
        string countryCode
    }
    StockItem {
        string productId FK
        string warehouseId FK
        integer onHand
        integer reserved
    }
    StockReservation {
        string reservationId PK
        string orderId FK
        string warehouseId FK
        list lines
        string lifecycleStatus
        datetime reservedAt
        datetime releasedAt
    }
    ReservationLine {
        string productId FK
        integer quantity
    }
    Partner {
        string partnerId PK
        string name
        string apiVersion
    }
    Shipment {
        string shipmentId PK
        string orderId FK
        string partnerId FK
        string reservationId FK
        list lines
        DeliveryAddress deliveryAddress
        string status
        string trackingNumber
        datetime bookedAt
        datetime dispatchedAt
        datetime deliveredAt
        datetime cancelledAt
    }
    ShipmentLine {
        string productId FK
        integer quantity
    }
    CloudEvent {
        string id PK
        string source
        string type
        datetime time
        string correlationid
        string customerid FK
        string orderid FK
        string partnerid FK
        string componentid
        object data
    }
    Order }o--|| Account : "customerId"
    Order ||--|{ OrderLine : "orderLines"
    Order ||--|| Money : "totalAmount"
    Order ||--|| DeliveryAddress : "deliveryAddress"
    Order }o--o| OrderReferences : "references"
    Order ||--|{ OrderMilestone : "timeline"
    OrderReferences }o--o| SalesOrder : "erpOrderNumber"
    OrderReferences }o--o| Invoice : "invoiceNumber"
    OrderReferences }o--o| CreditNote : "creditNoteNumber"
    OrderReferences }o--o| StockReservation : "reservationId"
    OrderReferences }o--o| Shipment : "shipmentId"
    OrderLine }o--|| Product : "productId"
    OrderLine ||--|| Money : "unitPrice"
    Opportunity }o--|| Account : "AccountId"
    SalesforceOrder }o--|| Account : "AccountId"
    SalesforceOrder }o--o| Opportunity : "OpportunityId"
    SalesforceOrder ||--|{ SalesforceOrderItem : "OrderItems"
    SalesforceOrderItem }o--|| Product : "Product2Id"
    SalesOrder }o--|| Order : "orderId"
    SalesOrder }o--|| Account : "customerId"
    SalesOrder ||--|| Money : "netValue"
    Invoice }o--|| SalesOrder : "erpOrderNumber"
    Invoice ||--|| Money : "amount"
    Invoice }o--o| CreditNote : "creditNoteNumber"
    CreditNote }o--|| Invoice : "invoiceNumber"
    CreditNote ||--|| Money : "amount"
    Payment }o--|| Invoice : "invoiceNumber"
    Payment ||--|| Money : "amount"
    StockItem }o--|| Product : "productId"
    StockItem }o--|| Warehouse : "warehouseId"
    StockReservation }o--|| Order : "orderId"
    StockReservation }o--|| Warehouse : "warehouseId"
    StockReservation ||--|{ ReservationLine : "lines"
    ReservationLine }o--|| Product : "productId"
    Shipment }o--|| Order : "orderId"
    Shipment }o--|| Partner : "partnerId"
    Shipment }o--|| StockReservation : "reservationId"
    Shipment ||--|{ ShipmentLine : "lines"
    Shipment ||--|| DeliveryAddress : "deliveryAddress"
    ShipmentLine }o--|| Product : "productId"
    CloudEvent }o--o| Account : "customerid"
    CloudEvent }o--o| Order : "orderid"
    CloudEvent }o--o| Partner : "partnerid"
```

## Order

```mermaid
erDiagram
    Order {
        string orderId PK
        string customerId FK
        string channel
        string status
        string paymentStatus
        list orderLines
        Money totalAmount
        DeliveryAddress deliveryAddress
        date requestedDeliveryDate
        string holdReason
        string cancellationReason
        OrderReferences references
        list timeline
        datetime createdAt
        datetime updatedAt
    }
    OrderReferences {
        string erpOrderNumber FK
        string invoiceNumber FK
        string creditNoteNumber FK
        string reservationId FK
        string warehouseId
        string shipmentId FK
        string trackingNumber
        string partnerId
    }
    OrderMilestone {
        string fact
        string domain
        datetime occurredAt
    }
    OrderLine {
        integer lineNumber
        string productId FK
        integer quantity
        Money unitPrice
    }
    DeliveryAddress {
        string street
        string postalCode
        string city
        string countryCode
    }
    Money {
        number value
        string currency
    }
    Account {
        string see_sales_domain
    }
    CreditNote {
        string see_finance_domain
    }
    Invoice {
        string see_finance_domain
    }
    Product {
        string see_sales_domain
    }
    SalesOrder {
        string see_finance_domain
    }
    Shipment {
        string see_logistics_domain
    }
    StockReservation {
        string see_supply_domain
    }
    Order }o--|| Account : "customerId"
    Order ||--|{ OrderLine : "orderLines"
    Order ||--|| Money : "totalAmount"
    Order ||--|| DeliveryAddress : "deliveryAddress"
    Order }o--o| OrderReferences : "references"
    Order ||--|{ OrderMilestone : "timeline"
    OrderReferences }o--o| SalesOrder : "erpOrderNumber"
    OrderReferences }o--o| Invoice : "invoiceNumber"
    OrderReferences }o--o| CreditNote : "creditNoteNumber"
    OrderReferences }o--o| StockReservation : "reservationId"
    OrderReferences }o--o| Shipment : "shipmentId"
    OrderLine }o--|| Product : "productId"
    OrderLine ||--|| Money : "unitPrice"
```

## Sales

```mermaid
erDiagram
    Account {
        string AccountNumber
        string Name
        string Industry
        string ShippingCity
        string CurrencyIsoCode
    }
    Opportunity {
        string OpportunityId
        string AccountId FK
        string StageName
        number Amount
        date CloseDate
    }
    SalesforceOrder {
        string id
        string OrderNumber PK
        string AccountId FK
        string OpportunityId FK
        string Status
        string Order_Status__c
        string Payment_Status__c
        string Channel__c
        list OrderItems
        string CurrencyIsoCode
        number TotalAmount
        string ShippingStreet
        date Requested_Delivery_Date__c
        string Idempotency_Key__c
        string ERP_Order_Number__c
        list Order_Milestones__r
        datetime CreatedDate
        datetime LastModifiedDate
    }
    SalesforceOrderItem {
        integer OrderItemNumber
        string Product2Id FK
        integer Quantity
        number UnitPrice
    }
    Product {
        string ProductCode
        string Name
        string Family
        number StandardPrice
        boolean IsActive
    }
    Opportunity }o--|| Account : "AccountId"
    SalesforceOrder }o--|| Account : "AccountId"
    SalesforceOrder }o--o| Opportunity : "OpportunityId"
    SalesforceOrder ||--|{ SalesforceOrderItem : "OrderItems"
    SalesforceOrderItem }o--|| Product : "Product2Id"
```

## Finance

```mermaid
erDiagram
    SalesOrder {
        string erpOrderNumber PK
        string orderId FK
        string customerId FK
        string status
        string refusalReason
        Money netValue
        datetime cancelledAt
        string cancellationReason
    }
    Invoice {
        string invoiceNumber PK
        string erpOrderNumber FK
        Money amount
        datetime issuedAt
        date dueDate
        string status
        string creditNoteNumber FK
    }
    CreditNote {
        string creditNoteNumber PK
        string invoiceNumber FK
        Money amount
        datetime issuedAt
    }
    Payment {
        string paymentId
        string invoiceNumber FK
        Money amount
        datetime receivedAt
    }
    Account {
        string see_sales_domain
    }
    Order {
        string see_order_domain
    }
    SalesOrder }o--|| Order : "orderId"
    SalesOrder }o--|| Account : "customerId"
    Invoice }o--|| SalesOrder : "erpOrderNumber"
    Invoice }o--o| CreditNote : "creditNoteNumber"
    CreditNote }o--|| Invoice : "invoiceNumber"
    Payment }o--|| Invoice : "invoiceNumber"
```

## Supply

```mermaid
erDiagram
    Warehouse {
        string warehouseId
        string name
        string countryCode
    }
    StockItem {
        string productId FK
        string warehouseId FK
        integer onHand
        integer reserved
    }
    StockReservation {
        string reservationId PK
        string orderId FK
        string warehouseId FK
        list lines
        string lifecycleStatus
        datetime reservedAt
        datetime releasedAt
    }
    ReservationLine {
        string productId FK
        integer quantity
    }
    Order {
        string see_order_domain
    }
    Product {
        string see_sales_domain
    }
    StockItem }o--|| Product : "productId"
    StockItem }o--|| Warehouse : "warehouseId"
    StockReservation }o--|| Order : "orderId"
    StockReservation }o--|| Warehouse : "warehouseId"
    StockReservation ||--|{ ReservationLine : "lines"
    ReservationLine }o--|| Product : "productId"
```

## Logistics

```mermaid
erDiagram
    Partner {
        string partnerId PK
        string name
        string apiVersion
    }
    Shipment {
        string shipmentId PK
        string orderId FK
        string partnerId FK
        string reservationId FK
        list lines
        DeliveryAddress deliveryAddress
        string status
        string trackingNumber
        datetime bookedAt
        datetime dispatchedAt
        datetime deliveredAt
        datetime cancelledAt
    }
    ShipmentLine {
        string productId FK
        integer quantity
    }
    Order {
        string see_order_domain
    }
    Product {
        string see_sales_domain
    }
    StockReservation {
        string see_supply_domain
    }
    Shipment }o--|| Order : "orderId"
    Shipment }o--|| Partner : "partnerId"
    Shipment }o--|| StockReservation : "reservationId"
    Shipment ||--|{ ShipmentLine : "lines"
    ShipmentLine }o--|| Product : "productId"
```

## Platform

```mermaid
erDiagram
    CloudEvent {
        string id PK
        string source
        string type
        datetime time
        string correlationid
        string customerid FK
        string orderid FK
        string partnerid FK
        string componentid
        object data
    }
    Account {
        string see_sales_domain
    }
    Order {
        string see_order_domain
    }
    Partner {
        string see_logistics_domain
    }
    CloudEvent }o--o| Account : "customerid"
    CloudEvent }o--o| Order : "orderid"
    CloudEvent }o--o| Partner : "partnerid"
```
