# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 3 — ASP.NET Core Web API"},
        {"t": "p", "text": "Day 3 is the request. A lead can draw the pipeline in order, name the status code before naming the library, and review a bad action without a style argument. The Orders API is still the system: a partner POSTs an order, retries, and later GETs it."},

        {"t": "h2", "text": "The pipeline for a secured POST"},
        {"t": "p", "text": "The host builds a pipeline. Order matters. Kestrel accepts the connection. Middleware runs in the order you registered it, and the endpoint runs in the middle. A typical API registers exception handling first so it wraps everything else, then HTTPS redirection, routing, CORS, authentication, authorization, rate limiting, and the endpoints. Authentication runs before authorization because authorization needs an identity. The correlation id belongs near the start so the 500 and the SQL log share one id."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """app.UseExceptionHandler();          // wraps the rest, writes ProblemDetails
app.UseHttpsRedirection();
app.UseRouting();
app.UseCors();                     // browser callers, after routing, before auth
app.UseAuthentication();           // bearer token -> ClaimsPrincipal, or 401
app.UseAuthorization();            // policy -> 403 if the identity may not
app.UseRateLimiter();
app.MapControllers();

// A correlation id, registered at the top, before the exception handler
// so the handler can log the same id:
app.Use(async (ctx, next) =>
{
    if (!ctx.Request.Headers.TryGetValue("X-Correlation-Id", out var incoming))
        incoming = Guid.NewGuid().ToString("n");
    ctx.TraceIdentifier = incoming.ToString();
    ctx.Response.Headers["X-Correlation-Id"] = ctx.TraceIdentifier;
    await next();
});"""},
        {"t": "p", "text": "For a secured POST the useful story is: routing selects the endpoint, CORS answers the browser, authentication builds the principal or fails with 401, authorization runs the policy and returns 403 if the caller is known and not allowed, model binding turns the JSON body into a request type, validation runs, the handler opens the scoped DbContext and awaits SQL, and the formatter writes JSON. If an exception escapes, the exception handler logs it with the correlation id and returns ProblemDetails with status 500. MVC filters wrap the action more tightly than middleware: authorization filters, resource filters, action filters, exception filters, and result filters. Say middleware for the request and filters for the action, and do not mix the two orders up."},
        {"t": "warn", "title": "What breaks", "text": "Authorization before authentication runs with an anonymous user and returns 403 for a missing token, which trains clients to treat 'log in' as 'forbidden'. Exception handling registered late does not see exceptions from earlier middleware. CORS in the wrong place fails the browser and works in Postman, so the team thinks the API is fine."},
        {"t": "lead", "title": "Say this", "text": "Exception handling wraps the pipeline. Authentication then authorization. I can draw that before I talk about patterns. The correlation id is on every log line, including the 500."},

        {"t": "h2", "text": "Controllers or minimal APIs"},
        {"t": "p", "text": "Controllers group HTTP actions in a class. Filters, model binding, and a large route surface are the habit they fit. Minimal APIs map a handler directly and stay short. Choose controllers when the team is large and the surface is wide. Choose minimal APIs for a small service with a short list of endpoints. Mixing both in one service without a written reason gives you two ways to forget a cancellation token."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Small service. One file can hold the contract.
orders.MapPost("/orders", async (CreateOrderRequest body, CreateOrderHandler handler, CancellationToken ct) =>
{
    Result<OrderDto> result = await handler.HandleAsync(body.ToCommand(), ct);
    return result.Ok
        ? Results.Created($"/orders/{result.Value!.Id}", result.Value)
        : Results.ValidationProblem(new Dictionary<string, string[]> { ["body"] = [result.Error!] });
});

// Large team. The same handler, an MVC action, filters already in use.
[HttpPost("/orders")]
public async Task<ActionResult<OrderDto>> Post(CreateOrderRequest body, CancellationToken ct)
{
    Result<OrderDto> result = await handler.HandleAsync(body.ToCommand(), ct);
    if (!result.Ok)
        return ValidationProblem(detail: result.Error);
    return CreatedAtAction(nameof(Get), new { id = result.Value!.Id }, result.Value);
}"""},
        {"t": "p", "text": "Both call the same handler. The HTTP style is a team rule, not a different architecture. I would not rewrite controllers to minimal APIs as a migration goal. I would pick one for new endpoints and leave the other until a slice is already open."},
        {"t": "warn", "title": "What breaks", "text": "A minimal API that closes over a scoped service captured at startup is a captive dependency. A controller base class that hides the DbContext encourages actions to query from HTTP methods. Two styles mean two copies of the error catalog."},
        {"t": "lead", "title": "Say this", "text": "Controllers for a wide surface and a team that already uses filters. Minimal APIs for a small service. The handler is the same either way."},

        {"t": "h2", "text": "DI lifetimes and a captive dependency"},
        {"t": "p", "text": "The container tracks how long an object lives. Transient is a new instance every time it is resolved. Scoped is one instance per request scope. Singleton is one instance until the process stops. DbContext is scoped. A singleton must not take a scoped service in its constructor. That is a captive dependency: the scoped instance would live as long as the singleton, either disposed after the first request or reused across requests and threads."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """builder.Services.AddScoped<AppDbContext>(); // or AddDbContext, which is scoped
builder.Services.AddScoped<CreateOrderHandler>();
builder.Services.AddSingleton<IClock, SystemClock>();

// The bug:
public sealed class OrderCache(AppDbContext db) { } // singleton capturing scoped
builder.Services.AddSingleton<OrderCache>();

// The fix for a hosted service, which is a singleton:
public sealed class OutboxRelay(IServiceScopeFactory scopes) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await using AsyncServiceScope scope = scopes.CreateAsyncScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            await RelayOnceAsync(db, stoppingToken);
            await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);
        }
    }
}"""},
        {"t": "p", "text": "The safe fixes are: make the consumer scoped, or inject IServiceScopeFactory and create a scope at the moment of work. ValidateScopes in development throws when a singleton takes a scoped service. Turn that check on. The registration lives in the composition root, not in the domain. A scoped service that creates a transient disposable and does not own it clearly is the quieter leak: the container does not dispose transients it did not create as part of the scope unless they were resolved from the scope."},
        {"t": "warn", "title": "What breaks", "text": "A captive DbContext throws 'a second operation was started on this context' under parallel requests, or returns one tenant's entities to another. A BackgroundService that constructor-injects DbContext fails at startup if scope validation is on, and fails in production in a worse way if it is off."},
        {"t": "lead", "title": "Say this", "text": "Transient per resolve, scoped per request, singleton per process. DbContext is scoped. A singleton creates a scope at the moment of work. I can find the captive dependency in a short sample."},

        {"t": "h2", "text": "Authentication and authorization"},
        {"t": "p", "text": "Authentication answers who called. Authorization answers whether that caller may do this. For a line-of-business API, Entra ID issues tokens and JwtBearer validates them: issuer, audience, lifetime, and signature. The API does not invent passwords if an identity provider already exists. Coarse access is a policy: can-manage-orders requires a scope or an app role. Fine access is resource-based: the handler loads the order and checks the tenant id. Keep the tenant id in a claim and also filter in EF, so one missed if does not leak rows."},
        {"t": "p", "text": "401 means unauthenticated. 403 means authenticated and refused. Returning 404 for every forbidden read hides existence. Do that only on purpose, and document it. The user's token and the app's managed identity are different. The user token decides what the human may do. The managed identity decides what the process may do in Azure SQL. Mixing them into one shared SQL login is how an over-privileged app login appears."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """builder.Services.AddAuthentication().AddJwtBearer(options =>
{
    options.Authority = builder.Configuration["Entra:Authority"];
    options.Audience = builder.Configuration["Entra:Audience"];
});
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("orders.write", p => p.RequireClaim("roles", "orders.write"));

[Authorize(Policy = "orders.write")]
[HttpPost("/orders")]
public async Task<ActionResult<OrderDto>> Post(CreateOrderRequest body, CancellationToken ct)
{
    int tenantId = int.Parse(User.FindFirstValue("tid")!); // from the token, never the body
    if (body.TenantId is not null)
        return ValidationProblem(detail: "TenantId is not accepted from the body.");
    return await handler.HandleAsync(body.ToCommand(tenantId), ct);
}"""},
        {"t": "p", "text": "The policy is the coarse gate. The handler still checks that the order id in a GET belongs to tenantId, and the global query filter is the safety net. A test that signs a token for tenant A and requests tenant B's id is the control. The filter alone is not the security boundary, because IgnoreQueryFilters and a raw SQL path can bypass it."},
        {"t": "warn", "title": "What breaks", "text": "Trusting TenantId or IsAdmin from the JSON body is over-posting. A valid signature with the wrong audience accepts another app's token. [Authorize] missing on one action is an anonymous write. 403 for a missing token makes the client show 'access denied' instead of a login."},
        {"t": "lead", "title": "Say this", "text": "Entra ID identifies the caller. A policy is the coarse check. The tenant comes from the token, and a test proves tenant A cannot read tenant B. 401 is unknown, 403 is known and refused. The managed identity is a different identity from the user."},

        {"t": "h2", "text": "Status codes and ProblemDetails"},
        {"t": "p", "text": "Clients write logic against status codes. An error catalog that changes 409 into 400 because a junior found it easier will break those clients. ProblemDetails, RFC 9457, is the error body: type, title, status, detail, and extensions such as traceId. Validation errors add an errors dictionary. Success codes are a contract too."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """return result.Status switch
{
    "created" => Created($"/orders/{dto.Id}", dto),             // 201
    "replayed" => Ok(dto),                                      // 200, same key, same body
    "invalid" => ValidationProblem(result.Errors),              // 400
    "conflict" => Conflict(new ProblemDetails                   // 409
    {
        Title = "Conflict",
        Detail = "The order was updated by someone else.",
        Extensions = { ["traceId"] = HttpContext.TraceIdentifier }
    }),
    "forbidden" => Forbid(),                                    // 403
    _ => throw new InvalidOperationException(result.Status)     // 500 via the handler
};

// 202 Accepted: the email is later. Location or a status URL points at the order.
// 204: a delete with nothing to return.
// 401: no usable credential. 404: not in the caller's scope.
// 412: If-Match failed. 429: rate limit, with Retry-After. 503: dependency down."""},
        {"t": "table", "headers": ["Outcome", "Status", "Body"], "rows": [
            ["Read or update that returns a representation", "200", "The DTO"],
            ["Resource created", "201", "The DTO and a Location header"],
            ["Accepted, finishes later", "202", "A status URL"],
            ["Success with nothing to say", "204", "Empty"],
            ["Validation", "400", "ProblemDetails plus errors"],
            ["Missing or bad credential", "401", "ProblemDetails"],
            ["Credential known, not allowed", "403", "ProblemDetails or empty from Forbid"],
            ["Not in the caller's scope", "404", "ProblemDetails"],
            ["Duplicate key or concurrency conflict", "409", "ProblemDetails"],
            ["Over the rate limit", "429", "Retry-After"],
            ["Defect on our side", "500", "ProblemDetails with traceId, no stack in the body"],
            ["Dependency down, client may retry", "503", "ProblemDetails"],
        ]},
        {"t": "warn", "title": "What breaks", "text": "200 with an error string in the JSON trains every client to parse bodies. 500 for a validation error triggers retries and pages. A ProblemDetails body that includes the SQL exception text leaks schema to the caller."},
        {"t": "lead", "title": "Say this", "text": "I publish the error catalog with the API. 401, 403, 404, 409, and 500 mean different things and I do not collapse them. ProblemDetails carries the status and the trace id."},

        {"t": "h2", "text": "Verbs, and POST /orders under retries"},
        {"t": "p", "text": "GET is safe. PUT replaces the resource. PATCH updates a subset. DELETE is idempotent: doing it twice leaves the resource gone. POST creates or starts work, and a retry can create a second order unless you add an idempotency key. Mobile networks and gateways are retry machines. If the team cannot explain the second POST, the endpoint is not ready."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class IdempotencyRow
{
    public string Key { get; set; } = "";
    public int TenantId { get; set; }
    public string RequestHash { get; set; } = "";
    public int StatusCode { get; set; }
    public string ResponseBody { get; set; } = "";
}

// In the same transaction as the order:
// unique (TenantId, Key)
var existing = await db.Idempotency.SingleOrDefaultAsync(
    r => r.TenantId == tenantId && r.Key == key, ct);
if (existing is not null)
{
    if (existing.RequestHash != hash)
        return Conflict(); // same key, different body
    return Stored(existing); // same key, same body: replay the first response
}
db.Orders.Add(order);
db.Idempotency.Add(new IdempotencyRow { Key = key, TenantId = tenantId, RequestHash = hash });
await db.SaveChangesAsync(ct);"""},
        {"t": "p", "text": "The client sends an Idempotency-Key header, a GUID per user action, not per HTTP attempt. The server stores the key, a hash of the body, and the response, in the same transaction as the order. A retry with the same key and the same body returns the stored response and does not insert a second order. The same key with a different body is 409. Keep the row for as long as the client retries, often about a day, and say that window out loud as a product choice. A unique constraint on the business key, such as one external reference per tenant, still exists. The idempotency key does not replace a data rule. GET, PUT, and DELETE should already be safe to retry."},
        {"t": "warn", "title": "What breaks", "text": "Storing the key after SaveChanges races two retries into two inserts. Hashing nothing means a client bug that reuses a key for a different order silently replays the first order. A key with no retention fills the table. Trusting the client's generated order id as the only idempotency control fails when two clients pick ids from different sequences and the business key was the email or the cart."},
        {"t": "lead", "title": "Say this", "text": "POST is not naturally idempotent. I store an Idempotency-Key with a hash of the body in the same transaction as the order. Same key and same body replays. Same key and different body is 409. The database unique constraint is still the business rule."},

        {"t": "h2", "text": "Validation, versioning, and pagination"},
        {"t": "p", "text": "Validation of shape lives in one place, FluentValidation or data annotations, before the handler. The handler can assume the JSON was well formed and still enforce business rules such as stock. Errors use the field names the client sent. Versioning is a contract. A URL segment is obvious for an enterprise API because gateways, caches, and humans see it. A header version keeps the URL stable and is easier to miss. Pick one, document it, and run an overlap window. Measure calls on the old version before you delete it."},
        {"t": "p", "text": "Pagination: limit plus a continuation token or a keyset on (CreatedUtc, Id). Offset is acceptable for a small admin screen and gets expensive on a deep page because SQL reads and discards the skipped rows. Cap the page size. Filtering and sorting are an allow-list, never a raw column name from the query string."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed record OrderListQuery(int Limit, DateTimeOffset? CreatedBefore, int? IdBefore);

// GET /v1/orders?limit=50&createdBefore=2026-10-30T00:00:00Z&idBefore=900
var page = await db.Orders.AsNoTracking()
    .Where(o => o.TenantId == tenantId)
    .Where(o => cursor == null || o.CreatedUtc < cursor.Created ||
                (o.CreatedUtc == cursor.Created && o.Id < cursor.Id))
    .OrderByDescending(o => o.CreatedUtc).ThenByDescending(o => o.Id)
    .Take(Math.Clamp(query.Limit, 1, 100))
    .Select(o => new OrderListItem(o.Id, o.Number, o.CreatedUtc, o.Total))
    .ToListAsync(ct);

// Sort allow-list:
string sort = query.Sort == "total" ? "Total" : "CreatedUtc";"""},
        {"t": "p", "text": "The keyset matches an index on (TenantId, CreatedUtc, Id). The next page sends the last item's created time and id. An unbounded GET that returns every order is an incident waiting for the first large tenant. Paging, a maximum, and a projection that omits heavy columns are acceptance criteria."},
        {"t": "warn", "title": "What breaks", "text": "ORDER BY on a string from the query is SQL injection if you concatenate it, and a scan if you allow every column. Offset 100000 on a hot table reads 100000 rows to throw them away. Two versions that share a DTO force a breaking change into both. Validation only in the UI means the partner's retry script bypasses it."},
        {"t": "lead", "title": "Say this", "text": "Shape validation is one component. Business rules stay in the handler. I version in the URL for an enterprise API and keep an overlap. Lists are keyset paginated, capped, and sorted from an allow-list."},

        {"t": "h2", "text": "Timeouts, retries, and a slow dependency"},
        {"t": "p", "text": "Every outbound call has a timeout shorter than the client's patience. Retry only idempotent operations, with a small jittered backoff. Do not retry a POST that creates a charge unless the idempotency story is solid. A circuit breaker opens when the failure ratio trips and fails fast for a cool-down so the dependency can recover. A concurrency limit stops one request, or one instance, from launching unlimited parallel calls. In .NET this belongs on the typed HTTP client. SQL uses a command timeout and an execution strategy for transient errors such as deadlock 1205 or a brief Azure SQL failover. When the policy is exhausted, return 503 or a controlled error. Log the dependency name and the correlation id."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """builder.Services.AddHttpClient<TaxClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Tax:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(2);
})
.AddStandardResilienceHandler(options =>
{
    options.Retry.MaxRetryAttempts = 2;          // GET-like tax quote only
    options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(1);
    options.CircuitBreaker.FailureRatio = 0.5;
    options.CircuitBreaker.MinimumThroughput = 20;
});

// The call site still passes CancellationToken.
decimal tax = await taxClient.QuoteAsync(draft, ct);"""},
        {"t": "p", "text": "The numbers above are an example policy, not a quota to memorize. Say you would set them from the dependency's latency and the user's budget, and you would review them like code. Retries without a budget multiply load on the thing that is already sick. Failing in about two seconds is kinder than three retries that hold a thread for thirty. Health checks split liveness and readiness. Liveness means the process can run. Readiness includes SQL. If liveness checks SQL, a database blip restarts every instance."},
        {"t": "code", "text": """builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("sql", tags: ["ready"]);
app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = c => c.Tags.Contains("ready") });"""},
        {"t": "warn", "title": "What breaks", "text": "A retry on a non-idempotent POST double-charges. A circuit breaker with MinimumThroughput of 1 opens on the first blip and fails the rest of checkout. A liveness probe that calls SQL turns a failover into a restart storm. new HttpClient() per request exhausts ephemeral ports."},
        {"t": "lead", "title": "Say this", "text": "Timeouts shorter than the user's patience, retries only when the call is safe, a breaker so a sick dependency fails fast, and a concurrency cap. Liveness does not include SQL. Readiness does. The policy is reviewed like code."},

        {"t": "h2", "text": "What you look for in a pull request"},
        {"t": "p", "text": "Read the contract first: route, verb, status codes, auth policy, and who can see the data. Then cancellation tokens into EF and HttpClient. Then over-posting: the client must not bind IsAdmin, TenantId, or Total as authority. Then sync-over-async, a captive dependency, and a catch that swallows exceptions. Then the query shape. Then logs that include tokens, card numbers, or full personal data. Then a test for the happy path and one failure path that would have cost money or leaked a row. Leave braces to the formatter. A review comment teaches a rule the author can apply next time."},
        {"t": "h3", "text": "Example: the action, and the comments"},
        {"t": "code", "text": """[HttpPost]
public OrderDto Create(OrderDto input)
{
    var ctx = new AppDbContext();
    var order = new Order { Id = input.Id, Total = input.Total, IsAdmin = input.IsAdmin };
    ctx.Orders.Add(order);
    ctx.SaveChanges();
    _bus.Publish(new OrderCreated(order.Id));
    return input;
}"""},
        {"t": "b", "numbered": True, "items": [
            "The action is synchronous. SaveChanges blocks a thread-pool thread. It should be async and take a CancellationToken.",
            "new AppDbContext() skips DI, so there is no scope, no options, and no disposal. Inject the context or, better, a handler.",
            "The body is an entity DTO. IsAdmin and Total are client-supplied authority. Tenant and price come from the token and the server.",
            "The client-supplied Id lets a caller choose keys and overwrite. The database assigns the id, or the idempotency key is a separate column.",
            "Publish sits after SaveChanges and outside a transaction. A crash between them commits an order and loses the email. Write an outbox row in the same SaveChanges.",
            "Returning input echoes the client's IsAdmin flag back as if it were stored truth.",
            "There is no [Authorize], no status code choice, and no test. A duplicate POST creates a second order.",
        ]},
        {"t": "p", "text": "The comment to leave is a rule, not a rewrite: we do not bind privilege or price from the body, we pass CancellationToken into every IO call, and a message that must match the order is an outbox row in the same transaction. The author can apply that to the next PR without you."},
        {"t": "warn", "title": "What breaks", "text": "A review that only fixes names ships the data bug. A review that rewrites the PR in the comment trains the team to wait for you. A review that ignores the SQL ships a list endpoint that will time out on the next tenant."},
        {"t": "lead", "title": "Say this", "text": "I review the contract, the auth, the cancellation token, the bound fields, and the query. My comment states the rule. Style belongs to the formatter."},
        {"t": "break"},
    ]
