# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 1 — C# a tech lead can defend"},
        {"t": "p", "text": "Day 1 is the language panel. They are not scoring a definition. They are scoring whether you can connect a language rule to a bug in an API: a copy that diverged, a query that ran twice, a thread that blocked, a dictionary key that moved, a socket that leaked. Every section below is one of those bugs, with the code that causes it and the code you would leave in the pull request."},

        {"t": "h2", "text": "Class, struct, and record"},
        {"t": "p", "text": "A class is a reference type. Variables hold a reference, and assignment copies that reference, so two variables can observe the same object. The instance lives on the heap. Use a class when identity matters: an EF Core entity, a service, anything the change tracker must recognize as the same row across a query and an update."},
        {"t": "p", "text": "A struct is a value type. Assignment copies the data. A local struct may live on the stack. A struct stored as a field of a class lives inside that object on the heap. A struct in an array of structs lives inline in the array. Copying a large struct copies every field. If one copy is mutated, the other copy does not change, which is a silent bug when the struct was meant to be one order draft."},
        {"t": "p", "text": "A record is a class with value-based equality, a compact constructor, and a useful ToString, unless you declare a record struct. Use a record for a DTO, a message, or a result. Use a record struct only when the data is small and equality should compare contents. EF entities stay classes, because the tracker depends on reference identity and because a record's synthesized equality is the wrong identity for a row whose fields change."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class Order          // identity: the row
{
    public int Id { get; set; }
    public string Number { get; set; } = "";
    public decimal Total { get; set; }
}

public readonly record struct Money(decimal Amount, string Currency);

public sealed record OrderCreated(int OrderId, DateTimeOffset OccurredUtc);

// A 200-byte mutable struct passed through the API is a review reject.
// Copies diverge, and each pass copies the payload.
public struct OrderDraft
{
    public string CustomerName;
    public string Line1;
    public decimal Total;
    // ... many more fields
}"""},
        {"t": "p", "text": "Money is a few bytes, immutable, and compared by value, so a record struct fits. OrderCreated is a message: two instances with the same order id and timestamp are the same fact, so a record fits. Order is an entity: two instances with the same Id are the same row only because you say so in the model, and EF must track one instance. OrderDraft is the shape a lead rejects. Pass a record or a class instead, and keep the payload small on purpose."},
        {"t": "warn", "title": "What breaks", "text": "A large mutable struct copied into a method, then mutated, leaves the caller's copy unchanged. A record used as an EF entity surprises the tracker and equality in dictionaries. The sentence 'structs live on the stack and classes live on the heap' is incomplete: a struct field inside a class lives with the object."},
        {"t": "lead", "title": "Say this", "text": "Class when identity matters, record when the value is the identity, struct when the value is small and immutable. I reject a large struct in the API layer and a record used as an EF entity."},

        {"t": "h2", "text": "ref, out, in, and params"},
        {"t": "p", "text": "All three of ref, out, and in pass a variable by reference so the method can reach the caller's storage. They differ in who initializes it and whether the callee may write. params packs a variable argument list. On a public Web API these are rarely the right surface, because HTTP has no ref. They still show up in parsers, hot numeric code, and the BCL's Try pattern, so a lead can explain them and then choose a return value."},
        {"t": "b", "items": [
            "ref: the caller assigns the variable first. The method may read and write it.",
            "out: the caller does not need to assign it. The method must assign it on every normal return path. TryParse is the pattern the BCL taught everyone.",
            "in: a readonly reference. The method cannot assign the variable. This matters for a large readonly struct, because the call does not copy the struct.",
            "params: the compiler packs arguments. Historically that was an array allocation. Current compilers can use params collections, including spans in hot paths, so a small call may avoid the array. Do not promise that every params call is allocation-free.",
        ]},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public readonly record struct Matrix4x4(float M11, float M12 /* ... 16 floats */);

public static void Scale(in Matrix4x4 matrix, float factor)
{
    // reads matrix.M11 without copying the 16 floats
}

public static bool TryParseOrderId(ReadOnlySpan<char> text, out int id)
    => int.TryParse(text, out id);

// The public shape I would actually ship:
public readonly record struct ParsedOrderId(bool Ok, int Id);

public static ParsedOrderId ParseOrderId(string text)
    => int.TryParse(text, out var id)
        ? new ParsedOrderId(true, id)
        : new ParsedOrderId(false, 0);"""},
        {"t": "p", "text": "Scale takes in so a 64-byte matrix is not copied at the call. TryParseOrderId is honest about failure without an exception, which is right for untrusted input. ParsedOrderId is the shape I want on a public method inside the solution: the result is a value, the caller cannot forget to declare an out variable, and the method signature still makes sense if a future transport is a queue rather than a direct call."},
        {"t": "warn", "title": "What breaks", "text": "A public ref or out parameter makes ownership unclear and cannot cross HTTP. An in parameter on a small struct is noise. A params object[] boxes value types. Forgetting that out must be assigned on every path is a compile error, which is the point of out."},
        {"t": "lead", "title": "Say this", "text": "ref reads and writes the caller's variable, out must be assigned by the callee, in is a readonly reference that avoids copying a large struct. On a Web API I return a result or a tuple. TryParse is the exception the BCL already taught."},

        {"t": "h2", "text": "Deferred LINQ, IEnumerable, and IQueryable"},
        {"t": "p", "text": "LINQ to Objects builds an iterator. The filter does not run when you write Where. It runs when you foreach, when you call Count, or when you materialize with ToList. A second enumeration runs the query again. That is deferred execution."},
        {"t": "p", "text": "IQueryable<T> holds an expression tree, not a delegate. EF Core walks that tree when you enumerate and tries to produce SQL. Where, OrderBy, and Select composed on IQueryable stay in the tree. The moment you treat the query as IEnumerable<T>, further operators run in memory on whatever the SQL already returned. The boundary rule is: keep IQueryable inside the data method, apply the filters, project, and materialize with ToListAsync or SingleOrDefaultAsync. Return a list, a page, or a DTO. Returning IQueryable from a service lets every caller change the SQL, and it drags the DbContext lifetime out of the method that opened it."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Two round trips. Often what you want: a total and a page.
IQueryable<Order> query = db.Orders.Where(o => o.TenantId == tenantId);
int count = await query.CountAsync(ct);
List<OrderListItem> page = await query
    .OrderByDescending(o => o.CreatedUtc)
    .Take(50)
    .Select(o => new OrderListItem(o.Id, o.Number, o.Total))
    .ToListAsync(ct);

// The bug: assigning to IEnumerable too early.
IEnumerable<Order> rows = db.Orders.Where(o => o.TenantId == tenantId);
List<Order> open = rows.Where(o => o.Status == "Open").ToList();
// SQL returned every order for the tenant. "Open" was filtered in the process.

// Deferred, so this hits the database twice if orders is IQueryable or a lazy iterator.
int a = orders.Count();
int b = orders.Count();"""},
        {"t": "p", "text": "The first block is two SQL statements by design. The second block looks like a filter and is a data leak of cost: the tenant's history comes over the wire so the process can throw most of it away. The third block is why a helper that enumerates a query for logging and then returns it will surprise the next caller. Materialize once, at the edge, into a concrete list."},
        {"t": "warn", "title": "What breaks", "text": "A second foreach on a deferred query repeats the work. A predicate EF cannot translate throws in current EF Core, or, if you forced client evaluation, silently pulls rows. A disposed DbContext throws if a caller enumerates an IQueryable after the request scope ended."},
        {"t": "lead", "title": "Say this", "text": "IQueryable is an expression tree that becomes SQL at enumeration. IEnumerable after that point is memory. I keep the query inside the data method, project, and materialize. I do not return IQueryable from a service."},

        {"t": "h2", "text": "async, await, and the ways production gets it wrong"},
        {"t": "p", "text": "An async method returns a Task or a ValueTask that represents the work. The compiler builds a state machine. At an await, if the operation is already complete, the method continues. If it is not, the method yields. In ASP.NET Core the continuation is scheduled on the thread pool. There is no SynchronizationContext to marshal back to, which is why ConfigureAwait(false) is not required in application code the way it was in classic ASP.NET or in UI apps. The request thread is free to serve something else while SQL or HTTP is in flight."},
        {"t": "p", "text": "The bugs that still take APIs down are independent of that fact. Sync-over-async calls .Result or .Wait and blocks a thread-pool thread until the task finishes. Under load, the pool has no thread left to run the continuation, and latency falls off a cliff. That is thread-pool starvation. async void is for event handlers. Anywhere else, the caller cannot wait, and an exception bypasses the caller's try. A missing CancellationToken means a disconnected client still holds a SQL command and an HTTP call. ValueTask is for a hot path that often completes synchronously. Await a ValueTask once. Task is the default for public methods."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """[HttpGet("{id:int}")]
public async Task<ActionResult<OrderDto>> Get(int id, CancellationToken ct)
{
    OrderDto? order = await db.Orders.AsNoTracking()
        .Where(o => o.Id == id && o.TenantId == tenant.Id)
        .Select(o => new OrderDto(o.Id, o.Number, o.Total))
        .SingleOrDefaultAsync(ct);          // pass the token into EF
    return order is null ? NotFound() : Ok(order);
}

// Pass HttpContext.RequestAborted from the controller, or the CancellationToken
// the framework already bound on the action.

// The bug a review rejects:
OrderDto stuck = db.Orders
    .Select(o => new OrderDto(o.Id, o.Number, o.Total))
    .SingleAsync(ct)
    .Result;

// Also a reject: starting unbounded work.
await Task.WhenAll(orderIds.Select(id => ChargeAsync(id))); // 500 charges at once"""},
        {"t": "p", "text": "Get yields at SingleOrDefaultAsync. The thread returns to the pool. When SQL completes, a pool thread resumes the method and writes the result. If the client disconnects, ct fires and EF attempts to cancel the command. The .Result line blocks a pool thread for the whole round trip. The WhenAll line is correct as a language feature and dangerous as a capacity plan: each ChargeAsync holds a connection. Cap the degree of parallelism with Parallel.ForEachAsync or a channel, and set a number you can justify against the SQL pool."},
        {"t": "warn", "title": "What breaks", "text": "ConfigureAwait(false) in a controller does not fix a blocked .Result. async void in a service drops exceptions. Awaiting a ValueTask twice is undefined. Catching an exception and not observing a task faults the process through the unobserved-task path only in older behaviors; on modern .NET you still log it, because a swallowed task is a lost order."},
        {"t": "lead", "title": "Say this", "text": "await releases the thread while IO is in flight. I pass CancellationToken from the request into EF and HttpClient. .Result fails review. I cap outbound parallelism so one request cannot open 500 SQL commands."},

        {"t": "h2", "text": "Equality, hash codes, and records"},
        {"t": "p", "text": "ReferenceEquals asks whether two variables point at the same object. Object.Equals on a class does that by default. Value types compare contents. GetHashCode must agree with Equals: if two objects are equal, they must have the same hash code. The hash must stay stable while the object sits in a Dictionary or a HashSet. If you override one, override the other, and implement IEquatable<T> on a value-like type so the generic path does not box."},
        {"t": "p", "text": "A record synthesizes Equals, GetHashCode, and equality operators from its members. That is what you want for a message or a DTO. It is the wrong default for an entity whose identity is the primary key and whose other fields change. Anonymous types and tuples also use value equality, which is useful in tests and a bad idea for a mutable cache key."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed record Sku(string Value);

Sku a = new("AB-1");
Sku b = new("AB-1");
bool same = a == b; // true, value equality

var seen = new HashSet<Sku>();
seen.Add(new Sku("AB-1"));
bool hit = seen.Contains(new Sku("AB-1")); // true

// The bug: a mutable class used as a key.
public sealed class CacheKey
{
    public string Tenant { get; set; } = "";
    public int OrderId { get; set; }
    public override int GetHashCode() => HashCode.Combine(Tenant, OrderId);
    public override bool Equals(object? obj)
        => obj is CacheKey k && k.Tenant == Tenant && k.OrderId == OrderId;
}

var key = new CacheKey { Tenant = "acme", OrderId = 10 };
var cache = new Dictionary<CacheKey, OrderDto> { [key] = dto };
key.Tenant = "other";          // bucket changed; lookup misses forever"""},
        {"t": "p", "text": "Sku works because nothing can change Value after construction. CacheKey looks correct and fails the moment a caller mutates Tenant. The entry remains in the old bucket. A lead bans mutable dictionary keys and uses a record, a value tuple, or a readonly struct for the key. For an Order entity, equality by Id can be useful in tests, and you still do not drop Order instances into a HashSet keyed by a hash of Total."},
        {"t": "warn", "title": "What breaks", "text": "Equal objects with different hash codes corrupt dictionaries. A hash that changes after insertion is a permanent miss. A record's with-expression returns a new instance, so the old instance is unchanged, which is what you want for a message and surprising if someone thought with mutated the entity."},
        {"t": "lead", "title": "Say this", "text": "Equal objects share a hash code, and the hash stays stable in the collection. Records give me that for contracts. Entities stay classes with key identity. I ban mutable dictionary keys."},

        {"t": "h2", "text": "Disposal and ownership in ASP.NET Core"},
        {"t": "p", "text": "IDisposable and IAsyncDisposable mean the type owns a resource that the garbage collector will not release on time: a socket, a file handle, an unmanaged buffer, or another disposable it created. using and await using put the lifetime on the screen. Dispose should be idempotent. The DI container disposes the instances it created: scoped services at the end of the request, singletons at host shutdown. You dispose what you created. You do not dispose what you were given, unless the contract says the recipient takes ownership."},
        {"t": "p", "text": "DbContext is registered scoped and disposed by the scope. Disposing it inside a handler, or holding it in a singleton, both break that contract. HttpClient created through IHttpClientFactory is the special case worth naming: disposing the client does not tear down the pooled handler. A new HttpClient per call, with its own handler, exhausts sockets. One static HttpClient held forever can ignore DNS changes. The factory is the default."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """await using var connection = new SqlConnection(connectionString);
await connection.OpenAsync(ct);
await using var command = connection.CreateCommand();
command.CommandText = "SELECT Total FROM orders.Orders WHERE Id = @id";
// both dispose at the end of the block, even if the query throws

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Orders")));
// scoped. The request scope disposes it. Business code does not.

builder.Services.AddHttpClient<TaxClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Tax:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(2);
});"""},
        {"t": "p", "text": "The connection and command are owned by the method, so await using is correct. The DbContext is owned by the scope, so the handler takes it in the constructor and does not call Dispose. TaxClient is typed and created by the factory. A BackgroundService that needs a DbContext creates a scope per unit of work with IServiceScopeFactory, awaits the work, and disposes the scope. It does not take AppDbContext in its own constructor, because the hosted service is a singleton."},
        {"t": "warn", "title": "What breaks", "text": "Disposing a singleton DbContext on the first request makes every later request fail. Not disposing a SqlConnection you opened yourself leaks pooled connections until the pool blocks. Double disposal must be safe. A using around an instance you do not own disposes it for the next caller in the same scope."},
        {"t": "lead", "title": "Say this", "text": "The creator disposes. DI disposes what it created, at the end of the scope or at shutdown. I use the HTTP client factory. Unclear ownership shows up as a leak under load, not in a single debug session."},

        {"t": "h2", "text": "Boxing, and when it matters on a Web API"},
        {"t": "p", "text": "Boxing allocates an object on the heap to hold a copy of a value type, which happens when the value is treated as object or as a non-generic interface it implements. Unboxing casts that object back to the value type and checks the type. One box is noise. A box per integer in a tight loop, a non-generic collection, or a logger that takes object for every argument shows up in a trace as allocations."},
        {"t": "p", "text": "Generics exist so List<int> stores ints without boxing. LINQ on a List<int> uses a struct enumerator for the same reason. For a normal CRUD API the time is usually in SQL, not in boxes. A lead asks for a trace before talking about boxing, and then talks about it when the trace says the parser or the formatter is allocating."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """int n = 42;
object boxed = n;       // allocates
int back = (int)boxed;  // unbox, type check

List<int> ids = [10, 11, 12];          // no box per int
var legacy = new ArrayList { 10, 11 }; // boxes each int

// Interface call on a struct can box unless the call site is constrained.
IComparable comparable = n;

void Log<T>(T value) { /* no box when T is a struct and you do not cast to object */ }
void LogObject(object value) { } // LogObject(n) boxes"""},
        {"t": "p", "text": "If an orders list endpoint is slow, open the SQL dependency first. If a high-volume webhook parser shows up as Gen0 allocations in a profile, then look at boxing, at string allocations, and at whether a Span-based parse can stay on the stack. Mentioning boxing in the interview without that sequence sounds like year four."},
        {"t": "warn", "title": "What breaks", "text": "Casting a boxed int to long throws. Boxing in a per-request log of every property allocates on the hot path. Micro-optimizing boxing while a query scans a million rows does not move p95."},
        {"t": "lead", "title": "Say this", "text": "Boxing wraps a value type in an object. Generics avoid it. I ask for a trace. If the time is in SQL, boxing is a distraction. If the time is allocations in a parser, then I remove the boxes."},

        {"t": "h2", "text": "Shared state, lock, and why lock cannot cross await"},
        {"t": "p", "text": "Immutable data needs no lock. A request-scoped DbContext is confined to one request, so you do not share it across threads. A counter can use Interlocked. A cache of independent keys can use ConcurrentDictionary. A critical section that must not run twice at once in one process can use lock on a private object. The lock statement is reentrant on the same thread and releases if the block throws. It cannot span an await: Monitor is owned by the thread that entered it, and the continuation may run on another thread. The compiler rejects awaiting inside a lock. Across an await, use SemaphoreSlim.WaitAsync and Release in a finally."},
        {"t": "p", "text": "A correct lock is still per process. Two App Service instances have two locks and two memories. A static list mutated from requests is a race even on one instance, and it is a consistency bug the moment you scale to two. Shared business state belongs in SQL, in a distributed cache you have chosen on purpose, or in a queue."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """public sealed class OrderNumberGenerator
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly AppDbContext _db;

    public async Task<string> NextAsync(CancellationToken ct)
    {
        await _gate.WaitAsync(ct);
        try
        {
            int n = await _db.Counters.Select(c => c.Value).SingleAsync(ct);
            // still the wrong design once two instances run: the gate is local
            return $"ORD-{n}";
        }
        finally
        {
            _gate.Release();
        }
    }
}

// In-process and honest:
private int _hits;
public void Hit() => Interlocked.Increment(ref _hits);

// The unique number that survives two instances:
// UNIQUE constraint or a SEQUENCE / identity in SQL, not a static int."""},
        {"t": "p", "text": "The semaphore makes NextAsync safe inside one process and still loses if two instances read the same counter. The fix is a SQL sequence, an identity, or an update that increments under a row lock and returns the new value. Interlocked is the right tool for a process-local metric. lock on this, on a Type, or on a string interned by the runtime can deadlock against code you do not own. Use a private readonly object, or do not use lock at all once an await is involved."},
        {"t": "warn", "title": "What breaks", "text": "Awaiting inside lock does not compile, and a hand-rolled Monitor.Enter that is not released on the same thread deadlocks. A static mutable field looks fine in a single-instance dev box and splits brain when the platform scales out. SemaphoreSlim constructed with (1, 1) and released too often throws. Forgetting finally leaks the gate forever."},
        {"t": "lead", "title": "Say this", "text": "lock is for a synchronous critical section on a private object. Across await I use SemaphoreSlim. A lock does not coordinate two App Service instances. Shared state goes in SQL or a real distributed store."},

        {"t": "h2", "text": "String immutability"},
        {"t": "p", "text": "A string cannot be changed. Concatenation allocates a new string and copies both sides. In a loop that builds a line per order, that copying becomes quadratic. StringBuilder mutates a buffer. For a handful of pieces, interpolation is clear and the allocation of the final string is the one you were going to pay anyway. An interpolated string still allocates the result. string.Create is the conscious API when you know the length and want to fill a buffer."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// Quadratic copying if lines is large.
string csv = "";
foreach (OrderLine line in lines)
    csv += line.Sku + "," + line.Quantity + "\\n";

var builder = new StringBuilder(lines.Count * 32);
foreach (OrderLine line in lines)
    builder.Append(line.Sku).Append(',').Append(line.Quantity).Append('\\n');
string once = builder.ToString();

// Fine: one result, a few pieces.
string label = $"{order.Number} ({order.Status})";"""},
        {"t": "warn", "title": "What breaks", "text": "Building a million-row export with += will allocate itself into a timeout. StringBuilder is the wrong tool for a SQL query: concatenate parameters and you have an injection bug. Use parameters."},
        {"t": "lead", "title": "Say this", "text": "Strings do not change. A loop that concatenates copies. StringBuilder, or a single interpolation, is the conscious choice. I do not build SQL by concatenating input."},

        {"t": "h2", "text": "Fundamentals they still ask"},
        {"t": "p", "text": "These are short. Each one has a decision, not only a definition. If the panel stops at the definition, give the first sentence and stop."},

        {"t": "h3", "text": "Abstract class versus interface"},
        {"t": "p", "text": "An abstract class shares a base implementation and consumes the single class inheritance slot. An interface is a contract, and a type can implement many. Start with an interface for a dependency you want to fake in tests. Use an abstract class when subclasses truly share state and a protected algorithm."},
        {"t": "code", "text": """public interface ITaxCalculator
{
    decimal Tax(Order order);
}

public abstract class FileImporter
{
    public async Task RunAsync(Stream input, CancellationToken ct)
    {
        IReadOnlyList<RawRow> rows = Parse(input);
        await SaveAsync(rows, ct);
    }
    protected abstract IReadOnlyList<RawRow> Parse(Stream input);
    protected abstract Task SaveAsync(IReadOnlyList<RawRow> rows, CancellationToken ct);
}"""},
        {"t": "lead", "title": "Say this", "text": "Interface for a swappable dependency. Abstract class only when the subclasses share real state and behavior. A base class that exists so two types can be stored in one list is usually an interface."},

        {"t": "h3", "text": "virtual, override, and new"},
        {"t": "p", "text": "virtual allows a derived class to replace the method through polymorphism. override is that replacement, and the call uses the runtime type. new hides the base method. A call through a base reference runs the base method. Hiding breaks the expectation that the variable's compile-time type does not change the behavior. Leads almost never accept new on a method."},
        {"t": "code", "text": """public class Pricing { public virtual decimal Total(Order o) => o.Total; }
public class DiscountPricing : Pricing
{
    public override decimal Total(Order o) => o.Total * 0.9m;
}
public class HiddenPricing : Pricing
{
    public new decimal Total(Order o) => 0m;
}

Pricing a = new DiscountPricing();
Pricing b = new HiddenPricing();
decimal discounted = a.Total(order); // 90 percent
decimal hidden = b.Total(order);     // base price, the new method is hidden"""},
        {"t": "lead", "title": "Say this", "text": "override replaces a virtual method for every caller. new hides it and surprises anyone holding the base type. I do not ship new on methods."},

        {"t": "h3", "text": "const, readonly, and static"},
        {"t": "p", "text": "const is a compile-time constant. Callers of another assembly embed the value, so changing a public const is a breaking change until every caller recompiles. readonly is assigned in the constructor or at the declaration and then fixed for that instance. static belongs to the type, one per process, not one per App Service farm."},
        {"t": "code", "text": """public static class Limits
{
    public const int PageSize = 50;          // baked into callers
    public static readonly TimeSpan Timeout = TimeSpan.FromSeconds(2);
}

public sealed class CreateOrderHandler
{
    private readonly IOrderStore _store;     // set in the constructor, then fixed
    public CreateOrderHandler(IOrderStore store) => _store = store;
}"""},
        {"t": "lead", "title": "Say this", "text": "const is compile-time and a versioning trap in a public library. readonly is fixed after construction. static is per process, which is not per farm."},

        {"t": "h3", "text": "First, FirstOrDefault, and Single"},
        {"t": "p", "text": "First returns the first match and throws if the sequence is empty. FirstOrDefault returns the default value, null for a reference type, which is the right signal for a missing optional row if you then branch. Single throws unless there is exactly one match, which is what you want on a primary key: zero rows and two rows are both defects. The async EF methods are FirstAsync, FirstOrDefaultAsync, SingleAsync, and SingleOrDefaultAsync. On a primary key, SingleOrDefaultAsync makes a duplicate fail loudly instead of silently returning one of them."},
        {"t": "code", "text": """Order? order = await db.Orders.AsNoTracking()
    .SingleOrDefaultAsync(o => o.Id == id && o.TenantId == tenantId, ct);

if (order is null)
    return NotFound();"""},
        {"t": "lead", "title": "Say this", "text": "First is any match. Single is exactly one. On a primary key I use Single or SingleOrDefault so a duplicate cannot hide."},

        {"t": "h3", "text": "throw versus throw ex"},
        {"t": "p", "text": "throw; inside a catch rethrows the same exception and keeps the original stack trace. throw ex; resets the stack trace at the new throw, so the log points at your catch block and hides the frame that failed. When you need context, wrap a new exception and pass the original as the inner exception."},
        {"t": "code", "text": """try
{
    await store.SaveAsync(order, ct);
}
catch (DbUpdateException ex)
{
    logger.LogWarning(ex, "Order {OrderId} failed to save", order.Id);
    throw; // keeps the stack
    // throw ex;              // resets the stack. Do not ship this.
    // throw new InvalidOperationException("save failed", ex); // when you add context
}"""},
        {"t": "lead", "title": "Say this", "text": "throw keeps the stack. throw ex resets it. I wrap only when I am adding a context the caller can use, and I keep the original as InnerException."},

        {"t": "h3", "text": "IEnumerable, ICollection, and IList"},
        {"t": "p", "text": "IEnumerable<T> can be streamed and may not have a count. ICollection<T> adds Count and mutation. IList<T> adds indexing. IReadOnlyList<T> is the honest return when the caller may index and must not add. Accept the smallest interface the method needs, so a caller can pass an iterator. Return a concrete list or a read-only view so the caller does not trigger a second enumeration by accident."},
        {"t": "code", "text": """public static decimal Sum(IEnumerable<OrderLine> lines)
    => lines.Sum(l => l.Quantity * l.UnitPrice);

public IReadOnlyList<OrderListItem> Latest()
    => items; // List<OrderListItem> implements IReadOnlyList<T>"""},
        {"t": "lead", "title": "Say this", "text": "Accept the smallest interface. Return a list or a read-only view. I do not return a lazy sequence that the caller will enumerate twice."},

        {"t": "h3", "text": "Covariance and contravariance"},
        {"t": "p", "text": "out on an interface type parameter makes it covariant: the interface only produces T, so IEnumerable<string> may be used as IEnumerable<object>. in makes it contravariant: the interface only consumes T, so an Action<object> may be used where an Action<string> is expected, because a method that accepts any object can accept a string. Invariant is the default, and it is why List<string> is not a List<object>: a list both produces and consumes."},
        {"t": "code", "text": """IEnumerable<string> skus = new[] { "AB-1" };
IEnumerable<object> asObjects = skus; // covariant, out T

Action<object> write = o => Console.WriteLine(o);
Action<string> writeSku = write;     // contravariant, in T

// List<string> is not a List<object>. Add(new object()) would be a lie."""},
        {"t": "lead", "title": "Say this", "text": "out is producer, covariant. in is consumer, contravariant. Lists are invariant because they do both. I mention this when a generic interface will not compile, not as a feature tour."},

        {"t": "h3", "text": "Nullable reference types"},
        {"t": "p", "text": "string? may be null. string should not. The compiler warns. The CLR does not change: these are annotations. Enable them on new projects so a missing null check is a build warning a review can treat as a comment. A suppression belongs next to a proven invariant, with a reason. Order? from SingleOrDefaultAsync is the annotation doing its job."},
        {"t": "code", "text": """#nullable enable
public sealed record OrderDto(int Id, string Number, string? Coupon);

public OrderDto Require(OrderDto? dto)
{
    if (dto is null)
        throw new InvalidOperationException("Order was expected.");
    return dto; // compiler now treats dto as non-null
}"""},
        {"t": "lead", "title": "Say this", "text": "Nullable reference types are a compile-time contract. I enable them so reviews talk about null at build time. A suppression needs a reason."},

        {"t": "h3", "text": "Partial classes and source generators"},
        {"t": "p", "text": "The compiler merges partial parts of a type into one class. EF migrations, designer files, and source generators use this so generated code and hand-written code can share a type. Keep domain rules out of the generated part. A regeneration then cannot delete the rule. If you need to add behavior to a generated type, put it in a second partial file that you own."},
        {"t": "code", "text": """// Generated. Regeneration may replace this file.
public partial class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b) { /* generated mapping */ }
}

// Yours. The generator does not own this file.
public partial class OrderConfiguration
{
    // Prefer a separate configuration class you control entirely.
}"""},
        {"t": "lead", "title": "Say this", "text": "Partial merges files. Generators and migrations need that. Hand-written rules live in a file the generator will not overwrite."},

        {"t": "h2", "text": "Features worth naming, and the traps"},
        {"t": "p", "text": "From the last few language versions, a lead can name records, required members, primary constructors, collection expressions, the field keyword in a C# 14 property accessor, and extension members. Name one you have used. A list of features you have not shipped is a weaker answer than one real use."},
        {"t": "code", "text": """public sealed class PricingOptions
{
    public required decimal Rate { get; init; }

    public decimal RatePercent
    {
        get => field;
        set => field = value is >= 0 and <= 1
            ? value
            : throw new ArgumentOutOfRangeException(nameof(value));
    }
}

List<int> ids = [order.Id, backup.Id];"""},
        {"t": "p", "text": "required means the caller must set Rate in an object initializer. The field keyword is the compiler's backing field, so you can validate a set accessor without declaring a private decimal _rate. Collection expressions are the [ ... ] syntax. None of these change the design of the Orders API. They shorten code you were going to write anyway."},
        {"t": "warn", "title": "Traps on Day 1", "text": "Value types do not always live on the stack. A struct field of a class lives on the heap with the object. ConfigureAwait(false) is the right habit in a library that must not resume on a captured context. ASP.NET Core application code has no sync context to return to. Blocking calls and missing cancellation still hurt. Do not recite C# 14 features you have not used."},
        {"t": "lead", "title": "Say this", "text": "I will name one language feature I shipped and the bug it removed. I will not claim structs are the stack, and I will not claim ConfigureAwait(false) is what saves an ASP.NET Core API. Cancellation and not blocking are what save it."},
        {"t": "break"},
    ]
