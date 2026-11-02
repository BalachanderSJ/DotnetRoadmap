# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Part B — System design for the whiteboard"},
        {"t": "p", "text": "Ten days. Day 1 is the checklist you write on the board before any product name. Day 2 teaches the order API in full, and later days reuse it. The load numbers are assumptions: about 50 requests a second at peak, about 2 million orders a year, a read p95 under 300 milliseconds, email within a minute. Label them. If the panel changes a number, change the design. A million events a second is a different system, and you do not design it unless they ask."},
        {"t": "p", "text": "The stack stays ASP.NET Core, EF Core, SQL Server or Azure SQL, Azure App Service for the request API, Azure Functions on the isolated worker for event and schedule work, Azure Service Bus when a consumer must finish under a lock, Entra ID for the caller, and managed identity for the process. A second deployable appears only when you can name its data and its failure. The microservices chapter in the roadmap and the deep dive is where that cut is practiced. Here you point at it and move on."},

        {"t": "h1", "text": "Part B, Day 1 — The design spine"},
        {"t": "p", "text": "Outcome. In three minutes you can put a checklist on the board that survives an interruption, and in twenty minutes you can walk it on a .NET backend without jumping to a platform you do not operate."},
        {"t": "p", "text": "Time box. About 3.5 hours. Read the checklist once. Then close the page and redraw it twice from memory. Spend an hour applying it to a returns endpoint, on paper, with no new Azure product. Spend the last hour giving the twenty-minute version out loud, and stop when the timer ends even if you love the next box."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "The panel says: design the backend. The resource is vague on purpose. Your job is to make the problem specific enough to draw, small enough to finish, and honest about what you refused. You are the tech lead. You still name the API, the table, the transaction, and the rollback."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "If they give no numbers, use the order-system assumptions and invite a correction: about 50 requests a second at peak, about 2 million orders a year, read p95 under 300 milliseconds, email within a minute, one region to start. Out of scope until they pull it in: a million-event stream, a second team, a synchronous payment capture, multi-region active-active. Write the out-of-scope line on the board so a later interruption has somewhere to land."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "Name the resource, the verb, and the status code before the framework. POST creates, and a partner retry is part of the contract, so the create takes an idempotency key. GET by id is the read. A list uses a cursor, not a page offset, once the list can grow. PATCH carries a rowversion when two people can edit. Status codes you must be able to place without a pause: 201 the first create, 200 a replay of the same request, 400 a body you will not accept, 401 the caller is unknown, 403 the caller is known and not allowed, 404 the id is not visible in this tenant, 409 a lost update or a key reused with a different body, 429 a limiter you chose to enforce, 503 a required dependency you gave up on. 500 is an unexpected fault with a correlation id, not a validation failure."},
        {"t": "h2", "text": "Data"},
        {"t": "p", "text": "Name the aggregate, the primary key, the business key, the tenant column, and the index that matches the hot query. The hot order list is (TenantId, CreatedUtc, Id), with the columns the list returns included so the query does not go back to the row for those fields. A uniqueness rule that is true in the domain becomes a unique index, and the tenant is part of that index. The application login can insert, update, and select. It cannot change the schema."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "Draw one box around what commits together. For the order that box is the order, its lines, the idempotency row, and the outbox row. Draw a second box around what is allowed to lag: the email, the search copy, the cache. Say the lag in the same units as the assumption, here within a minute for mail. A distributed transaction across SQL and Service Bus is the thing you refuse. The outbox is how the message still happens after the commit."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "Walk five failures, each with what the user sees. The database is down: the API returns 503, and the health check fails so the instance leaves rotation. The bus is down after the commit: the order stays, the outbox retries. The partner times out and posts again with the same key: they get the original order. Two workers update the order: one gets 409 and re-reads. A message cannot be processed: it dead-letters, the order is not deleted, someone is paged on the dead-letter depth. You do not need a sixth failure in the first twenty minutes."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "Three identities, every time. The caller's Entra token decides what the human or the partner app may do. The API's managed identity is the SQL user app_orders_runtime, limited to the schema it writes. The pipeline's migration identity applies DDL and is not the login the site uses all day. A function that sends mail can be a fourth identity if its rights are smaller. Logs carry a correlation id, the tenant, and the order id, and they do not carry a full address or a secret. The dashboard you name is request latency, SQL duration, outbox age, and dead-letter depth. Deploy is a reviewed migration, then a slot, then a smoke test, then a swap. Rollback is the swap back, and only while the schema is still one the old bits can run. That means expand, then contract later."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse four things in the first slice, and you say them so the panel knows you saw them. You refuse a microservice per noun. You refuse a shared SQL login in a high-privilege role. You refuse to publish to Service Bus inside the SQL transaction. You refuse to call Database.Migrate on startup, because a bad migration then takes every instance down during boot, and two instances can race. The pipeline applies the script before traffic moves."},
        {"t": "h2", "text": "Sketch"},
        {"t": "p", "text": "The board is the sketch. The pipeline order is the part you can also write as code, and it matches the request path you study in the deep dive and in the pipeline guide. Exception handling wraps the rest. Authentication runs before authorization. The rate limiter runs before the endpoint when the endpoint is what you are protecting. Correlation id is early so a 500 and a SQL log share it."},
        {"t": "code", "text": """Board, first three minutes:

  User and success: partner creates an order, customer reads it, mail can lag.
  Assume: 50 req/s peak, 2 million orders/year, read p95 < 300 ms, mail < 1 min.
  Out of scope: multi-region, a pricing service, a million-event stream.

  API:    POST /orders, GET /orders/{id}, GET /orders?cursor=, PATCH with rowversion
  Data:   orders schema, TenantId, unique (TenantId, IdempotencyKey), rowversion
  Commit: order + lines + idempotency + outbox
  After:  relay publishes, function sends mail, consumer dedupes
  Fail:   503, retry, 409, dead-letter
  Ops:    Entra token, app_orders_runtime, pipeline migrator, slot swap
  Refuse: extra service, db_owner, two-phase commit, Migrate at startup

// The request path you are willing to write if they ask.
app.UseExceptionHandler();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();
app.MapControllers();
app.MapHealthChecks("/health/ready");"""},
        {"t": "p", "text": "Health for readiness includes a short SQL check. Liveness does not, or a SQL blip restarts every instance. Always On stays on for the API so the process is up. ARR affinity stays off. Those are operating choices from the Azure day of the deep dive, and you repeat them here because a second instance is the first interruption you will get."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. Read the assumptions and the out-of-scope line. Ask them to correct the number.",
            "Minute 2 to 6. API and the status codes, including the retry.",
            "Minute 6 to 10. Tables, the unique key, the index for the list, the SQL role.",
            "Minute 10 to 14. The one transaction, then the outbox, then the lag.",
            "Minute 14 to 17. The five failures and what the caller sees.",
            "Minute 17 to 20. Identities, the swap, and the tradeoff you refused. Stop.",
        ]},
        {"t": "p", "text": "Practice this clock on a returns API the same evening: POST /returns is a new aggregate, it references an order, it has its own idempotency key, and it does not become a new service. If you cannot finish returns in twenty minutes, the spine is not yours yet."},
        {"t": "warn", "title": "Interview trap", "text": "Opening with a cluster, a cache, and six services before you have named the user. Inventing a quota or a price when you do not remember the document. Mixing 401 and 403. Putting the page offset on a list that will grow. Hiding the SQL role. Spending the last five minutes on a product you would not operate next month."},
        {"t": "lead", "title": "Say this", "text": "I write the user, the assumed number, and the out-of-scope line first. Then the API, the transaction, the failure the caller sees, and the rollback. I keep one API and one database at this load. A second process has to bring its own data, and that conversation lives in the microservices chapter, not in the first three minutes."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 2 — The order API"},
        {"t": "p", "text": "Outcome. You can teach the order API from the header to the dead-letter: idempotency, rowversion, outbox, App Service, and a Function on the isolated worker. This is the anchor. Later days only add a workload. The short version sits in the deep dive. This day is the one you can redraw and code."},
        {"t": "p", "text": "Time box. About 3.5 hours. Spend 40 minutes reading the flow once. Spend an hour writing the SQL and the create path from memory. Spend 40 minutes on the relay lease and the consumer. Spend the rest of the time giving the twenty-minute version twice, with a friend or a timer interrupting on the second instance."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "Design the backend for creating an order, reading it, and emailing a confirmation. Partners retry when they time out. Two staff members must not lose each other's updates. You are the tech lead. Ship one slice a team can operate."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "About 50 requests a second at peak, about 2 million orders a year, read p95 under 300 milliseconds, email within a minute. One region. The partner is an Entra application using an app role. A human user, if you have one, uses a delegated scope. The server prices the order. The client sends a sku, a quantity, and a ship-to. The client does not send the total, a tenant id, or an admin flag. Pricing is a module behind an interface in this process, not a service. Say that the numbers are assumptions."},
        {"t": "h2", "text": "API"},
        {"t": "table", "headers": ["Call", "Contract", "Code"], "rows": [
            ["POST /orders", "Header Idempotency-Key. Body is sku, quantity, ship-to. Raw body bytes are the hash.", "201 the first time, with Location. 200 when the same key and the same bytes are retried. 409 when the key is reused with different bytes. 400 when the key or the body is missing or invalid."],
            ["GET /orders/{id}", "Projection, no tracking. The id must be in the caller's tenant.", "200 or 404. 404 when the row exists for another tenant, so you do not reveal it."],
            ["GET /orders?cursor=&limit=", "Keyset on (CreatedUtc, Id), limit capped. The cursor is the last row's created time and id.", "200 and the next cursor. An offset is the design you mention and do not ship."],
            ["PATCH /orders/{id}", "The client sends the rowversion it read. Status moves only through a rule you can say.", "200, 404, or 409 when the version lost or the transition is illegal."],
            ["Auth failures", "No token, bad token, or missing role.", "401 unknown. 403 known and not allowed."],
        ]},
        {"t": "p", "text": "You require the idempotency key on create. A create without a key is a duplicate waiting for a timeout. That requirement is a product choice, and you label it. GET does not need a key. The first response is 201. The replay is 200 with the stored order id, so the client can tell a retry from a first insert if it cares, and either way it has the id."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE TABLE orders.Orders
(
    Id           uniqueidentifier NOT NULL CONSTRAINT PK_Orders PRIMARY KEY,
    TenantId     uniqueidentifier NOT NULL,
    Number       nvarchar(40)     NOT NULL,
    Status       nvarchar(32)     NOT NULL,
    Total        decimal(18, 2)   NOT NULL,
    RowVersion   rowversion       NOT NULL,
    CreatedUtc   datetime2        NOT NULL
);

CREATE UNIQUE INDEX UX_Orders_Tenant_Number
    ON orders.Orders (TenantId, Number);

CREATE INDEX IX_Orders_Tenant_Created
    ON orders.Orders (TenantId, CreatedUtc DESC, Id DESC)
    INCLUDE (Status, Total);

CREATE TABLE orders.IdempotencyKeys
(
    TenantId       uniqueidentifier NOT NULL,
    KeyValue       nvarchar(128)    NOT NULL,
    RequestHash    binary(32)       NOT NULL,
    OrderId        uniqueidentifier NOT NULL,
    ResponseStatus int              NOT NULL,
    CreatedUtc     datetime2        NOT NULL,
    CONSTRAINT PK_IdempotencyKeys PRIMARY KEY (TenantId, KeyValue)
);

CREATE TABLE orders.Outbox
(
    Id              uniqueidentifier NOT NULL CONSTRAINT PK_Outbox PRIMARY KEY,
    Type            nvarchar(64)     NOT NULL,
    Payload         nvarchar(max)    NOT NULL,
    CreatedUtc      datetime2        NOT NULL,
    PublishedUtc    datetime2        NULL,
    LeasedUntilUtc  datetime2        NULL,
    LeaseOwner      nvarchar(64)     NULL
);

CREATE INDEX IX_Outbox_Unpublished
    ON orders.Outbox (CreatedUtc)
    WHERE PublishedUtc IS NULL;"""},
        {"t": "p", "text": "The hash is SHA-256 of the raw request body, not of a DTO you serialized again. Two JSON texts that differ only by whitespace are different bodies under that rule, and the client must retry the same bytes. That is the contract you document. Re-hashing a reordered object is how a retry becomes a false 409. Rowversion is not the idempotency mechanism. The key is for a retry of the same request. The rowversion is for two different updates of an order that already exists."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "The create commits the order, the key, and the outbox row in one SQL transaction. If that commit succeeds, the order is durable and a relay will see the outbox row. If it fails, none of the three exist, and the client can retry. You do not insert the key in a transaction of its own and the order in another. A crash in between is a key that points at nothing, or an order with no key."},
        {"t": "p", "text": "The publish sits outside the transaction. A relay leases unpublished rows, sends them to Service Bus with MessageId set to the outbox id, then sets PublishedUtc. A crash after the send and before the mark sends the message again after the lease expires. The consumer treats that as normal. Service Bus duplicate detection, if you turn it on, has a history window you configure. You do not memorize the window, and you do not depend on it alone, because a duplicate after the window is still a duplicate to the business. The consumer's unique key is the one you can explain at night."},
        {"t": "p", "text": "The API does not wait for the mail provider. 201 means the order and the outbox row committed. Mail within a minute is the assumption, measured from commit to the provider accepting the message, and you watch outbox age to see if you are inside it. Two concurrent creates with the same key: one commits, the other hits unique index 2601 or unique constraint 2627, rolls back, clears the change tracker, and reads the winner. Same hash returns 200. Different hash returns 409."},
        {"t": "h2", "text": "Failure"},
        {"t": "table", "headers": ["What broke", "What you do", "What the caller sees"], "rows": [
            ["SQL is down", "Readiness fails. The instance leaves the load balancer. You do not retry the business create in a loop inside the request.", "503"],
            ["The partner times out after the commit", "They retry the same bytes and the same key.", "200 and the original order id"],
            ["The partner retries with a different body", "The stored hash does not match.", "409"],
            ["Service Bus is down", "The outbox row stays unpublished. The relay tries again. The order is already saved.", "201 already happened"],
            ["Two staff PATCH the same order", "The WHERE includes the rowversion. Zero rows is a concurrency exception.", "409, then the client re-reads"],
            ["The mail payload can never succeed", "The subscription dead-letters it. The order stays placed.", "The customer still has an order. Support sees the dead letter."],
        ]},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "The API runs on Azure App Service. Always On is on. ARR affinity is off. A staging slot gets the new bits, a smoke test hits it, and you swap. The Function app runs the isolated worker. One timer function relays the outbox. One Service Bus function sends mail. Each process uses a managed identity. app_orders_runtime may insert and update the orders schema and may not alter it. The relay's identity may read and update the outbox and send to the topic. The mail function's identity may write a delivery row and may not delete orders. The pipeline identity applies migrations and is not in the application connection string. Connection strings use Authentication=Active Directory Managed Identity. There is no SQL password in app settings."},
        {"t": "p", "text": "Rollback is a slot swap back, and you say the condition: this release only expanded the schema, so the previous bits still run. A dropped column means you cannot swap back, so you do not drop a column in the same release as the code that stops writing it. Messages already published are not recalled. Consumers accept the current payload and the previous one for that release. A feature flag can stop the relay if the consumer is bad. You do not delete orders to undo a mail bug."},
        {"t": "p", "text": "A second API instance is the normal case. Idempotency lives in the unique key, not in a static dictionary. The rate limit, when you add Day 7, is per instance unless a gateway holds the shared budget. The relay lease uses UPDLOCK and READPAST so two relay instances skip locked rows. If both still publish, the MessageId keeps the consumer idempotent. You do not run Database.Migrate from either instance."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse a two-phase commit between SQL and Service Bus. You refuse to send mail inside the request. You refuse to accept the total from the client. You refuse a pricing microservice in this slice. You refuse an in-memory idempotency cache. You refuse receive-and-delete on the subscription, because a crash after receive and before send loses the only copy of the work. Peek-lock is the mode, and complete happens after the work is durable."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """[Authorize(Policy = "OrdersWrite")]
[HttpPost("/orders")]
public async Task<IActionResult> Create(CancellationToken ct)
{
    if (!Request.Headers.TryGetValue("Idempotency-Key", out var keyHeader)
        || string.IsNullOrWhiteSpace(keyHeader))
        return Problem(statusCode: 400, title: "Idempotency-Key is required.");

    using var reader = new StreamReader(Request.Body);
    string raw = await reader.ReadToEndAsync(ct);
    var body = JsonSerializer.Deserialize<CreateOrderRequest>(raw);
    if (body is null || body.Quantity <= 0)
        return Problem(statusCode: 400, title: "The order body is invalid.");

    byte[] hash = SHA256.HashData(Encoding.UTF8.GetBytes(raw));
    Guid tenantId = _tenant.TenantId;
    decimal total = await _pricing.PriceAsync(body.Sku, body.Quantity, ct);
    var order = new Order
    {
        Id = Guid.NewGuid(),
        TenantId = tenantId,
        Number = AllocateNumber(),
        Status = "Placed",
        Total = total,
        CreatedUtc = DateTime.UtcNow
    };

    await using var tx = await _db.Database.BeginTransactionAsync(ct);
    try
    {
        _db.Orders.Add(order);
        _db.IdempotencyKeys.Add(new IdempotencyKey
        {
            TenantId = tenantId,
            KeyValue = keyHeader.ToString(),
            RequestHash = hash,
            OrderId = order.Id,
            ResponseStatus = StatusCodes.Status201Created,
            CreatedUtc = DateTime.UtcNow
        });
        _db.Outbox.Add(new OutboxMessage
        {
            Id = Guid.NewGuid(),
            Type = "OrderPlaced",
            Payload = JsonSerializer.Serialize(new { order.Id, order.TenantId }),
            CreatedUtc = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);
        await tx.CommitAsync(ct);
    }
    catch (DbUpdateException ex) when (IsUniqueViolation(ex))
    {
        await tx.RollbackAsync(ct);
        _db.ChangeTracker.Clear();
        return await ReplayOrConflict(tenantId, keyHeader.ToString(), hash, ct);
    }

    return Created($"/orders/{order.Id}", new { orderId = order.Id });
}

static bool IsUniqueViolation(DbUpdateException ex) =>
    ex.InnerException is SqlException sql && sql.Number is 2601 or 2627;"""},
        {"t": "p", "text": "ReplayOrConflict loads the key on a clean tracker. A matching hash returns 200 and the stored order id. A different hash returns 409. If the key row is absent, the unique violation was some other index, such as the order number, and that is a 409 with a different title. ChangeTracker.Clear matters: after the failed SaveChanges the context still holds the inserts, and the next SaveChanges would try them again."},
        {"t": "code", "text": """public async Task<IActionResult> Patch(Guid id, UpdateOrder body, CancellationToken ct)
{
    var order = await _db.Orders.FirstOrDefaultAsync(o => o.Id == id, ct);
    if (order is null)
        return NotFound();

    _db.Entry(order).Property(o => o.RowVersion).OriginalValue =
        Convert.FromBase64String(body.RowVersion);
    order.Status = body.Status;
    try
    {
        await _db.SaveChangesAsync(ct);
    }
    catch (DbUpdateConcurrencyException)
    {
        return Conflict();
    }
    return Ok();
}

-- Two relay instances. Locked rows are skipped. A dead worker's lease expires.
;WITH due AS
(
    SELECT TOP (50) *
    FROM orders.Outbox WITH (ROWLOCK, READPAST, UPDLOCK)
    WHERE PublishedUtc IS NULL
      AND (LeasedUntilUtc IS NULL OR LeasedUntilUtc < SYSUTCDATETIME())
    ORDER BY CreatedUtc
)
UPDATE due
SET LeasedUntilUtc = DATEADD(minute, 2, SYSUTCDATETIME()),
    LeaseOwner = @worker
OUTPUT inserted.Id, inserted.Type, inserted.Payload;"""},
        {"t": "p", "text": "The two-minute lease is a choice you make so a crashed worker does not block the row forever. It is not a platform default. After a successful send, set PublishedUtc. Do not set it before the send. The Service Bus message uses the outbox id as MessageId. The timer that calls the lease is a Function on the isolated worker, a few times a minute, so the outbox age stays inside the one-minute mail assumption. The exact cron is an operating choice. The function timeout for the plan you are on is a number you look up, and one batch of 50 small publishes fits in a wide margin. You do not put the mail provider call in this relay if Day 6 is going to fan out. The relay only publishes."},
        {"t": "code", "text": """// App Service / Function application settings. Names, not secrets.
// ServiceBus__fullyQualifiedNamespace: orders.servicebus.windows.net
// ConnectionStrings__Orders:
//   Server=tcp:orders.database.windows.net,1433;Database=orders;
//   Authentication=Active Directory Managed Identity;Encrypt=True;"""},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. Partner retries, server prices, the four assumptions, one region.",
            "Minute 2 to 6. POST with the key, 201 versus 200 versus 409, GET, PATCH with the rowversion. The client cannot send the total.",
            "Minute 6 to 11. The three tables, the unique key, the filtered outbox index, the list index. Hash the raw bytes.",
            "Minute 11 to 15. One transaction. Relay after commit. MessageId is the outbox id. Consumer dedupes. Lease so two relays skip locked rows.",
            "Minute 15 to 18. 503, replay, 409, dead-letter. The order survives a mail failure.",
            "Minute 18 to 20. App Service, affinity off, Function isolated worker, three identities, swap back only on an expanded schema. Pricing stays a module.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Using the rowversion as the retry key. Hashing a re-serialized DTO. Committing the outbox in a different transaction from the order. Completing the message before the send, or using receive-and-delete. Calling Migrate on startup. Drawing a pricing service before the idempotency row exists. Forgetting ChangeTracker.Clear after the unique violation. Caching the idempotency key in memory and missing the other instance."},
        {"t": "lead", "title": "Say this", "text": "One transaction holds the order, the idempotency row, and the outbox. The relay publishes after commit, the consumer dedupes on the message id, and a lost update returns 409 from the rowversion. The API is App Service, the worker is a Function on the isolated worker, and the SQL login cannot migrate. I hash the raw body. I do not accept the price from the client."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 3 — Catalog reads and order writes"},
        {"t": "p", "text": "Outcome. You can put a read-heavy catalog next to the write-heavy order path, choose a cache only where a staleness budget exists, page with a keyset, and say when you still do not split a service."},
        {"t": "p", "text": "Time box. About 3.5 hours. Redraw the order transaction from Day 2 in ten minutes so you do not design the catalog by forgetting it. Then the catalog read path, the keyset, and the cache key. Spend the last hour defending, out loud, the decision to keep one deployable."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "The same company has a product catalog that is read constantly and an order path that is the system of record. Design both. The panel will ask why the catalog is not its own service. Answer that with a condition, not with a slogan."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "The order assumptions still hold: about 50 requests a second at peak across the API, read p95 under 300 milliseconds. Catalog point reads are inside that budget. A product description may be up to 60 seconds stale. That 60 seconds is a product choice, not a cache product's limit. The price on the order is current at the moment of purchase, so the price used for an order is read from SQL inside the create, not from the description cache. One team owns both. Search with ranking is out of scope. If they add a real search box with its own relevance needs, you name a search index then, and you still do not start there."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "GET /products/{id} returns the description the page needs. GET /products?cursor=&limit= is the admin or the browse list, keyset on (Name, Id) or on the product id if that is the sort. POST /orders is unchanged from Day 2 and calls the pricing module on the way into the transaction. The catalog write, when a merchandiser edits a description, is a separate command with its own rowversion. It does not share a transaction with an order. There is no public endpoint that returns another tenant's product. 404 hides a cross-tenant id."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE TABLE catalog.Products
(
    Id          uniqueidentifier NOT NULL CONSTRAINT PK_Products PRIMARY KEY,
    TenantId    uniqueidentifier NOT NULL,
    Sku         nvarchar(64)     NOT NULL,
    Name        nvarchar(200)    NOT NULL,
    Description nvarchar(max)    NULL,
    UnitPrice   decimal(18, 2)   NOT NULL,
    UpdatedUtc  datetime2        NOT NULL,
    CONSTRAINT UQ_Products_Tenant_Sku UNIQUE (TenantId, Sku)
);

CREATE INDEX IX_Products_Tenant_Name
    ON catalog.Products (TenantId, Name, Id)
    INCLUDE (Sku, UnitPrice);

-- Order list, repeated so the contrast is on the board.
-- Hot path is a point read by id plus this list:
--   (TenantId, CreatedUtc DESC, Id DESC) INCLUDE (Status, Total)

SELECT TOP (@limit) Id, Name, Sku
FROM catalog.Products
WHERE TenantId = @tenant
  AND (Name > @afterName OR (Name = @afterName AND Id > @afterId))
ORDER BY Name, Id;"""},
        {"t": "p", "text": "OFFSET and FETCH for a deep page makes SQL read and throw away every skipped row. A keyset asks for the next page after the last key you returned. The sort must be unique, so Name alone is not enough and the id breaks the tie. The cursor is opaque to the client in the sense that you do not promise they can edit it, and it is still just the last key, so you can explain it."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "Orders stay read-your-writes from the primary. You do not put the create behind a cache, and you do not serve the GET-by-id that follows a 201 from a replica that might lag, not at this scale, because you have not measured a need. The description cache is allowed to lag for the 60-second budget. A price change is visible to the next order immediately because pricing reads SQL. If the business cannot accept a stale description either, you drop the cache and keep the keyset. At 50 requests a second a primary-key lookup is a reasonable thing to ask Azure SQL to do. You add a cache because a page got expensive or because you measured CPU, not because a diagram had a cylinder missing."},
        {"t": "p", "text": "IMemoryCache is per instance. An edit on instance A does not clear instance B. That is acceptable for a description inside a labeled budget, and it is unacceptable for a price you promised was current. A distributed cache gives you a shared key and a shared delete, and it adds a dependency. You take that dependency when the invalidation has to be prompt across instances, or when the cached object is expensive to rebuild and you have already measured the stampede. You do not take it on day one for a point read."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "SQL down means both the order create and the catalog read fail ready, and the API returns 503. A cache that still holds descriptions can serve those keys, and you may do that only if you are explicit that the page is cached and the price is not on it. A poisoned cache key, for example a key that omitted the tenant, leaks one tenant's description to another. That failure is worse than a slow page. The key includes the tenant id and the product id and the fact that it is the description, not the price. Output caching of a whole response has the same bug if the vary key forgets the tenant. For an authenticated tenant API you cache inside the service, where the key is obvious, and you leave response caching for a page that is truly identical for every caller."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "One App Service, one Azure SQL database, two schemas, two SQL users if you want the catalog writer and the order writer separated. The API identity can read products and write orders. A merchandiser role in Entra is allowed to PATCH a product. The list endpoint's index is part of the PR, with the filter and a sample plan, which is the same review rule as the rest of the roadmap. You watch SQL duration and cache hit rate if a cache exists. A hit rate with no latency win is a cache you delete."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse to split the catalog into its own service while one team owns it, the order transaction only needs a price lookup, and you have not measured a read workload that hurts the order path. A split is justified later by a release train, a measured resource fight, or a team that will carry the pager. The deep dive's microservices day has the cut: own schema, a contract test, and an owner. You can point at that day. You do not redraw it here. You also refuse a read replica at 50 requests a second, a cache of the order command, and OFFSET paging on the hot list."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """public async Task<ProductDescription?> GetDescription(Guid id, CancellationToken ct)
{
    string key = $"desc:{_tenant.TenantId:N}:{id:N}";
    if (_cache.TryGetValue(key, out ProductDescription? cached))
        return cached;

    var row = await _db.Products.AsNoTracking()
        .Where(p => p.Id == id)
        .Select(p => new ProductDescription(p.Id, p.Name, p.Description))
        .FirstOrDefaultAsync(ct);

    if (row is not null)
    {
        // 60 seconds is the staleness budget for text, not for price.
        _cache.Set(key, row, TimeSpan.FromSeconds(60));
    }
    return row;
}

public async Task<decimal> PriceAsync(string sku, int quantity, CancellationToken ct)
{
    decimal unit = await _db.Products.AsNoTracking()
        .Where(p => p.Sku == sku)
        .Select(p => p.UnitPrice)
        .SingleAsync(ct);
    return unit * quantity;
}"""},
        {"t": "p", "text": "The query filter from Day 5, or an explicit TenantId predicate, still applies. The cache key repeats the tenant so a missing filter is not the only line of defense. PriceAsync hits SQL on the create path. It does not read the description cache."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. One team, the order assumptions, a 60-second budget for description text only.",
            "Minute 2 to 6. Catalog GET and the order POST. The price is computed on the server from SQL.",
            "Minute 6 to 10. Two schemas, the keyset query, the covering index, why OFFSET loses.",
            "Minute 10 to 14. Orders are read-your-writes. Descriptions may lag 60 seconds per instance. Prices are not cached.",
            "Minute 14 to 17. A cache key without the tenant is a leak. SQL down is 503. A useless cache is removed.",
            "Minute 17 to 20. You refuse the split, the replica, and the cache on the command. You name the condition that would reopen the split.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Caching the price inside the description object and then claiming the order total is current. A cache key of only the product id. Output caching an authenticated page without varying on the tenant. Splitting a service because the word catalog sounds like a bounded context, before you can name the data owner and the failure. Using OFFSET because the first page looked fast."},
        {"t": "lead", "title": "Say this", "text": "Orders stay on the primary, uncached, with a keyset list. Catalog text can sit in a per-instance cache for a staleness budget I state, and the price for a new order comes from SQL. I keep one deployable until a team, a release train, or a measured fight forces a cut. The cache key includes the tenant."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 4 — Nightly file ingest"},
        {"t": "p", "text": "Outcome. You can take a nightly file of about a million rows from blob storage into SQL in chunks, make a retry safe, keep the HTTP API responsive, and show the partner which lines failed."},
        {"t": "p", "text": "Time box. About 3.5 hours. Draw the four hops without code. Then write the chunk transaction and the status API. Spend a full hour on the failure where one chunk is poison and the other chunks must continue. Speak the twenty-minute version once at a normal pace and once with someone asking where the file is parsed."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "A partner drops a CSV in storage every night, about a million rows. You validate, load, and report failures. The order API must stay inside its latency assumption while this runs. The mistake the panel is listening for is parsing the million rows on a request thread or inside the single function invocation that saw the blob."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "The file is about a million data rows, which is the problem statement, not a platform limit. A chunk of 5,000 rows is the starting size you will change after you look at log growth and lock time. The business wants the file in a terminal state by a deadline you agree with them, and you alert if it is not. The API's interactive budget is unchanged: read p95 under 300 milliseconds at about 50 requests a second. The import does not have to finish in one second. It has to finish in the night window without taking the API with it. You look up the function timeout for the plan you run. You do not memorize it. You size the chunk so one invocation finishes with room to spare."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "The partner does not upload through the order POST. They drop the blob, or an internal admin calls a small POST /imports that records a blob name you already accepted into the container. GET /imports/{fileId} returns the status and the error count. GET /imports/{fileId}/errors returns the bad lines, paged with a keyset on line number. The API never opens the file. 404 is a file id the caller cannot see. 409 is a second registration of a hash you have already merged, if that is the rule you documented."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE TABLE ingest.Files
(
    FileId       uniqueidentifier NOT NULL CONSTRAINT PK_Files PRIMARY KEY,
    TenantId     uniqueidentifier NOT NULL,
    BlobName     nvarchar(400)    NOT NULL,
    ContentHash  binary(32)       NOT NULL,
    Status       nvarchar(32)     NOT NULL,
    CreatedUtc   datetime2        NOT NULL
);

CREATE UNIQUE INDEX UX_Files_Hash_Merged
    ON ingest.Files (ContentHash)
    WHERE Status = N'Merged';

CREATE TABLE ingest.FileChunks
(
    FileId    uniqueidentifier NOT NULL,
    RowStart  int              NOT NULL,
    RowCount  int              NOT NULL,
    CONSTRAINT PK_FileChunks PRIMARY KEY (FileId, RowStart)
);

CREATE TABLE ingest.FileErrors
(
    FileId      uniqueidentifier NOT NULL,
    LineNumber  int              NOT NULL,
    Reason      nvarchar(400)    NOT NULL,
    CONSTRAINT PK_FileErrors PRIMARY KEY (FileId, LineNumber)
);

CREATE TABLE ingest.ProductBatch
(
    FileId     uniqueidentifier NOT NULL,
    TenantId   uniqueidentifier NOT NULL,
    Sku        nvarchar(64)     NOT NULL,
    Name       nvarchar(200)    NOT NULL,
    SourceHash binary(32)       NOT NULL
);"""},
        {"t": "p", "text": "The chunk primary key is the idempotency key for a range. A retry of the same file id and row start finds the row and stops, or it runs an upsert that is itself idempotent and then inserts the marker. The filtered unique index stops a second successful load of the same bytes. A failed file can be replayed after a fix because the filter only covers Merged. ProductBatch is staging. It is not the table the API reads for a product page."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "Each chunk is one transaction: the set-based upsert into the real table, the error rows for that range, and the FileChunks marker. You do not hold one transaction open for a million rows. You do not call SaveChanges per row. A million tracked entities will miss the window and keep the log and the locks busy while the API is trying to place orders."},
        {"t": "p", "text": "The upsert is idempotent on (TenantId, Sku). A replay of a chunk writes the same result. MERGE is a sketch you can defend for a single worker that already holds the chunk key. It has sharp edges with concurrency and triggers, so you are equally happy to write an UPDATE of the matching rows and an INSERT of the missing ones. Say that you will review the plan either way. The API's product read can see a chunk as soon as that chunk commits. That is acceptable for a nightly catalog load. If the business wants all-or-nothing visibility, you load into a staging table and swap a partition or flip a version column at the end. That is a bigger mechanism. You name it only if they ask for a point-in-time cutover. The default you ship is chunk-at-a-time visibility and a file status that says Processing until the last chunk lands."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "A bad line is a FileErrors row, not a failed file. The rest of the chunk commits. A poison chunk, meaning a bug or a data shape that throws every time, dead-letters that chunk message. The other chunks continue. The file status stays Processing until a completion check sees the gap, then it becomes CompletedWithErrors or Failed, and the status payload lists the missing range. An alert fires if the file is not terminal by the deadline. A retry of a successful chunk does not double-insert, because of the chunk key and the idempotent upsert. A function timeout, whatever the current number is for the plan, is handled by making the chunk smaller, not by raising the timeout until a million-row parse fits."},
        {"t": "p", "text": "The shared database can still stall the API if a chunk escalates locks or floods the log. You start with short transactions, row locks, a staging schema, and a worker identity. If you measure lock waits on the order workload during the window, you move staging to its own database. You do not start with a second server because a diagram had two cylinders. You also do not run the import on the App Service request thread."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "Blob created raises an Event Grid event, or a small function notices the blob. That function inserts ingest.Files and enqueues one control message. It does not read the million rows. A splitter reads the blob only far enough to emit chunk messages: file id, blob name, row start, row count. Workers on the isolated worker pull from a Service Bus queue, peek-lock, and complete after the chunk transaction commits. The worker's managed identity can read the container and write the ingest and catalog tables it owns. It cannot alter. It is not app_orders_runtime. The API identity can select file status and errors for the tenant. The dashboard is files not terminal, dead-letter depth on the chunk queue, and SQL lock waits during the window. You prove the retry on a small file before you talk about the million."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse to parse the file in the blob trigger. You refuse EF per row. You refuse one transaction for the whole file. You refuse to stop the other 99 chunks because one chunk is poison. You refuse to give the worker the API's SQL login. You refuse a second database until a measurement says the shared log or the shared locks are the problem."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """public sealed record FileChunkMessage(Guid FileId, string BlobName, int RowStart, int RowCount);

[Function("RegisterFile")]
public async Task Register([EventGridTrigger] EventGridEvent evt, CancellationToken ct)
{
    // Insert ingest.Files as Received and send one control message.
    // Do not open the CSV here.
}

[Function("ImportChunk")]
public async Task Import(
    [ServiceBusTrigger("file-chunks", Connection = "ServiceBus")]
    ServiceBusReceivedMessage message,
    ServiceBusMessageActions actions,
    CancellationToken ct)
{
    var chunk = JsonSerializer.Deserialize<FileChunkMessage>(message.Body);
    if (chunk is null)
    {
        await actions.DeadLetterMessageAsync(message, deadLetterReason: "BadPayload");
        return;
    }

    if (await ChunkExists(chunk.FileId, chunk.RowStart, ct))
    {
        await actions.CompleteMessageAsync(message);
        return;
    }

    await using var tx = await _db.Database.BeginTransactionAsync(ct);
    await BulkUpsertRange(chunk, ct); // set-based, idempotent on (TenantId, Sku)
    _db.FileChunks.Add(new FileChunk(chunk.FileId, chunk.RowStart, chunk.RowCount));
    await _db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
    await actions.CompleteMessageAsync(message);
}"""},
        {"t": "p", "text": "Turn auto-complete off for that function when you settle the message yourself, or you will complete twice and throw. host.json on the isolated worker is where that flag lives. A transient SQL failure should throw or abandon, not dead-letter. A payload you cannot parse should dead-letter on the first try. Bulk upsert can be a bulk copy into ProductBatch for that file and range, then an UPDATE plus an INSERT into catalog.Products, then a delete of the staged rows, all in the chunk transaction. The sketch name BulkUpsertRange is the boundary. You do not need the bulk-copy API on the whiteboard unless they ask. You do need to say it is set-based."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. A million rows is the file. 5,000 is the chunk size you will tune. The API latency assumption does not move.",
            "Minute 2 to 5. The API only reads status and errors. The file lands in the container.",
            "Minute 5 to 9. Register, split, work. The register function does not parse. The queue carries ranges.",
            "Minute 9 to 13. One transaction per chunk, set-based upsert, unique (FileId, RowStart), bad lines in FileErrors.",
            "Minute 13 to 16. A poison chunk dead-letters. The other chunks continue. The file status shows the gap. Alert on the deadline.",
            "Minute 16 to 20. Separate managed identity, short locks, no Migrate, no import on the request thread. A second database only after you measure lock waits. Prove retry on a small file.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Reading the whole blob in the trigger and retrying from byte zero after a timeout. SaveChanges per row. A chunk retry with no range key, so the million rows double. A poison chunk that fails the orchestrator and leaves the rest unprocessed. Sharing the API's SQL login with the worker. Quoting a function timeout from memory and building the design around that fiction."},
        {"t": "lead", "title": "Say this", "text": "The trigger records the file. Workers own chunks. Each chunk commits with a unique range key and a set-based upsert. Bad rows are queryable. A poison chunk dead-letters without stopping the others. The API only reads status, and the worker has its own identity. I look up the function timeout and I size the chunk under it."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 5 — Multi-tenant SaaS"},
        {"t": "p", "text": "Outcome. You can put many tenants in one Azure SQL database safely, and you can say the specific condition under which one tenant gets a database of its own."},
        {"t": "p", "text": "Time box. About 3.5 hours. Write the filter and the unique index from memory. Write the cross-tenant test in words until the expected status code is 404. Then the dedicated-database story, including the migration cost, in under five minutes. The twenty-minute clock is the last hour, twice."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "The order API is becoming a SaaS product. Many customers share it. Design the tenancy. The panel wants to know both the default and the escape hatch. They will try to get you to start from a database per tenant. Do not."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "Hundreds of small tenants, one team, the same order assumptions until a tenant actually arrives with volume. No tenant has a contractual residency requirement yet. You have not measured a noisy neighbor. If either of those becomes true, the escape hatch applies to that tenant, not to all of them. The tenant id comes from the Entra token, a claim you issued at provisioning, not from the body and not from a route value the caller can edit. A route that includes a tenant slug is fine as a hint, and the token still wins when they disagree."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "The URLs stay /orders and /products. The tenant is ambient, from the token. A body field named tenantId is ignored. An admin API, if you need one, is a separate role and a separate policy, and it still takes the tenant as an explicit argument the admin is allowed to pass, checked against an allow list, not as a silent override on the customer route. GET of another tenant's id returns 404. POST that would write another tenant's id writes the token's tenant instead, or it returns 400 if you would rather reject the mismatched body. Pick one and test it. Ignoring the field is the choice that matches the rest of this guide."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE UNIQUE INDEX UX_Orders_Tenant_Number
    ON orders.Orders (TenantId, Number);

-- Every tenant-owned table has TenantId.
-- Every unique business key includes TenantId.
-- The leading column of the hot index is TenantId.

CREATE TABLE tenants.Directory
(
    TenantId    uniqueidentifier NOT NULL CONSTRAINT PK_Directory PRIMARY KEY,
    Name        nvarchar(200)    NOT NULL,
    DatabaseKey nvarchar(64)     NOT NULL  -- 'shared', or a dedicated key
);"""},
        {"t": "p", "text": "DatabaseKey names a connection. The connection string itself lives in Key Vault or in an app setting the managed identity can read. It does not live in the directory table. Most rows say shared. A dedicated key points at that tenant's database. The application resolves the connection per request after it knows the tenant, and the DbContext is scoped to the request."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "Inside one tenant, Day 2's transaction is unchanged. Across tenants there is no transaction, because there is no cross-tenant business operation in this product. A global query filter is a safety net. It is not the only control. The authorization policy checks the caller. The query takes the tenant from the context. A test proves the cross-tenant read fails. Raw SQL bypasses the filter, and IgnoreQueryFilters bypasses it. A review rule says a raw SQL string names TenantId in the predicate, and a worker that has no ambient tenant must set one on purpose."},
        {"t": "p", "text": "Row-level security in Azure SQL is the extra net if you want the engine to enforce the tenant even when a query forgets the predicate. The session context is set when the connection opens, from the same tenant id as the filter. A bug that sets the wrong context and a bug that trusts the body are still bugs you test for. RLS does not replace the token. A background worker has no user token. It sets the session context from the message, which carries the tenant id that was written at commit time, and it uses a SQL login that is still not a database owner."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "The failure you design for is a cross-tenant read or write. The status code is 404 on the read. The test uses tenant A's token and tenant B's order id. The failure you operate is a noisy neighbor: lock waits or CPU that you can show on one tenant's queries. You do not guess a DTU or a vCore number in the interview. You say you would look at Query Store and the resource metrics, and a tenant who shows up there is a candidate for a dedicated database. A missed migration on that dedicated database is a drift incident. That is the failure mode of the escape hatch, and you name it before you offer the hatch."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "One Azure SQL database is the default, with the tenant column, the filter, the index, and the test. Backups restore everyone together, which is acceptable until a tenant needs their own restore point. The pipeline applies migrations to the shared database and, when dedicated databases exist, to each of them. A inventory of DatabaseKey values is part of the release. The app identity can read the directory and can touch tenant data only through the runtime role. Provisioning a tenant is an insert in the directory and an Entra app registration or an app role assignment, done by a workflow, not by a row somebody typed in production."},
        {"t": "p", "text": "Moving one tenant out is a copy, a catch-up, and a cutover. You can put the tenant in a read-only window, copy the rows, apply the migrations to the new database, point Directory.DatabaseKey at the new key, and then allow writes. Dual-write is the alternative if you cannot take the window, and it is more moving parts than this scale needs. You say which one you would run. You do not build a shard map for hundreds of small tenants on the first drawing."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse a database per tenant as the default. You would multiply every migration, every connection leak, and every forgotten index by the tenant count, and the team is one team with hundreds of small customers. You refuse to trust the body. You refuse a unique index on the order number alone, because numbers then collide across tenants or, if you catch the collision, you leak that a number exists. You refuse to let the filter be the only control."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """public sealed class OrdersDbContext : DbContext
{
    private readonly ITenantContext _tenant;
    public Guid TenantId => _tenant.TenantId;

    public OrdersDbContext(DbContextOptions<OrdersDbContext> options, ITenantContext tenant)
        : base(options)
    {
        _tenant = tenant;
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>().HasQueryFilter(o => o.TenantId == TenantId);
        modelBuilder.Entity<Order>().Property(o => o.RowVersion).IsRowVersion();
        modelBuilder.Entity<Order>().HasIndex(o => new { o.TenantId, o.Number }).IsUnique();
    }
}

-- Optional engine-side net. The app still sets the tenant from the token.
CREATE OR ALTER FUNCTION orders.fn_tenant(@TenantId uniqueidentifier)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS ok
    WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS uniqueidentifier);"""},
        {"t": "p", "text": "The filter reads a property on the context so EF evaluates the current tenant per query. A scoped DbContext and a scoped tenant context are required. A singleton context would pin the first tenant and would also be illegal for EF's lifetime rules. The connection interceptor that sets SESSION_CONTEXT runs when the connection opens, with a parameter, not with the tenant id concatenated into the SQL text."},
        {"t": "code", "text": """[Fact]
public async Task Tenant_a_cannot_read_tenant_b()
{
    Guid id = await SeedOrder(tenantB);
    using var scope = factory.WithToken(tenantA);
    HttpResponseMessage response = await scope.Client.GetAsync($"/orders/{id}");
    Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
}"""},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. Hundreds of small tenants, one team, no residency clause yet, token wins over the body.",
            "Minute 2 to 5. URLs do not take a tenant from the caller. 404 hides the other tenant. Admin is a separate policy.",
            "Minute 5 to 9. TenantId on every table, unique keys include it, hot indexes lead with it, directory row points at shared.",
            "Minute 9 to 13. Filter plus authorization plus a test. Raw SQL is a review rule. RLS is the extra net, session context set from the same id.",
            "Minute 13 to 16. Noisy neighbor is a measurement, not a guess. Dedicated database is that tenant only.",
            "Minute 16 to 20. The cost of the hatch: a migration per database, a cutover, drift if you miss one. You refuse the hatch as the default.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Trusting tenantId from JSON. A unique index on Number alone. Returning 403 for another tenant's id and confirming the row exists. A singleton DbContext. Believing the query filter covers FromSqlRaw. Starting from a database per tenant because a slide said isolation. Quoting a vCore number you do not have."},
        {"t": "lead", "title": "Say this", "text": "One Azure SQL database. TenantId comes from the token. The unique index and the hot index include it. A filter, a policy, and a cross-tenant test that expects 404. A dedicated database is a named exception for residency or for a neighbor I measured, and every migration then runs once per database."},
        {"t": "break"},
    ]
