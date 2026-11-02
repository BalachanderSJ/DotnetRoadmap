# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Azure, in more depth"},
        {"t": "p", "text": "The Orders API runs on App Service. The mail worker is an Azure Function on the isolated worker. Azure SQL stores the rows. Service Bus carries the committed fact. Key Vault holds secrets. Entra ID issues the caller's token. The process uses a managed identity. This section is the follow-up on those pieces. Prices, SKU quotas, and cold-start milliseconds stay in the current document for the service. You name the document. You do not recite a number you have not opened."},

        {"t": "h2", "text": "App Service"},
        {"t": "p", "text": "The plan is the SKU you are paying for: the features it includes, the size of an instance, and how many instances you may run. Scale up changes the size. Scale out adds instances of the same site. Slots, Always On, and a useful instance maximum exist on tiers that include them. You confirm that on the plan in front of you."},
        {"t": "p", "text": "Always On keeps the process loaded when traffic is quiet, which is what you want for an API with a p95 target. ARR affinity pins a client to an instance with a cookie. Turn it off for this stateless API. A health check path is the URL App Service probes. Several failures take the instance out of rotation, and continued failure can replace it. Point that path at a cheap live check that the process can answer. A ready check that opens SQL is for operators and for a gateway that can drain an instance without deleting it. If you point the App Service probe at SQL, a database blip can remove the fleet. Say that choice if you make it."},
        {"t": "p", "text": "A staging slot runs the new bits. You warm it, you hit the live check, and you run a smoke call. Swap exchanges the slots. The previous bits remain on the slot you swapped out of, and swap-back is real when those bits still understand the current schema. A setting marked as a slot setting stays on its slot. A setting without that mark moves with the bits. Connection strings that point at a different database are slot settings on purpose, or both slots are given the production-like string before the swap. The deep dive's release order still holds: expand the schema, deploy to the slot, smoke, swap, swap back only while the old bits can read the new schema."},
        {"t": "code", "text": """Release for a new nullable column the new code reads:
1. Pipeline applies the expand script with the migrator identity.
2. Deploy bits to the staging slot. Slot settings do not point this slot
   at a database the smoke test must not touch.
3. Warm the slot. GET /health/live returns 200 without depending on SQL.
4. Smoke a read on the slot hostname.
5. Swap. Watch error rate, p95, and SQL dependency time.
6. Swap back if the chart moves and the previous bits still match the schema.

A dropped column in the same release makes step 6 a lie."""},
        {"t": "p", "text": "System-assigned identity is born with the slot and is a different principal from production. User-assigned identity is a resource you attach. The SQL user and the Key Vault access policy have to exist for the identity that will serve traffic after the swap. An identity that was granted only on the staging slot fails the first query once production is serving those bits."},

        {"t": "h2", "text": "Azure SQL"},
        {"t": "p", "text": "The app connects with Authentication=Active Directory Managed Identity, Encrypt required. An admin creates a user from that identity and adds it to the runtime role. There is no SQL password in the string. EnableRetryOnFailure covers transient errors the provider treats as retryable, including a brief failover. The retry re-runs the whole operation. A transaction you begin yourself goes through CreateExecutionStrategy, so the retry starts the transaction over. The idempotency unique key makes that retry safe. A retry of a bare insert, with no unique key, can duplicate the order."},
        {"t": "p", "text": "DTU is a bundled performance model. vCore is a more explicit choice of compute, with storage and IO you select alongside it. In the room you say which signal you have: CPU, IO, connection count, or the bill. Then you open the limit document for that tier. You do not pick a SKU from memory, and you do not quote a price."},
        {"t": "p", "text": "The firewall is a public-network allow list. App Service outbound addresses can change as you scale. Allowing every Azure service is a wide door. A private endpoint is the conceptual alternative: the public path can be closed, the name resolves to a private address, and the app reaches SQL through the virtual network. You describe that shape. You look up the current private-link steps when you build it. The user's Entra token is still not the SQL login. The managed identity is."},
        {"t": "code", "text": """builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Orders"), sql =>
    {
        sql.EnableRetryOnFailure(maxRetryCount: 5);
    }));

var strategy = db.Database.CreateExecutionStrategy();
await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync(ct);
    db.Orders.Add(order);
    db.IdempotencyKeys.Add(keyRow);
    await db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
});

-- Once, as an admin, not at app startup:
-- CREATE USER [id-api-prod] FROM EXTERNAL PROVIDER;
-- ALTER ROLE app_orders_runtime ADD MEMBER [id-api-prod];"""},

        {"t": "h2", "text": "Service Bus"},
        {"t": "p", "text": "Peek-lock delivers a message under a lease. Complete removes it after the work commits. Abandon makes it visible again. After the delivery count you configured, Service Bus dead-letters it. You alert when the dead-letter count is above zero, you read the reason, and you have a replay. The handler is idempotent because a lock that expires produces a second delivery. Keep the work inside the lock, or renew the lock. The lock duration is a queue property you read on the queue. You do not memorize a default in the interview."},
        {"t": "p", "text": "Duplicate detection drops a second message with the same MessageId inside a window configured on the queue. Outside that window the same id is a new message. A partner who retries tomorrow is outside a short window. The business guarantee remains the unique idempotency key in SQL. Duplicate detection is a short-range convenience for a publisher that retries immediately."},
        {"t": "p", "text": "Sessions process messages that share a session id one at a time, in order, with a single active receiver for that session. Use a session when the events of one order must not run in parallel. The email worker usually skips sessions: each message is independent, and the processed-message row covers the duplicate. Sessions cost parallelism. Say the cost when you turn them on."},
        {"t": "p", "text": "Prefetch asks the client to pull extra messages and hold their locks before the handler is ready. A high prefetch and a slow mail provider pin messages on one instance. Other instances sit idle. Locks expire. The messages reappear and you have manufactured duplicates. Start with a small prefetch, or none, and raise it when the handler is faster than the network and you have measured the lock."},

        {"t": "h2", "text": "Functions, secrets, and telemetry"},
        {"t": "p", "text": "New functions use the isolated worker. Your code runs in a separate process from the Functions host. The HTTP API stays on App Service because people are waiting and the read has a p95 target. The Function owns the mail because that work scales with the queue and must be allowed to retry without occupying API threads. Consumption can scale to zero, and the next invocation pays a cold start. That plan is a candidate when the mail still arrives inside the minute you assumed, and you have measured the cold start. A plan that keeps an instance warm is the candidate when a person is waiting. You decide on that question. You do not decide on a price you guessed."},
        {"t": "p", "text": "A Key Vault reference in an App Service setting resolves to the secret at runtime, using the managed identity. The secret value is not in appsettings.json. That file may hold non-secrets: the audience, queue names, and timeouts you have chosen. It does not hold client secrets, SQL passwords, storage keys, signing keys, or connection strings that embed those. Local development uses user secrets or a developer vault. Production instrumentation uses a connection string in an app setting too."},
        {"t": "code", "text": """// App setting, value stored in Azure, not in git:
// ConnectionStrings__Orders =
//   Server=tcp:orders.database.windows.net,1433;Database=orders;
//   Authentication=Active Directory Managed Identity;Encrypt=True

// Pricing__Rate =
//   @Microsoft.KeyVault(SecretUri=https://orders-kv.vault.azure.net/secrets/pricing-rate/)"""},
        {"t": "p", "text": "Trace the request, the HTTP dependency, and the SQL dependency, and keep the correlation id on the log line. A trace attribute for an order id is useful on that one request. A metric dimension is a series. Order id as a dimension creates a series per order and will blow the metric bill and the query. Dimension on a low-cardinality value such as the route, the status code, or the dependency name. Tenant id joins order id in the danger list once you have many tenants. Put it on the trace or the log."},
        {"t": "code", "text": """builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("orders-api"))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddSqlClientInstrumentation())
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddRuntimeInstrumentation());

Activity.Current?.SetTag("order.id", orderId.ToString());
ordersPlaced.Add(1,
    new KeyValuePair<string, object?>("result", "created"));"""},

        {"t": "h2", "text": "Front Door, API Management, and a BFF"},
        {"t": "p", "text": "You do not add all three because the diagram looks complete. A BFF is the only host the Angular app calls. It holds the cookie session and the tokens, and it calls the Orders API. API Management belongs when partners need a published product: a front door for keys, quotas, and a stable external contract. Front Door belongs when you need a global entry, TLS at the edge, or a WAF in front of public traffic. The Orders partner API can sit behind API Management later. The first-party app can sit behind a BFF later. The API still validates the token itself. A gateway that checked the token is a help. It is not the only check."},
        {"t": "table", "headers": ["Piece", "Add it when", "Leave it out when"], "rows": [
            ["BFF", "A browser must call something that can hold tokens", "The only caller is a confidential partner"],
            ["API Management", "External partners need a product, a quota, and a key surface", "One internal caller already has a contract with the API"],
            ["Front Door", "You need a global edge or a WAF in front of the public site", "A single-region App Service is the whole public surface and you have no edge requirement yet"],
        ]},

        {"t": "warn", "title": "Interview trap", "text": "A slot swap after a column drop, with swap-back offered as the safety net. A sticky connection string that still points at staging after the swap, or a staging string that was not sticky and moved into production. An App Service health probe that opens SQL and then replaces instances during a failover. Duplicate detection described as the order idempotency guarantee. A metric tagged with order id. A price or a connection quota recited from memory."},
        {"t": "h2", "text": "Questions and answers"},
        {"t": "qa", "q": "What is an App Service plan, and what does scale out change?",
         "a": "The plan is the tier: instance size, how many instances you can run, and whether slots and Always On are included. I confirm those on the plan we pay for. Scale up replaces the size. Scale out adds instances. Each instance has its own memory and its own pool. At the assumed peak of about 50 requests a second I do not invent an instance count. I watch CPU, the request queue, and SQL, and I keep at least two instances when I want one recycle to leave the site up. That two is an availability choice.",
         "lead": "I separate the plan limit from the traffic assumption. The assumption is 50 requests a second. The plan maximum is whatever the portal shows, and the code has to be correct at that maximum."},
        {"t": "qa", "q": "Walk a deployment slot, a swap, and a sticky setting.",
         "a": "Staging runs the new bits. I warm it and smoke it on the slot hostname. Swap moves the bits into production and leaves the previous bits on the other slot. A slot setting stays behind. A normal app setting swaps. I use a slot setting for a value that must not follow the bits, such as a staging-only secret. I do not accidentally leave the production database string as a sticky staging value, and I do not let a staging database string swap into production. Schema changes are a pipeline step before traffic moves.",
         "lead": "I can say which settings on our app are slot settings and why. If I cannot, I am not ready to swap."},
        {"t": "qa", "q": "Why is ARR affinity off, and why is Always On on?",
         "a": "The API is stateless, so any instance may take the next call. Affinity would pin a partner to a dead instance and would make an in-memory cache look correct. Always On keeps the worker process loaded when the site is idle, which protects the first request of the day and the p95 target. I turn affinity on only as a temporary patch while I move state out of the process, and I name the day it comes off.",
         "lead": "Affinity off, Always On on, HTTPS only. Those three are the App Service sentence I can say without the portal in front of me."},
        {"t": "qa", "q": "What should the App Service health check path hit?",
         "a": "A live path that proves the process can answer, without opening SQL. App Service removes a failing instance and can replace it if failures continue. A probe that depends on SQL turns a database failover into a fleet replacement. I still expose a ready path that touches SQL lightly, for humans and for a gateway that can stop routing. Both paths are anonymous and return nothing about orders. The assumed read target is a reason to notice a bad instance. It is not a reason to tie process replacement to the database.",
         "lead": "Live and ready are two URLs. I say which one the platform probes, and I say what a SQL outage does to that probe."},
        {"t": "qa", "q": "How does managed identity reach Key Vault and Azure SQL?",
         "a": "The app has a system-assigned or user-assigned identity. Key Vault grants that identity get on the secrets it needs. App settings hold references, and the platform resolves them. Azure SQL has a user created from the same identity, in app_orders_runtime, with DML and EXECUTE, not DDL. The connection string uses Active Directory Managed Identity. The identity that serves traffic after a swap is the one that was granted. A pipeline identity applies migrations. The caller's token is a third identity and is not the SQL login.",
         "lead": "I draw the user, the app, and the pipeline every time. A design that uses one login for all three is the finding."},
        {"t": "qa", "q": "How do you retry Azure SQL without creating a second order?",
         "a": "EnableRetryOnFailure handles transient errors, including a short failover. I route my own transaction through the execution strategy so a retry repeats the transaction from the start. Inside that transaction I insert the order and the idempotency row. The unique key on tenant plus key means the second attempt conflicts, reads the winner, and returns the stored response. I do not retry by looping SaveChanges on a fresh order with a new id. Command timeout still applies. A deadlock victim, error 1205, retries only when that same story is safe.",
         "lead": "The retry policy and the unique key are one design. A retry without the key is how a failover duplicates a payment."},
        {"t": "qa", "q": "DTU or vCore. What do you say in the room?",
         "a": "DTU bundles compute into one measure. vCore lets you talk about cores, memory, and storage more directly. I choose by opening the bill and the limit document: connections, CPU, IO, and storage for the workload we measured. I bring the connection product, pool size times maximum instances, as the number I compare with the tier's connection limit. I do not quote a price or a SKU quota from memory. If we are on the wrong model, the evidence is a limit we are hitting or a bill that does not match the shape of the work.",
         "lead": "I say 'I would check the tier document' and I mean it. A memorized DTU number from a blog is how you lose the follow-up."},
        {"t": "qa", "q": "How do you think about the SQL firewall and private access?",
         "a": "The firewall is who may open the public endpoint. App Service outbound IPs are a brittle allow list because they can change when the stamp changes. A rule that allows all Azure services is broad. Private access means a private endpoint, the public path closed, and the app reaching SQL through the virtual network, with name resolution that follows. I describe that. I look up the current steps when I implement them. The private path does not replace the SQL permissions. The managed identity is still a user in a runtime role.",
         "lead": "Network reach and SQL permission are two gates. I want both. Opening the firewall to the world and hiding the password is one gate, and it is the wrong one."},
        {"t": "qa", "q": "Walk a Service Bus message from delivery to dead-letter.",
         "a": "Peek-lock gives the Function a lease. The handler writes its idempotent SQL, then completes. An exception abandons the message, and it becomes visible again until MaxDeliveryCount. Then it is dead-lettered with a reason. I alert on dead-letter depth. I can replay after a fix. If the work can outlive the lock, I renew the lock or I split the work. I complete after the commit. Completing before the commit loses the mail on a crash. The API has already returned 201. The user is not waiting on this thread.",
         "lead": "Complete after the side effect, abandon on failure, dead-letter after the count, alert, replay. That is the poison path I want on the runbook."},
        {"t": "qa", "q": "Why is duplicate detection not your idempotency story?",
         "a": "Duplicate detection is a window on the queue. A repeated MessageId inside the window is dropped. The same MessageId after the window is delivered. I read the window on our queue when I operate it. I do not memorize a default. A business retry the next day, a second publisher, and a message that was dead-lettered and resubmitted can all sit outside that window. The order's idempotency is the unique key in SQL, stored with the request hash, in the same transaction as the order.",
         "lead": "I let Service Bus help with an immediate publisher retry. I let SQL decide whether this order already exists."},
        {"t": "qa", "q": "When do you enable Service Bus sessions?",
         "a": "When messages that share a session id must run one at a time and in order. An order's events are the usual session id. One active receiver owns that session, so parallelism drops to the number of active sessions, not the number of messages. The confirmation email in this system does not need a session if each message carries a message id we dedupe in SQL. I add sessions when a real ordering bug appears, and I say what parallelism I gave up.",
         "lead": "Sessions are an ordering tool with a throughput cost. They are not a default on every queue because the portal offered a checkbox."},
        {"t": "qa", "q": "What goes wrong with a large prefetch?",
         "a": "Prefetch pulls messages onto one consumer and starts their locks before the handler runs. A slow mail provider plus a large prefetch holds a pile of messages on one instance. The other instances have nothing. Locks expire, Service Bus redelivers, and the idempotent handler spends its time proving it already sent the mail. I keep prefetch small until I have measured a handler that finishes well inside the lock.",
         "lead": "I treat prefetch as a performance knob with a duplicate side effect. I do not copy a sample that sets it to hundreds."},
        {"t": "qa", "q": "When is the isolated worker the right host, and how do you choose Consumption?",
         "a": "Isolated worker is the model I target for new functions: our process, separate from the host, on the runtime that moves forward with .NET 10. It is the right host for the mail, a schedule, and short work behind Service Bus. It is the wrong host for the whole CRUD API when callers expect the read to stay hot all day. Consumption can scale to zero, so the next call pays a cold start. I consider it when the work can still finish inside the assumed minute for email, and I measure that cold start. If a person is waiting on the call, I keep an instance warm on a plan that allows it. I do not quote the plan price.",
         "lead": "The split is failure and latency. The API stays up for the user. The Function retries the mail. Cold start is acceptable only for the side that nobody is staring at."},
        {"t": "qa", "q": "What must never be committed in appsettings?",
         "a": "Client secrets, SQL passwords, storage account keys, signing keys, and any connection string that contains those. The Entra authority, the audience, queue names, and the timeouts we chose can live in the file because they are not secret. Key Vault references and the managed-identity SQL string belong in App Service settings. Local secrets stay in user secrets or a developer vault. A production Application Insights connection string is an app setting too. I also keep tokens and connection strings out of logs.",
         "lead": "If a secret reached git, the fix is rotation, not a commit that deletes the line. The history still has it."},
        {"t": "qa", "q": "What do you trace, and why is order id a bad metric dimension?",
         "a": "I trace the ASP.NET Core request, outbound HTTP, and SQL, with one correlation id. I may tag the trace with the order id, because that tag lives on one trace. A metric dimension creates a time series per value. Order id means a series per order. Tenant id becomes the same problem as the tenant count grows. I dimension metrics on result, route, and dependency name. I put the order id on the log and the trace when I am debugging one order.",
         "lead": "Cardinality is a bill and a query that stops returning. I say the rule in review when someone adds a tag 'just in case'."},
        {"t": "qa", "q": "When do you add Front Door or API Management, and how is that different from a BFF?",
         "a": "The BFF is the browser's backend. It owns the cookie and the tokens and calls the Orders API. API Management is for publishing the partner surface: products, quotas, and a place for partner credentials, when we have external consumers who need that. Front Door is the global edge and a WAF when the public entry needs one. The Orders API does not require all three on day one. Whichever one I add, the API still validates the bearer token. A gateway check is not a substitute.",
         "lead": "I add a box when it owns a job I can name. A box that only forwards bytes is a thing I will debug at night for no gain."},
        {"t": "qa", "q": "Tell the rollback story when a slot swap goes wrong.",
         "a": "I look at the deploy marker, the error rate, and the dependency time. If the previous bits still match the schema, I swap back first and diagnose second. Expand-only migrations are what make that true: a new nullable column, a new table, no rename and no drop in the same release. If this release dropped a column the old bits read, swap-back fails closed and I fix forward with a plan I say out loud. I send a one-line status while I do it. I do not scale out to hide a bad query that arrived with the bits, and I do not spend the first half hour in the editor when the slot can still reverse the change.",
         "lead": "Reversible means the previous process can run on the current database. I decide that before the swap, not during the incident."},
        {"t": "qa", "q": "Production p95 jumped after the swap. What do you open, in order?",
         "a": "The correlation id from one slow request, then the chart: rate, latency, errors, SQL time, HTTP dependency time, CPU. The study target I compare against is p95 under 300 milliseconds for the read, labeled as the guide's target. If SQL time moved and the old bits are safe, I swap back. If a dependency is timing out, I look at retries and the breaker before I add instances. If CPU is high and SQL is flat, I look for a hot loop or thread-pool starvation. Scaling out during a lock storm adds waiters. I write the customer impact and the guard after the service is calm.",
         "lead": "Metrics, a reversible action, then the plan or the code. The panel is listening for that order."},
        {"t": "break"},
    ]
