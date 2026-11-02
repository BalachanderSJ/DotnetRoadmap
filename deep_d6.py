# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 6 — Azure App Service and Azure Functions"},
        {"t": "p", "text": "Day 6 is where the code runs, how a release moves, and how the process proves who it is. The Orders API is the running example: HTTP on App Service, email after commit on a Function, secrets and SQL through managed identity. Do not invent a price, a SKU limit, or a cold-start millisecond. Say which plan property you would check."},

        {"t": "h2", "text": "Where the code runs"},
        {"t": "p", "text": "Pick the host from the traffic shape and the failure you can tolerate. The request API wants a process that is already warm. The email worker wants to scale with the queue and must not be able to starve the API. A workflow with waits wants an orchestrator. A platform you do not operate yet is a cost, even when the diagram looks current."},
        {"t": "table", "headers": ["Host", "Fits the Orders system when", "Watch"], "rows": [
            ["App Service", "The HTTP API, steady traffic, a latency target", "Many instances. Memory is not shared. Slots for release."],
            ["Functions, isolated worker", "The email, a schedule, a file arrival, short work behind a queue", "Cold start on Consumption. A long job needs a plan that stays warm and a timeout that fits."],
            ["Durable Functions", "Reserve, pay, compensate, with waits", "The orchestrator stays deterministic. Work goes in activities."],
            ["Container Apps or AKS", "You already operate that platform, or you need a sidecar", "You are taking on a platform. One Web API does not justify the start."],
            ["Hosted BackgroundService", "A tiny loop that must live next to the API", "It scales with the API, including when the API is what you wanted to protect."],
        ]},
        {"t": "p", "text": "New functions target the isolated worker. Your code runs in a separate process from the Functions host, which is the model that moves forward with .NET 10. The older in-process model shared the host's CLR and is the legacy path. In the room, say isolated worker, say why a cold start exists, and say which plan property matches the latency you need."},
        {"t": "lead", "title": "Say this", "text": "I put the HTTP API on App Service and the email on a queue and a Function. I do not start on Kubernetes for one API, and I do not put a steady user-facing API on a plan that scales to zero unless the product accepts the wait."},

        {"t": "h2", "text": "App Service or Functions for an order API that also sends email"},
        {"t": "p", "text": "The HTTP API goes on App Service because the traffic is steady, the read has a p95 target, and the process owns the request. The email goes on a queue. A function triggered by Service Bus sends the mail and completes the message. If the mail provider is slow or down, the API has already committed the order and returned 201. The function retries through the Service Bus delivery count. The user does not wait on the provider."},
        {"t": "p", "text": "A function is a reasonable host for a small HTTP API with spiky traffic when a cold start is acceptable or the plan keeps instances warm. It is a poor host for the whole CRUD API if the product expects hot latency all day. The split is about scaling and failure, not about fashion. The API and the worker scale for different reasons. In one process, a mail-provider outage and a retry loop can starve the threads the API needs."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// API: commit the order and the outbox, return 201. Do not SmtpClient.Send here.

// Function, isolated worker. The message is the unit of work.
public sealed class SendOrderEmail(IEmailSender email, IOrderMailLog log)
{
    [Function(nameof(Run))]
    public async Task Run(
        [ServiceBusTrigger("order-confirmed", Connection = "ServiceBus")]
        ServiceBusReceivedMessage message,
        ServiceBusMessageActions actions,
        CancellationToken ct)
    {
        var body = message.Body.ToObjectFromJson<OrderConfirmed>();
        if (await log.AlreadySentAsync(message.MessageId, ct))
        {
            await actions.CompleteMessageAsync(message, ct);
            return;
        }
        await email.SendAsync(body!, ct);
        await log.MarkSentAsync(message.MessageId, ct);
        await actions.CompleteMessageAsync(message, ct);
    }
}"""},
        {"t": "warn", "title": "What breaks", "text": "Sending mail inside POST couples the user's latency to a third party and turns a provider outage into API errors. Completing the message before the send loses the mail on a crash. Sending without a message-id check double-emails on redelivery."},
        {"t": "lead", "title": "Say this", "text": "The API owns the request and returns after the commit. The Function owns the mail and can retry without touching the API thread pool. I split them because they fail and scale differently."},

        {"t": "h2", "text": "Deployment slots"},
        {"t": "p", "text": "A staging slot runs the new bits with production-like settings. You warm it, hit the health endpoint, and run a smoke check. Swap exchanges the slots. The previous bits remain on the staging slot for a swap-back. That is the reversible part of a release, and it is only true when the previous bits still work against the current schema."},
        {"t": "p", "text": "App settings and connection strings can be sticky to a slot. Be deliberate. A staging slot must not point at a destructive action by accident, and it must not keep a staging-only secret after swap unless you marked it sticky on purpose. Always On stays on for the API so the process is up. The App Service health check should hit readiness, including a lightweight dependency check, so traffic does not land on an instance that cannot reach SQL. Migrations run as a pipeline step before traffic moves, using the expand/contract rule from Day 4. A swap is not a migration strategy."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Release order for a nullable column the new code reads:
1. Pipeline applies the expand script (add nullable column). Migrator identity.
2. Deploy the new bits to the staging slot. Sticky setting: none that point at a
   different database. The slot uses production-like config on purpose.
3. Warm the slot. GET /health/ready must touch SQL and return 200.
4. Swap. Watch the error rate and the SQL dependency time.
5. Swap back if the chart moves and the old bits can still read the schema.

A rename in the same release makes step 5 a lie. The old bits look for the old name."""},
        {"t": "warn", "title": "What breaks", "text": "A slot swap after a column rename or drop cannot roll back. A sticky connection string that still points at staging after swap sends production traffic at the wrong database. Health that always returns 200 sends traffic at an instance that cannot reach SQL."},
        {"t": "lead", "title": "Say this", "text": "I warm the slot, smoke it, and swap. Swap-back is real only when the previous bits still work on the current schema. Migrations are a pipeline step before traffic moves, not something the slot does on its own."},

        {"t": "h2", "text": "Secrets and Azure SQL without a password"},
        {"t": "p", "text": "The App Service has a system-assigned or user-assigned managed identity. That identity is granted access to the Key Vault secrets it needs, and app settings reference those secrets so they appear as configuration. For Azure SQL you create a user for the same identity and add it to app_orders_runtime from Day 5. The SQL client uses an Azure identity credential. There is no SQL password and no secret in source control."},
        {"t": "p", "text": "Locally, developers use their own Entra login or a dev database, with a user secret stored outside git. Rotation becomes an identity story. Validate options on startup so a missing vault reference fails the slot before swap, which is the Options rule from Day 2."},
        {"t": "p", "text": "Draw three identities every time. The user's token decides what the human may do. The API's managed identity decides what the process may do in SQL, Key Vault, and Service Bus. The pipeline's migration identity applies DDL. Mixing them into one shared SQL login is how an over-privileged app login appears."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// App setting, not a password in the repo:
// ConnectionStrings__Orders =
//   Server=tcp:orders.database.windows.net;Database=orders;
//   Authentication=Active Directory Managed Identity;Encrypt=True;

builder.Services.AddDbContext<AppDbContext>(o =>
    o.UseSqlServer(builder.Configuration.GetConnectionString("Orders")));

// Key Vault reference in an app setting, resolved by the same identity:
// Pricing__Rate = @Microsoft.KeyVault(SecretUri=https://orders-kv.vault.azure.net/secrets/pricing-rate/)

// SQL user, created once by an admin, not by the app:
// CREATE USER [id-api-prod] FROM EXTERNAL PROVIDER;
// ALTER ROLE app_orders_runtime ADD MEMBER [id-api-prod];"""},
        {"t": "warn", "title": "What breaks", "text": "A connection string with a SQL password in app settings will show up in a diagnostic dump or a careless log. A user-assigned identity that was granted on the slot and not on the swapped app fails at the first query. One identity used for runtime and migrations means the site can run DDL all day."},
        {"t": "lead", "title": "Say this", "text": "Managed identity to Key Vault and to a SQL user in the runtime role. No password in the string. Three identities: the user, the app, and the pipeline. If I cannot name all three, the design is not finished."},

        {"t": "h2", "text": "Cold start, and which plan you choose"},
        {"t": "p", "text": "On the Consumption plan, Azure can scale to zero. The next invocation loads the host and the isolated worker. That delay is the cold start. Premium and dedicated plans can keep instances warm, with a higher floor cost. You do not need a memorized millisecond. You need the product question: is a person waiting?"},
        {"t": "p", "text": "Consumption fits low-volume jobs, a nightly cleanup, and work that can wait. Premium or a dedicated plan fits a user who is waiting, or a function that must hold a connection and run with predictable throughput. Also watch the timeout for the plan. A function that parses a million-row file in one invocation will hit the limit. Split the file into messages, or move that job to a host whose duration matches the work. Day 9's file design does exactly that."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Email worker:
  Volume is the queue, not a person staring at a spinner.
  Consumption is acceptable if a cold start still lands the mail inside the
  minute we assumed. If the business says the mail is part of checkout latency,
  buy a plan that keeps an instance warm and write that in the design note.

Order API:
  People are waiting. App Service, Always On. Not Consumption.

Nightly file of a million rows:
  Not one function invocation. A control message, then chunk messages,
  on a plan whose timeout and concurrency match a chunk."""},
        {"t": "warn", "title": "What breaks", "text": "Choosing Consumption because the invoice looks small, then discovering checkout waits on a cold start, is a lead miss. A single invocation that reads the whole file dies at the plan timeout and retries from the start."},
        {"t": "lead", "title": "Say this", "text": "Cold start is the cost of scale to zero. If a user is waiting, I keep the instance warm and I put the plan next to the latency target. If the work can finish after the response, Consumption is a real option."},

        {"t": "h2", "text": "A Service Bus trigger, from delivery to completion"},
        {"t": "p", "text": "Service Bus delivers under a peek lock. The lock is a lease, not a deletion. The function runs. If it finishes, it completes the message and Service Bus removes it. If it throws, the message is abandoned and becomes visible again after the lock, up to MaxDeliveryCount. After that it is dead-lettered. You inspect the dead-letter reason, fix the poison or the bug, and you have a replay path."},
        {"t": "p", "text": "Keep the work shorter than the lock, or renew the lock. A long job whose lock expires is processed twice: another worker receives it. The handler is idempotent either way. A unique key or a processed-message table stops a double charge. Prefetch holds messages on one instance. A huge prefetch on a slow handler pins messages that another instance could have finished."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """try
{
    await HandleAsync(message, ct);          // writes SQL with a unique MessageId
    await actions.CompleteMessageAsync(message, ct);
}
catch (Exception) // poison or a bug
{
    // Abandon makes it visible again. After MaxDeliveryCount, Service Bus
    // dead-letters it. The rest of the queue stays healthy.
    await actions.AbandonMessageAsync(message);
    throw;
}

// Alert: dead-letter count on order-confirmed > 0.
// Replay: fix the payload or the bug, then resubmit from the dead-letter queue.
// A payload that always throws burns the count and sits there. That is the
// poison message. The happy path is not the design."""},
        {"t": "warn", "title": "What breaks", "text": "Completing before the SQL commit loses the work. A lock that expires mid-send double-processes. Prefetch of hundreds on a handler that calls a slow provider stalls the queue. No alert on dead-letter depth means the poison sits until a customer asks where the mail is."},
        {"t": "lead", "title": "Say this", "text": "Peek lock, complete after the commit, abandon on failure, dead-letter after the delivery count. The handler dedupes. I alert on dead-letter depth and I can replay. That is the poison-message path."},

        {"t": "h2", "text": "What belongs in a Durable Functions orchestration"},
        {"t": "p", "text": "An orchestration coordinates. It can wait, fan out activities, and run compensations. It must be deterministic, because the runtime replays the history. No direct IO, no DateTime.Now, no Guid.NewGuid inside the orchestrator. Those belong in activities. The orchestrator calls them through the context and uses context.CurrentUtcDateTime when it needs a clock. State is checkpointed, so a replay must make the same decisions."},
        {"t": "p", "text": "Use Durable Functions when the workflow is long, has a human wait, or needs a compensation owner: reserve inventory, take payment, release inventory if payment fails. Use a single message and a database row when the workflow is one step. Do not hide a simple retry policy inside an orchestration. If the interviewer has not used Durable Functions, you still show that you know when a row and a queue are enough."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """[Function(nameof(OrderOrchestrator))]
public static async Task Run([OrchestrationTrigger] TaskOrchestrationContext context)
{
    var input = context.GetInput<OrderStart>();
    // Deterministic. No DateTime.Now, no HTTP, no SQL in this method.
    bool reserved = await context.CallActivityAsync<bool>(nameof(Reserve), input);
    if (!reserved)
        return;

    bool paid = await context.CallActivityAsync<bool>(nameof(CapturePayment), input);
    if (!paid)
    {
        await context.CallActivityAsync(nameof(Release), input);
        return;
    }
    await context.CallActivityAsync(nameof(MarkPaid), input);
}"""},
        {"t": "warn", "title": "What breaks", "text": "DateTime.Now or a random id inside the orchestrator changes on replay and the workflow double-charges or takes a different branch. Putting the HTTP call in the orchestrator is the same bug. An orchestration for one email is a platform you now have to debug."},
        {"t": "lead", "title": "Say this", "text": "The orchestrator decides. Activities do the IO. Replay must make the same decision, so the clock and the network stay out of the orchestrator. One step is a queue and a row, not a workflow engine."},

        {"t": "h2", "text": "What breaks when you scale from one instance to ten"},
        {"t": "p", "text": "Anything in a static field or an in-memory cache becomes ten copies, possibly inconsistent. A background timer inside the API runs ten times unless you use a distributed lock or move it to one scheduled function. A file on local disk is not shared. Session affinity hides the mistake and then sticks users to a dead instance, so a stateless API turns affinity off."},
        {"t": "p", "text": "SQL connections scale with instances. Ten instances with a fat pool can exhaust Azure SQL. Set the pool with the maximum instance count in mind. You do not need a magic pool number in the interview. You need to say the pool times the instance count is the real connection count. A lock or a singleton still covers one process. The second instance has its own lock and its own memory. Shared state belongs in SQL, Service Bus sessions, or a store you chose on purpose."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Correct on one instance. Wrong on ten.
public static class Cache
{
    public static List<Sku> Catalog { get; } = Load();
}

// A timer in the API. Ten instances expire the same orders ten times,
// and ten of them will run during a scale-out you did not schedule.
builder.Services.AddHostedService<ExpireOrdersTimer>();

// The question on every design: what happens on the second instance?
// If the answer is 'we only run one', the next question is what happens
// when the platform restarts that one. Single instance is an availability
// decision, and it belongs on paper."""},
        {"t": "warn", "title": "What breaks", "text": "A static mutable list corrupts under concurrency and diverges across instances. Affinity left on hides a sticky-session bug until one instance dies and ARR keeps sending people there. An unbounded connection pool times ten is how you tip Azure SQL."},
        {"t": "lead", "title": "Say this", "text": "In-memory state is per process. Timers in the API run once per instance. I turn affinity off for a stateless API, and I size the SQL pool against the maximum instance count."},

        {"t": "h2", "text": "Production is slow right now"},
        {"t": "p", "text": "Start from the user symptom and one correlation id, then the request chart: rate, latency, errors, and dependency time. If SQL time dominates, open Query Store and blocking, not a code deploy. If an outbound HTTP dependency dominates, check the timeout, a retry storm, and the circuit breaker. If CPU is high and SQL is fine, look for a hot loop, a bad cache, or thread-pool starvation from blocking calls. Check the deploy marker and the slot-swap time."},
        {"t": "p", "text": "Decide rollback versus fix-forward with a clock. If the last deploy lines up and rollback is safe, swap back first and diagnose second. Say a one-line status while you do it. Afterward write the cause, the customer impact, and the guard that would have caught it. The panel listens for sequence. A lead who opens the editor and reads code for twenty minutes while the slot can be swapped back has the wrong order."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """11:20  GET /orders p95 is above four seconds. Correlation id from one slow request.
11:22  Chart: error rate flat, SQL dependency time up, CPU on the app flat.
11:23  Deploy marker at 11:00. Migration was a nullable column. Old bits are safe.
11:25  Swap back. p95 returns. Then Query Store, not before.
11:40  The new screen's query scans Orders. Covering index in a reviewed script.
       The index ships after the swap, with a plan, not during the first five minutes."""},
        {"t": "warn", "title": "What breaks", "text": "Scaling out during a lock storm multiplies the waiters. Fixing forward on a schema the old bits cannot read removes the rollback. Debugging for half an hour with no status leaves the stakeholders inventing their own incident."},
        {"t": "lead", "title": "Say this", "text": "Metrics, a reversible action, then root cause. If SQL time moved with the deploy and swap-back is safe, I swap back first. I do not scale the app to hide a scan."},

        {"t": "h2", "text": "Settings worth naming"},
        {"t": "b", "items": [
            "App Service: Always On for the API, HTTPS only, a current TLS policy, a health check path that means ready, ARR affinity off, one identity per app.",
            "Functions: the plan, the timeout, concurrency per instance, Service Bus MaxDeliveryCount, a dead-letter alert, and a retry that matches the idempotency key.",
            "Both: structured logs, a correlation id, no secrets in logs, a test that hits the endpoint from outside the region, and a dashboard that splits dependency duration from your own CPU.",
        ]},
        {"t": "code", "text": """// Readiness includes the dependency. Liveness does not.
// A database blip must not restart every instance.
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>(tags: new[] { "ready" });

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => !check.Tags.Contains("ready")
});
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});"""},
        {"t": "warn", "title": "What breaks", "text": "Pointing the platform health probe at a check that opens SQL means a brief database failure restarts the fleet. Logging the Authorization header or the connection string turns the dashboard into a leak."},
        {"t": "lead", "title": "Say this", "text": "Always On, affinity off, HTTPS only, ready versus live split. Functions get a plan, a timeout, a delivery count, and a dead-letter alert. Logs have a correlation id and no secrets."},
        {"t": "break"},
    ]
