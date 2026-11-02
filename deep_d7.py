# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 7 — Microservices, as a person who has to operate them"},
        {"t": "p", "text": "Day 7 is the boundary question. A lead draws a module first, names the data owner, and only then cuts a process. Every extra process adds a network failure, a contract, a dashboard, and an on-call question. The examples stay on Orders, Inventory, and email."},

        {"t": "h2", "text": "What a service is, and what a folder is"},
        {"t": "p", "text": "A microservice is a deployable with its own data and a business capability, owned by a team that can release it. A folder or a project inside one solution is a module. A schema with its own login is a step toward a boundary. A separate process that shares tables with another process is a distributed monolith: you paid for the network and kept the coupling."},
        {"t": "p", "text": "Start from a modular monolith when one team owns the domain and the boundaries are still moving. Extract a service when a part needs its own scale, its own release train, or a different availability target. Each service writes its own data. Another service gets that data through an API or a message, or it keeps a copy it accepts may lag."},
        {"t": "p", "text": "Synchronous HTTP is for a query the user is waiting on, when the caller can tolerate the dependency. Asynchronous messaging is for work that can finish after the response, and for fan-out. Azure Service Bus is for commands and business events that need locks, dead-letter, sessions, and a consumer. Event Grid is for event distribution and for reacting to platform events such as a blob landing. Event Hubs is a high-volume stream, closer to telemetry and ingestion than to one business command that must be completed exactly once from the consumer's point of view."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """One deployable today:
  Api
    Modules/Orders        writes orders schema, login app_orders_runtime
    Modules/Catalog       writes catalog schema, login app_catalog_runtime
    Modules/Pricing       IPriceService, no database of its own yet

Not a service yet:
  A second App Service that still selects from orders.Orders.

A service, when you cut:
  Catalog API, its own database, its own release.
  Orders hears product changes from a message, or calls Catalog for a read
  the user is waiting on. Orders does not get a SQL login on the catalog tables."""},
        {"t": "warn", "title": "What breaks", "text": "Two deployables and one shared table means a migration in either service can break the other, and neither dashboard shows the join. Event Hubs for 'order placed' gives you a stream and makes you build lock, dead-letter, and replay yourself. Event Grid for a command that must be completed under a lease is the wrong tool."},
        {"t": "lead", "title": "Say this", "text": "A module is a boundary inside one deployable. A service owns its data and its release. Service Bus for the business message, Event Grid for distribution and platform events, Event Hubs for a stream. A second process on a shared table is a distributed monolith."},

        {"t": "h2", "text": "When you split, and when you keep the monolith"},
        {"t": "p", "text": "Keep one deployable while one team is learning the domain, the transactions are local, and you can still draw modules as projects and schemas. Split when a capability has a different scaling profile, a different compliance boundary, or a team that must release without waiting for the rest. Catalog reads often dwarf order writes, and a second team may own catalog. That is a reason. A modern diagram is not a reason."},
        {"t": "p", "text": "Before the cut, three things are true: the schema is already independent, a contract test exists, and a team can run the new service next week. If you cannot name the data owner and the failure the user will see, the split is early. In the interview, draw the modules, then one dotted line, and say what has to be true before you cut."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Keep together this quarter:
  Orders and pricing. One team. One query shape. IPriceService is the seam.

Cut catalog when:
  Catalog deploys twice a week and orders deploys with a migration window.
  Catalog read p95 is dominated by a workload orders does not share.
  The catalog team can be on call for their own database.

Do not cut payments into a service because a slide had six boxes.
Payments that must commit with the order stay in the order transaction
until you are ready to own a saga."""},
        {"t": "warn", "title": "What breaks", "text": "A split without a contract test ships a broken JSON field to production as a deploy of 'the other repo'. A split that leaves a shared database recreates the coupling and hides it from the API review."},
        {"t": "lead", "title": "Say this", "text": "I keep a modular monolith until scale, compliance, or a release train forces a cut. The cut needs its own schema, a contract test, and an owner. I can name the failure before I draw the box."},

        {"t": "h2", "text": "Database per service, and the join you lost"},
        {"t": "p", "text": "The hard part of a database per service is the report that used to join Orders and Customers. After the split, that join is a distributed query. You have three honest options. The UI calls both services and composes, which fits a small screen. One service stores the few customer fields it needs, updated by events, which fits a hot path and accepts lag. A reporting store ingests both streams, which fits analytics. You do not give the order service a SQL login on the customer tables. Cross-service work that needs both commits to succeed becomes a saga, not a TransactionScope over two databases."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Before: one database, one report.
SELECT o.Id, c.Name, o.Total
FROM orders.Orders o
JOIN customers.Customers c ON c.Id = o.CustomerId;

-- After: Orders keeps a copy it is willing to see go stale.
CREATE TABLE orders.CustomerSnapshot
(
    CustomerId int NOT NULL PRIMARY KEY,
    Name nvarchar(200) NOT NULL,
    UpdatedUtc datetime2 NOT NULL
);
-- Filled by CustomerChanged events. The order list does not call Customers
-- on the hot path. A screen that must be current calls Customers at read time
-- and shows a controlled error if Customers is down.

-- The report for finance does not run this join in the order service.
-- It reads a reporting store fed by both streams."""},
        {"t": "warn", "title": "What breaks", "text": "A SQL login across the boundary becomes the path every future feature uses, and the service boundary is a fiction. A snapshot with no lag budget surprises support when the name on the order is an hour old and nobody wrote that down. A distributed transaction across two databases will fail in exactly the way the saga was invented to avoid, and it will hold locks while it does."},
        {"t": "lead", "title": "Say this", "text": "The service owns its writes. The old join becomes a UI composition, a copied snapshot that may lag, or a reporting store. I say the reporting question in the design review so the shared database does not sneak back."},

        {"t": "h2", "text": "The outbox, and the crash between save and publish"},
        {"t": "p", "text": "If you save the order and then publish, a crash or a bus outage between the two leaves a committed order and no message. The email never sends. If you publish and then save, a failed save leaves a message for an order that does not exist. The outbox inserts the order and an outbox row in one SQL transaction. A relay reads unpublished rows, sends them, and marks them published. The relay can send twice if it crashes after the send and before the mark, so the consumer deduplicates on the message id. Polling the outbox is the version you can explain and operate. A transaction-log reader is an optimization you reach for when the poll cannot keep up, and you say that rather than pretending you run one."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """await using var tx = await db.Database.BeginTransactionAsync(ct);

db.Orders.Add(order);
db.Outbox.Add(new OutboxMessage
{
    Id = messageId,
    Type = "OrderPlaced",
    Payload = JsonSerializer.Serialize(new OrderPlaced(order.Id, order.TenantId)),
    OccurredUtc = time.GetUtcNow()
});
await db.SaveChangesAsync(ct);
await tx.CommitAsync(ct);
// Nothing has been sent. The user's 201 is already honest: the order exists.

// Relay, a separate loop. It may send twice. Consumers dedupe on Id.
var pending = await db.Outbox.Where(m => m.PublishedUtc == null).Take(50).ToListAsync(ct);
foreach (var message in pending)
{
    await sender.SendMessageAsync(new ServiceBusMessage(message.Payload)
    {
        MessageId = message.Id.ToString(),
        Subject = message.Type
    }, ct);
    message.PublishedUtc = time.GetUtcNow();
}
await db.SaveChangesAsync(ct);"""},
        {"t": "p", "text": "The outbox table is an operational object. It has a count, an age, and an owner. Alert when the oldest unpublished row is older than the budget you told the business, which in the running example is inside a minute for email. A visible unpublished row is a better failure than a message that existed only in memory."},
        {"t": "warn", "title": "What breaks", "text": "Publish after SaveChanges drops the message on a crash. Publish before SaveChanges emits a ghost order. Marking the row published before the send drops it the other way. A relay with no alert looks like a healthy API and a silent email."},
        {"t": "lead", "title": "Say this", "text": "The order and the outbox row commit together. A relay publishes and may publish twice. Consumers dedupe. I alert on the age of unpublished rows. I never hold the SQL transaction open while I call the bus."},

        {"t": "h2", "text": "A saga for order, payment, and inventory"},
        {"t": "p", "text": "A saga is a long-running process with a forward path and a compensation path. There is no distributed lock across the three databases. Orchestration puts the policy in one process manager, which is easier to see, to test, and to change. Choreography lets each service react to events, which couples them less and becomes harder to trace. For order, payment, and inventory, orchestration is the right default because the compensation policy is a business rule you want in one place."},
        {"t": "p", "text": "The order service writes an order in Pending. The orchestrator asks inventory to reserve, then asks payment to capture. If payment fails, it sends a release and marks the order Failed. If the release fails, the saga stays in a compensating state and alerts a human. Each of inventory and payment commits its own local transaction and honors its own idempotency key. A reservation expires if the saga never completes. Timeouts are explicit."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """States you can query, not only log:
  Pending
  Reserved                 inventory said yes, payment not finished
  Paid                     both said yes
  Failed                   payment said no, inventory released
  CompensationFailed       payment said no, release did not stick
  PaymentUnknown           the call timed out; do not capture again blindly

Each call carries the order id as the idempotency key.
Reserve twice is one reservation.
Capture twice is one charge.
A timeout on capture moves to PaymentUnknown and pages a person.
It does not start a second capture because the first one might have landed."""},
        {"t": "warn", "title": "What breaks", "text": "A second capture after a timeout double-charges. A choreography of three consumers hides the policy that should release inventory. A saga with no stuck-state query means support reads distributed traces to answer 'where is my order'. Compensation that is not idempotent releases twice or not at all."},
        {"t": "lead", "title": "Say this", "text": "I orchestrate this saga because the compensation is one business rule. Each service commits locally and dedupes. I name the stuck states: Pending too long, PaymentUnknown, and CompensationFailed. Those states have a query and an owner."},

        {"t": "h2", "text": "Idempotent consumption in SQL"},
        {"t": "p", "text": "At-least-once delivery is the realistic Service Bus contract. Exactly-once processing is your deduplication, not a checkbox on the bus. The message has a stable id. The consumer inserts that id into a processed-message table with a unique primary key, in the same transaction as the business write. A duplicate key means this message was already applied, and the consumer completes it without doing the work again. For a create, the business unique key can be the idempotency key itself. For an increment, you store the message id so you do not add the quantity twice."},
        {"t": "p", "text": "Complete the bus message only after the transaction commits. If you complete first and then crash, the work is lost. If you commit first and then crash before complete, the message redelivers and the unique key saves you. A unit test that calls the handler twice is the cheapest proof. Teams that say the bus is exactly-once and skip the key double-ship one order."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE TABLE orders.ProcessedMessages
(
    MessageId uniqueidentifier NOT NULL PRIMARY KEY,
    ProcessedUtc datetime2 NOT NULL
);

BEGIN TRAN;
    INSERT INTO orders.ProcessedMessages (MessageId, ProcessedUtc)
    VALUES (@MessageId, SYSUTCDATETIME());
    -- 2627 or 2601: already applied. Commit nothing else. Complete the message.

    UPDATE orders.Inventory
    SET OnHand = OnHand - @Qty
    WHERE Sku = @Sku;
COMMIT;
-- Complete the Service Bus message only after COMMIT succeeds."""},
        {"t": "warn", "title": "What breaks", "text": "An increment without the message id adds the quantity on every redelivery. Completing the message before the commit drops the reservation on a crash. A unique key in a different transaction from the stock update still double-applies."},
        {"t": "lead", "title": "Say this", "text": "The bus delivers at least once. I insert the message id in the same transaction as the business write. A duplicate key means I complete and do nothing. I complete the message after commit."},

        {"t": "h2", "text": "Versioning an event"},
        {"t": "p", "text": "The event is a contract. It carries a version, a message id, a correlation id, an occurred time, and a payload that tolerates new fields. Adding an optional field is a compatible change. Renaming a field or changing a meaning is a new event type or a new version, and you publish both until consumers move. You do not share a C# entity project across services, because a rebuild then couples their releases. A small contract package or a published schema is enough. Consumers ignore fields they do not understand. They do not throw on an unknown optional field and dead-letter the queue."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """{
  "specVersion": "1.0",
  "type": "orders.orderPlaced",
  "id": "8f1c...",
  "time": "2026-10-30T12:00:00Z",
  "correlationId": "req-441",
  "data": { "orderId": 100, "tenantId": 10, "total": 42.00 }
}

A later producer adds "currency": "USD". Old consumers ignore it.
A later producer that renames total to amount publishes
orders.orderPlaced.v2 and keeps v1 until the email worker and inventory move.
The shared project Orders.Entities.dll referenced by both services is the
distributed monolith. Do not do that."""},
        {"t": "warn", "title": "What breaks", "text": "A required new field dead-letters every old consumer. A shared EF model means a column rename in one service fails the other service's build, or worse, its runtime. Deserializing with a setting that throws on extra members turns a compatible change into an outage."},
        {"t": "lead", "title": "Say this", "text": "Optional fields are compatible. A new meaning is a new version, published beside the old one. I do not share the entity project. Consumers ignore what they do not understand."},

        {"t": "h2", "text": "Logs, metrics, and traces across services"},
        {"t": "p", "text": "Every request and every message carries a correlation id. If a message causes another message, carry a causation id too. Logs are structured: correlation id, service name, message id, tenant, and a duration. Do not log the full payload when it contains personal data. Metrics that matter: request rate, latency, error rate, dependency latency, queue depth, dead-letter depth, outbox age, and saga state counts. Traces connect the HTTP call to SQL and to the consumer with OpenTelemetry. Alert on symptoms users feel and on queues that will become those symptoms. One dashboard per service, and one picture of the business flow."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """HTTP POST /orders
  traceId = 441
  writes orders.Outbox.CorrelationId = 441

Relay
  publishes ServiceBus message ApplicationProperties["traceId"] = 441

Email function and inventory consumer
  start a span with that trace id
  log messageId and the outcome, not the customer's email address

Alert:
  outbox age > the minute we promised
  dead-letter depth > 0
  CompensationFailed count > 0"""},
        {"t": "warn", "title": "What breaks", "text": "Adding correlation ids after five services are live is a project. A dashboard of CPU with no queue depth looks green while mail is an hour behind. Logging the order payload logs a name, an address, and sometimes a payment reference."},
        {"t": "lead", "title": "Say this", "text": "One correlation id crosses HTTP, the outbox, and the consumers. I alert on outbox age and dead-letter depth, not only on CPU. Tracing is in the first release, because retrofitting it is a project."},

        {"t": "h2", "text": "A downstream service is down"},
        {"t": "p", "text": "Classify the call when you design the endpoint, not during the incident. If the call is synchronous and required, the user sees a controlled 503 after the timeout and the circuit breaker, and you do not hold threads for a minute. If the work is asynchronous, the user sees 202 Accepted and a status they can poll, and the message waits on the bus or in the outbox. Also decide the backlog: if inventory is down, do you keep accepting orders into Pending, or do you stop at the edge? That is a business decision. Write it down. Automatic retry with backoff and a dead-letter path keeps the rest of the platform moving."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Tax service, user is waiting, business says we cannot price without it:
  timeout budget inside the request
  small retry only if the tax call is idempotent
  circuit open -> 503 ProblemDetails, trace id included
  we do not queue a half-priced order

Email, user is not waiting:
  201 as soon as the order and the outbox commit
  the provider outage shows up as outbox age or dead-letters
  the order status stays Confirmed, mail status stays Pending

Inventory down, business has chosen to keep taking orders:
  order stays Pending
  the saga retries reserve
  a query shows Pending older than the reservation window
  support sees the state without reading five logs"""},
        {"t": "warn", "title": "What breaks", "text": "A synchronous tax call with a 60-second timeout and three retries holds the thread pool and amplifies the outage. Accepting orders while inventory is down, with no Pending state, sells stock you cannot reserve. Rejecting orders that could have been queued is a product decision the team invented in the incident channel."},
        {"t": "lead", "title": "Say this", "text": "Required and synchronous becomes a fast 503. Work that can wait becomes 202 and a visible pending state. I decide accept-versus-reject with the product owner before go-live, and I write it down."},

        {"t": "h2", "text": "The picture you draw from memory"},
        {"t": "p", "text": "This is the whole day on one page. If you can redraw it and name the failure at each arrow, you can run the design question."},
        {"t": "b", "numbered": True, "items": [
            "The client calls the Order API. The API writes Order and Outbox in one transaction and returns 201.",
            "A relay publishes OrderPlaced to Service Bus and then marks the outbox row. A crash in between redelivers. Consumers dedupe.",
            "The email function and the inventory consumer both receive. Each inserts the message id with its own write.",
            "Inventory failure retries, then dead-letters. The order stays in a state support can query. The email path is independent.",
            "The correlation id is on the HTTP log, the outbox row, and both consumers.",
        ]},
        {"t": "code", "text": """Client
  |  POST /orders   trace 441
  v
Order API  --commit-->  Orders row + Outbox row
  |  201
  v
Relay  --publish-->  Service Bus order-placed
  |
  +--> Email function      dedupe, send, complete
  +--> Inventory consumer  dedupe, reserve, complete
                              |
                              +--> on poison: dead-letter, order state visible"""},
        {"t": "lead", "title": "Say this", "text": "I draw the commit, the relay, the two consumers, the dedupe, and the dead-letter. If I cannot point at the row support would open, the design is not done."},
        {"t": "break"},
    ]
