# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "SQL questions and sample queries"},
        {"t": "p", "text": "The panel is not asking you to be the DBA. They are asking you to read a plan, pick an index with a write cost, and write a predicate that stays inside one tenant. The schema below completes the Orders example so the statements in this section have somewhere to land. Confirm the plan on your own SQL Server or Azure SQL before you argue about row counts. This guide explains the shape. It does not ship a result grid."},

        {"t": "h2", "text": "Schema"},
        {"t": "p", "text": "Orders is clustered on a bigint identity. That key is narrow and ever-increasing, so inserts land at the end of the leaf. TenantId is on every tenant-owned row. The hot list index matches the API keyset: tenant, then CreatedUtc, then Id, with the columns the list paints included at the leaf. The idempotency primary key is the business guarantee the scale section relies on."},
        {"t": "code", "text": """CREATE TABLE orders.Tenants
(
    TenantId int           NOT NULL,
    Name     nvarchar(200) NOT NULL,
    CONSTRAINT PK_Tenants PRIMARY KEY CLUSTERED (TenantId)
);

CREATE TABLE orders.Customers
(
    CustomerId  int IDENTITY(1,1) NOT NULL,
    TenantId    int               NOT NULL,
    Email       nvarchar(320)     NOT NULL,
    DisplayName nvarchar(200)     NOT NULL,
    DeletedUtc  datetime2(3)      NULL,
    CONSTRAINT PK_Customers PRIMARY KEY CLUSTERED (CustomerId),
    CONSTRAINT FK_Customers_Tenants FOREIGN KEY (TenantId) REFERENCES orders.Tenants (TenantId)
);

CREATE UNIQUE INDEX UX_Customers_Tenant_Email_Active
    ON orders.Customers (TenantId, Email)
    WHERE DeletedUtc IS NULL;

CREATE TABLE orders.Orders
(
    Id         bigint IDENTITY(1,1) NOT NULL,
    TenantId   int                  NOT NULL,
    CustomerId int                  NOT NULL,
    Number     nvarchar(40)         NOT NULL,
    Status     nvarchar(32)         NOT NULL,
    CreatedUtc datetime2(3)         NOT NULL,
    Total      decimal(18, 2)       NOT NULL,
    RowVersion rowversion           NOT NULL,
    CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (Id),
    CONSTRAINT FK_Orders_Tenants FOREIGN KEY (TenantId) REFERENCES orders.Tenants (TenantId),
    CONSTRAINT FK_Orders_Customers FOREIGN KEY (CustomerId) REFERENCES orders.Customers (CustomerId)
);

CREATE NONCLUSTERED INDEX IX_Orders_Tenant_Created
    ON orders.Orders (TenantId, CreatedUtc DESC, Id DESC)
    INCLUDE (Status, Total, CustomerId, Number);

CREATE UNIQUE INDEX UX_Orders_Tenant_Number
    ON orders.Orders (TenantId, Number);

CREATE TABLE orders.OrderLines
(
    OrderLineId bigint IDENTITY(1,1) NOT NULL,
    OrderId     bigint               NOT NULL,
    TenantId    int                  NOT NULL,
    Sku         nvarchar(40)         NOT NULL,
    Quantity    int                  NOT NULL,
    UnitPrice   decimal(18, 2)       NOT NULL,
    CONSTRAINT PK_OrderLines PRIMARY KEY CLUSTERED (OrderLineId),
    CONSTRAINT FK_OrderLines_Orders FOREIGN KEY (OrderId) REFERENCES orders.Orders (Id)
);

CREATE NONCLUSTERED INDEX IX_OrderLines_Order
    ON orders.OrderLines (TenantId, OrderId)
    INCLUDE (Sku, Quantity, UnitPrice);

CREATE TABLE orders.IdempotencyKeys
(
    TenantId     int              NOT NULL,
    KeyValue     uniqueidentifier NOT NULL,
    RequestHash  binary(32)       NOT NULL,
    OrderId      bigint           NULL,
    StatusCode   int              NOT NULL,
    CreatedUtc   datetime2(3)     NOT NULL,
    CONSTRAINT PK_IdempotencyKeys PRIMARY KEY CLUSTERED (TenantId, KeyValue)
);

CREATE TABLE orders.IdempotencyRejections
(
    RejectionId bigint IDENTITY(1,1) NOT NULL,
    TenantId    int              NOT NULL,
    KeyValue    uniqueidentifier NOT NULL,
    RequestHash binary(32)       NOT NULL,
    RejectedUtc datetime2(3)     NOT NULL,
    CONSTRAINT PK_IdempotencyRejections PRIMARY KEY CLUSTERED (RejectionId)
);

CREATE INDEX IX_IdempotencyRejections_Key
    ON orders.IdempotencyRejections (TenantId, KeyValue, RejectedUtc);"""},
        {"t": "p", "text": "The list index is the one the deep dive already uses, with CustomerId and Number added to the include list so the queries in this companion can be covered. Every included column is a write cost. Cover the list and the date-range report. Do not INCLUDE every future column because it might be selected."},

        {"t": "h2", "text": "Words you need before the questions"},
        {"t": "p", "text": "A seek jumps into the index at the first key that qualifies and stops at the end of the range. A scan reads all or most of a leaf. A scan of a tiny table is cheap. A seek that then does a key lookup per row, for a large range, can cost more than a scan. A covering index holds every column the query needs in the nonclustered leaf: the key columns, the included columns, and the clustering key, which rides along for free. The query then skips the lookup."},
        {"t": "p", "text": "SARGable means the column stands alone on one side of the predicate, so the optimizer can seek. Equality, a range, and a small IN list are the usual shapes. A function on the column, a conversion of the column, or a leading-wildcard LIKE hides the key. Put the function on the constant. A half-open range, greater than or equal to the start and less than the end, keeps the column bare."},
        {"t": "p", "text": "Under locking read committed, readers take shared locks and writers take exclusive locks, so they block each other. Read committed snapshot serves the statement a committed version of the row and readers do not take those shared locks. Writers still block writers. Snapshot isolation is a transaction-wide view as of the start, and a writer can fail with an update conflict. Both use a version store. Confirm the database setting before you recommend a change. A lost update, two sessions reading a total and both writing it back, still needs an atomic update or the RowVersion token. Versioning does not invent that for you."},
        {"t": "p", "text": "Parameter sniffing is a plan cached for the first parameter values. A plan compiled for a tenant with a dozen orders is reused for a tenant with a huge share of the table, or the reverse. Estimated versus actual rows is how you see it. Query Store is the place to look on Azure SQL. A hint is a pin with an owner and a removal date."},
        {"t": "warn", "title": "Interview trap", "text": "SELECT * pulls columns that are not in the covering leaf, so the seek grows key lookups, and the optimizer may abandon the seek for a clustered scan. A function on CreatedUtc, or an OR across unrelated columns, does the same to a seek you thought you had. NOLOCK is not the standard fix for blocking. It can return torn or missing rows. Reach for the snapshot setting you have confirmed, a shorter transaction, and an index that locks only the rows you mean."},

        {"t": "h2", "text": "Questions and answers"},
        {"t": "qa", "q": "Which index serves the tenant's newest orders, and why that column order?",
         "a": "IX_Orders_Tenant_Created on (TenantId, CreatedUtc DESC, Id DESC), including Status, Total, CustomerId, and Number. TenantId is the equality. CreatedUtc is the range and the order. Id is the tie-breaker so two orders in the same instant do not collapse. The clustered key is Id alone, which keeps inserts orderly and keeps every secondary index narrow. A nonclustered index that leads with CreatedUtc would seek a time range across every tenant and then filter, which is the wrong leading column for a multi-tenant list.",
         "lead": "Equality columns first, then the range and the ORDER BY, then INCLUDE for the select list. I say the write I slow down when I add the include."},
        {"t": "qa", "q": "What is a covering index, and what does INCLUDE cost?",
         "a": "The nonclustered leaf contains every column the query outputs and filters, so SQL seeks that index and stops. Without Status and Total in the leaf, a list of those columns seeks and then key-looks up into the clustered index once per row. INCLUDE puts Status, Total, CustomerId, and Number on the leaf without making them part of the sort key. Each included column widens the leaf and slows the insert and the update of that column. I cover the hot list. I do not cover a report that runs once a night if it doubles the write path the partner feels.",
         "lead": "I ask for the actual plan on production-like data before I add the index. An include list copied from SELECT * is how the index becomes a second copy of the table."},
        {"t": "qa", "q": "What does SARGable mean? Rewrite a filter on the year of CreatedUtc.",
         "a": "The column has to stay bare so a seek can start at a key. WHERE YEAR(CreatedUtc) = 2026 computes the year for every row and scans. The range form is CreatedUtc >= '2026-01-01' AND CreatedUtc < '2027-01-01'. The same bug in LINQ is o.CreatedUtc.Year == 2026. I write a range in the LINQ too. A trailing-wildcard LIKE can seek. A leading wildcard cannot. CONVERT(date, CreatedUtc) = @day is the same trap. I put the bounds on the parameter side: CreatedUtc >= @day AND CreatedUtc < DATEADD(day, 1, @day).",
         "lead": "If the index exists and the plan still scans, I read the predicate before I scale the App Service. More instances run the scan more often."},
        {"t": "qa", "q": "Show an implicit conversion that turns a seek into a scan.",
         "a": "Number is nvarchar. A .NET string parameter is nvarchar, so WHERE TenantId = @TenantId AND Number = @Number can seek UX_Orders_Tenant_Number. WHERE Number = 1001 compares an nvarchar column to an int. Int has higher type precedence, so SQL converts the column, the seek is gone, and a non-numeric Number throws. The other classic is a varchar column compared with an nvarchar parameter: nvarchar wins, the column converts, and the index on that varchar column is not seekable. I match the parameter type to the column. I do not 'fix' it by wrapping the column in CONVERT.",
         "lead": "I look at the plan's predicate for CONVERT_IMPLICIT on the column. That glyph is the scan. The C# type of the parameter is the fix."},
        {"t": "qa", "q": "A procedure is fast for one tenant and slow for another. What do you do?",
         "a": "I capture the statement, the parameters, and the duration from Query Store. I compare estimated rows with actual rows. A plan compiled for a small tenant and reused for a large one is parameter sniffing. I also check the opposite, and I check blocking, because a lock wait looks like a slow procedure when you run it alone and it is fine. I fix a non-SARGable predicate or a missing index first. OPTIMIZE FOR, a plan guide, or a targeted recompile is a pin I can name and a person who will remove. A local variable copied from the parameter hides the sniffed value and also hides a good estimate for the common tenant. OPTION (RECOMPILE) on a query at 50 requests a second spends CPU compiling. That 50 is the study assumption, not a hint license.",
         "lead": "The API symptom is one route, one tenant, bad p95. The SQL symptom is a plan. I do not scale out to hide it."},
        {"t": "qa", "q": "Compare read committed, read committed snapshot, and snapshot isolation.",
         "a": "Locking read committed: shared locks for readers, exclusive locks for writers, and they block. Read committed snapshot keeps statement-level read committed behavior and serves versions, so readers do not block writers. Writers still block each other on the same row. Snapshot isolation gives each transaction a view from its start, and a second writer can fail with a conflict it must handle. I read is_read_committed_snapshot_on before I recommend a change. Versioning uses a version store. On current Azure SQL I confirm whether accelerated database recovery holds it, and I do not recite a tempdb myth. RCSI does not make read-modify-write safe. I still update with a single statement, Total = Total + @delta, or I compare RowVersion and return 409.",
         "lead": "I name the setting we run, not the setting I wish we ran. Turning RCSI on in the middle of an outage is a database change, and it gets a test plan."},
        {"t": "qa", "q": "What is a deadlock, and what do you change after error 1205?",
         "a": "Two sessions hold locks the other needs, in a cycle. SQL kills one with 1205. The EF execution strategy may retry when the operation is idempotent. The lasting fix is one lock order in every transaction, a short transaction, and an index that stops a scan from locking a wide range. The sample later in this section is Orders then OrderLines in both sessions. I read the deadlock graph: processes, resources, statements. Triggers and an ORM that updates every column create orders of locks nobody wrote down. A retry that succeeds with no graph leaves the cycle in place. I put a metric on 1205. A rising retry count is a ticket even when the caller eventually sees 200.",
         "lead": "I retry only the safe unit of work. Then I remove the cycle. I do not hold the transaction open across the payment HTTP call, which is how the window gets long enough to hit."},
        {"t": "qa", "q": "When is a scan acceptable, and when is a seek a trap?",
         "a": "A scan of a small table, or of a range that really is most of the tenant, can be the honest plan. A seek is a trap when it performs a key lookup for every row of a large range, or when it seeks once per row from a nested loop the client caused. I look at the operator and the actual rows. I also look at the residual predicate. A seek on Id with a residual TenantId is the right plan for a point read, and it is still wrong as a security story if I forget the tenant predicate and seek only on Id.",
         "lead": "I refuse 'we need a seek' as a slogan. I want the operator, the rows, and the columns. Then I decide."},
        {"t": "qa", "q": "What do you compare on an estimated plan versus an actual plan?",
         "a": "Estimated rows against actual rows, on the same operator. A gap of orders of magnitude means statistics, a sniffed parameter, or a predicate the optimizer could not see through, often a function on the column. I also look for a spill, a lookup count, and a join type that made sense for the estimate and not for the actual. Query Store shows that on production without my running an actual plan against the live primary at the peak. An estimated plan alone has no actual rows. It is a guess I use to see the shape, and I say it is a guess.",
         "lead": "I ask for the actual numbers from Query Store. I do not approve an index from an estimated plan on an empty developer database."},
        {"t": "qa", "q": "Why is SELECT * a problem on IX_Orders_Tenant_Created?",
         "a": "The star includes RowVersion and any column we add later. Those are not in the include list, so a covering seek becomes a seek plus key lookups. If the range is large, the optimizer often scans the clustered index instead. The API also serializes columns the screen does not show, which is a payload and a privacy problem. I list Id, Number, Status, Total, CreatedUtc. That list is covered. A new column in the DTO is a deliberate include, with a write cost I mention in the review.",
         "lead": "The projection is part of the index design. SELECT * makes every future column part of the hot query without a decision."},
        {"t": "qa", "q": "When does OR defeat a seek, and when is OR still a keyset?",
         "a": "OR across different columns, Status = N'Paid' OR CustomerId = @CustomerId, on an index that leads with TenantId and CreatedUtc, gives the optimizer two predicates that index cannot satisfy together. The usual result is a scan, or a seek of the whole tenant. I rewrite that as UNION ALL of two seeks when each branch has its own index. The keyset predicate is a different OR: CreatedUtc is less than the cursor, or it is equal and Id is less. Both branches are the same ordered key. It should seek IX_Orders_Tenant_Created. I still read the plan. If that OR scans, I rewrite it as UNION ALL so each branch is an obvious range.",
         "lead": "I do not ban OR. I ban an OR I cannot point at on the plan. The keyset form stays only while the plan seeks."},
        {"t": "qa", "q": "Who should the API connect as?",
         "a": "A managed identity, mapped with CREATE USER FROM EXTERNAL PROVIDER, in a custom role that has DML and EXECUTE on the orders schema. Not db_owner, and not the pipeline identity that runs DDL. db_datareader plus db_datawriter is a stepping stone I can explain, and it covers every table, including ones this API should not touch. A new table with no grant fails safe under the custom role. Humans use their own audited accounts. The connection string uses Active Directory Managed Identity. There is no SQL password to commit.",
         "lead": "If the panel says db_owner is fine because the app migrates at startup, I split the identity and I move DDL to the pipeline. That is the answer they are scoring."},

        {"t": "h2", "text": "Sample queries"},
        {"t": "p", "text": "Each statement is the answer you would write on the board. The paragraph under it is why you think the predicate matches an index, and what you would change if the plan scans. Parameters are typed to the columns: int for TenantId, datetime2 for instants, nvarchar for Number."},

        {"t": "h3", "text": "Orders for one tenant in a date range"},
        {"t": "p", "text": "Question. Return one tenant's orders created in a half-open range, newest first, with the columns the list screen shows."},
        {"t": "code", "text": """SELECT Id, Number, Status, Total, CreatedUtc
FROM orders.Orders
WHERE TenantId = @TenantId
  AND CreatedUtc >= @FromUtc
  AND CreatedUtc <  @ToUtc
ORDER BY CreatedUtc DESC, Id DESC;"""},
        {"t": "p", "text": "TenantId is an equality on the leading key of IX_Orders_Tenant_Created. CreatedUtc is a range on the next key, and the ORDER BY matches the index direction, so the range can be read in order without a sort. Number, Status, and Total are included, and Id is the clustering key already stored in the leaf, so the select list is covered. @FromUtc inclusive and @ToUtc exclusive keeps a row that falls on the boundary in exactly one page of a report."},
        {"t": "p", "text": "The plan scans if you write YEAR(CreatedUtc) or CONVERT(date, CreatedUtc) on the column, if you omit TenantId and filter only by time, or if @TenantId arrives as nvarchar and you get a conversion you did not intend on a different column. SELECT * can turn the seek into a clustered scan once lookups dominate. A range that truly covers most of a huge tenant is a long read of that index leaf. That is a large seek range, and you say so, then you cap it or you summarize."},

        {"t": "h3", "text": "Top customers by total"},
        {"t": "p", "text": "Question. For one tenant and one date range, return the twenty customers with the highest sum of order totals."},
        {"t": "code", "text": """SELECT TOP (20)
    c.CustomerId,
    c.DisplayName,
    SUM(o.Total) AS TotalSpend,
    COUNT_BIG(*) AS OrderCount
FROM orders.Orders AS o
INNER JOIN orders.Customers AS c
    ON c.CustomerId = o.CustomerId
   AND c.TenantId = o.TenantId
WHERE o.TenantId = @TenantId
  AND o.CreatedUtc >= @FromUtc
  AND o.CreatedUtc <  @ToUtc
GROUP BY c.CustomerId, c.DisplayName
ORDER BY TotalSpend DESC;"""},
        {"t": "p", "text": "The filter is the same seek as the date-range list. Total and CustomerId are included, so the aggregate does not key-lookup the order. The join to Customers is a seek on the customer primary key, and the tenant predicate on the join refuses a customer row that does not belong to the order's tenant. GROUP BY will hash or sort the qualifying orders. That is expected. TOP (20) limits the output, not the amount of aggregation, unless the optimizer finds a cheaper ordered path. Joining OrderLines into this query multiplies Total by the line count. Keep the aggregate on Orders."},
        {"t": "p", "text": "It scans when the date predicate wraps CreatedUtc, when the query is asked for every tenant at once, or when an OR such as Status = N'Paid' OR CustomerId = @CustomerId is added on columns the index cannot serve together. A missing include of Total still seeks and then looks up. That is the plan you fix by INCLUDE, after you accept the wider leaf."},

        {"t": "h3", "text": "Find duplicate idempotency use"},
        {"t": "p", "text": "Question. Show whether an idempotency key was stored twice, and show keys that clients reused with a different body."},
        {"t": "code", "text": """-- Must return zero rows. The primary key is (TenantId, KeyValue).
-- A row here means a load path bypassed the constraint.
SELECT TenantId, KeyValue, COUNT(*) AS Uses
FROM orders.IdempotencyKeys
GROUP BY TenantId, KeyValue
HAVING COUNT(*) > 1;

-- Same key, different request hash. The API inserts this row on 409
-- and does not insert a second order.
SELECT TenantId, KeyValue, COUNT(*) AS Conflicts, MAX(RejectedUtc) AS LastSeen
FROM orders.IdempotencyRejections
GROUP BY TenantId, KeyValue
HAVING COUNT(*) >= 1;"""},
        {"t": "p", "text": "The first statement is the audit of the guarantee. The clustered primary key is the index, and a correct table cannot contain a duplicate, so the having-count query is empty. You still run it after a bulk import or a replica you built without the key. The second statement uses IX_IdempotencyRejections_Key, whose leading columns are TenantId and KeyValue, which matches the group. Those rows are the business duplicates the primary key refused: same tenant, same key, different hash."},
        {"t": "p", "text": "You get a scan of IdempotencyKeys if you drop the primary key and also have no index on (TenantId, KeyValue), or if you wrap KeyValue in a function. An empty rejection table is not proof that nobody retried. It is proof you did not log the 409. The order table's unique (TenantId, Number) is the other duplicate to ask about, with the same GROUP BY shape, when the idempotency key was fine and the business number was not."},

        {"t": "h3", "text": "A page of orders with keyset pagination"},
        {"t": "p", "text": "Question. Return the next page after a cursor, without OFFSET. The first page uses a cursor later than any real row, or omits the cursor predicate."},
        {"t": "code", "text": """SELECT TOP (@Take) Id, Number, Status, Total, CreatedUtc
FROM orders.Orders
WHERE TenantId = @TenantId
  AND (
        CreatedUtc < @CursorUtc
        OR (CreatedUtc = @CursorUtc AND Id < @CursorId)
      )
ORDER BY CreatedUtc DESC, Id DESC;"""},
        {"t": "p", "text": "This is the deep page. @Take is capped in the API, for example at 100, and you say the cap is a product choice. The predicate continues the index order: everything strictly older than the cursor instant, plus the tie on Id at that same instant. IX_Orders_Tenant_Created leads with TenantId, then CreatedUtc DESC, then Id DESC, and it includes Number, Status, and Total. The page should be a seek and a short ordered range. The cursor values are the last row the client already showed. A new insert newer than the cursor does not shift this page."},
        {"t": "p", "text": "OFFSET @Skip ROWS FETCH NEXT @Take ROWS ONLY is the form you show for a small admin screen and then refuse for a deep page. SQL reads and discards the skipped rows, and inserts at the top move the page. The keyset OR scans if the plan cannot see it as one range. The repair is UNION ALL: one branch for CreatedUtc < @CursorUtc, one branch for the equal instant and Id < @CursorId, each able to seek, with TOP applied carefully so you do not read the entire history. A cursor that omits Id repeats or skips rows that share CreatedUtc. An uncapped @Take is how one tenant asks for a million rows."},
        {"t": "code", "text": """SELECT TOP (@Take) Id, Number, Status, Total, CreatedUtc
FROM (
    SELECT Id, Number, Status, Total, CreatedUtc
    FROM orders.Orders
    WHERE TenantId = @TenantId
      AND CreatedUtc < @CursorUtc
    UNION ALL
    SELECT Id, Number, Status, Total, CreatedUtc
    FROM orders.Orders
    WHERE TenantId = @TenantId
      AND CreatedUtc = @CursorUtc
      AND Id < @CursorId
) AS page
ORDER BY CreatedUtc DESC, Id DESC;"""},

        {"t": "h3", "text": "A tenant-safe update"},
        {"t": "p", "text": "Question. Mark an order paid only if it belongs to this tenant and the caller still holds the RowVersion they read."},
        {"t": "code", "text": """UPDATE orders.Orders
SET Status = @NewStatus
WHERE TenantId = @TenantId
  AND Id = @OrderId
  AND RowVersion = @RowVersion;

-- @@ROWCOUNT = 1: updated.
-- @@ROWCOUNT = 0: read again by TenantId and Id.
--   no row  -> 404, outside this tenant or unknown id
--   a row   -> 409, someone else wrote it"""},
        {"t": "p", "text": "@TenantId comes from the token, the same way the API section requires. @OrderId comes from the route. @RowVersion is binary(8), the value the client read. The clustered primary key seeks Id. TenantId and RowVersion are residual predicates on that one row. The seek stays efficient. The tenant predicate is what makes a guessed id update zero rows. Leaving it off is fast and wrong."},
        {"t": "p", "text": "The statement scans if you update by a function of Number, or by a predicate with no selective key, such as Status = @Old across the table. Two writers who both read the total and both set a new total will lose one update even under row versioning. The RowVersion check is the lost-update control. A set-based alternative, Total = Total + @delta, is safer when the business rule is an increment. Either way the tenant predicate stays."},

        {"t": "h3", "text": "One join instead of N+1"},
        {"t": "p", "text": "Question. Load one order and its lines in a single statement. The N+1 shape is a query for the order, then a query per line, or a list call followed by a line call per order from Angular."},
        {"t": "code", "text": """SELECT o.Id, o.Number, o.Total, l.Sku, l.Quantity, l.UnitPrice
FROM orders.Orders AS o
INNER JOIN orders.OrderLines AS l
    ON l.OrderId = o.Id
   AND l.TenantId = o.TenantId
WHERE o.TenantId = @TenantId
  AND o.Id = @OrderId;"""},
        {"t": "p", "text": "Orders seeks the clustered primary key on Id and checks TenantId. OrderLines seeks IX_OrderLines_Order on (TenantId, OrderId) and returns Sku, Quantity, and UnitPrice from the include list, so the line side is covered. One round trip, one tenant predicate on both sides. If the screen needs twenty orders, filter those ids in one statement, still with TenantId, and group the lines in the API. EF's version of the same idea is a projection or Include with AsSplitQuery when several collections would multiply rows. Split query is two round trips on purpose, still constant, not one per line."},
        {"t": "p", "text": "The line side scans if the only index is the clustered OrderLineId and you filter by OrderId, once the table is large. The order side scans if you look the order up by a non-SARGable expression on Number. Joining lines when you only wanted order totals, as in the top-customers query, multiplies the sum. That is a different bug. A loop in C# that runs this statement once per order id is still N+1 at the API boundary, just with a nicer inner statement."},

        {"t": "h3", "text": "A deadlock, and the lock order that removes it"},
        {"t": "p", "text": "Question. Two sessions update an order and its lines. Show the cycle, then show the rule you enforce."},
        {"t": "code", "text": """-- Session A. Parent, then child.
BEGIN TRAN;
UPDATE orders.Orders
SET Status = N'Paid'
WHERE Id = 10 AND TenantId = 1;

UPDATE orders.OrderLines
SET Quantity = Quantity
WHERE OrderId = 10 AND TenantId = 1;
COMMIT;

-- Session B. Child, then parent. Cycle. One session dies with 1205.
BEGIN TRAN;
UPDATE orders.OrderLines
SET Quantity = Quantity + 1
WHERE OrderId = 10 AND TenantId = 1;

UPDATE orders.Orders
SET Status = N'Packed'
WHERE Id = 10 AND TenantId = 1;
COMMIT;"""},
        {"t": "p", "text": "Session A holds the order row and wants the lines. Session B holds the lines and wants the order. The fix is a rule every transaction follows: touch Orders first, then OrderLines, then anything else you must name. Keep the transaction free of HTTP. The point updates seek Id and (TenantId, OrderId), so they lock the rows they mean rather than a scanned range. The same cycle happens on one table when session A updates id 10 then id 12 and session B updates id 12 then id 10. One set-based update, or a locked order by Id, removes that cycle too."},
        {"t": "code", "text": """-- Both sessions, same order. The HTTP call to take payment stays outside.
BEGIN TRAN;
UPDATE orders.Orders
SET Status = N'Paid'
WHERE Id = @OrderId AND TenantId = @TenantId;

UPDATE orders.OrderLines
SET Quantity = Quantity
WHERE OrderId = @OrderId AND TenantId = @TenantId;
COMMIT;"""},
        {"t": "p", "text": "A missing index on the line filter turns the second update into a scan that locks many tenants' lines and creates cycles you did not draw. Retrying 1205 is allowed when the unique idempotency key makes the whole transaction safe to run again. Retrying a payment insert that has no unique key charges twice. The graph is the evidence. The metric on 1205 is how you notice the retry is hiding a design problem."},
        {"t": "warn", "title": "Interview trap", "text": "Offering NOLOCK on the read side of this bug. The deadlock is a write cycle. A dirty read does not give the two updates a single lock order. Offering a bigger App Service plan does not either. The plan runs the same two statements on more connections."},
        {"t": "lead", "title": "Say this", "text": "I write the tenant predicate on every statement, I keep the column bare so the index can seek, and I touch tables in one order. The unique key and the RowVersion token are what C# cannot guarantee across two instances."},

        {"t": "h2", "text": "A short drill"},
        {"t": "b", "numbered": True, "items": [
            "On paper, write the date-range select and name the index key columns in order.",
            "Rewrite YEAR(CreatedUtc) = 2026 so it can seek, and say what SELECT * does to that plan.",
            "Write the tenant-safe update. Say what @@ROWCOUNT of 0 means the second time you read the row.",
            "Draw two sessions deadlocking on Orders and OrderLines, then write the one order both will use.",
        ]},
        {"t": "break"},
    ]
