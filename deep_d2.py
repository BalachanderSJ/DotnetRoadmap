# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 2 — SOLID and design patterns"},
        {"t": "p", "text": "A traditional panel wants the name. A product panel wants the smallest design that keeps the next change local. Day 2 trains both. For each pattern, know the problem it removes, the problem it adds, and the day you would delete it. The Orders API is still the example: create an order, price it, tax it, and send a confirmation after commit."},

        {"t": "h2", "text": "Single responsibility"},
        {"t": "p", "text": "A type has one reason to change. In a Web API that usually means the controller translates HTTP, a handler runs the use case, and EF mapping stays at the data edge. A class that validates the body, calculates tax, writes SQL, and sends email has four reasons to change, and a test for tax has to boot HTTP."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """[HttpPost("/orders")]
public async Task<ActionResult<OrderDto>> Post(CreateOrderRequest request, CancellationToken ct)
{
    Result<OrderDto> result = await handler.HandleAsync(request.ToCommand(tenant.Id), ct);
    return result.ToActionResult(); // HTTP only
}

public sealed class CreateOrderHandler
{
    public async Task<Result<OrderDto>> HandleAsync(CreateOrder command, CancellationToken ct)
    {
        decimal tax = taxCalculator.Tax(command);
        Order order = Order.Place(command, tax);
        await store.SaveAsync(order, ct);
        return Result<OrderDto>.Ok(OrderDto.From(order));
    }
}"""},
        {"t": "p", "text": "The action does not know the tax rate. The handler does not know the status code. The store does not send email. Email is a later consumer of the outbox, which is a different reason to change. A one-class endpoint is still legitimate in a tiny service. Say that. Judgment is the signal, not a six-project solution for eight classes."},
        {"t": "warn", "title": "What breaks", "text": "A controller that owns business rules cannot be tested without the host, and every new channel (a queue consumer, a retry job) copies the rule. A handler that also formats ProblemDetails has two owners for the error catalog."},
        {"t": "lead", "title": "Say this", "text": "The controller translates HTTP. The handler runs the use case. I collapse those on a tiny endpoint and I say so. I split them when a second caller needs the same rule."},

        {"t": "h2", "text": "Open/closed"},
        {"t": "p", "text": "Open for extension means a new shipping provider is a new class behind an interface you already registered. Closed for modification means the checkout handler does not grow a switch. This is not a plugin system. Two branches of an if do not deserve a registry."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface IShippingRate
{
    string Code { get; }
    decimal Quote(Shipment shipment);
}

builder.Services.AddKeyedScoped<IShippingRate, UpsRate>("ups");
builder.Services.AddKeyedScoped<IShippingRate, DhlRate>("dhl");

public sealed class ShippingQuoter(IServiceProvider sp)
{
    public decimal Quote(string code, Shipment shipment)
        => sp.GetRequiredKeyedService<IShippingRate>(code).Quote(shipment);
}"""},
        {"t": "p", "text": "Adding a carrier is a class plus a registration. Checkout does not change. If the business has exactly two carriers and the choice is a configuration flag, a single if in the quoter is easier to operate than keyed services. Extract the interface when the third carrier arrives or when the rule needs its own tests."},
        {"t": "warn", "title": "What breaks", "text": "A registry nobody can see in the handler hides the policy. A switch that is the policy, sitting in one tested method, is often the better design. Open/closed applied too early scatters a simple rule."},
        {"t": "lead", "title": "Say this", "text": "A new provider is a new class when the set actually grows. I do not invent a plugin system for two branches of an if."},

        {"t": "h2", "text": "Liskov substitution"},
        {"t": "p", "text": "A subtype honors the contract callers already rely on. If the base method returns a rate, the override returns a rate. An override that throws NotSupportedException for a method on the base type will surprise every caller that was given the base type. Prefer a smaller interface that does not include the method you cannot implement."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface IReadOrders
{
    Task<OrderDto?> FindAsync(int id, CancellationToken ct);
}

public interface IWriteOrders
{
    Task SaveAsync(Order order, CancellationToken ct);
}

// A reporting replica implements IReadOrders only.
// It does not implement IWriteOrders and then throw on Save."""},
        {"t": "p", "text": "A read replica that is typed as a full store and throws on Save violates Liskov. Callers cannot tell from the type that Save is a lie. Split the interface. The same issue shows up with a square inheriting a mutable rectangle: setting width changes height, and every rectangle algorithm breaks. In a Web API the practical form is a subtype that strengthens preconditions or throws for a base operation."},
        {"t": "warn", "title": "What breaks", "text": "Tests written against the base type pass with the production subtype and fail with the stub, or the reverse. Support then finds a 500 where the contract promised a result."},
        {"t": "lead", "title": "Say this", "text": "A subtype keeps the promises of the type I substituted. If a method does not make sense, it is not on the interface. Throwing NotSupportedException from an override is the smell."},

        {"t": "h2", "text": "Interface segregation"},
        {"t": "p", "text": "Callers depend on the slice they use. IOrderQueries and IOrderCommands, or a single IClock, beat one IOrderService with forty methods. A fat interface forces a fake to stub methods the test does not care about, and it forces a replica, a cache, and a writer to pretend they are the same type."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface IClock
{
    DateTimeOffset UtcNow { get; }
}

public sealed class SystemClock : IClock
{
    public DateTimeOffset UtcNow => DateTimeOffset.UtcNow;
}

// The handler depends on IClock, not on DateTime.
// A test supplies a clock frozen at 2026-10-30T09:00:00Z."""},
        {"t": "p", "text": "IClock is the smallest interface in the solution and the one that prevents a class of flaky tests. IOrderService with Place, Cancel, Refund, Report, Export, and AdminSearch is the one that grows until every change recompiles every caller. Split by caller, not by a diagram."},
        {"t": "warn", "title": "What breaks", "text": "A god interface becomes a merge conflict. A test double that throws on unused methods hides the fact that production started calling them."},
        {"t": "lead", "title": "Say this", "text": "I depend on the slice I use. A forty-method service interface is a bunch of reasons to change wearing one name."},

        {"t": "h2", "text": "Dependency inversion"},
        {"t": "p", "text": "High-level policy depends on an abstraction it owns. The SQL or HTTP adapter implements that abstraction. The handler does not reference a concrete SDK type. The composition root, Program.cs, is the place that knows both sides."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface IOrderStore
{
    Task<Order?> FindAsync(int id, CancellationToken ct);
    Task SaveAsync(Order order, CancellationToken ct);
}

public sealed class EfOrderStore(AppDbContext db) : IOrderStore
{
    public Task<Order?> FindAsync(int id, CancellationToken ct)
        => db.Orders.SingleOrDefaultAsync(o => o.Id == id, ct);

    public async Task SaveAsync(Order order, CancellationToken ct)
    {
        db.Orders.Update(order);
        await db.SaveChangesAsync(ct);
    }
}

builder.Services.AddScoped<IOrderStore, EfOrderStore>();
builder.Services.AddScoped<CreateOrderHandler>();"""},
        {"t": "p", "text": "CreateOrderHandler takes IOrderStore. It does not take AppDbContext unless the team has chosen to keep EF in the application project on purpose. Both choices are defensible. The one that fails is a handler that new's up a SqlConnection, because the policy and the adapter are welded together and the test needs a database for a tax rule."},
        {"t": "warn", "title": "What breaks", "text": "An abstraction that mirrors every DbSet method is not inversion. It is a pass-through. Inversion pays off when the port is the use case's language: Find and Save of an aggregate, not GetAll with an Expression."},
        {"t": "lead", "title": "Say this", "text": "The handler owns the interface. Infrastructure implements it. Program.cs wires them. I do not invert a single method that only calls new."},

        {"t": "h2", "text": "Singleton, the interview implementation, and the one you ship"},
        {"t": "p", "text": "Singleton means one instance, with controlled creation. The classic teaching form is a private constructor and a static instance. Static initialization in .NET runs once per process and is safe for that pattern. Lazy<T> with LazyThreadSafetyMode.ExecutionAndPublication is the form you can explain if they ask for lazy creation. Double-checked locking is the interview variant you hope never to maintain."},
        {"t": "p", "text": "In ASP.NET Core you register AddSingleton. The container creates one instance for the process. The type must be thread-safe. It must not hold per-request data, and it must not take a scoped service such as DbContext in its constructor. A second App Service instance is a second singleton. Cross-instance uniqueness is a database constraint, not a static field."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class PricingCatalog
{
    public static readonly PricingCatalog Instance = new();
    private PricingCatalog() { }
    public decimal Rate { get; } = 0.2m;
}

// What I actually ship:
builder.Services.AddSingleton<PricingCatalog>();
builder.Services.AddSingleton(TimeProvider.System);

// Illegal: singleton capturing a scoped DbContext.
// builder.Services.AddSingleton<OrderCache>(); // if OrderCache takes AppDbContext"""},
        {"t": "p", "text": "PricingCatalog.Instance hides the dependency. Tests cannot replace it without a static reset. AddSingleton makes the same lifetime visible in the composition root, and a test can register a different instance. TimeProvider is the modern way to inject a clock as a singleton without writing a static DateTime wrapper. If the catalog must refresh from SQL, it is not a singleton that captures a context. It is a singleton that creates a scope per refresh, or it is scoped."},
        {"t": "warn", "title": "What breaks", "text": "A handwritten singleton in a web app becomes ambient state. A singleton DbContext is disposed after the first request or shared across threads. A lock inside the singleton still does not coordinate the second instance."},
        {"t": "lead", "title": "Say this", "text": "I can write the static singleton. I ship AddSingleton for a thread-safe type with no request data. One instance per process is not one instance per farm. Uniqueness belongs in SQL."},

        {"t": "h2", "text": "Factory versus Strategy at checkout"},
        {"t": "p", "text": "A factory decides how to build an object. A strategy decides how to do a behavior. The names get mixed because both are interfaces with more than one implementation. The question to ask is whether you are choosing a constructor or choosing an algorithm."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface ITaxCalculator
{
    decimal Tax(OrderDraft draft);
}

public sealed class UsTaxCalculator : ITaxCalculator
{
    public decimal Tax(OrderDraft draft) => Math.Round(draft.Subtotal * 0.07m, 2);
}

public sealed class VatCalculator(decimal rate) : ITaxCalculator
{
    public decimal Tax(OrderDraft draft) => Math.Round(draft.Subtotal * rate, 2);
}

public sealed class TaxCalculatorFactory(IConfiguration config)
{
    public ITaxCalculator ForCountry(string country) => country switch
    {
        "US" => new UsTaxCalculator(),
        "DE" => new VatCalculator(config.GetValue<decimal>("Tax:De")),
        _ => throw new InvalidOperationException($"No tax rule for {country}.")
    };
}"""},
        {"t": "p", "text": "ITaxCalculator is the strategy: the handler calls Tax and does not know the rate. TaxCalculatorFactory is the factory: it knows which implementation to build. Keyed DI can replace the factory when the set is fixed at startup. A factory method that only calls new UsTaxCalculator and has one implementation is ceremony. Leave the new at the call site until a second construction path exists. IHttpClientFactory is a factory worth naming because it owns handler lifetimes, which is a real decision, not a wrapper around new."},
        {"t": "warn", "title": "What breaks", "text": "A strategy interface with one implementation and a factory that only forwards new add two types and no test. A factory that contains the tax rule and the construction rule becomes the god class the strategy was meant to avoid."},
        {"t": "lead", "title": "Say this", "text": "Factory builds. Strategy behaves. At checkout the tax rule is a strategy. I extract it when the third country arrives or the rule needs its own tests. Two countries and one if can stay in the handler."},

        {"t": "h2", "text": "Decorator, middleware, and filters"},
        {"t": "p", "text": "All three add behavior around something else. They sit at different layers. Middleware sits on the HTTP pipeline and runs for requests that reach it: correlation ids, exception handling to ProblemDetails, security headers, request logging. Filters sit closer to MVC actions: authorization, validation, result shaping. A decorator wraps an application interface, such as IPriceService, and adds caching or timing. The price service does not know. A queue consumer can use the decorator with no HTTP at all."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class TimingPriceService(IPriceService inner, ILogger<TimingPriceService> log) : IPriceService
{
    public async Task<decimal> PriceAsync(Sku sku, CancellationToken ct)
    {
        var watch = Stopwatch.StartNew();
        decimal price = await inner.PriceAsync(sku, ct);
        log.LogInformation("Priced {Sku} in {Ms} ms", sku.Value, watch.ElapsedMilliseconds);
        return price;
    }
}

// Registration order: the decorator is the outer scoped service.
builder.Services.AddScoped<SqlPriceService>();
builder.Services.AddScoped<IPriceService>(sp =>
    new TimingPriceService(sp.GetRequiredService<SqlPriceService>(),
        sp.GetRequiredService<ILogger<TimingPriceService>>()));"""},
        {"t": "p", "text": "Discount logic does not belong in middleware just because the user id was in a header. The handler can see the rule, and a test can call the handler without the host. Middleware that reads the body and writes a business decision becomes invisible in code review. Use middleware when the concern is every request. Use a filter when it is every action, or a named set of actions. Use a decorator when the concern is a port that has more than one caller."},
        {"t": "warn", "title": "What breaks", "text": "A decorator that swallows exceptions hides faults from the exception handler. Middleware registered after the endpoint does not run for that concern. A chain of three decorators that always all run is a pipeline you should write as three lines in the handler if each line is the business rule."},
        {"t": "lead", "title": "Say this", "text": "Middleware is HTTP. Filters are MVC. A decorator is the port, so a queue consumer gets the same cache or timing. Business rules stay in the handler where a test can see them."},

        {"t": "h2", "text": "Repository and unit of work with EF Core"},
        {"t": "p", "text": "DbContext is a unit of work. It tracks changes and SaveChanges commits them as one transaction by default. DbSet is already a repository. A second generic IRepository<T> that exposes Get, Add, and a predicate usually hides none of the complexity and blocks Include shape, split queries, projections, and ExecuteUpdate."},
        {"t": "p", "text": "A focused port is different. IOrderStore with Find and Save of an aggregate lets the domain stay ignorant of EF when you are serious about that boundary. The implementation is a thin class in the infrastructure project. One SaveChanges per use case is the unit of work. Add an explicit transaction when one use case writes through two contexts or needs a lock hint you can explain."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public interface IOrderStore
{
    Task<Order?> FindAsync(int id, int tenantId, CancellationToken ct);
    Task SaveAsync(Order order, CancellationToken ct);
}

// The generic repository I refuse as a standard:
public interface IRepository<T> where T : class
{
    IQueryable<T> Query();
    Task AddAsync(T entity, CancellationToken ct);
}
// Query() returns IQueryable and makes every caller a query author."""},
        {"t": "p", "text": "IOrderStore is a boundary. IRepository<T> is a wrapper around DbSet that teaches the team to hide SQL. In a small service I inject AppDbContext into the handler and skip the port. I say that in the interview. Four projects for eight classes is how a lead loses the team."},
        {"t": "warn", "title": "What breaks", "text": "A generic repository that calls SaveChanges inside Add commits half of the use case. A unit-of-work wrapper around one DbContext adds a type and no behavior. Two SaveChanges calls without a transaction can commit the order and fail the outbox row."},
        {"t": "lead", "title": "Say this", "text": "DbContext is the unit of work. I will defend a thin store per aggregate. I will not defend IRepository<T> as a house style. It makes bad queries harder to see."},

        {"t": "h2", "text": "CQRS and Mediator on a real API"},
        {"t": "p", "text": "CQRS means the write path and the read path may differ. On a small API that is two handlers and two queries, still on the same database. On a hot read model it can be a projection updated from events, and the read side lags. Split databases when the read and the write need different scaling or different shapes, not when a form has three fields."},
        {"t": "p", "text": "Mediator dispatches a command or query object to one handler. MediatR is the common library. It gives a pipeline for logging, validation, and transactions. The cost is indirection: F12 lands on an interface. Use it when the pipeline behaviors earn their keep. Skip it when the controller can call one application service that is already clear."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed record CreateOrder(int TenantId, string Sku, int Quantity) : IRequest<Result<OrderDto>>;

public sealed class CreateOrderHandler(IOrderStore store, ITaxCalculator tax)
    : IRequestHandler<CreateOrder, Result<OrderDto>>
{
    public async Task<Result<OrderDto>> Handle(CreateOrder request, CancellationToken ct)
    {
        // commands change state. This handler does not call other handlers.
        Order order = Order.Place(request, tax);
        await store.SaveAsync(order, ct);
        return Result<OrderDto>.Ok(OrderDto.From(order));
    }
}

public sealed record GetOrder(int TenantId, int OrderId) : IRequest<OrderDto?>;
// GetOrderHandler projects with AsNoTracking. It does not call SaveChanges."""},
        {"t": "p", "text": "A written rule keeps the mediator honest: commands change state, queries do not, handlers do not call other handlers, and cross-cutting work is a pipeline behavior. Without that rule the mediator becomes a web of hidden calls and the stack trace is noise. A read model in a second table is justified when the list query and the aggregate shape have already fought each other in production."},
        {"t": "warn", "title": "What breaks", "text": "Handlers calling handlers hide the transaction boundary. A query handler that saves 'just a last-viewed stamp' makes GET unsafe. Two databases on day one double the operational load before the domain is stable."},
        {"t": "lead", "title": "Say this", "text": "CQRS is a separate read and write shape, on one database until the shapes diverge. Mediator is a dispatcher I adopt when validation and transaction behaviors earn the indirection. Handlers do not call handlers."},

        {"t": "h2", "text": "Options: which interface you inject"},
        {"t": "p", "text": "Bind a configuration section to a class and validate it on start. A bad setting then fails deployment, not the first order. IOptions<T> is a singleton and does not see later changes. IOptionsSnapshot<T> is scoped and sees changes on the next request, which fits a normal Web API. IOptionsMonitor<T> is for a singleton, such as a hosted service, that must observe changes. Inject the one the lifetime requires. Do not pass IConfiguration into the domain. Secrets come from Key Vault through configuration. The options class exposes only what the feature needs."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class PricingOptions
{
    public decimal Rate { get; init; }
    public string Currency { get; init; } = "USD";
}

builder.Services.AddOptions<PricingOptions>()
    .Bind(builder.Configuration.GetSection("Pricing"))
    .Validate(o => o.Rate is >= 0 and <= 1, "Pricing:Rate must be between 0 and 1.")
    .ValidateOnStart();

public sealed class CreateOrderHandler(IOptionsSnapshot<PricingOptions> pricing)
{
    public decimal Rate => pricing.Value.Rate;
}"""},
        {"t": "p", "text": "ValidateOnStart runs the checks when the host starts. A slot swap to a configuration that omits Pricing:Rate fails the new slot before traffic moves, if the health check actually starts the host. IOptionsSnapshot inside a scoped handler sees a reload on the next request. A singleton that captured IOptions<PricingOptions> at construction keeps the old rate, which is sometimes what you want and must be a choice."},
        {"t": "warn", "title": "What breaks", "text": "Reading IConfiguration string keys deep in the domain scatters configuration. A missing ValidateOnStart lets the process boot and crash on the first order. Injecting IOptionsSnapshot into a singleton is a captive dependency."},
        {"t": "lead", "title": "Say this", "text": "I bind a typed options class and ValidateOnStart. IOptions is a fixed snapshot, IOptionsSnapshot is per request, IOptionsMonitor is for singletons that watch changes. Startup validation is a release check."},

        {"t": "h2", "text": "Result or throw"},
        {"t": "p", "text": "Throw for defects and for situations the caller cannot usefully handle: a broken invariant, a null the type system promised would exist, an IO failure after retries. Return a Result, or a validation problem, for expected business outcomes: invalid input, insufficient stock, a duplicate idempotency key. Validation becomes HTTP 400 with ProblemDetails. A conflict becomes 409. An exception you did not expect becomes 500 from one exception-handler middleware, with a correlation id. Do not catch Exception at the bottom of every method."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public readonly record struct Result<T>(T? Value, string? Error)
{
    public bool Ok => Error is null;
    public static Result<T> Success(T value) => new(value, null);
    public static Result<T> Fail(string error) => new(default, error);
}

public Result<Order> Place(CreateOrder command)
{
    if (command.Quantity <= 0)
        return Result<Order>.Fail("Quantity must be positive."); // expected
    if (string.IsNullOrWhiteSpace(command.Sku))
        return Result<Order>.Fail("Sku is required.");
    return Result<Order>.Success(new Order { /* invariant holds */ });
}

// A bug still throws:
if (store is null)
    throw new InvalidOperationException("IOrderStore was not registered.");"""},
        {"t": "p", "text": "Quantity less than one is a client mistake. A null store is a defect in composition. Treating both as Result means the hosting model never sees the defect, and crash telemetry stays quiet. Treating both as exceptions means clients parse 500s for validation. The split is the design."},
        {"t": "warn", "title": "What breaks", "text": "A Result that carries a stack trace for bugs hides failures from the process. An exception for 'coupon does not apply' trains clients to retry a 500. Catching Exception and returning Ok is how a failed save becomes a 200."},
        {"t": "lead", "title": "Say this", "text": "Expected business outcomes return a result and a 4xx. Defects throw, and one middleware turns them into a 500 with a trace id. I do not hide bugs inside Result."},

        {"t": "h2", "text": "When to add a pattern in review"},
        {"t": "p", "text": "Ask what change you are protecting, who feels the pain, and what the pattern costs in navigation and tests. If the change is speculative, keep the code in one type. If the change has already happened twice, extract an interface at the seam that varied. Ask how the failure will look in logs. A pattern that adds three layers and no correlation id has made the system harder to operate. Write the decision in the PR or a one-page ADR: context, decision, consequences."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """# ADR 004 — Pricing stays a module
# Context: one team, one query shape, a proposal to extract a pricing service
# and a generic repository before the release.
# Decision: IPriceService in this process. No IRepository<T>. No new deployable.
# Consequences: SQL stays visible in one class. A later split is possible
# because callers already depend on IPriceService. We do not operate a second
# database this quarter."""},
        {"t": "p", "text": "The ADR is the interview artifact. Offer to walk one: why you kept a modular monolith, why you chose Service Bus, or why you dropped a generic repository. That story beats a pattern list. The relationship cost belongs in the story too. The senior developer who wanted the service can own the module boundary so the later split is still possible."},
        {"t": "warn", "title": "What breaks", "text": "Patterns added for a resume are permanent. The team pays the navigation cost every week. A verbal decision that is not written gets relitigated in the next PR."},
        {"t": "lead", "title": "Say this", "text": "I add a pattern when the change has happened twice or the seam is already obvious. I write the decision down. Speculative flexibility is a cost."},

        {"t": "h2", "text": "Pattern catalog, with the refusal"},
        {"t": "p", "text": "The interview questions above are the ones to go deep on. The rest of the catalog still needs a sentence, a shape, and the day you refuse it. Skim these until the refusal is automatic."},

        {"t": "h3", "text": "Abstract factory"},
        {"t": "p", "text": "An abstract factory builds a family of related objects together. In a CRUD API this is rare. A per-tenant set of a blob container plus a topic plus a SQL connection factory can be one, if those objects must match. One product is not a family. Inject the one service."},
        {"t": "code", "text": """public interface ITenantInfrastructure
{
    IOrderStore Store { get; }
    ServiceBusSender Sender { get; }
}"""},
        {"t": "lead", "title": "Say this", "text": "I use it when several objects must be created as a matched set. One product is just a constructor."},

        {"t": "h3", "text": "Builder"},
        {"t": "p", "text": "A builder assembles a complex object step by step. WebApplicationBuilder and a test-data builder are the ones you have used. An object with two constructor parameters does not need a builder. Required members and a constructor are clearer."},
        {"t": "code", "text": """Order order = new OrderBuilder()
    .WithTenant(10)
    .WithLine("AB-1", 2, 19.00m)
    .WithLine("CD-2", 1, 5.00m)
    .Build();"""},
        {"t": "lead", "title": "Say this", "text": "Builders earn their place in tests and in host setup. Two parameters is a constructor."},

        {"t": "h3", "text": "Adapter"},
        {"t": "p", "text": "An adapter makes an outside API look like your interface. A class that wraps a payment SDK is an adapter. Wrapping a type you own and control is an extra hop. Map at the boundary so the vendor's DTO does not leak into the handler."},
        {"t": "code", "text": """public sealed class StripePaymentAdapter(StripeClient sdk) : IPaymentCapture
{
    public async Task<CaptureResult> CaptureAsync(Money amount, string key, CancellationToken ct)
    {
        var charge = await sdk.Charges.CreateAsync(amount.Amount, key, ct);
        return new CaptureResult(charge.Id, charge.Status == "succeeded");
    }
}"""},
        {"t": "lead", "title": "Say this", "text": "I adapt types I do not own. The handler sees CaptureResult, not the vendor's charge object."},

        {"t": "h3", "text": "Facade"},
        {"t": "p", "text": "A facade is one entry in front of a messy subsystem. An application service that places an order by calling inventory, tax, and the store is a facade if those three calls are an accident of history. The failure mode is a new god class. If the facade grows a rule, move the rule into a type with a name."},
        {"t": "code", "text": """public async Task<OrderDto> PlaceAsync(CreateOrder command, CancellationToken ct)
{
    await inventory.ReserveAsync(command, ct);
    decimal tax = taxCalculator.Tax(command);
    return await store.SaveAsync(Order.Place(command, tax), ct);
}"""},
        {"t": "lead", "title": "Say this", "text": "A facade hides a messy edge. I delete it when it becomes the only place business rules live without a name."},

        {"t": "h3", "text": "Proxy"},
        {"t": "p", "text": "A proxy is a stand-in that controls access to the real object. EF Core lazy-loading proxies and a caching proxy are the examples. The trap is a proxy that hides a query. Touching order.Lines then runs SQL, and a loop becomes N+1. Prefer an explicit load or a projection unless a specific screen needs lazy loading and the team logs the SQL."},
        {"t": "code", "text": """public sealed class CachingPriceService(IPriceService inner, IMemoryCache cache) : IPriceService
{
    public Task<decimal> PriceAsync(Sku sku, CancellationToken ct)
        => cache.GetOrCreateAsync(sku.Value, entry =>
        {
            entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5);
            return inner.PriceAsync(sku, ct);
        })!;
}"""},
        {"t": "lead", "title": "Say this", "text": "A proxy controls access. A cache is a proxy I can explain. An EF lazy proxy that hides N+1 is one I leave off."},

        {"t": "h3", "text": "Observer"},
        {"t": "p", "text": "Dependents hear a change. A C# event is an in-process observer. Across processes, a Service Bus message is the durable form. A C# event does not survive a crash and does not reach the second instance. If you need a guaranteed cross-service workflow, use a message with a consumer contract, not an event handler on a singleton."},
        {"t": "code", "text": """public sealed class OrderPlaced
{
    public event EventHandler<int>? Placed;
    public void Raise(int orderId) => Placed?.Invoke(this, orderId);
}
// Fine inside one process. The email worker still needs the outbox."""},
        {"t": "lead", "title": "Say this", "text": "In-process, an event. Across services, a message. An event is not a transaction."},

        {"t": "h3", "text": "Command"},
        {"t": "p", "text": "A command represents a request as an object so it can be queued, logged, or retried. A MediatR IRequest and a Service Bus message are commands. A command object that is only a method call with extra steps is noise. The object earns its place when it crosses a boundary or a pipeline."},
        {"t": "code", "text": """public sealed record CreateOrder(int TenantId, string Sku, int Quantity, string IdempotencyKey);"""},
        {"t": "lead", "title": "Say this", "text": "I make a command when the request is a message or a pipeline. I keep a method call when it is a method call."},

        {"t": "h3", "text": "Chain of responsibility"},
        {"t": "p", "text": "A request passes along handlers until one handles it. ASP.NET Core middleware and the filter pipeline are the chain you already operate. A chain of three classes that always all run is a pipeline you should write plainly. Use the chain when some handlers may stop the request, as authentication does."},
        {"t": "code", "text": """app.UseExceptionHandler();
app.UseHttpsRedirection();
app.UseRouting();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();
app.MapControllers();"""},
        {"t": "lead", "title": "Say this", "text": "The HTTP pipeline is my chain of responsibility. I do not add a second chain of classes that always all run."},

        {"t": "h3", "text": "Template method"},
        {"t": "p", "text": "A base class defines the algorithm and subclasses replace steps. A file importer with abstract Parse and Save is the honest example. If the base class forces a step a subclass does not need, prefer composition: pass the steps in. Template method plus a deep inheritance tree is hard to test."},
        {"t": "code", "text": """public abstract class FileImporter
{
    public async Task RunAsync(Stream input, CancellationToken ct)
    {
        var rows = Parse(input);
        await SaveAsync(rows, ct);
    }
    protected abstract IReadOnlyList<RawRow> Parse(Stream input);
    protected abstract Task SaveAsync(IReadOnlyList<RawRow> rows, CancellationToken ct);
}"""},
        {"t": "lead", "title": "Say this", "text": "Template method when the skeleton is stable and the steps vary. Composition when a subclass would have to stub a step it does not want."},

        {"t": "h3", "text": "Specification"},
        {"t": "p", "text": "A specification encapsulates a business predicate so two queries can share it and a test can run it without SQL. A specification engine for one Where clause is ceremony. A testable expression for 'open orders older than 30 days' is the version worth keeping, and it must stay translatable if EF will use it."},
        {"t": "code", "text": """public static class OrderSpecs
{
    public static Expression<Func<Order, bool>> OpenUnpaid(DateTimeOffset cutoff)
        => o => o.Status == "Open" && o.PaidUtc == null && o.CreatedUtc < cutoff;
}

await db.Orders.Where(OrderSpecs.OpenUnpaid(cutoff)).ToListAsync(ct);"""},
        {"t": "lead", "title": "Say this", "text": "I extract a predicate when two queries and a test share it. I do not build a specification framework for one filter."},

        {"t": "h3", "text": "Outbox, saga, circuit breaker, strangler, anti-corruption"},
        {"t": "p", "text": "These show up again on later days with full examples. The Day 2 answer is the refusal."},
        {"t": "b", "items": [
            "Outbox: the business row and the message row commit together. Refuse publish-then-save and save-then-publish.",
            "Saga: a long process with compensation. Refuse it when one local SQL transaction would do.",
            "Circuit breaker: fail fast when a dependency is sick, on an HTTP resilience pipeline. Refuse a breaker on your own database for a single timeout with no policy.",
            "Strangler fig: one route at a time to the new host. Refuse a nine-month rewrite branch.",
            "Anti-corruption layer: translate a legacy model at the edge. Refuse sharing the legacy entity project to go faster.",
        ]},
        {"t": "lead", "title": "Say this", "text": "I can name each of these in one sentence and name the day I would not use it. The full mechanics are Days 6, 7, and 8."},

        {"t": "h2", "text": "Patterns you have rarely shipped"},
        {"t": "p", "text": "Have a one-line honest answer. A calm scope statement beats a bluffed UML diagram."},
        {"t": "b", "items": [
            "Prototype: clone to avoid expensive setup. I copy DTOs explicitly. I rarely keep a prototype registry.",
            "Flyweight: share immutable intrinsic state. String interning is the example I cite. I do not design it into CRUD.",
            "Bridge: split abstraction from implementation so both can vary. I usually inject an interface and stop.",
            "Composite: a tree of parts treated as one part. A category tree or a menu. Uncommon on a flat order API.",
            "State: behavior changes with state. An order status transition belongs in a named method that rejects illegal jumps, not a pile of flags.",
            "Memento: capture and restore state. I use a persisted workflow row or an audit table.",
            "Visitor: add an operation over a fixed type hierarchy. Compilers and document trees. I have rarely shipped one.",
            "Interpreter: a grammar and an evaluator. EF expression trees are the interpreter I use. I do not write a rules language unless the business truly authors rules.",
        ]},
        {"t": "h3", "text": "Example of State, the one worth showing"},
        {"t": "code", "text": """public sealed class Order
{
    public string Status { get; private set; } = "Pending";

    public void MarkPaid()
    {
        if (Status != "Pending")
            throw new InvalidOperationException($"Cannot pay from {Status}.");
        Status = "Paid";
    }
}"""},
        {"t": "p", "text": "That is a state machine small enough to live on the entity. A table of State objects is justified when each status has different behavior and the if statements have already spread. Say you have shipped the method more often than the pattern."},
        {"t": "lead", "title": "Say this", "text": "I will say I have rarely shipped Visitor or Interpreter. I will show a status method on the order, which is the state rule the business actually has."},

        {"t": "h2", "text": "A solution shape you can draw"},
        {"t": "p", "text": "Four projects is a boundary, not a badge. Use it when the team needs the dependency rule enforced by the compiler. Collapse it when the service is small."},
        {"t": "b", "items": [
            "Api: controllers or endpoints, auth, middleware, the composition root.",
            "Application: use cases, ports, validators. No EF reference if you are serious about the boundary.",
            "Domain: entities, value objects, domain rules. No ASP.NET reference.",
            "Infrastructure: EF Core, HTTP adapters, Service Bus. Implements the ports.",
            "Tests: domain tests with no host, and a smaller set of API tests with WebApplicationFactory.",
        ]},
        {"t": "code", "text": """builder.Services.AddScoped<IOrderStore, EfOrderStore>();
builder.Services.AddScoped<CreateOrderHandler>();
builder.Services.AddOptions<PricingOptions>()
    .Bind(builder.Configuration.GetSection("Pricing"))
    .Validate(o => o.Rate is >= 0 and <= 1, "Pricing:Rate must be between 0 and 1.")
    .ValidateOnStart();"""},
        {"t": "p", "text": "The compiler enforces the rule only if Api references Application and Infrastructure, Application references Domain, and Domain references nothing of yours. Infrastructure references Application so it can implement the ports. If every project references every other project, the folders are decorative."},
        {"t": "warn", "title": "What breaks", "text": "Domain referencing EF 'just for attributes' pulls the data stack upward. A test project that only boots the host means a tax rule takes seconds to fail. Four projects for eight classes slows the team more than it protects them."},
        {"t": "lead", "title": "Say this", "text": "I draw Api, Application, Domain, and Infrastructure when the boundary is real. I collapse Application and Domain on a small service and I say so."},
        {"t": "break"},
    ]
