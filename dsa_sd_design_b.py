# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Part B, Day 6 — Notification fan-out"},
        {"t": "p", "text": "Outcome. You can take the order outbox and fan it out to email, SMS, and push with Service Bus, an idempotent consumer, and a dead-letter path that does not roll back the order."},
        {"t": "p", "text": "Time box. About 3.5 hours. Redraw Day 2's transaction in ten minutes. Then the topic, the delivery row, and the crash after the provider accepts the message. Spend the last hour speaking the twenty-minute version, and answer a poison-message interruption without deleting the order."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "When an order is placed, the customer may get an email, an SMS, and a push. Each channel fails on its own. A retry must not send a second email. Design the fan-out. The order API from Day 2 stays the system of record."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "One OrderPlaced message per committed order. The write rate sits inside the existing assumption of about 50 requests a second at peak, and most of those requests are reads, so the mail volume is the order-create slice of that number, not a new million-message stream. Email within a minute remains the target you are willing to say out loud. SMS and push use the same target unless the business says one of them can lag longer. The provider can take an idempotency key. If a provider cannot, you say that the remaining duplicate window is the crash after their accept and before your commit, and you pick a provider call that is safe to repeat or you record the send more carefully. You do not invent a Service Bus quota."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "There is no public POST /notify that the partner can spam. The notification is a consequence of the order commit. Support gets GET /orders/{id}/notifications, a list of channel, state, and last error, paged if you must, from a table the API can read. The customer does not get a webhook in this slice. If they ask for one, it is another subscription with the same dedupe rules, and the receiver still has to dedupe. 202 is the wrong code for the original POST /orders. That call remains 201, because the order is created. Mail is not the definition of created."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE TABLE orders.NotificationDeliveries
(
    Channel        nvarchar(16)     NOT NULL,
    MessageId      nvarchar(128)    NOT NULL,
    OrderId        uniqueidentifier NOT NULL,
    TenantId       uniqueidentifier NOT NULL,
    State          nvarchar(16)     NOT NULL, -- Sending, Sent, Failed
    AttemptCount   int              NOT NULL,
    UpdatedUtc     datetime2        NOT NULL,
    CONSTRAINT PK_NotificationDeliveries PRIMARY KEY (Channel, MessageId)
);"""},
        {"t": "p", "text": "The primary key is the dedupe. Channel plus the Service Bus message id, which is the outbox id from Day 2, so a redelivery of the same publish is the same row. A second business event, such as OrderShipped, is a new outbox id and a new delivery. Do not dedupe on order id alone or you will drop the shipping notice."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "The order transaction does not include the provider. Day 2 already committed the outbox. The relay publishes one message to a Service Bus topic. Subscriptions named email, sms, and push each get a copy, each with its own peek-lock and its own dead-letter queue. A SQL filter on a subscription is how you skip SMS for an order that has no phone number, using a property the relay sets on the message. The filter is a convenience. The consumer still checks the payload."},
        {"t": "p", "text": "The consumer's rule: insert the delivery row as Sending, call the provider with an idempotency key equal to the message id, mark the row Sent, then complete the Service Bus message. The unique key stops two workers. Peek-lock should already allow only one owner, and a lock that expires while the provider is slow is how a second worker appears. The second insert hits the primary key. If the row is Sent, the second worker completes the message and does not call the provider. If the row is Sending and the lease you stored in UpdatedUtc is still fresh, the second worker abandons or simply returns so the lock can expire, and the first worker remains the owner. If Sending is older than the lease you chose, the second worker may take over, and the provider idempotency key is what prevents a second email when the first call actually succeeded."},
        {"t": "p", "text": "That lease interval is your choice, aligned with the lock duration you configured on the subscription. You look up how lock renewal works in the SDK you are on, and you renew a lock for a slow provider instead of hoping the default covers it. You do not quote a default duration from memory."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "A transient provider error throws or abandons. Service Bus redelivers until the max delivery count you set on the subscription. A small count is a team choice so a poison message reaches the dead-letter queue during the incident rather than the next day. You read the portal default when you create the subscription, and you set the value on purpose. A malformed payload, an order id that does not exist, or an address the provider says is permanently invalid is poison. You dead-letter it with a reason. You do not abandon it in a loop. You do not delete the order. You do not mark the order failed because the SMS failed and the email succeeded. Each channel has its own row. An alert on dead-letter count greater than zero is the page. A replay after the fix uses the same message id so the delivery row still dedupes."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "The consumers are Azure Functions on the isolated worker, one function per subscription or one function with the subscription name bound, whichever your team will actually find in the portal at night. Managed identity reaches Service Bus and SQL. The SQL user app_orders_notify may insert and update NotificationDeliveries and may select the order fields it needs to render the message. It may not alter tables and it may not delete orders. The API user is not this user. Auto-complete is off when the function settles the message itself. The dashboard adds, per subscription, the active message count, the dead-letter count, and the age of the oldest message. Outbox age from Day 2 is still there, because a stuck relay never reaches this topic."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse one queue that the email worker forwards to SMS. A failure in the first consumer then blocks the other channels, and you have built an ordering nobody asked for. You refuse receive-and-delete. You refuse to complete the message before the provider call returns. You refuse to depend only on Service Bus duplicate detection. You refuse a distributed transaction. You refuse to send the three channels inside the order request. A topic with three subscriptions is the fan-out. If you only have email, one queue is enough, and the topic is what you add when the second channel arrives. That is a fair first slice, and you say so."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """{
  "version": "2.0",
  "extensions": {
    "serviceBus": {
      "autoCompleteMessages": false
    }
  }
}

[Function("SendEmail")]
public async Task Send(
    [ServiceBusTrigger("order-events", "email", Connection = "ServiceBus")]
    ServiceBusReceivedMessage message,
    ServiceBusMessageActions actions,
    CancellationToken ct)
{
    if (!TryReadOrder(message, out Guid orderId))
    {
        await actions.DeadLetterMessageAsync(message, deadLetterReason: "BadPayload");
        return;
    }

    var delivery = new NotificationDelivery
    {
        Channel = "email",
        MessageId = message.MessageId,
        OrderId = orderId,
        State = "Sending",
        AttemptCount = 1,
        UpdatedUtc = DateTime.UtcNow
    };

    try
    {
        _db.NotificationDeliveries.Add(delivery);
        await _db.SaveChangesAsync(ct);
    }
    catch (DbUpdateException ex) when (IsUniqueViolation(ex))
    {
        _db.ChangeTracker.Clear();
        if (await AlreadySent("email", message.MessageId, ct))
        {
            await actions.CompleteMessageAsync(message);
            return;
        }
        await actions.AbandonMessageAsync(message);
        return;
    }

    await _email.SendAsync(orderId, idempotencyKey: message.MessageId, ct);
    delivery.State = "Sent";
    delivery.UpdatedUtc = DateTime.UtcNow;
    await _db.SaveChangesAsync(ct);
    await actions.CompleteMessageAsync(message);
}"""},
        {"t": "p", "text": "A permanent provider rejection is a catch you write next to this method: mark the row Failed, dead-letter, do not throw. A transient rejection throws before the complete, so the lock rolls back to an abandon and the Sending row is what the next attempt finds. The next attempt's unique-key path has to be allowed to continue a Sending row whose owner died. The sketch above abandons on any existing row that is not Sent, which is safe when the first worker is still running and slightly slow when it died. Say the lease takeover in the interview even if you do not write every branch on the board. The important line is the provider idempotency key."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. Fan-out is a consequence of OrderPlaced. Volume stays inside the order assumption. One minute is still the mail target.",
            "Minute 2 to 5. No public notify API. Support reads delivery state. POST /orders is still 201.",
            "Minute 5 to 8. Topic order-events, three subscriptions, each with its own dead-letter. Delivery primary key is channel plus message id.",
            "Minute 8 to 13. Insert Sending, call the provider with the message id, mark Sent, then complete. A duplicate key means already done or still in flight.",
            "Minute 13 to 17. Transient abandons. Poison dead-letters. The order stays. Alert on dead-letter depth. Replay keeps the message id.",
            "Minute 17 to 20. Isolated worker, its own SQL user, auto-complete off, peek-lock. You refuse a chain of queues and a two-phase commit.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Deduping on order id and dropping later events. Completing the message and then calling the provider. Receive-and-delete. One shared queue with a hand-rolled fan-out that stops all channels when email throws. Treating a dead letter as a reason to roll back the order. Quoting a lock duration or a duplicate-detection window you have not checked. Leaving auto-complete on and also calling Complete."},
        {"t": "lead", "title": "Say this", "text": "The outbox publishes once to a topic. Each channel is a subscription with its own lock and its own dead-letter. The consumer inserts a delivery row keyed by channel and message id, calls the provider with that id, and only then completes. A poison message waits in the dead-letter queue. The order stays placed."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 7 — Rate limiting and the public gateway"},
        {"t": "p", "text": "Outcome. You can put the ASP.NET Core rate limiter on the order API, return 429, and explain who enforces the limit when more than one instance is running."},
        {"t": "p", "text": "Time box. About 3.5 hours. Write the policy from memory, including the partition key. Then the two-instance arithmetic on a whiteboard: a per-instance window is not a global window. Spend the last hour on where a gateway fits, without naming a price or a quota you would have to look up."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "Partners call the order API from the public internet. Design how you stop one partner from consuming the database. Say what the caller receives, and say which hop enforces the rule."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "The friendly load is still about 50 requests a second at peak for the whole API, and the limiter exists for the unfriendly case. A policy of 100 requests per minute per client application, per instance, is a number you chose so you can talk about it. It is not an Azure default and it is not a capacity plan. You change it after a test, and you write the chosen number down next to the client contract. Anonymous traffic, if you have any, is partitioned by a coarser key and a smaller budget. The read p95 target stays under 300 milliseconds for callers inside the budget."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "Every partner route uses the policy, including POST /orders and the GETs. A rejected call returns 429 with a Retry-After header when the limiter provides a retry interval. The body is a short problem document, not a stack trace. 429 is not 503 and not 500. A client that retries immediately is a client bug, and your Retry-After is the hint. The order idempotency key still matters, because a retry after 429 must not create a second order if the first attempt actually committed and the 429 was a later duplicate. In practice a limited request is rejected before the handler. Say that. The dangerous retry is the timeout, which Day 2 already handles."},
        {"t": "p", "text": "Authentication still returns 401 and authorization returns 403. A caller who fails authentication does not get a 429 instead. A flood of bad tokens is a reason to limit before you spend work on them, which is the gateway's job as well as a coarse limiter at the edge of the app."},
        {"t": "h2", "text": "Data"},
        {"t": "p", "text": "The built-in limiter keeps its counters in memory in the process. There is no SQL table in the first slice. The partition key is the Entra application id, the azp claim or the appid claim, not a field in the JSON and not the raw IP address of a partner who shares a NAT with the rest of their company. IP is the key only for traffic that has no token. A successful order still writes the Day 2 tables. The limiter does not become a second source of truth for idempotency."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "A fixed window is easy to explain and allows a burst at the boundary between two windows. A sliding window or a token bucket smooths that burst and is still an in-process structure. You start with a fixed window, queue limit zero, so an over-budget call fails immediately instead of occupying a thread. A concurrency limiter is the other knob, for a whole instance, so a flood cannot schedule unbounded work even if the per-client windows are wide. Both can be on. The endpoint policy and a global limiter both run."},
        {"t": "p", "text": "Two instances means two independent windows. A client whose policy is 100 per minute per instance can do about 200 per minute if the load balancer spreads them evenly, and more if they pin to one instance and you misread the metric. That is acceptable only if you meant it. A shared budget across instances lives in a place that sees every call. That place is the gateway in front: Azure Front Door, Azure API Management, or a reverse proxy you already operate. You look up that product's current limits when you pick it. You do not recite them. The app limiter stays, because a caller who reaches an instance directly, or a misconfigured route that bypasses the gateway, must still be unable to melt SQL."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "The limiter fails closed in the sense that a request over budget is rejected. A process recycle resets the in-memory window, so a deploy gives everyone a fresh budget. That is fine. A limiter bug that rejects everyone is an incident: you would rather have a config flag to disable the policy than a code change, and you watch 429 rate next to 500 rate so you can tell a limit from a crash. SQL is not your rate limiter. If SQL is the thing returning errors under load, the limiter was set too high or it was not on the right route. The health check stays cheap and is excluded from the partner policy, or a busy partner can push the instance out of rotation by starving the probe. Confirm the probe path is anonymous and not limited by the partner key."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "The gateway is the shared door. It terminates TLS, it can reject traffic that has no token if you configure it to, and it enforces the budget that is in the contract. The app always validates the token itself. A gateway that checked the token is a performance help, not a trust boundary you rely on alone. App Service keeps ARR affinity off. You do not turn affinity on to make an in-memory rate limit look global. That would pin a partner to one instance and make the other instance idle, and it would still be wrong the day you scale. Managed identity is unchanged. The policy numbers live in configuration so a change is not a recompile, and the configuration is still a choice you review."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse a limiter that only exists at the gateway. You refuse a limiter that only exists in one process and is described to the partner as a global contract. You refuse to build a new ASP.NET gateway service for this. If the estate already has YARP in front for a migration, a limit can live there too, and the app still has its own. You refuse a custom distributed limiter in Redis as the first design. You add a shared store only after the gateway cannot express the rule. You refuse to queue limited requests inside the app and call that protection. A queue of waiters is how a flood becomes a thread-pool incident."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.OnRejected = async (context, ct) =>
    {
        if (context.Lease.TryGetMetadata(MetadataName.RetryAfter, out TimeSpan retryAfter))
        {
            context.HttpContext.Response.Headers.RetryAfter =
                Math.Ceiling(retryAfter.TotalSeconds).ToString(CultureInfo.InvariantCulture);
        }
        await context.HttpContext.Response.WriteAsync("Too many requests.", ct);
    };

    options.AddPolicy("per-client", httpContext =>
    {
        string key = httpContext.User.FindFirst("azp")?.Value
            ?? httpContext.User.FindFirst("appid")?.Value
            ?? "anonymous";

        return RateLimitPartition.GetFixedWindowLimiter(
            key,
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 100, // team policy, per instance, not an Azure default
                Window = TimeSpan.FromMinutes(1),
                QueueLimit = 0
            });
    });
});

app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();

[EnableRateLimiting("per-client")]
[HttpPost("/orders")]
public Task<IActionResult> Create(CancellationToken ct) => /* Day 2 */;"""},
        {"t": "code", "text": """# Policy you chose. Change it in config, review it like a contract.
RateLimit:
  PermitLimit: 100
  WindowSeconds: 60
  QueueLimit: 0"""},
        {"t": "p", "text": "The middleware order puts authentication first so the partition key can be the application id. A flood of unauthenticated calls still spends the authentication middleware. The gateway is what sheds that flood before it reaches the instance. A global concurrency limiter, with a permit count you set from a load test rather than from a guess you memorize, is the backstop on the instance. Exclude the health path."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. Public partners, the 50 request assumption for friendly traffic, and a per-client policy you label as a choice.",
            "Minute 2 to 6. 429 and Retry-After. 401 and 403 stay what they are. The handler does not run when the limit rejects.",
            "Minute 6 to 10. In-memory fixed window, queue limit zero, partition key from the token. IP only when there is no token.",
            "Minute 10 to 14. Two instances mean two budgets. The contract's shared number is enforced at the gateway. The app limit stays for bypass.",
            "Minute 14 to 17. Recycle resets the window. Health probes are not in the partner policy. SQL is not the limiter.",
            "Minute 17 to 20. You refuse gateway-only, app-only sold as a global contract, a homegrown gateway, and a Redis limiter as the opening move.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Returning 500 when the limit trips. Using the JSON tenant or the client-supplied api key header as the only partition key when the token already has an app id. Turning on ARR affinity so the memory counter looks stable. Describing a per-instance window as a global guarantee. Quoting a Front Door or API Management number you have not opened the document for. Rate limiting by queuing thousands of requests."},
        {"t": "lead", "title": "Say this", "text": "The app uses the built-in fixed window, partitioned by the Entra application id, and it returns 429. That window is per instance. The shared contract is enforced at the gateway in front, and the app still limits so a bypass cannot melt SQL. I look up the gateway's limits when I pick the product. I do not put a queue of waiters in the process."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 8 — A URL shortener"},
        {"t": "p", "text": "Outcome. You can design a redirect service in ASP.NET Core: unguessable keys, a cache in front of a primary-key lookup, and a plan for one code that suddenly gets all the traffic."},
        {"t": "p", "text": "Time box. About 3.5 hours. This day is the deep one. Write create and resolve from memory, including the collision retry and the 302. Then spend a full hour on the hot key only: what is cached, where, and what a second instance changes. The twenty-minute version should still leave five minutes for the hot key. If you run out of time, you cut the analytics story, not the redirect."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "Design a service that stores a long URL and redirects a short code to it. Creation is rare. Redirect is the hot path. One code may become popular. You are not designing a general pastebin, and you are not counting every click in the redirect transaction."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "These numbers are for this design, and they are assumptions, separate from the order API. About 200 redirects a second at peak, about 5 creates a second, a cache-hit p95 under 50 milliseconds, a cache-miss p95 under 300 milliseconds. One region. Links are unlisted: guessing a code should not be practical. Targets change rarely. A 10-second cache of a target is an acceptable staleness budget for a redirect, and you label those 10 seconds as your choice. Expiry is a timestamp on the row, not a cache feature. You are not promising a click count that is exact to the second."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "POST /links takes an absolute http or https URL and returns 201 with the code and the short URL. 400 when the target is missing, relative, or a scheme you do not redirect to. GET /{code} returns 302 with a Location header, 404 when the code is unknown, and 410 when the row exists and is expired. You use 302, not 301. A 301 is cached hard by clients, and you will not be able to expire or change the target. The redirect target is the value you stored, never a URL from the query string. That is how this stays a shortener and does not become an open redirect. A stats route, if you add one, is not on the redirect path and can be minutes behind."},
        {"t": "h2", "text": "Data"},
        {"t": "code", "text": """CREATE TABLE links.Links
(
    Code       varchar(12)      NOT NULL CONSTRAINT PK_Links PRIMARY KEY,
    TargetUrl  nvarchar(2048)   NOT NULL,
    CreatedUtc datetime2        NOT NULL,
    ExpiresUtc datetime2        NULL
);"""},
        {"t": "p", "text": "The code is the primary key. It is 7 characters from a 62-symbol alphabet, generated with RandomNumberGenerator, not with a guessable identity column. Seven characters is a choice: the space is 62 to the 7th, about 3.5 trillion codes, which is mathematics, not an Azure limit. You still handle a primary-key collision, because the check is cheap and the unique index is the real guard. A sequential integer encoded into base62 is shorter to generate and easier to scan. You refuse it for unlisted links. Modulo bias exists if you take a random byte and reduce it modulo 62. For this sketch the bias is small, and if they push, you switch to rejection sampling: discard a byte at or above the largest multiple of 62 that fits in a byte. Say that you know the bias is there."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "Create is a single insert. There is no outbox, because nothing else must happen for the link to be real. A collision rolls back that insert and tries a new code, with a small attempt limit, then 503 if you somehow cannot find a free code. You will not hit that limit at 5 creates a second in a space this large. Redirect is a read. The cache is an optimization of a primary-key lookup. SQL remains the record. A cache hit can be at most the staleness budget behind an update or a delete. If you need a taken-down link to die everywhere immediately, you delete it from SQL and you accept that a per-instance cache can still redirect until the local entry expires, or you put a distributed cache in front and delete the key. Immediate global revocation is the requirement that justifies the distributed cache. A viral cat picture is not."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "SQL down and a warm cache: hits still redirect, misses return 503. SQL down and a cold cache: 503. An unknown code is a 404, and you cache that negative answer for a short budget, for example 30 seconds, so a scanner walking random codes does not pin those misses forever and does not hammer SQL. The 30 seconds is your choice. The race is a code that was probed before it was created. With random 7-character codes that race is rare, and a short negative TTL is why you can live with it. A hot key is one code that draws a large fraction of the 200 redirects a second. A primary-key lookup of one row can take that rate. The failure is a stampede when the cache entry expires and every instance misses together, or a design that counts a click in the same transaction as the redirect and turns a read into a write hotspot on one row."},
        {"t": "p", "text": "You keep a small local cache even if a distributed cache exists, with the 10-second budget, so the hottest code is served from the process. The distributed cache, if you add one, absorbs the misses of many instances. You do not take a distributed lock on the read path. One instance missing and querying SQL by primary key is cheap. If you measured a stampede, a single-flight lock inside the process is the first tool, and it only collapses the misses on that instance. Say the measurement before you add the lock."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "The API runs on App Service, affinity off, more than one instance. The local cache is therefore a per-instance cache, and that is what you want for the hot key: each instance holds the popular code and does not coordinate. Managed identity reaches Azure SQL. The app user can insert and select links and cannot alter. There is no Function in the first slice. Click analytics, if required, is a sampled write or a message, consumed off the redirect path, and it is allowed to lose samples. The dashboard is redirect latency, cache hit rate, SQL duration, and 404 rate. A sudden rise in 404 rate is a scanner or a bad deploy, and you want to see it. Health checks the database and is not redirected."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse a 301. You refuse a sequential public code. You refuse to increment a click counter in the redirect transaction. You refuse a distributed lock around every read. You refuse to generate the code on the client and trust it. You refuse to put the target URL in the query string and redirect there. You refuse a cache that has no tenant or owner only if this service is multi-tenant: the code itself is the secret, and the code is globally unique in this design, so the key is the code. If two tenants could claim the same code, the code would include a tenant, and this design does not do that. One global namespace of unguessable codes is the product."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """public static string NewCode(int length = 7)
{
    const string Alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    Span<char> chars = stackalloc char[length];
    Span<byte> bytes = stackalloc byte[length];
    RandomNumberGenerator.Fill(bytes);
    for (int i = 0; i < length; i++)
        chars[i] = Alphabet[bytes[i] % Alphabet.Length];
    return new string(chars);
}

app.MapPost("/links", async (CreateLink body, LinksDb db, CancellationToken ct) =>
{
    if (!Uri.TryCreate(body.TargetUrl, UriKind.Absolute, out Uri? uri)
        || uri.Scheme is not ("https" or "http"))
        return Results.Problem(statusCode: 400, title: "Target must be an absolute http(s) URL.");

    for (int attempt = 0; attempt < 5; attempt++)
    {
        var link = new Link { Code = NewCode(), TargetUrl = uri.AbsoluteUri, CreatedUtc = DateTime.UtcNow };
        db.Links.Add(link);
        try
        {
            await db.SaveChangesAsync(ct);
            return Results.Created($"/links/{link.Code}", new { code = link.Code });
        }
        catch (DbUpdateException ex) when (IsUniqueViolation(ex))
        {
            db.ChangeTracker.Clear();
        }
    }
    return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
});

app.MapGet("/{code}", async (string code, LinkCache cache, CancellationToken ct) =>
{
    string? target = await cache.Resolve(code, ct);
    return target is null ? Results.NotFound() : Results.Redirect(target, permanent: false);
});"""},
        {"t": "code", "text": """public async Task<string?> Resolve(string code, CancellationToken ct)
{
    if (_cache.TryGetValue(code, out CachedLink? cached))
        return cached!.Found ? cached.Target : null;

    var row = await _db.Links.AsNoTracking().FirstOrDefaultAsync(l => l.Code == code, ct);
    if (row is null || (row.ExpiresUtc is not null && row.ExpiresUtc <= DateTime.UtcNow))
    {
        _cache.Set(code, new CachedLink(false, null), TimeSpan.FromSeconds(30));
        return null;
    }

    // 10 seconds: staleness budget for a hot redirect, per instance.
    _cache.Set(code, new CachedLink(true, row.TargetUrl), TimeSpan.FromSeconds(10));
    return row.TargetUrl;
}

public sealed record CachedLink(bool Found, string? Target);"""},
        {"t": "p", "text": "Results.Redirect with permanent false is a 302. The negative cache stores a record, not a null, because the memory cache is a poor place to store null and a missed null is indistinguishable from a miss. Span in NewCode avoids a heap buffer for a 7-byte draw. The modulo line is the one you replace with rejection sampling if they ask about bias. Do not do that replacement until they ask. The first version has to be correct about the unique index, the scheme check, and the 302."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 2. 200 redirects a second, 5 creates, hit under 50 milliseconds, miss under 300, all assumptions. Unguessable codes.",
            "Minute 2 to 6. POST validates http(s). GET returns 302. 404 unknown, 410 expired. Never redirect to a query-string URL.",
            "Minute 6 to 10. varchar code as the primary key. Random 7-character code, retry on unique violation. No sequential public id.",
            "Minute 10 to 14. SQL is the record. Local cache, 10-second budget, negative cache at 30 seconds. Both numbers are choices.",
            "Minute 14 to 17. A hot key stays in each instance's memory. No click update on the redirect. No distributed lock. SQL down serves hits only.",
            "Minute 17 to 20. App Service, affinity off, managed identity, a SQL user that cannot migrate. Analytics is off the hot path or it is not in this slice.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "A 301. An IDENTITY column as the public code. Trusting the client to pick the code. Redirecting to a URL supplied on the GET. Updating a hit counter on the only row everyone wants. A distributed lock on the read. Caching null and being unable to tell a 404 from a cold key. Quoting a Redis operations limit you have not measured."},
        {"t": "lead", "title": "Say this", "text": "The code is a random primary key, generated on the server, with a retry on collision. GET is a 302 to the stored http(s) URL. A per-instance cache absorbs the hot code for a staleness budget I state. SQL remains the record. I do not count clicks on the redirect, and I do not take a distributed lock to read one row."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 9 — Realtime order status"},
        {"t": "p", "text": "Outcome. You can choose polling or SignalR for order status, defend the choice with the open-screen count, and explain a scale-out backplane without quoting a product limit."},
        {"t": "p", "text": "Time box. About 3.5 hours. Compute the poll rate on paper for three different watcher counts until the arithmetic is fast. Then the SignalR sketch and the backplane tradeoff. The twenty-minute version must include the sentence that SQL is still the record and the push is a hint."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "A customer page and an internal warehouse board both show order status. Status changes a handful of times over the life of an order. Design the update path. Pick polling, SignalR, or both, and say why."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "The order API assumptions still hold for the write path. The new number is how many screens are open. Assumption for the first slice: dozens of customer screens, not tens of thousands, and a warehouse board that a shift of people keep open all day. A customer poll every 2 seconds is a product choice. Dozens of screens at that interval fit inside a budget like 50 requests a second. Twenty thousand tablets at a 2-second poll are 10,000 requests a second, which breaks the assumption, and that is the moment the warehouse stops polling. You label the watcher count. You do not invent a SignalR connection quota. When the count matters you open the current Azure SignalR Service SKU page."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "GET /orders/{id} remains the source of truth and returns the status and the rowversion. The customer page and the partner poll it. The warehouse board opens a SignalR connection and joins a group for the orders on that bench, or one group per order. The hub method is Watch(orderId). The server checks the tenant and that this caller may see the order before it adds the connection to the group. A push message contains the order id, not the new status. The client calls GET. A push that carried the status could arrive out of order and paint an old state over a new one. The GET after the hint cannot. If the socket is down, the board falls back to the same GET on a slow timer, so the socket is not required to see the truth."},
        {"t": "h2", "text": "Data"},
        {"t": "p", "text": "No new table is required for polling. The status column and the index you already have for the point read are the data. SignalR groups live in memory on the connection host, not in SQL. You do not store sockets in a table. If you later need a missed-event replay, the order row is the replay. The client that reconnects calls GET and is current. That is simpler than an event log, and you add an event log only when a client must see the sequence rather than the latest status. This product needs the latest status."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "The status change commits in SQL first, in the same transaction as the order update and, if someone else must hear about it, the outbox row. After commit, the API notifies the group. A notify that runs before commit is how the client refetches and still sees the old status, then ignores the next push because it thinks it already handled that id. After commit, a failed notify is not a failed order. The client's poll or its next reconnect sees the row. The push is a hint. You refuse to make the hub the system of record."},
        {"t": "p", "text": "You choose both, on purpose. Polling for the customer and the partner, because the count is small, the GET already exists, and App Service can stay with affinity off and no extra product. SignalR for the warehouse board, because those screens sit open and a 2-second poll from a wall of browsers is the load you do not want, and because a one-second hint is the point of the board. If the panel forces a single mechanism for the first release, you ship polling. The GET is the contract. The hub is an optimization you can add without changing the write path."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "SQL down: the GET returns 503, and the hub has nothing true to say. You do not cache a status and serve it as current. SignalR Service down, or your hub down: the board falls back to polling, and the customer path never notices because it was already polling. A second API instance with in-process SignalR and no backplane drops events that were raised on the other instance, and a client connected to instance A never hears a notify executed on instance B. That is the scale-out bug. A client that fails the tenant check is not added to the group. A leaked group name that includes only the order id, without a tenant check on join, is a cross-tenant subscription. The check is in the hub method, not in the group name string alone."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "The order API stays on App Service with ARR affinity off. Polling does not care which instance answers. SignalR in-process would care, because the connection lives on one instance. Sticky sessions would pin the socket, and they fight the affinity-off decision you already made for the API: scale-in and restarts drop pins, and a pinned hot board lands on one instance. You do not turn affinity on."},
        {"t": "p", "text": "The backplane choice, at the level of a name and a tradeoff: Azure SignalR Service holds the client connections. The app server sends to the service, and the service fans out to the group. The app stays stateless and affinity stays off. You take a dependency and a network hop, and you look up the SKU when you know the connection count. The alternative is a Redis backplane: each app instance still holds its own WebSockets, and Redis spreads the group messages between instances. You operate Redis, and the connection count sits on App Service, which you measure rather than memorize. You pick Azure SignalR Service for the warehouse board so the API process is not the socket server. You do not quote a connection ceiling in the interview."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "You refuse the hub as the source of truth. You refuse sticky sessions as the scale-out plan. You refuse to notify before the SQL commit. You refuse a design where the only way to see status is the socket. You refuse to poll 20,000 clients every 2 seconds and call it simple once the arithmetic is on the board. You refuse a second status column that only the hub writes."},
        {"t": "h2", "text": "Sketch"},
        {"t": "code", "text": """public sealed class OrderHub : Hub
{
    public async Task Watch(Guid orderId)
    {
        if (!await _orders.CallerMaySee(orderId, Context.User))
            throw new HubException("Not found.");
        await Groups.AddToGroupAsync(Context.ConnectionId, Name(orderId));
    }

    public static string Name(Guid orderId) => $"order:{orderId:N}";
}

// After the status transaction commits. The payload is a hint.
await _hub.Clients.Group(OrderHub.Name(order.Id))
    .SendAsync("statusChanged", new { order.Id }, ct);

// Program.cs, when the warehouse board is in this release.
builder.Services.AddSignalR().AddAzureSignalR();"""},
        {"t": "p", "text": "AddAzureSignalR is the managed backplane. The app authenticates to it with a connection string held as a secret, or with the managed-identity setup in the current documentation. You say you will use managed identity and you will read the current setup, rather than pasting a key into a sketch from memory. The customer client does not reference the hub. It polls GET /orders/{id} on the 2-second timer while the page is visible, and it stops when the page is hidden. That last clause is how a few dozen open tabs do not become a few dozen forgotten tabs."},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 3. Dozens of customer screens poll every 2 seconds, a labeled choice. The warehouse board is the screen that stays open. Write the request-rate arithmetic.",
            "Minute 3 to 7. GET is the record. 200 with status and rowversion. The partner uses the same GET.",
            "Minute 7 to 11. Polling for the customer. SignalR for the board. The event carries the id. The client refetches. Join checks the tenant.",
            "Minute 11 to 15. Commit, then notify. A missed notify is healed by GET. The hub is not a database.",
            "Minute 15 to 18. Affinity stays off. Azure SignalR Service holds the sockets. Redis is the backplane you would operate yourself, and then the sockets still sit on the app. You look up the SKU when the count is real.",
            "Minute 18 to 20. If they force one mechanism, ship polling. Refuse sticky sessions and a socket-only status.",
        ]},
        {"t": "warn", "title": "Interview trap", "text": "Sending the status in the push and letting the client paint it with no GET. Notifying before commit. Turning ARR affinity on and calling that a backplane. Forgetting the tenant check on group join. Quoting a connection limit from memory. Polling a population you have not multiplied by the interval. Making SignalR the only read path."},
        {"t": "lead", "title": "Say this", "text": "GET /orders/{id} is the status. Customers poll it while the page is open, at an interval I state, and I do the arithmetic before I keep that choice. The warehouse board uses SignalR, joins a group only after a tenant check, and treats the push as a hint to read. Azure SignalR Service is the backplane so the API can stay affinity off. I look up the SKU instead of inventing a connection limit."},
        {"t": "break"},

        {"t": "h1", "text": "Part B, Day 10 — A 45-minute mock"},
        {"t": "p", "text": "Outcome. You can hold a 45-minute design that combines the order API and the notification fan-out, and you can answer the four panel questions: the SQL role, the rollback, the second instance, and the poison message."},
        {"t": "p", "text": "Time box. About 3.5 hours. The first hour is a silent redraw of Day 2 and Day 6 on one sheet, no notes. The next hour is the 45-minute clock once, alone. The last 90 minutes is the clock again, and you stop to answer each panel question in under two minutes when an imaginary interviewer interrupts. If you only do one run-through, do the interrupted one."},
        {"t": "h2", "text": "The prompt"},
        {"t": "p", "text": "Design the system that accepts an order from a partner, stores it, and notifies the customer by email and SMS. Partners retry. The warehouse may later want live status. You have 45 minutes. The panel will interrupt. Combine Day 2 and Day 6. Leave realtime as a sentence unless they pull it in, and if they do, use Day 9's choice: polling first, SignalR only for a board whose watcher count justifies it."},
        {"t": "h2", "text": "Assumptions"},
        {"t": "p", "text": "Say them in the first two minutes and write them where you can point: about 50 requests a second at peak, about 2 million orders a year, read p95 under 300 milliseconds, email and SMS within a minute, one region, one team, server-side pricing. Out of scope until they open it: a second region, a pricing service, a million-row nightly file, a database per tenant. If they change a number, stop and say what moves. At this number, one App Service and one Azure SQL database stay. The file ingest and the dedicated tenant database are other days. You can name them as the next review, not as boxes on this drawing."},
        {"t": "h2", "text": "API"},
        {"t": "p", "text": "POST /orders with Idempotency-Key. 201, replay 200, conflicting body 409, missing key 400. The body is sku, quantity, and ship-to. GET /orders/{id} is 200 or 404. GET /orders?cursor= is the keyset list. PATCH uses the rowversion and returns 409 on a lost update. GET /orders/{id}/notifications is the support view of email and SMS state. 401 and 403 stay on the auth middleware. 429 is Day 7, and you mention the limiter in one sentence if the word public is in the prompt: per-client fixed window in the app, shared budget at the gateway, no invented quota. Do not spend the mock designing the limiter unless they ask."},
        {"t": "h2", "text": "Data"},
        {"t": "p", "text": "orders.Orders with TenantId, rowversion, and the list index. orders.IdempotencyKeys unique on (TenantId, KeyValue) with the raw-body hash. orders.Outbox with the unpublished filtered index and the lease columns. orders.NotificationDeliveries unique on (Channel, MessageId). The topic is order-events. The subscriptions are email and SMS. Push is a third subscription you can add without a new publisher. The SQL users are app_orders_runtime for the API and app_orders_notify for the consumers. The pipeline migrator is not either of them."},
        {"t": "h2", "text": "Consistency"},
        {"t": "p", "text": "One transaction: order, idempotency row, outbox. After commit, the relay leases unpublished rows with UPDLOCK and READPAST, publishes with MessageId equal to the outbox id, then marks published. Each subscription inserts a Sending row, calls the provider with that message id, marks Sent, and completes the peek-lock. A duplicate publish is a duplicate key in the delivery table, not a second email. The API response does not wait for either provider. 201 means the order is durable."},
        {"t": "h2", "text": "Failure"},
        {"t": "p", "text": "Walk the four panel questions as failures, because that is how they will ask them. They are written in full below so you can practice the answer, not so you can read it in the room. In the mock you give the answer from the drawing."},
        {"t": "h3", "text": "What SQL role does the app use?"},
        {"t": "p", "text": "The API connects with its managed identity as app_orders_runtime. That user can select, insert, and update in the orders schema. It cannot alter, drop, or own the database. The notify functions use app_orders_notify, which can write delivery rows and read the order fields the template needs, and cannot delete orders. The pipeline uses a migrator identity that is allowed to apply the reviewed script and is not in the application connection string. The partner's Entra token is not a SQL login. It is how the API decides 401 versus 403 versus the tenant id. If you can only remember one sentence: the application login is not db_owner, and it is not the migrator."},
        {"t": "h3", "text": "How do you roll back?"},
        {"t": "p", "text": "The release expanded the schema. New tables and nullable columns are already there, and the previous bits do not need them. You swap the App Service slot back. You do not restore the database. A release that dropped a column or narrowed a type is not reversible by a swap, so that release is not the shape you shipped. Messages already on the topic are not recalled. Consumers accept this payload and the previous one for the overlap. If the consumer is the bad bit, you stop the relay with the flag or the function setting, you fix the consumer, and you replay. You do not delete orders to get back to a quiet topic."},
        {"t": "h3", "text": "What changes when a second instance is running?"},
        {"t": "p", "text": "The second API instance is normal, and affinity stays off. Idempotency is the unique key in SQL, so both instances can take the same retry and one of them loses the insert. An in-memory set of keys would have created two orders. The outbox lease skips rows the other relay locked, and a double publish still meets the delivery primary key. A per-instance rate limit is twice the budget unless the gateway holds the contract. A static cache of order status would be stale and split-brained, which is why GET hits SQL. SignalR is not in this slice. If they add the warehouse board, the second instance is why you want Azure SignalR Service rather than in-process sockets. Readiness must pass before the load balancer sends traffic, and readiness includes SQL, so a second instance that cannot reach the database does not take orders."},
        {"t": "h3", "text": "What do you do with a poison message?"},
        {"t": "p", "text": "A poison message is a payload you cannot parse, an order you cannot find, or an address the provider has permanently rejected. A timeout from the provider is not poison. You abandon transient failures until the max delivery count you set on that subscription, then the message dead-letters. You alert when the dead-letter count is above zero. You do not abandon forever, and you do not complete the message to make the queue look healthy. The order remains placed. Support can see the delivery row in Failed or can see the gap. After the fix, you replay the dead-letter with the same message id so the dedupe still holds. SMS dying does not roll back email and does not roll back the order."},
        {"t": "h2", "text": "Operations"},
        {"t": "p", "text": "App Service for the API, staging slot, Always On, affinity off, health on /health/ready. Functions on the isolated worker for the relay and for each subscription, auto-complete off where you settle the message. Managed identity throughout. The dashboard is request latency, SQL duration, outbox age, and dead-letter depth per subscription. The release is migrate, then deploy the slot, then smoke, then swap. The smoke creates an order with a key, retries it, and checks that one row exists. That smoke is the idempotency test you are willing to run in production against a canary tenant or a synthetic sku."},
        {"t": "h2", "text": "The tradeoff refused"},
        {"t": "p", "text": "In this mock you refuse, out loud, a pricing microservice, a two-phase commit, mail inside the request, receive-and-delete, an in-memory idempotency cache, Migrate on startup, and a shared SQL login in a high-privilege role. You also refuse to spend the forty-fifth minute on Kubernetes. If they ask what you would add next, the answer is the gateway limiter from Day 7 if the partners are untrusted, or the polling client from Day 9 if a screen needs status. The nightly file and a dedicated tenant database stay off this drawing until a number or a contract puts them on it."},
        {"t": "h2", "text": "Sketch"},
        {"t": "p", "text": "One sheet, which you should be able to redraw from memory. The boxes are the partner, App Service, Azure SQL, the relay function, the topic, two subscription functions, and the two providers. The arrow from App Service to SQL is labeled with the transaction. The arrow from the relay to the topic is labeled after commit. The arrow from a function to a provider is labeled with the message id. The identities sit under the boxes, three of them, plus Entra above the partner."},
        {"t": "code", "text": """Partner -- Entra token --> App Service (affinity off, two instances)
                         |  one SQL transaction
                         v
                    Azure SQL
                      orders.Orders
                      orders.IdempotencyKeys
                      orders.Outbox
                      orders.NotificationDeliveries
                         |
           relay function, lease, after commit
                         v
                  topic order-events
                    |                 |
                 email               sms
                    |                 |
              provider, keyed by MessageId

SQL roles: app_orders_runtime, app_orders_notify, pipeline migrator
Rollback: slot swap, schema was expanded only
Second instance: unique keys, not memory
Poison: dead-letter the subscription, keep the order"""},
        {"t": "h2", "text": "What to say in 20 minutes"},
        {"t": "p", "text": "The mock is 45 minutes, so the twenty-minute spine is the first half and the interruptions are the second. If they do not interrupt, you use the spare time on failure and operations, not on a new box."},
        {"t": "b", "numbered": True, "items": [
            "Minute 0 to 5. Assumptions, out of scope, one API, one database, server prices.",
            "Minute 5 to 15. API codes, the four tables, the raw-body hash, the one transaction.",
            "Minute 15 to 25. Relay, topic, two subscriptions, delivery key, complete after the provider accept.",
            "Minute 25 to 35. The four panel answers: SQL role, rollback, second instance, poison message.",
            "Minute 35 to 45. Dashboard, slot swap, the smoke that retries a key, and the list of things you refused. Stop. Ask them which assumption you should redraw.",
        ]},
        {"t": "p", "text": "Score yourself the way the roadmap scores a spoken answer. Correct: a working lead would agree with the transaction and the dedupe. Tradeoff: you named the microservice, the two-phase commit, and the in-memory cache as the things you did not ship. Consequence: the partner, the on-call person, or the customer feels a 409, a dead letter, or a swap. A correct drawing with no consequence is an incomplete mock. Do a second pairing on another evening if this one feels easy: the catalog and the realtime board, Days 3 and 9, with the same four questions. The SQL role, the swap, the second instance, and the poison message are not special to email. They fit any of these designs."},
        {"t": "warn", "title": "Interview trap", "text": "Redrawing six services because the mock is longer than twenty minutes. Answering the SQL-role question with the name of a cloud product and no permission. Promising a swap back after a destructive migration. Forgetting the second instance and leaving idempotency in a static field. Deleting the order because the SMS payload was bad. Inventing a quota when you run out of design."},
        {"t": "lead", "title": "Say this", "text": "The order, the idempotency row, and the outbox commit together. A topic fans out to email and SMS, and each consumer dedupes on the message id. The API login is not the migrator. I roll back by swapping a slot only while the old bits still match the schema. A second instance is safe because the unique keys are in SQL. A poison message dead-letters, and the order stays."},

        {"t": "h2", "text": "After the twenty days"},
        {"t": "p", "text": "Part A is done when you can write each pattern from a blank file and say the pitfall: missing key, overflow, unstable sort, recursion depth, off-by-one. Part B is done when you can redraw the order sheet and answer the four panel questions without this PDF. The roadmap is still the script for the leadership round. The deep dive is still the worked example when a follow-up goes into EF, SQL plans, or the service cut. The pipeline and MVC guide is still the request path. You do not reread all four the night before. You redraw the order sheet, you write two-sum and a binary search from memory, and you sleep."},
        {"t": "break"},
    ]
