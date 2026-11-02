# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 4 — Entity Framework Core"},
        {"t": "p", "text": "Day 4 is the point where a clean C# method becomes a SQL statement, a lock, and a migration. A lead can say what the change tracker is for, when it is turned off, and when the team drops to SQL on purpose. The Orders API still writes one aggregate and reads a page."},

        {"t": "h2", "text": "The change tracker, and when you turn it off"},
        {"t": "p", "text": "DbContext is a unit of work and an identity map. A tracking query snapshots the entity. If you change a property, SaveChanges compares current values to the snapshot and writes an UPDATE for the columns that changed. A second query for the same key in that context returns the tracked instance, not a fresh copy from the database. That is useful while you edit an aggregate. It costs CPU and memory on a list, and a stale tracked instance can hide a change another request committed."},
        {"t": "p", "text": "AsNoTracking skips the snapshot. Use it for read endpoints. You do not update those instances later in the same context. AsNoTrackingWithIdentityResolution still returns one instance per key when a graph would otherwise duplicate a parent. Keep one context per request. Do not cache a context. Do not use one context across threads."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Command path: tracking is the feature.
Order order = await db.Orders.SingleAsync(o => o.Id == id && o.TenantId == tenantId, ct);
order.MarkPaid();
await db.SaveChangesAsync(ct);
// UPDATE orders.Orders SET Status = @p, RowVersion = ... WHERE Id = @id AND RowVersion = @original

// Read path: no snapshot.
OrderDto? dto = await db.Orders.AsNoTracking()
    .Where(o => o.Id == id && o.TenantId == tenantId)
    .Select(o => new OrderDto(o.Id, o.Number, o.Status, o.Total))
    .SingleOrDefaultAsync(ct);"""},
        {"t": "p", "text": "The command loads one aggregate, mutates it through a method that enforces the status rule, and saves. The read projects four columns and never attaches an Order. A list endpoint that tracks every column of every order pays for change detection it will never use. Project to the DTO."},
        {"t": "warn", "title": "What breaks", "text": "Updating an AsNoTracking instance and calling SaveChanges writes nothing, because the context is not watching it. A context shared across requests throws, or worse, mixes tenants. Attaching a DTO and marking every property modified overwrites columns the client did not send."},
        {"t": "lead", "title": "Say this", "text": "Tracking is for the command, where change detection is the point. Reads project and use AsNoTracking. One context per request, never across threads."},

        {"t": "h2", "text": "Include, split queries, lazy loading, and projection"},
        {"t": "p", "text": "Eager loading uses Include. One SQL statement with several collection includes multiplies rows: two lines and three shipments become six rows. AsSplitQuery runs a query per include and avoids that explosion. The split queries are not one atomic read, so a concurrent update can make the pieces disagree. Lazy loading pulls related data on property access and hides N+1. Leave it off unless a specific screen needs it and the team can see the queries in logs. Explicit loading is LoadAsync when you already have the parent and sometimes need the children. Project with Select when the caller needs a DTO. The SQL then returns the columns you named."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Cartesian explosion: lines x shipments in one result set.
var heavy = await db.Orders
    .Include(o => o.Lines)
    .Include(o => o.Shipments)
    .ToListAsync(ct);

// Separate queries. Not one atomic snapshot.
var split = await db.Orders.AsSplitQuery()
    .Include(o => o.Lines)
    .Include(o => o.Shipments)
    .Where(o => o.Id == id)
    .SingleAsync(ct);

// The list does not need the graph.
var page = await db.Orders.AsNoTracking()
    .Where(o => o.TenantId == tenantId && (cursor == null || o.CreatedUtc < cursor))
    .OrderByDescending(o => o.CreatedUtc)
    .Take(limit)
    .Select(o => new OrderListItem(o.Id, o.Number, o.Status, o.Total))
    .ToListAsync(ct);"""},
        {"t": "p", "text": "Use the graph when you are about to enforce a rule that needs lines and shipments together, and keep the page size small. Use the projection for the list. Lazy loading would let a serializer touch Lines for each order and issue a query per row while writing JSON. That passes a unit test with an in-memory stand-in and fails in production."},
        {"t": "warn", "title": "What breaks", "text": "Two collection includes on a large page return a result set the API then spends more time reading than the database spent finding. AsSplitQuery under READ COMMITTED can observe a line that was deleted between the parent query and the child query. Serializing entities with cycles and lazy loads is an accidental query storm."},
        {"t": "lead", "title": "Say this", "text": "Include for a small aggregate I am about to edit. AsSplitQuery when two collections would multiply rows, and I accept it is not one atomic read. Lists project. Lazy loading stays off."},

        {"t": "h2", "text": "Finding an N+1 and fixing it"},
        {"t": "p", "text": "N+1 is one query for the parents and one query per parent for the children, usually a loop or a lazy load. The API looks like a single method. The dependency list in Application Insights, or the SQL log, shows fifty statements for fifty orders. The fix is one query with a projection, or a controlled include. EF cannot make a non-SARGable predicate fast. Measure before and after on a realistic volume, not on ten rows."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// The bug. One query, then one query per order.
List<Order> orders = await db.Orders.Where(o => o.TenantId == tenantId).Take(50).ToListAsync(ct);
foreach (Order order in orders)
{
    order.LineCount = await db.OrderLines.CountAsync(l => l.OrderId == order.Id, ct);
}

// One query. The count is a subquery in the projection.
var page = await db.Orders.AsNoTracking()
    .Where(o => o.TenantId == tenantId)
    .OrderByDescending(o => o.CreatedUtc)
    .Take(50)
    .Select(o => new OrderListItem(
        o.Id,
        o.Number,
        o.Lines.Count(),
        o.Total))
    .ToListAsync(ct);"""},
        {"t": "p", "text": "The loop is obvious once you see it and invisible in review if the count hides behind a navigation property getter. A team rule helps: list endpoints project, they do not return entities, and a loop around a query needs a log sample in the PR. One explicit SQL statement is easier to tune than a clean-looking loop."},
        {"t": "warn", "title": "What breaks", "text": "The in-memory EF provider does not run SQL, so the N+1 test stays green. A projection that calls a .NET method EF cannot translate throws at runtime. Fixing the N+1 without an index on TenantId still scans."},
        {"t": "lead", "title": "Say this", "text": "I confirm N+1 in the SQL log: one parent query and a child query per row. I replace it with one projection. I measure on a realistic volume, and I still check the index."},

        {"t": "h2", "text": "Migrations locally and in production"},
        {"t": "p", "text": "A developer changes the model and adds a migration. EF generates a C# migration and updates the model snapshot. Review the Up method. EF does not always guess a rename. It may drop a column and add a column, and that is data loss. In CI, generate an idempotent SQL script and read it. In production, a pipeline applies that script with a migration identity that has DDL rights. The application identity does not own the schema."},
        {"t": "p", "text": "Calling Database.Migrate at startup races when many instances boot, and a bad migration takes the fleet down during boot. A single migrator job, or a pipeline step before traffic shifts, is the controlled path. Backward-compatible steps come first, because a slot swap runs old bits and new bits against the same database. That is expand/contract: add a nullable column, deploy code that writes both, backfill, then enforce the constraint. A rename in one step breaks the instances still on the old bits."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Expand: add a nullable column. Old code ignores it. New code writes it.
migrationBuilder.AddColumn<string>(
    name: "ExternalRef",
    schema: "orders",
    table: "Orders",
    maxLength: 64,
    nullable: true);

// Later, after backfill and after no instance reads the old shape:
migrationBuilder.AlterColumn<string>(
    name: "ExternalRef",
    schema: "orders",
    table: "Orders",
    nullable: false,
    oldNullable: true);

// Pipeline, not Program.cs:
// dotnet ef migrations script --idempotent -o migrate.sql
// applied by the migration identity before the slot receives traffic"""},
        {"t": "p", "text": "The idempotent script records itself in the migrations history table, so a rerun skips applied steps. A human still reads the SQL. A drop of Orders.Total because a property was renamed will pass a build that only compiles. The review of the script is the control. One owner of the schema during an overlap with a legacy app is non-negotiable. Two migration histories on one database is how a Friday deploy drops a column the old app still reads."},
        {"t": "warn", "title": "What breaks", "text": "Migrate() from every instance can deadlock on the history table or apply a half-tested migration on boot. A required column added in the same release as the code that reads it breaks the old slot during swap. A down migration in production is rarely rehearsed. Prefer a forward fix."},
        {"t": "lead", "title": "Say this", "text": "Migrations are source-controlled SQL, applied by a pipeline identity before traffic moves. I expand then contract so old and new instances both run. I do not call Migrate at startup."},

        {"t": "h2", "text": "Two users update the same order"},
        {"t": "p", "text": "A concurrency token, usually a rowversion column, detects a lost update. SQL Server updates the rowversion on every write. EF sends the original token in the WHERE clause. If zero rows match, someone else wrote first, and SaveChanges throws DbUpdateConcurrencyException. The API returns 409. The client reloads. Do not catch the exception and blindly save again. That overwrites the other user's change. A merge of a specific field is explicit code, not a retry loop."},
        {"t": "p", "text": "Isolation does not replace the token. Isolation controls locks during one transaction. The lost update happens when two transactions read, think, and write back in sequence, each in its own short transaction. Put the token on aggregates where losing an update costs money or trust: orders, balances, inventory. A lookup table does not need a merge UI."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class Order
{
    public int Id { get; set; }
    public string Status { get; set; } = "Pending";
    public byte[] RowVersion { get; set; } = [];
}

modelBuilder.Entity<Order>(b =>
{
    b.ToTable("Orders", "orders");
    b.Property(o => o.RowVersion).IsRowVersion();
});

try
{
    order.MarkPaid();
    await db.SaveChangesAsync(ct);
}
catch (DbUpdateConcurrencyException)
{
    return Results.Conflict(); // 409, client reloads
}

// The UPDATE EF sends is shaped like:
// UPDATE orders.Orders SET Status = @status
// WHERE Id = @id AND RowVersion = @original
// IF @@ROWCOUNT = 0 -> concurrency exception"""},
        {"t": "p", "text": "Keep the write transaction short. Do not hold it open while you call a payment provider. Read the order, call the provider with an idempotency key, then update the order with the token. If the token fails, the charge and the order can disagree, which is why the provider call and the database row need their own reconciliation story, often the outbox or a recorded payment id, not a longer lock."},
        {"t": "warn", "title": "What breaks", "text": "A client that omits the token, and a server that then ignores it, silently last-writes. Retrying SaveChanges after a concurrency exception overwrites the winner. Mapping rowversion as an ordinary byte array without IsRowVersion means EF will not put it in the WHERE clause."},
        {"t": "lead", "title": "Say this", "text": "rowversion goes in the WHERE clause. Zero rows is a 409, not a silent overwrite. Isolation does not stop two read-modify-write transactions. I keep the transaction off the HTTP call to the payment provider."},

        {"t": "h2", "text": "Transactions and the SQL retry strategy"},
        {"t": "p", "text": "SaveChanges uses a transaction. Several operations that must commit together, including raw SQL or an outbox insert, share one explicit transaction. Azure SQL can fail transiently: a deadlock, a throttle, a failover. An execution strategy retries those errors. A retry must re-run the whole transaction, so the transaction starts inside the strategy's ExecuteAsync delegate. If you start a user transaction outside that delegate, EF refuses the combination or the retry cannot repeat the work. Make the work idempotent inside the delegate, or a retry can double-insert when the first attempt committed and the connection died before the response."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """var strategy = db.Database.CreateExecutionStrategy();
await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync(ct);
    db.Orders.Add(order);
    db.Outbox.Add(new OutboxMessage
    {
        Id = order.MessageId,
        Type = "OrderCreated",
        Payload = JsonSerializer.Serialize(new { order.Id })
    });
    await db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
});

// Enable retries when you configure SQL, for transient errors including 1205.
options.UseSqlServer(connectionString, sql => sql.EnableRetryOnFailure());"""},
        {"t": "p", "text": "The order and the outbox row commit together or not at all. The relay publishes later. Email, Service Bus, and the card processor stay outside this delegate. A transaction that waits on HTTP holds locks and exhausts the pool. Clear the change tracker at the start of a retry if you add entities manually, because a failed attempt may have left them in the Added state. EF's strategy does this when you use its execution pattern. Know that a custom loop must do it too."},
        {"t": "warn", "title": "What breaks", "text": "BeginTransaction outside ExecuteAsync throws when retries are enabled. A retry of a non-idempotent insert duplicates the order if the first commit succeeded and the client never saw it. Holding the transaction across an HTTP call turns a slow partner into blocked orders."},
        {"t": "lead", "title": "Say this", "text": "The transaction lives inside the execution strategy so a retry can run it again. The bus and the payment call live outside it. If the message must match the commit, it is an outbox row in the same transaction."},

        {"t": "h2", "text": "Tenant isolation and soft delete"},
        {"t": "p", "text": "Both are global query filters. EF adds the predicate to queries. The tenant filter compares TenantId to a value from the current request, usually a scoped accessor populated from a claim. The soft-delete filter excludes rows where IsDeleted is true. Index (TenantId, ...) so the filter can seek. IgnoreQueryFilters is rare, audited, and tested, because a single call bypasses every filter on that entity. If you need to bypass only soft delete, model that path on purpose. Unique indexes include the tenant. A filtered unique index can allow the same external reference again after a soft delete."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class AppDbContext(DbContextOptions<AppDbContext> options, ITenant tenant) : DbContext(options)
{
    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<Order>().HasQueryFilter(o =>
            o.TenantId == tenant.Id && !o.IsDeleted);
        model.Entity<Order>().HasIndex(o => new { o.TenantId, o.ExternalRef })
            .IsUnique()
            .HasFilter("[IsDeleted] = 0");
    }
}

// Admin repair, reviewed and tested. It bypasses tenant AND soft delete.
var ghost = await db.Orders.IgnoreQueryFilters()
    .SingleAsync(o => o.Id == id, ct);"""},
        {"t": "p", "text": "The tenant value comes from the token when the scope is created, never from the body. For a shared database this is logical isolation. A noisy or regulated tenant can move to a separate database, and you should say that operational cost before you offer it. A filter is not the only control. Authorize the route, reject a cross-tenant id, and add a test that a token for tenant A cannot read tenant B's key."},
        {"t": "warn", "title": "What breaks", "text": "A new entity without the filter leaks rows. IgnoreQueryFilters in a list endpoint leaks them back. A unique index that ignores IsDeleted blocks a customer from reusing a reference after a delete. Raw SQL does not get the filter. Write the predicate yourself or call a procedure that has it."},
        {"t": "lead", "title": "Say this", "text": "Tenant and soft delete are query filters, indexed, with a test that tenant A cannot read tenant B. The tenant id comes from the token. IgnoreQueryFilters is an audited escape. The filter is a safety net, not the only authorization check."},

        {"t": "h2", "text": "ExecuteUpdate, raw SQL, or a stored procedure"},
        {"t": "p", "text": "Load and save through the tracker when you are enforcing an aggregate's rules and updating a few rows. ExecuteUpdate or ExecuteDelete when you are doing a set operation and do not want to load the rows. They skip the change tracker and also skip some save interceptors, so a tenant stamp or an audit interceptor will not see them. Raw SQL or a procedure when the query is a reporting shape EF translates badly, when you need a lock hint you have justified, or when a DBA-owned procedure is the agreed contract. FromSql and ExecuteSql use parameters. Do not concatenate user input into SQL."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Set-based. One UPDATE. Interceptors on SaveChanges do not run.
int expired = await db.Orders
    .Where(o => o.Status == "Pending" && o.CreatedUtc < cutoff)
    .ExecuteUpdateAsync(s => s.SetProperty(o => o.Status, "Expired"), ct);

// Parameterized. The value is not concatenated.
int id = 42;
var row = await db.Database.SqlQuery<OrderTotal>(
    $"SELECT Id, Total FROM orders.Orders WHERE Id = {id}")
    .SingleAsync(ct);

// A procedure is a boundary: source-controlled, deployed with the migration,
// EXECUTE granted to the runtime role, tested like the C#."""},
        {"t": "p", "text": "The interpolated SQL form above is parameterized by the provider. It is not string concatenation. A stored procedure earns its place for a hot, stable query. It does not earn a place as the default data layer, because the business rule then leaves the C# review. If the rule is in a procedure, the procedure needs the same PR, a test, and an owner. If the rule is in C#, the SQL must still be visible in logs."},
        {"t": "warn", "title": "What breaks", "text": "ExecuteUpdate bypasses a concurrency token unless you put it in the Where. A procedure updated in production and not in source control drifts. String concatenation of a sort column is injection. FromSqlRaw with an interpolated string that is not a FormattableString is the API that does not parameterize. Use the form that takes FormattableString or explicit parameters."},
        {"t": "lead", "title": "Say this", "text": "Tracker for the aggregate. ExecuteUpdate for a set. A procedure for a hot query the team has agreed to own in SQL. Parameters always. The lead decision is where the rule is visible."},

        {"t": "h2", "text": "Behaviors you warn a team about"},
        {"t": "p", "text": "These are the onboarding sentences. They belong on one page in the repo so a new joiner does not learn them by causing an incident."},
        {"t": "b", "items": [
            "If a predicate cannot translate, it should throw. Keep non-translatable work after ToListAsync on purpose.",
            "Several collection includes can explode into a huge payload that looks like a slow query.",
            "A global filter forgotten on a new entity leaks tenant data or returns soft-deleted rows.",
            "A migration that drops a column because a property was renamed will compile. Someone reads the SQL.",
            "Lazy loading in a loop passes an in-memory test and fails against SQL.",
            "The in-memory provider is not a database. Query filters, transactions, and constraints get an integration test against SQL.",
            "Startup Migrate is forbidden. The pipeline applies a reviewed script.",
            "A client-generated entity graph attached with Update marks every column modified and races the concurrency token.",
        ]},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Looks portable. The in-memory provider will not prove the filter or the index.
public class OrderListTests : IClassFixture<SqlFixture>
{
    [Fact]
    public async Task Tenant_a_does_not_see_tenant_b()
    {
        await fixture.SeedAsync(tenantA: 1, tenantB: 2);
        using var scope = fixture.CreateScope(tenantId: 1);
        var db = scope.Get<AppDbContext>();
        int count = await db.Orders.CountAsync();
        Assert.Equal(1, count);
    }
}"""},
        {"t": "warn", "title": "What breaks", "text": "A green unit-test suite with the in-memory provider, a missing filter, and a startup migration is three incidents stacked. The page in the repo is how you stop teaching those by pager."},
        {"t": "lead", "title": "Say this", "text": "I keep a short data-access page: tracking, migrations, tenant filters, and the ban on startup Migrate. Anything with a filter, a transaction, or a constraint gets a test against SQL."},
        {"t": "break"},
    ]
