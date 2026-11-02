# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 5 — SQL Server, query performance, and database roles"},
        {"t": "p", "text": "Day 5 is the hour after the API looks fine and the database does not. A lead does not have to be the DBA. A lead has to read a plan, choose an index with a write cost, explain why two sessions blocked, and refuse db_owner for the application login. The examples use one orders schema."},

        {"t": "h2", "text": "Clustered index, nonclustered index, and key lookup"},
        {"t": "p", "text": "A clustered index is the table. The leaf pages are the rows, stored in clustering-key order. A table has one clustered index. Every nonclustered index stores its own key plus the clustering key, so a wide clustering key is copied into every secondary index. A narrow, ever-increasing key such as a bigint identity keeps inserts at the end of the leaf. A random uniqueidentifier as the clustered key scatters inserts and fragments the leaf."},
        {"t": "p", "text": "A nonclustered index is a separate structure. A seek jumps to a range. A scan reads all or most of the leaf. A scan is not automatically bad on a small table. A seek is not automatically good if it then does a million key lookups. INCLUDE puts extra columns on the nonclustered leaf so the query can be covered and skip the lookup. Every included column slows writes and grows the index, so you cover the hot query, not every column in the table."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE TABLE orders.Orders
(
    Id         bigint IDENTITY(1,1) NOT NULL,
    TenantId   int                  NOT NULL,
    CreatedUtc datetime2            NOT NULL,
    Status     nvarchar(32)         NOT NULL,
    Total      decimal(18,2)        NOT NULL,
    CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (Id)
);

-- Hot list: tenant, newest first, showing status and total.
CREATE NONCLUSTERED INDEX IX_Orders_Tenant_Created
    ON orders.Orders (TenantId, CreatedUtc DESC, Id DESC)
    INCLUDE (Status, Total);

-- A lookup by business number. The clustering key Id rides along for free.
CREATE UNIQUE NONCLUSTERED INDEX UX_Orders_Tenant_Number
    ON orders.Orders (TenantId, Number);"""},
        {"t": "p", "text": "SELECT Id, Status, Total FROM orders.Orders WHERE TenantId = 10 AND CreatedUtc < @cursor seeks the nonclustered index and returns from the leaf because Status and Total are included. Drop the INCLUDE and the same query seeks, then key-looks up into the clustered index once per row. A few lookups are noise. Lookups for tens of thousands of rows dominate the plan. SELECT * also defeats the covering index, because the star includes columns that are not in the leaf."},
        {"t": "warn", "title": "What breaks", "text": "An index that makes the report fast can slow the insert path the business cares about more. A random GUID clustered key fragments the table as it grows. Adding an index without a plan on production-like data is a guess."},
        {"t": "lead", "title": "Say this", "text": "Clustered is the row order. Nonclustered is a second path, with the clustering key attached. INCLUDE covers the hot select list. I ask for the actual plan before I add the index, and I name the write I might slow down."},

        {"t": "h2", "text": "SARGable predicates, seeks, and scans"},
        {"t": "p", "text": "SARGable means the column stands alone so the optimizer can seek: column equals a value, column is greater than a value, column is in a small list. A function on the column hides it. YEAR(CreatedUtc) = 2026 cannot seek CreatedUtc, because every row's year has to be computed. Put the function on the constant, or write a range. A leading-wildcard LIKE also hides the column. A trailing wildcard can seek."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Not SARGable. The index on CreatedUtc cannot seek.
SELECT Id FROM orders.Orders WHERE YEAR(CreatedUtc) = 2026;

-- SARGable. A range seek.
SELECT Id
FROM orders.Orders
WHERE CreatedUtc >= '2026-01-01'
  AND CreatedUtc <  '2027-01-01';

-- Not SARGable. The conversion is on the column.
SELECT Id FROM orders.Orders WHERE CONVERT(date, CreatedUtc) = @day;

-- SARGable. The bounds are on the parameter side.
SELECT Id
FROM orders.Orders
WHERE CreatedUtc >= @day
  AND CreatedUtc <  DATEADD(day, 1, @day);"""},
        {"t": "p", "text": "EF Core produces the non-SARGable form when you write o => o.CreatedUtc.Year == 2026. Write a range in the LINQ instead. The same rule applies to o.Email.ToLower() == email. A case-insensitive collation already compares without the function, and the function blocks the seek."},
        {"t": "warn", "title": "What breaks", "text": "The query is correct and the index exists, and the plan still scans because the predicate wrapped the column. Scaling the App Service runs the scan more often. It does not make the predicate SARGable."},
        {"t": "lead", "title": "Say this", "text": "I keep the column bare on the left of the predicate. I put the function on the constant. If the plan scans a large table, I look at the predicate before I look at the instance count."},

        {"t": "h2", "text": "Statistics, Query Store, and a procedure that is slow for one customer"},
        {"t": "p", "text": "The optimizer estimates cardinality from statistics. A big load that does not update stats produces a bad estimate and a bad plan. Parameter sniffing is the related trap: SQL compiles a plan for the first parameter values it sees and caches that plan. A plan compiled for a tenant with 20 orders is reused for a tenant with 2 million, or the reverse. The API sees one customer as slow and the others as fine."},
        {"t": "p", "text": "Work the problem from the statement, the parameters, and the duration. Query Store on Azure SQL keeps plans and runtime stats so you can compare the actual plan with the estimate. Look for a scan where a seek should be, a huge gap between estimated and actual rows, a key-lookup storm, or a spill. Update statistics if a load invalidated them. Fix the query or the index first. A hint, OPTIMIZE FOR, or a plan guide is a pin you can name and a person who will remove it. A local variable copied from the parameter is an old way to hide the sniffed value, and it has its own estimate. Confirm with the plan before you sprinkle hints."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE OR ALTER PROCEDURE orders.ListByTenant
    @TenantId int
AS
SELECT Id, Status, Total
FROM orders.Orders
WHERE TenantId = @TenantId;
-- Compiled for tenant 1 (12 rows): a seek plus lookups may be fine.
-- Reused for tenant 40 (1.8 million rows): the same plan thrashes.
-- First evidence is Query Store: one query id, two parameter sets, two durations.
-- Also check blocking. A fast query waiting on a lock looks slow in the API
-- and innocent when you run it alone."""},
        {"t": "p", "text": "The API symptom is a latency chart for one route. The SQL symptom is a plan, a wait, or a lock. Do not scale out the App Service to hide a scan. More instances run the bad query more often and can exhaust the SQL connection or CPU budget."},
        {"t": "warn", "title": "What breaks", "text": "A hint with no owner stays after the data shape changes and becomes the next incident. OPTION (RECOMPILE) on a query that runs 50 times a second spends CPU compiling. A local-variable trick that 'fixed' sniffing also threw away a good estimate for the common tenant."},
        {"t": "lead", "title": "Say this", "text": "I capture the statement, the parameters, and the plan. I fix the SARGable predicate or the index first. I pin a plan only when I can name the plan and the person who will remove the pin. I do not scale the API to hide a scan."},

        {"t": "h2", "text": "Isolation, RCSI, and when readers block writers"},
        {"t": "p", "text": "ACID is the transaction contract: atomicity, consistency, isolation, durability. Isolation is the one panels probe. Under locking READ COMMITTED, a reader takes shared locks and a writer takes exclusive locks, so they block each other. READ COMMITTED SNAPSHOT keeps statement-level read committed semantics and serves the previous row version, so a reader does not take the shared locks that block the writer. Writers still block writers on the same row. SNAPSHOT isolation is transaction-level: the transaction sees the database as of its start, and a write can fail with an update conflict if another transaction changed the row."},
        {"t": "p", "text": "Both versioning options use a version store. On modern Azure SQL that store is often under accelerated database recovery, not the old tempdb picture, so say you would confirm the setting rather than recite a tempdb myth. RCSI does not make a read-modify-write safe. Two transactions can still read a balance, add one, and write back. That lost update needs a concurrency token or an atomic UPDATE, which is Day 4."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Confirm before you recommend it. This is a database change, not a connection flag.
SELECT is_read_committed_snapshot_on, snapshot_isolation_state_desc
FROM sys.databases
WHERE name = DB_NAME();

ALTER DATABASE CURRENT SET READ_COMMITTED_SNAPSHOT ON;

-- Still a lost update under RCSI. Both sessions read 10 and both write 11.
-- Fix: UPDATE orders.Orders SET Total = Total + @delta WHERE Id = @id;
-- or a rowversion token so the second writer gets zero rows and the API returns 409."""},
        {"t": "warn", "title": "What breaks", "text": "Turning RCSI on during an outage without a test plan changes locking behavior for every query. Versioning is not free. RCSI does not replace a unique constraint or a concurrency token. SNAPSHOT can start failing writes with conflicts the application never handled."},
        {"t": "lead", "title": "Say this", "text": "Locking read committed lets readers and writers block. RCSI serves readers from row versions so they do not block writers. Writers still block writers. I confirm the current setting, and I still use a concurrency token for lost updates."},

        {"t": "h2", "text": "Deadlocks"},
        {"t": "p", "text": "A deadlock is a cycle of locks. Session A holds row 1 and wants row 2. Session B holds row 2 and wants row 1. SQL detects the cycle and kills one session with error 1205. The victim can retry when the work is idempotent and the EF execution strategy includes 1205. The lasting fix is a consistent lock order, a shorter transaction, and an index that stops a query from locking a wider range than it needs."},
        {"t": "p", "text": "Read the deadlock graph: the processes, the resources, the statements. Deadlocks come from an ORM that updates every column and takes locks in an order nobody wrote down, from triggers that lock a second table, and from two procedures that touch Orders and Payments in opposite orders. A retry that succeeds without a graph is how the same deadlock stays for a year. Put a metric on 1205. A rising retry rate is a design ticket even when the customer eventually gets a 200."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Session A
BEGIN TRAN;
UPDATE orders.Orders   SET Status = 'Paid' WHERE Id = 10;  -- locks order 10
UPDATE orders.Payments SET Status = 'Paid' WHERE Id = 88;  -- waits on session B

-- Session B, opposite order
BEGIN TRAN;
UPDATE orders.Payments SET Status = 'Paid' WHERE Id = 88;  -- locks payment 88
UPDATE orders.Orders   SET Status = 'Paid' WHERE Id = 10;  -- waits on session A
-- SQL kills one with 1205.

-- The rule: every transaction touches Orders, then Payments, then Inventory.
-- And the transaction does not stay open across an HTTP call to the card processor."""},
        {"t": "warn", "title": "What breaks", "text": "Retrying a non-idempotent charge doubles the charge. A missing index turns a point update into a scan that locks far more rows and creates cycles you did not design. Holding the transaction while you call a payment API makes the window long enough for the cycle to form."},
        {"t": "lead", "title": "Say this", "text": "1205 is a lock cycle. I retry only if the work is safe to repeat, then I read the graph and remove the cycle with one lock order, shorter transactions, and the index that stops the extra locks."},

        {"t": "h2", "text": "Keyset pagination versus offset"},
        {"t": "p", "text": "Offset pagination is ORDER BY plus OFFSET and FETCH. It is simple and fine for a small admin page. For a deep page, SQL reads and discards the skipped rows, so page 400 costs more than page 1. Inserts at the top also shift rows, so the user sees a duplicate or a skip. Keyset pagination remembers the last key the client saw and asks for the next rows beyond that key. The client sends a cursor, not a page number. The index matches the ORDER BY."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Offset. Fine for a small screen. Deep pages get slower, and the page moves.
SELECT Id, CreatedUtc, Status, Total
FROM orders.Orders
WHERE TenantId = @TenantId
ORDER BY CreatedUtc DESC, Id DESC
OFFSET @Skip ROWS FETCH NEXT @Take ROWS ONLY;

-- Keyset. @CursorUtc and @CursorId are the last row of the previous page.
-- The first page passes a cursor beyond any real row, or omits the predicate.
SELECT TOP (@Take) Id, CreatedUtc, Status, Total
FROM orders.Orders
WHERE TenantId = @TenantId
  AND (
        CreatedUtc < @CursorUtc
        OR (CreatedUtc = @CursorUtc AND Id < @CursorId)
      )
ORDER BY CreatedUtc DESC, Id DESC;"""},
        {"t": "p", "text": "The matching index is (TenantId, CreatedUtc DESC, Id DESC) INCLUDE (Status, Total), the same one from the lookup section. Cap @Take. If an admin UI must jump to page 400, say the cost out loud or filter harder so the page number sits inside a small set. Align the API with the SQL. A cursor in the contract on day one avoids a breaking change later. The Day 3 API section uses the same cursor."},
        {"t": "warn", "title": "What breaks", "text": "An ORDER BY that does not match the index turns the keyset into a sort of a large set. A cursor that omits the tie-breaker Id skips or repeats rows that share a timestamp. An uncapped page size is an incident when one tenant asks for a million rows."},
        {"t": "lead", "title": "Say this", "text": "Offset is for small pages. Keyset seeks from the last key and stays stable. I design the cursor into the API, cap the page, and match the index to the order."},

        {"t": "h2", "text": "Who the application connects as"},
        {"t": "p", "text": "SQL Server has server roles and database roles. The tech-lead answer is least privilege for each identity. db_owner can do everything in the database. db_ddladmin can change schema. db_datareader reads every table. db_datawriter modifies every table. Those built-in roles are broad. A lead creates a custom role and grants at schema or object level."},
        {"t": "p", "text": "On Azure SQL the API uses a managed identity. You create a user from that identity and add it to the runtime role. There is no SQL password in the connection string. The connection uses Authentication=Active Directory Managed Identity, or the Microsoft.Data.SqlClient equivalent your platform standardizes on. Humans use their own accounts through a group, with auditing. A shared sa password in a wiki is a finding, not a convenience."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE ROLE app_orders_runtime AUTHORIZATION dbo;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::orders TO app_orders_runtime;
GRANT EXECUTE ON SCHEMA::orders TO app_orders_runtime;
ALTER ROLE app_orders_runtime ADD MEMBER [id-api-prod];

CREATE ROLE app_orders_migrator AUTHORIZATION dbo;
GRANT ALTER ON SCHEMA::orders TO app_orders_migrator;
-- Pipeline identity only. Never the App Service.

CREATE ROLE app_orders_reader AUTHORIZATION dbo;
GRANT SELECT ON SCHEMA::orders TO app_orders_reader;
-- Reporting. No INSERT, no UPDATE."""},
        {"t": "table", "headers": ["Identity", "May do", "Must not do"], "rows": [
            ["API runtime", "DML and EXECUTE on the orders schema", "DDL, db_owner, other databases"],
            ["Function worker", "Only the tables and procedures that worker uses", "Reuse the API role by habit"],
            ["Migration pipeline", "DDL during release", "Be the login the site uses all day"],
            ["Reporting reader", "SELECT on views or a schema", "Write"],
            ["Human admin", "Their own audited account", "A shared sa password"],
            ["Local developer", "More rights on a dev database", "Those rights copied into production"],
        ]},
        {"t": "p", "text": "A new table with no grant fails safely when the runtime role is custom. A new table under db_owner fails open: the app can touch audit and payment tables nobody reviewed. Review grants in the migration PR. db_datareader plus db_datawriter is a stepping stone you can explain, and it is broader than you want."},
        {"t": "warn", "title": "What breaks", "text": "Startup Migrate plus db_owner is two problems: many instances racing DDL, and a runtime that can drop tables. A worker that shares the API role can update tables the worker was never meant to touch. A password in app settings will leak into a log or a slot swap."},
        {"t": "lead", "title": "Say this", "text": "The API is a managed identity in a custom runtime role: DML and EXECUTE on its schema, not db_owner. A different identity migrates. If the panel says db_owner is fine because the app migrates at startup, I split both the identity and the job."},

        {"t": "h2", "text": "Stored procedure or EF query"},
        {"t": "p", "text": "EF is the default for an aggregate command and an ordinary filter, because the model, the migration, and the C# rule stay in one review. A procedure or a hand-written statement is justified when the plan is critical, the SQL is set-based and ugly in LINQ, or a reporting query is owned by someone who lives in Query Store. The procedure is parameterized, lives in source control, and deploys with the migration. EXECUTE on that procedure, rather than a blanket data-writer role, is the right grant when the procedure is the only write path you want to allow."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Default: the handler and EF own 'place an order'.
await db.Orders.AddAsync(order, ct);
await db.SaveChangesAsync(ct);

-- Justified: a nightly set-based expire that LINQ would load row by row.
CREATE OR ALTER PROCEDURE orders.ExpireUnpaid
    @Cutoff datetime2
AS
UPDATE orders.Orders
SET Status = 'Expired'
WHERE Status = 'Pending'
  AND CreatedUtc < @Cutoff;"""},
        {"t": "p", "text": "Moving every CRUD action into procedures splits the team and hides the rule from the people who change it. Leaving a hot report in a LINQ query nobody can tune splits the team the other way. Write the decision down so the next developer does not invent a third style."},
        {"t": "warn", "title": "What breaks", "text": "A procedure edited in production and missing from the migration drifts. A business rule that exists only in the procedure is invisible in the C# review. Three data-access styles in one service means nobody owns performance."},
        {"t": "lead", "title": "Say this", "text": "EF for the aggregate. A procedure for a hot, stable, set-based query, in source control, with EXECUTE granted to the runtime role. I write that decision once."},

        {"t": "h2", "text": "What a unique constraint does that C# cannot"},
        {"t": "p", "text": "Two API instances can both check that an email is free and both insert. The check in C# is not atomic across processes. A unique index is. Use one for business identity: an idempotency key, an external reference per tenant, one active subscription. Catch the unique violation and return 409. Validate early for a friendly message, and still accept that the database is the authority under concurrency. A filtered unique index enforces uniqueness only for the rows that match the filter, which is what you want when a soft-deleted email should not block a new signup."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE UNIQUE INDEX UX_Idempotency
    ON orders.IdempotencyKeys (TenantId, KeyValue);

CREATE UNIQUE INDEX UX_Customer_Email_Active
    ON customers.Customers (TenantId, Email)
    WHERE DeletedUtc IS NULL;

-- In the handler, a duplicate key becomes 409.
// catch (DbUpdateException ex) when (SqlServerException.IsUniqueViolation(ex))
//     return Results.Conflict();"""},
        {"t": "warn", "title": "What breaks", "text": "Check-then-act in the controller creates two charges or two users under retry. A unique index that includes soft-deleted rows blocks a legitimate re-create. Catching every DbUpdateException and returning 409 hides a real bug such as a truncated column."},
        {"t": "lead", "title": "Say this", "text": "If two instances can both pass the if, the rule belongs in a unique index. I still validate early. I return 409 only for the violation I meant to catch."},

        {"t": "h2", "text": "Waits worth naming"},
        {"t": "p", "text": "You do not need every wait type. You need to name the one on the screen, ask for the blocker or the plan, and connect it to a decision in the API."},
        {"t": "table", "headers": ["Wait", "What it usually means", "What you do"], "rows": [
            ["CXPACKET / CXCONSUMER", "Parallel workers coordinating. Not automatically a problem.", "Look for a skewed parallel plan before you disable parallelism."],
            ["PAGEIOLATCH", "Waiting to read a page. Often a scan or a cold cache.", "Find the scan. Do not add API instances."],
            ["LCK_M_*", "Waiting on a lock.", "Find the blocker and the transaction that is still open."],
            ["WRITELOG", "Waiting on the log flush.", "Shorten transactions. Stop chatty commits inside a loop."],
            ["RESOURCE_SEMAPHORE", "A memory grant is queued. A large sort or hash.", "Reduce the sort, or match an index so the sort goes away."],
            ["SOS_SCHEDULER_YIELD", "CPU is busy.", "The query is burning CPU, or the database is. Check the plan's CPU, not only duration."],
        ]},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """-- Who is blocking whom. The waiter is the symptom. The blocker is the decision.
SELECT r.session_id AS waiter, r.wait_type, r.wait_time,
       r.blocking_session_id AS blocker
FROM sys.dm_exec_requests r
WHERE r.blocking_session_id <> 0;"""},
        {"t": "warn", "title": "What breaks", "text": "Tuning the waiter while the blocker holds a transaction open across an HTTP call fixes nothing. Disabling parallelism because CXPACKET appeared once can make a large report slower."},
        {"t": "lead", "title": "Say this", "text": "I name the wait, then I ask for the blocker or the plan. Lock waits send me to the open transaction. IO and CPU waits send me to the scan, not to a bigger App Service."},
        {"t": "break"},
    ]
