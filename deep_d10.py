# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 10 — Mock day and compression"},
        {"t": "p", "text": "Day 10 adds no new theory. The roadmap's job today is speaking: ninety seconds, rapid fire, a blank-page design, your own stories. This chapter is the check. Each rapid-fire line has a miniature example and a pointer to the full section. If the miniature feels thin, go back. Do not open a new topic because you are nervous."},

        {"t": "h2", "text": "The ninety-second shape"},
        {"t": "p", "text": "Sentence one is the decision. Sentence two is how it works in the Orders example. Sentence three is the tradeoff or the person who feels it. Then stop. Silence is fine. If you hear yourself listing pattern names, return to the problem."},
        {"t": "h3", "text": "Example, spoken against a timer"},
        {"t": "code", "text": """Question: how do you keep a retried POST from creating two orders?

"The client sends an Idempotency-Key, and I store it uniquely with the
response in the same transaction as the order. A retry with the same key
and the same body returns the stored response. The same key with a different
body is a 409. I still keep a unique business key, because an idempotency
header is not a data rule. The tradeoff is retention: I keep the key for as
long as the client retries, not forever."

That is the whole answer. The outbox, the email, and the rowversion wait
until they ask."""},
        {"t": "b", "items": [
            "Round 1: eight questions from the roadmap, ninety seconds, one follow-up, scored.",
            "Round 2: the miniatures below. A hesitation means the short answer is not yours yet.",
            "Round 3: Design A from a blank page in twenty minutes, then a two-minute close.",
            "Round 4: your incident story and your migration plan, back to back. The Day 9 scaffolds are not your script.",
        ]},
        {"t": "lead", "title": "Say this", "text": "Decision, example, tradeoff, stop. I practice out loud. I do not add a chapter the night before."},

        {"t": "h2", "text": "Rapid fire, each with a miniature"},
        {"t": "p", "text": "Read the miniature, cover it, and say the one-sentence answer. The pointer is where the full example lives if you miss."},

        {"t": "h3", "text": "401 versus 403"},
        {"t": "p", "text": "401 means we do not know you. 403 means we know you and you may not do this. A missing bearer token on POST /orders is 401. A valid token without orders.write is 403. Full treatment: Day 3."},
        {"t": "code", "text": """no Authorization header        -> 401
valid token, missing role      -> 403
valid token, other tenant's id -> 404 or 403, and you have written which"""},

        {"t": "h3", "text": "PUT versus PATCH versus POST"},
        {"t": "p", "text": "PUT replaces the resource. PATCH changes a part. POST creates, or starts work that is not a simple replace. Full treatment: Day 3."},
        {"t": "code", "text": """PUT   /orders/10   body is the whole order you want stored
PATCH /orders/10   body is { "status": "Cancelled" }
POST  /orders      creates; a retry needs an idempotency key"""},

        {"t": "h3", "text": "Transient, scoped, singleton"},
        {"t": "p", "text": "Per resolve, per request, per process. DbContext is scoped. A singleton must not take a scoped service in its constructor. Full treatment: Day 3."},
        {"t": "code", "text": """AddDbContext<AppDbContext>();          // scoped
AddSingleton<IClock, SystemClock>();  // no DbContext in this constructor
// A hosted service creates a scope per unit of work."""},

        {"t": "h3", "text": "Why not .Result"},
        {"t": "p", "text": "It blocks a thread-pool thread and can starve the API under load. Await, and pass a CancellationToken. Full treatment: Day 1."},
        {"t": "code", "text": """var orders = db.Orders.ToListAsync(ct).Result;   // review reject
var orders = await db.Orders.ToListAsync(ct);"""},

        {"t": "h3", "text": "IEnumerable versus IQueryable"},
        {"t": "p", "text": "IEnumerable runs in memory. IQueryable can become SQL. Materialize at the boundary. Full treatment: Day 1."},
        {"t": "code", "text": """IEnumerable<Order> q = db.Orders.Where(o => o.TenantId == id);
q = q.Where(o => o.Status == "Open");   // this Where is LINQ to Objects
// The SQL already returned every order for the tenant."""},

        {"t": "h3", "text": "AsNoTracking"},
        {"t": "p", "text": "Use it on reads so EF does not snapshot entities you will not update. Full treatment: Day 4."},
        {"t": "code", "text": """await db.Orders.AsNoTracking()
    .Where(o => o.Id == id && o.TenantId == tenantId)
    .Select(o => new OrderListItem(o.Id, o.Number, o.Total))
    .SingleOrDefaultAsync(ct);"""},

        {"t": "h3", "text": "N+1"},
        {"t": "p", "text": "One query for the parents and one query per child, usually a loop or a lazy load. Replace it with one projection or a controlled include. Full treatment: Day 4."},
        {"t": "code", "text": """foreach (var order in orders)
    order.Lines = await db.Lines.Where(l => l.OrderId == order.Id).ToListAsync(ct);
// One round trip instead: project the page, include lines only if the UI needs them."""},

        {"t": "h3", "text": "rowversion"},
        {"t": "p", "text": "A concurrency token. The update matches the old value. Zero rows means 409, not a silent overwrite. Full treatment: Day 4."},
        {"t": "code", "text": """UPDATE orders.Orders
SET Status = @Status, RowVersion = <generated>
WHERE Id = @Id AND RowVersion = @Original;
-- @@ROWCOUNT = 0 -> DbUpdateConcurrencyException -> 409"""},

        {"t": "h3", "text": "Clustered versus nonclustered"},
        {"t": "p", "text": "Clustered orders the table. Nonclustered is a secondary key path. Include columns to avoid lookups. Full treatment: Day 5."},
        {"t": "code", "text": """PRIMARY KEY CLUSTERED (Id)
INDEX (TenantId, CreatedUtc DESC, Id DESC) INCLUDE (Status, Total)"""},

        {"t": "h3", "text": "SARGable"},
        {"t": "p", "text": "The column stands alone so an index can seek. Do not wrap the column in a function. Full treatment: Day 5."},
        {"t": "code", "text": """WHERE YEAR(CreatedUtc) = 2026                         -- scan
WHERE CreatedUtc >= '2026-01-01' AND CreatedUtc < '2027-01-01'  -- seek"""},

        {"t": "h3", "text": "Deadlock 1205"},
        {"t": "p", "text": "A lock cycle. SQL kills a victim. Retry if the work is safe, then remove the cycle with one lock order, an index, and a shorter transaction. Full treatment: Day 5."},
        {"t": "code", "text": """Session A: update Orders 10, then Payments 88
Session B: update Payments 88, then Orders 10
-- Pick one order. Do not hold either transaction across an HTTP call."""},

        {"t": "h3", "text": "RCSI"},
        {"t": "p", "text": "Readers use row versions and do not block writers the way shared locks do. It does not replace a concurrency token. Full treatment: Day 5."},
        {"t": "code", "text": """ALTER DATABASE CURRENT SET READ_COMMITTED_SNAPSHOT ON;
-- Two sessions can still both read a balance of 10 and both write 11.
-- The fix is an atomic UPDATE or a rowversion, not the isolation flag."""},

        {"t": "h3", "text": "db_owner for the app"},
        {"t": "p", "text": "No. A custom runtime role for DML. A separate identity for migrations. Full treatment: Day 5."},
        {"t": "code", "text": """app_orders_runtime  : SELECT, INSERT, UPDATE, DELETE, EXECUTE on schema orders
app_orders_migrator : ALTER on schema orders, pipeline only"""},

        {"t": "h3", "text": "Idempotency key"},
        {"t": "p", "text": "A client key stored uniquely with the first response, so a retried POST does not create a second order. Full treatment: Day 3 and Design A."},
        {"t": "code", "text": """UNIQUE (TenantId, KeyValue)
same key, same body  -> stored 201
same key, other body -> 409"""},

        {"t": "h3", "text": "Outbox"},
        {"t": "p", "text": "The business row and the message row commit together. A relay publishes. Consumers dedupe. Full treatment: Day 7."},
        {"t": "code", "text": """BEGIN TRAN  insert Orders; insert Outbox; COMMIT
-- relay sends after. A crash before the send leaves a visible unpublished row."""},

        {"t": "h3", "text": "Peek lock"},
        {"t": "p", "text": "Service Bus hides the message until you complete it. Abandon or lock expiry makes it visible again. Too many failures dead-letter it. Full treatment: Day 6."},
        {"t": "code", "text": """handle -> SQL commit -> Complete
throw  -> Abandon -> retry until MaxDeliveryCount -> dead-letter"""},

        {"t": "h3", "text": "Cold start"},
        {"t": "p", "text": "A scaled-to-zero function pays startup latency on the next call. Buy a warm plan if a user is waiting. Do not memorize a millisecond. Full treatment: Day 6."},
        {"t": "code", "text": """Email that can take a minute: Consumption is a real option.
Checkout the user is staring at: not a scale-to-zero plan."""},

        {"t": "h3", "text": "Deployment slot"},
        {"t": "p", "text": "Stage and warm the new bits, swap, keep the old bits for swap-back. The schema must still suit both. Full treatment: Day 6 and Day 4."},
        {"t": "code", "text": """add nullable column -> deploy slot -> ready check -> swap
rename-and-drop in the same release -> swap-back is a lie"""},

        {"t": "h3", "text": "Managed identity"},
        {"t": "p", "text": "The Azure resource authenticates without a password. Grant it Key Vault and a SQL user in a least-privilege role. Full treatment: Day 6."},
        {"t": "code", "text": """Authentication=Active Directory Managed Identity
CREATE USER [id-api-prod] FROM EXTERNAL PROVIDER;
ALTER ROLE app_orders_runtime ADD MEMBER [id-api-prod];"""},

        {"t": "h3", "text": "Strangler fig"},
        {"t": "p", "text": "Route one slice at a time to the new host. Delete the old slice only when traffic, logs, and rollback are proven. Full treatment: Day 8."},
        {"t": "code", "text": """POST /orders -> net10
GET  /catalog -> Framework, until its own slice
metric: percent of order traffic, not percent of projects"""},

        {"t": "h3", "text": "Generic repository"},
        {"t": "p", "text": "DbContext is already a unit of work. Prefer a focused store per aggregate so the SQL stays visible. Full treatment: Day 2."},
        {"t": "code", "text": """interface IOrderStore { Task<Order?> GetAsync(int id, CancellationToken ct); Task SaveAsync(Order order, CancellationToken ct); }
// Not IRepository<T> with Get, Add, and a predicate that hides Include and ExecuteUpdate."""},

        {"t": "h3", "text": "Mediator"},
        {"t": "p", "text": "A dispatcher to one handler, useful when pipeline behaviors earn it. Handlers do not call handlers. Full treatment: Day 2."},
        {"t": "code", "text": """CreateOrder -> CreateOrderHandler
validation and the transaction are pipeline behaviors
the handler does not send GetOrder through the mediator"""},

        {"t": "h3", "text": "Circuit breaker"},
        {"t": "p", "text": "Fail fast when a dependency is sick, then probe. Retries need a budget or they amplify the outage. Full treatment: Day 3."},
        {"t": "code", "text": """tax client: timeout, two jittered retries, breaker
open breaker -> 503 now, not a 30-second hang
do not retry a charge unless the idempotency story is solid"""},

        {"t": "h3", "text": "Sync versus async integration"},
        {"t": "p", "text": "Sync when the user needs the answer now and you accept the dependency. Async when the work can finish after the response. Full treatment: Day 7."},
        {"t": "code", "text": """tax required to price  -> sync, then 503 if it is down
email confirmation     -> outbox, 201 immediately"""},

        {"t": "h3", "text": "Database per service"},
        {"t": "p", "text": "The service owns its writes. Cross-service joins become an API, a copied snapshot, or a reporting store. Full treatment: Day 7."},
        {"t": "code", "text": """orders.CustomerSnapshot filled by CustomerChanged
-- not a SQL login from Orders onto customers.Customers"""},

        {"t": "h3", "text": "Startup Migrate"},
        {"t": "p", "text": "Unsafe with many instances. Apply a reviewed SQL script from the pipeline before traffic moves. Full treatment: Day 4."},
        {"t": "code", "text": """// not this
app.Services.GetRequiredService<AppDbContext>().Database.Migrate();
// this: pipeline, migrator identity, then the slot swap"""},

        {"t": "h3", "text": "ConfigureAwait(false)"},
        {"t": "p", "text": "Important in a library that must not resume on a captured context. ASP.NET Core application code has no sync context to return to. Blocking calls still hurt. Full treatment: Day 1."},
        {"t": "code", "text": """// library code that may be called from a UI or older ASP.NET
await stream.ReadAsync(buffer, ct).ConfigureAwait(false);

// a controller: just await, and do not call .Result"""},

        {"t": "h3", "text": "Record versus class"},
        {"t": "p", "text": "A record for a value-shaped contract. A class for an entity with identity that EF tracks. Full treatment: Day 1."},
        {"t": "code", "text": """sealed record OrderCreated(int OrderId, DateTimeOffset OccurredUtc);
sealed class Order { public int Id { get; set; } }"""},

        {"t": "h3", "text": "ProblemDetails"},
        {"t": "p", "text": "A consistent error body with status, title, and a trace id. Clients and logs share it. Full treatment: Day 3."},
        {"t": "code", "text": """{ "status": 409, "title": "Conflict", "traceId": "441" }
validation adds an errors dictionary. Do not invent a new shape per endpoint."""},

        {"t": "h3", "text": "Keyset versus offset"},
        {"t": "p", "text": "Keyset seeks the next row from the last key. Offset discards skipped rows and gets worse on deep pages. Full treatment: Day 5."},
        {"t": "code", "text": """WHERE CreatedUtc < @CursorUtc OR (CreatedUtc = @CursorUtc AND Id < @CursorId)
ORDER BY CreatedUtc DESC, Id DESC"""},

        {"t": "h3", "text": ".NET support"},
        {"t": "p", "text": ".NET 10 is the LTS to target, supported into November 2028. .NET 8 and .NET 9 reach end of support in November 2026. Full treatment: Day 8."},
        {"t": "code", "text": """new work: net10.0
a Framework host still in production past that window is a dated risk,
not a backlog theme"""},

        {"t": "h2", "text": "Where the mock prompts live"},
        {"t": "p", "text": "Pull eight at random, as the roadmap says. This table is only a map so a miss sends you to a chapter instead of to a new Google search."},
        {"t": "table", "headers": ["Prompt", "Open"], "rows": [
            ["Tell me about yourself as a backend lead.", "The positioning line in the roadmap front matter. Decisions, cost, rollback."],
            ["Explain async to someone who used .Result.", "Day 1, async. Show the blocked call and the token."],
            ["Design POST /orders so partners can retry.", "Day 9 Design A. Idempotency key, unique constraint, stored response."],
            ["Your list endpoint is slow. Walk the first hour.", "Day 6 incident sequence, then Day 4 N+1 and Day 5 plans."],
            ["Would you use a generic repository?", "Day 2. DbContext is the unit of work. Focused store, or no store."],
            ["Two updates hit one row.", "Day 4 rowversion. 409. No blind retry."],
            ["What SQL role does the application have?", "Day 5. Runtime role versus migrator. Not db_owner."],
            ["App Service or Functions?", "Day 6. API versus email."],
            ["What is a dead-letter queue for?", "Day 6 peek lock. Poison payload, alert, replay."],
            ["Should this system be microservices?", "Day 7. Module first. Name the data owner and the failure."],
            ["Migrate a Framework Web API to .NET 10.", "Day 8. One slice, traffic percent, expand/contract rollback."],
            ["A production incident.", "Your story, Day 9 shape. Decision minute, number, team rule."],
            ["A disagreement on design.", "Your story. What change were you protecting?"],
            ["What do you look for in a pull request?", "Day 3 review, and the bad Create action."],
            ["What do you want to know about on-call and release?", "Day 9 questions. Ask two."],
        ]},

        {"t": "h2", "text": "How to score, and when to stop"},
        {"t": "p", "text": "Score each practice answer from 0 to 2 on three lines: correct, tradeoff, consequence. A 6 is a hire signal on that question. A correct answer with no consequence still sounds like year four. Any row under 4 gets one more spoken pass the next morning. It does not get a new chapter tonight."},
        {"t": "h3", "text": "Example of a score"},
        {"t": "code", "text": """Question: startup Migrate.
Correct 2:    many instances race, and a bad script takes the fleet down at boot.
Tradeoff 2:   the pipeline is slower than a startup call and needs a migrator login.
Consequence 2: a failed boot is an outage, and db_owner on the app is the second incident.
6/6. Move on.

Question: RCSI.
Correct 2, tradeoff 0, consequence 0.
You defined it and stopped. Tomorrow morning, add: version store cost,
and it does not fix a lost update. That is the missing 4 points."""},
        {"t": "p", "text": "Depth on orders, SQL, and one migration story beats a thin pass over every pattern name. The one-page sheet you rewrite by hand is the one you may read the night before: positioning line, pipeline order, lifetimes, the status codes you mix up, the transaction boundary, the index for your hottest list, the runtime role versus the migrator, peek lock through dead-letter, the strangler metric, the incident in six lines, and two questions for them."},
        {"t": "lead", "title": "Say this", "text": "I still want to design the backend and read the SQL. The difference in this role is that I also own the boundary, the release, the permissions, and the way the team reviews the next change. I will leave you with a decision, the cost of that decision, and how we roll it back."},

        {"t": "h2", "text": "After the interview"},
        {"t": "p", "text": "Within an hour, write down every question they asked. Mark the ones where you listed tools and forgot the consequence. Those are the only topics to repair before the next round. Send a short thank-you that mentions one specific thread, such as their migration or their on-call model, and the judgment you would bring to it. Two paragraphs. Do not attach this guide."},
        {"t": "note", "title": "The last check", "text": "You already have eight years. The panel is deciding whether they can hand you a production API, a SQL database, a release, and a less experienced developer. Speak in decisions, costs, and rollbacks. Use your own incidents. The examples in this guide are the evidence you understand the mechanism. They are not the story of your career."},
        {"t": "break"},
    ]
