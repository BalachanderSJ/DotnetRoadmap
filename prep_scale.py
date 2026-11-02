# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Web API scalability"},
        {"t": "p", "text": "The Orders API is assumed to peak at about 50 requests a second. That number comes from the study guides. It is an assumption, and you say so. About 2 million orders a year is the other assumption. A year has 31,536,000 seconds, so 2,000,000 orders is about 0.063 orders a second on average, roughly one order every 16 seconds. Peak and average are different shapes. Most of the 50 requests are reads. If you assume four reads for every write, peak is about 40 reads and 10 writes a second. Label that split as an assumption too. The read target in these guides is p95 under 300 milliseconds. Email is within a minute, off the request."},
        {"t": "p", "text": "If a contract says 99.9 percent over a 30-day month, the arithmetic is 30 times 24 times 60, which is 43,200 minutes, times 0.001, which is about 43 minutes. That is a budget you can say out loud. It is not the Orders API's measured availability. You spend those minutes on a failover, a bad deploy, or a dependency. A retry storm spends them for you."},

        {"t": "h2", "text": "Stateless instances"},
        {"t": "p", "text": "A stateless API keeps the durable facts outside the process. The order is in Azure SQL. The idempotency row is in Azure SQL. A shared cache, if you add one, is Redis or another store every instance can see. The process may keep a short-lived memory cache of a public catalog, and it may lose that cache on recycle. The next request still works."},
        {"t": "p", "text": "Sticky sessions exist to hide state you stored by accident: an in-memory session, a static cart, a dictionary of locks. ARR affinity pins the caller to one App Service instance. The pin survives after that instance is sick, and it defeats the even spread you wanted when you scaled out. Move the state out, then turn affinity off. Affinity is not the design for POST /orders."},
        {"t": "p", "text": "Horizontal scale adds instances of the same site. Each instance has its own memory, its own static fields, and its own connection pool. A lock in a static object covers one process. The second instance has its own lock and will enter the same critical section. Shared coordination is a unique index, a SQL row, or a Service Bus session you chose on purpose."},
        {"t": "table", "headers": ["State", "Where it lives at 2 or more instances"], "rows": [
            ["Order, lines, idempotency key", "Azure SQL, in one transaction"],
            ["User session for the Angular app", "BFF cookie backed by a server store, or a distributed cache"],
            ["Catalog cache", "Per-process output cache, or Redis when every instance must agree"],
            ["Partner rate-limit counters", "In-process if the limit is per instance and you say so; a gateway when the budget is global"],
            ["Email send", "Service Bus, then the Function, with a processed-message row"],
            ["Lock around 'create order'", "Unique index on the idempotency key, not a Dictionary"],
        ]},

        {"t": "h2", "text": "Async, the thread pool, and sync-over-async"},
        {"t": "p", "text": "ASP.NET Core runs requests on the thread pool. An await on SQL or HTTP releases the thread for the duration of the IO. The thread returns when the operation completes. That is async all the way: the action is async, EF is ToListAsync or SaveChangesAsync, HttpClient is awaited, and the CancellationToken from the request is passed into each of them."},
        {"t": "p", "text": "Sync-over-async is .Result, .Wait(), or GetAwaiter().GetResult() on work that is already asynchronous. The thread stays borrowed while the IO runs. Under a context that needs that same thread to finish the operation, it can deadlock. Under load, it starves the pool. The pool adds threads slowly. Requests queue inside the server. Latency climbs while CPU still looks calm. That chart is the clue."},
        {"t": "p", "text": "A small illustration, not a measurement of this API. At 50 requests a second, a call that blocks a thread for 200 milliseconds of SQL holds about 10 threads on average, because 50 times 0.2 is 10. A call that blocks for a hung 10 second dependency represents 50 times 10, or 500 threads of waiting. The pool will not grow to 500 on the spot. New requests wait, and the probe can time out. The read target remains p95 under 300 milliseconds, with the thread released during the SQL wait."},
        {"t": "code", "text": """[HttpPost("/orders")]
public async Task<IActionResult> Post(CreateOrderRequest body, CancellationToken ct)
{
    var tenantId = RequireTenant(User);
    var result = await handler.HandleAsync(body.ToCommand(tenantId), ct);
    return ToActionResult(result);
}

// The bug in review:
// var order = handler.HandleAsync(command, ct).Result;"""},
        {"t": "warn", "title": "Interview trap", "text": "Wrapping a synchronous block in Task.Run inside the request. That still occupies a pool thread, and now you have two. Also catching every exception from .Result and returning 500, which hides the deadlock until the next spike. The fix is async to the edge, including the filter and the middleware you added."},

        {"t": "h2", "text": "Timeouts, retries, jitter, and a circuit breaker"},
        {"t": "p", "text": "Every outbound call has a timeout shorter than the caller's patience and shorter than the gateway's timeout, so you return a controlled error. Retry only when the call is safe to repeat. A GET of a catalog price can retry. A POST that creates a charge retries only when that call carries an idempotency key the other side honors. Jitter spreads retries so a blip does not become a synchronized stampede. A circuit breaker opens after a failure ratio you chose, and it fails fast for a cool-down so the sick dependency can recover."},
        {"t": "p", "text": "The numbers below are an example policy, the same kind of sketch the deep dive uses. They are not a quota. You set them from the dependency's latency and the user's budget, and you review them like code."},
        {"t": "code", "text": """builder.Services.AddHttpClient<CatalogClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Catalog:BaseUrl"]!);
    client.Timeout = Timeout.InfiniteTimeSpan;
})
.AddStandardResilienceHandler(options =>
{
    options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(2);
    options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(5);
    options.Retry.MaxRetryAttempts = 2;
    options.Retry.UseJitter = true;
    options.CircuitBreaker.FailureRatio = 0.5;
    options.CircuitBreaker.MinimumThroughput = 20;
});"""},
        {"t": "p", "text": "HttpClient.Timeout is disabled here so it does not race the attempt timeout inside the resilience handler. The attempt timeout is the per-try budget. The total timeout bounds the tries together. MinimumThroughput of 1 would open the breaker on a single blip. SQL uses a command timeout and EnableRetryOnFailure for transient errors, including a brief Azure SQL failover. The retry must re-run a unit of work that is safe to re-run. The idempotency unique key is what makes a retried insert safe. When the policy is exhausted, return 503 or a problem document. Log the dependency name and the correlation id."},

        {"t": "h2", "text": "Caching"},
        {"t": "p", "text": "Response caching follows HTTP cache headers. A public catalog GET can send Cache-Control: public with a short max-age. An order GET sends Cache-Control: no-store. A shared cache that stores /orders/10 without varying on the caller will serve tenant A's order to tenant B. Authorization headers usually keep shared caches from storing the response. Set the header you mean, and do not rely on a default you have not read."},
        {"t": "p", "text": "Output caching remembers the generated response on the server. The built-in store is in the process, so ten instances are ten caches. Use it for an anonymous catalog response with a short expiry. An order response is personalized. If you output-cache it, the vary key includes the tenant claim. A cache entry whose key omits the tenant is a data leak that scales with your hit rate."},
        {"t": "p", "text": "IDistributedCache, usually Redis, is the store every instance shares. The key includes the tenant and the id. You choose the TTL. Reference data that is the same for many callers, and a tenant's own lookup with the tenant in the key, are the safe cases. An order total that a second POST can change needs a TTL you can explain, or you delete the key on write. A cached authorization decision needs the user or the client id in the key."},
        {"t": "p", "text": "A cache stampede is many requests missing the same key at once and all running the SQL. It happens on expiry and on a cold start after a deploy. At the assumed 50 requests a second, a single popular catalog key that expires can turn into 50 identical queries in that instant. Mitigate with a single-flight lock per key, a slightly random TTL so keys do not expire together, or by serving the previous value while one request refreshes. Across instances the lock is a short-lived Redis set-if-not-exists, not a static Dictionary."},
        {"t": "code", "text": """builder.Services.AddOutputCache();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration["Redis:Connection"];
});

app.MapGet("/catalog/{sku}", GetSku)
    .CacheOutput(p => p.Expire(TimeSpan.FromSeconds(30)));

var key = $"orders:{tenantId}:{orderId}";
var cached = await cache.GetAsync(key, ct);"""},
        {"t": "p", "text": "The catalog route is anonymous reference data. GET /orders stays out of that policy. The Redis connection string is configuration, not a value in the git file. HybridCache, from .NET 9 onward, is the API for a local cache in front of a distributed cache. The key still includes the tenant."},

        {"t": "h2", "text": "Pagination, cancellation, bounded concurrency, idempotency"},
        {"t": "p", "text": "Keyset pagination seeks from the last (CreatedUtc, Id) the client saw. Offset asks SQL to read and discard the skipped rows. A deep offset at 50 requests a second is a scan you scheduled on purpose. Cap the page. The SQL section writes the keyset statement. The API contract is the cursor, not a page number the client invents by multiplying."},
        {"t": "p", "text": "Pass the request CancellationToken to EF and to HttpClient. A caller who disconnects should stop the SQL command. Catching the cancellation and returning 500 turns a hang-up into an error budget incident. Link a shorter timeout only when you mean a budget inside the request:"},
        {"t": "code", "text": """using var budget = CancellationTokenSource.CreateLinkedTokenSource(ct);
budget.CancelAfter(TimeSpan.FromSeconds(2));
var page = await queries.ListAsync(tenantId, cursor, budget.Token);"""},
        {"t": "p", "text": "Bounded concurrency is the cap on fan-out inside one request. Fifty lines, each calling a tax service with no limit, is 50 outbound calls per order. At 10 order writes a second that is 500 outbound calls a second, and that split was already an assumption. Parallel.ForEachAsync with a small MaxDegreeOfParallelism is the local cap. The resilience handler's timeout and breaker are the other cap. Queue limit zero on a rate limiter rejects with 429 instead of parking work on the thread pool."},
        {"t": "p", "text": "Idempotency under concurrency is a unique key on (TenantId, KeyValue), inserted in the same transaction as the order. Two retries arrive together. One insert wins. The other gets the unique violation, reads the stored row, and returns it when the request hash matches. A different hash is 409. An in-memory dictionary of keys works on one instance during a demo and creates two orders on two instances."},
        {"t": "code", "text": """await Parallel.ForEachAsync(lines, new ParallelOptions
{
    MaxDegreeOfParallelism = 4,
    CancellationToken = ct
}, async (line, token) =>
{
    line.Tax = await tax.QuoteAsync(line.Sku, line.Quantity, token);
});"""},

        {"t": "h2", "text": "N+1 at the API boundary"},
        {"t": "p", "text": "N+1 is one query for the page and one query per row. EF does it when you loop and touch a navigation that was not loaded, or when the Angular app calls GET /orders/{id}/lines for every row of a list it already displayed. The fix at the API is one shaped query: a projection, or Include with AsSplitQuery when a join would multiply rows, or a SQL statement you wrote. AsNoTracking belongs on the read. Tracking every line of a list allocates a graph you will not save."},
        {"t": "code", "text": """var page = await db.Orders.AsNoTracking()
    .Where(o => o.TenantId == tenantId)
    .OrderByDescending(o => o.CreatedUtc).ThenByDescending(o => o.Id)
    .Take(50)
    .Select(o => new OrderListItem(o.Id, o.Number, o.Total, o.Status))
    .ToListAsync(ct);

var detail = await db.Orders.AsNoTracking()
    .Where(o => o.TenantId == tenantId && o.Id == id)
    .Include(o => o.Lines)
    .AsSplitQuery()
    .SingleOrDefaultAsync(ct);"""},
        {"t": "p", "text": "Drop to SQL when the LINQ still produces a loop, a client-evaluated filter, or a plan you cannot explain. The list endpoint returns the columns the screen needs. The Angular client renders that payload. It does not issue one HTTP call per order id to fill the grid."},

        {"t": "h2", "text": "Backpressure"},
        {"t": "p", "text": "429 means the caller is over a budget you defined. Return Retry-After when you have a retry interval. 429 is not 500 and not 503. A limiter with a queue of thousands accepts work you cannot do and holds threads. Queue limit zero fails the extra call immediately. An in-process window is per instance. At two instances, a partner can get about twice the per-instance budget. Say that. A global budget lives at a gateway in front. Turning on ARR affinity to make the memory counter look global pins the partner to one instance."},
        {"t": "p", "text": "Unbounded fan-out is the other failure. One request starts a task per line, per shipment, and per notification, with no cap, and each task opens SQL. The assumed 50 requests a second become thousands of concurrent commands. Bound the parallelism. Cap the page. Let Service Bus carry the work that can finish after the 201."},
        {"t": "code", "text": """builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("partner", limiter =>
    {
        limiter.PermitLimit = 100; // team choice, per instance, not an Azure default
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
    });
});"""},

        {"t": "h2", "text": "What does not scale"},
        {"t": "b", "items": [
            "A static Dictionary used as a lock or as the idempotency store. The second instance has an empty one.",
            "A static mutable list used as a catalog cache. It tears under concurrency and diverges across instances.",
            "SaveChanges, or an HTTP call, inside a loop over order lines when one set-based write would do.",
            "The Angular app calling SQL indirectly once per row: a list of ids, then a GET per id.",
            "A HostedService timer inside the API that sends mail. It runs once per instance.",
            "An unbounded SqlClient pool times the maximum instance count. That product is the connection count you compare with the Azure SQL limit document.",
        ]},
        {"t": "p", "text": "The SqlClient default maximum pool size is 100 per process. Confirm the connection string you ship, because a teammate may have raised it. If the plan maximum is 8 instances, 8 times 100 is 800 connections from this app, before the Function app opens its own pools. You compare 800 with the connection limit on the current Azure SQL tier. You look up the limit. You do not recite one from memory."},

        {"t": "h2", "text": "Questions and answers"},
        {"t": "qa", "q": "What does stateless mean for the Orders API, and when do sticky sessions show up?",
         "a": "Stateless means any instance can serve the next request. The order, the idempotency key, and the outbox row are in Azure SQL. The process keeps no cart and no session. Sticky sessions show up when someone stored that state in memory and then turned on ARR affinity so the same instance would see it. I move the state out and turn affinity off. A load balancer pin is a temporary patch during an incident, and I write down the date I will remove it.",
         "lead": "The question I ask of every field is: what happens on the second instance? If the answer is we only run one, the follow-up is what happens when the platform restarts that one."},
        {"t": "qa", "q": "What has to live outside the process when you scale App Service from one instance to several?",
         "a": "Session, a cache that must be coherent, distributed locks, and anything a timer does exactly once. Files on local disk are per instance. Static fields are per process. The SQL connection count becomes pool size times instance count, and that has to fit the database tier. Rate limits kept in memory become per-instance limits, which is acceptable only when the contract says so. The email worker stays on Service Bus so it does not scale just because the API scaled, and it does not starve the API when the mail provider slows down.",
         "lead": "I size the pool against the maximum instance count on the plan, not against the two instances we happen to be running today."},
        {"t": "qa", "q": "Explain async all the way and thread-pool starvation.",
         "a": "The request thread should be busy only while we run CPU. Await releases it during SQL and HTTP. At the assumed 50 requests a second, blocking for a 200 millisecond call holds on the order of 10 threads. Blocking for a 10 second hang holds on the order of 500 threads of wait, and the pool grows slowly, so requests queue and latency rises before CPU does. I pass CancellationToken into EF and HttpClient. I keep controllers, handlers, and middleware async. The 200 milliseconds and 10 seconds are illustrations. The read target I will defend is p95 under 300 milliseconds.",
         "lead": "If p95 is high and CPU is low, I look for blocked threads and a slow dependency before I add instances. More instances of a blocked thread multiply the blocked threads."},
        {"t": "qa", "q": "What is sync-over-async, and why is Task.Run not the repair?",
         "a": "Sync-over-async blocks a thread on asynchronous work with Result, Wait, or GetResult. On ASP.NET Core it can deadlock when a single-threaded context is waiting for itself, and it starves the pool when it merely blocks. Task.Run moves the block onto another pool thread. The request still occupies a thread until the inner work finishes, and you have added scheduling. The repair is HandleAsync awaited from an async action, with the same CancellationToken.",
         "lead": "In review, Result and Wait on an async call are a blocking comment. I ask for the await, not for a wrapper."},
        {"t": "qa", "q": "How do timeouts, retries, jitter, and a circuit breaker fit together?",
         "a": "The attempt timeout bounds one try. The total timeout bounds the whole pipeline. I retry idempotent calls, a small number of times, with jitter, so a blip does not wake every instance in the same millisecond. I do not retry POST /orders from a client that has no idempotency key. The breaker opens after a failure ratio and a minimum throughput I can say, and then it fails fast. The sketch in this section is an example policy: two retries, a two-second attempt, minimum throughput 20. SQL transient retries go through the execution strategy and a unique idempotency key. When the budget is gone I return 503.",
         "lead": "Retries without a budget attack the dependency that is already sick. I would rather fail inside a few seconds than hold a thread for half a minute."},
        {"t": "qa", "q": "Response cache, output cache, or Redis. Which one, for what?",
         "a": "Response caching is HTTP. Public catalog responses can be cached by intermediaries for a short max-age. Order responses are no-store. Output caching stores the server's response. The default store is the process, so it is a latency help for anonymous GETs, and it is not one shared picture of a tenant's orders. Redis is the shared store. The key includes tenant id and the entity id. I cache reference data, and I cache a tenant's read model only with a TTL or an invalidation story. I leave authorization results out of a key that omits the caller.",
         "lead": "If I cannot say who is allowed to receive a cached byte, I do not cache it. A cross-tenant hit is worse than a slow query."},
        {"t": "qa", "q": "What is a cache stampede, and what do you do about it?",
         "a": "Many requests observe a miss at the same moment and all run the backing query. Expiry of a hot catalog key, or a deploy that empties memory, does it. At about 50 requests a second that key can produce a burst of identical SQL. I single-flight the refresh per key, add jitter to the TTL, or serve a stale value while one caller refreshes. The cross-instance lock is a short Redis lock. A static lock object single-flights only the current process.",
         "lead": "I mention stampede when I propose a one-minute cache on a popular key. The cache is a kindness to SQL only if the miss path stays single."},
        {"t": "qa", "q": "How do pagination, cancellation, and idempotency behave under load?",
         "a": "The list is a keyset on CreatedUtc and Id, with a cap, matching the index in the SQL section. Offset on a deep page reads the skipped rows on every request. CancellationToken flows to EF and HTTP so a disconnected client aborts the command. Two POSTs with the same idempotency key hit a unique index inside the order transaction. One wins, the other replays the stored response when the body hash matches. An in-memory set of keys does not survive the second instance or the recycle.",
         "lead": "Paging, a maximum page size, and the idempotency unique key are acceptance criteria. I do not schedule them for a later hardening sprint."},
        {"t": "qa", "q": "Where does N+1 show up, and when do you drop to SQL?",
         "a": "It shows up as a list query plus a query per order for lines, often from a loop in C# or from the Angular client calling one endpoint per row. I project the list with AsNoTracking and a Take. I load one order's lines with Include and AsSplitQuery when the join would duplicate parent columns. I drop to a single SQL statement when I still cannot get one round trip or the plan is wrong. The client receives a page DTO. It does not reassemble the page with fifty GETs.",
         "lead": "I look at the SQL trace for a page load, not only at the C#. Fifty similar commands for one screen is the finding."},
        {"t": "qa", "q": "How do you apply backpressure, and what is unbounded fan-out?",
         "a": "Backpressure is a 429 with Retry-After, from a limiter whose queue length is zero, so extra calls fail instead of waiting. A fixed window of 100 per minute per instance is a team choice I label as a choice, the same way the other notes in this repo do. It is not an Azure default. Two instances mean two windows. A shared budget is a gateway. Unbounded fan-out is one request that starts unlimited parallel SQL or HTTP. I cap it with Parallel.ForEachAsync, a small degree of parallelism, and the same cancellation token. Work that can finish later goes to Service Bus.",
         "lead": "I would rather return 429 to one partner than let that partner hold the SQL connection pool for everyone else."},
        {"t": "qa", "q": "Name the designs that fall over when the second instance arrives.",
         "a": "An in-memory dictionary of idempotency keys or locks. A static mutable cache. A timer hosted in the API. ARR affinity left on to make those bugs look stable. Chatty EF that saves once per line. An Angular screen that calls the API once per cell. A connection pool copied unchanged onto a higher instance maximum. Each of those is correct on a single process and wrong at the assumed peak once you scale out for availability.",
         "lead": "Two instances is my minimum when I want a deploy or a fault to leave one process up. That is an availability choice. The code has to deserve it."},
        {"t": "qa", "q": "At about 50 requests a second, what do you actually size?",
         "a": "I label 50 a second as the study assumption, mostly reads, with about 2 million orders a year underneath it, which is about one order every 16 seconds on average. I watch p95 against the 300 millisecond read target, CPU, the thread-pool queue, dependency duration, and SQL. I compare pool size times maximum instances with the Azure SQL connection limit in the tier document. I do not invent an instance count. I add an instance when the measurement says the process is the bottleneck, and I keep two when I need one to survive a recycle. If someone cites 99.9 percent, I translate a 30-day month into about 43 minutes and ask which failures are allowed to spend that budget.",
         "lead": "I size from the chart and the limit document. I can do the 43-minute arithmetic in the room. I cannot do a fake capacity number."},
        {"t": "break"},
    ]
