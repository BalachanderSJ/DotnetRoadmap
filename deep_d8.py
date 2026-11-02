# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 8 — .NET Framework to modern .NET"},
        {"t": "p", "text": "Day 8 is a plan a manager can fund. The opening line is the whole day: you do not rewrite the system in a branch for nine months. You inventory the blockers, put a facade in front of the surface that must stay stable, move one vertical slice to .NET 10, run both, and delete the old slice only when the new one has the same logs, the same auth, and a rollback. The goal is an empty Framework footprint on a date, not a heroic cutover weekend."},

        {"t": "h2", "text": "What actually changes"},
        {"t": "p", "text": "Modern .NET is cross-platform. The project is SDK-style with PackageReference. Configuration is appsettings, environment variables, and Key Vault. The HTTP pipeline is ASP.NET Core middleware. .NET Framework is Windows-first: System.Web, Global.asax, web.config, sometimes OWIN, and often EF6 or ADO.NET. The .NET Upgrade Assistant and the API analyzer find APIs that do not exist on .NET 10. They do not find a behavioral change or a bad module boundary. The lead still reads the report."},
        {"t": "p", "text": "A class library can multi-target net48 and net10 for a bridge period if the code stays on the shared surface. That lets the old host and the new host share a pure domain library. It is a temporary state with an end date. ASP.NET to ASP.NET Core replaces System.Web. HttpContext is a different type. Session, cache, and authentication modules become middleware and services. Web Forms does not come along. MVC views can move with work. Web API controllers move more naturally."},
        {"t": "p", "text": "WCF does not ship as a full equivalent. CoreWCF keeps some SOAP services alive on modern .NET. A public contract you can change should become REST or gRPC. Do not promise that every binding will appear. Authentication often moves from Windows auth or OWIN cookies to Entra ID and JWT for an API, or to cookie auth for a site. System.Drawing, COM, the registry, Event Log assumptions, Windows services, and impersonation are the usual blockers. List them in week one."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """<!-- Bridge library. An end date is part of the PR. -->
<PropertyGroup>
  <TargetFrameworks>net48;net10.0</TargetFrameworks>
  <Nullable>enable</Nullable>
</PropertyGroup>

// Framework code that will not compile on the new host, and must not be
// copied forward:
var user = HttpContext.Current.User;
var setting = ConfigurationManager.AppSettings["TaxUrl"];"""},
        {"t": "warn", "title": "What breaks", "text": "A multi-target library with no end date becomes the permanent compatibility swamp. Treating the analyzer's green report as a behavioral guarantee misses a changed EF query plan and a missing HTTP module. Promising a WCF binding you have not checked becomes the date slip."},
        {"t": "lead", "title": "Say this", "text": "SDK-style projects, ASP.NET Core, and a temporary multi-target library with an end date. The analyzer finds missing APIs. I still inventory modules, WCF, EF, and Windows-only calls myself."},

        {"t": "h2", "text": "The migration plan"},
        {"t": "p", "text": "Week zero is an inventory: projects, target framework, NuGet packages, System.Web usage, WCF, EF6 or EDMX, auth type, Windows-only APIs, scheduled jobs, and how you deploy. You run the upgrade analyzer and you sit with the person who knows the ugly paths. You pick .NET 10 as the target. You freeze new features that deepen Framework-only APIs. You add characterization tests around the slices you will move, at the HTTP boundary if unit tests do not exist."},
        {"t": "p", "text": "You move a pure class library first, then one vertical API slice, behind the existing URL via a reverse proxy. You ship that slice to a small share of production traffic with the old path still available. You repeat. Schema changes use expand/contract so both runtimes can work. You remove a Framework project only when nothing calls it. You report percent of traffic on the new runtime, not percent of projects converted. Seven of ten class libraries converted is not 70 percent migrated if the revenue path is still on Framework."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """YARP in front of the existing host. One route moves. The rest stay.

POST /orders     -> new .NET 10 app      (the first slice)
GET  /orders/*   -> new .NET 10 app      (after the write is proven)
GET  /catalog/*  -> old Framework app    (not this quarter)
POST /payments/* -> old Framework app    (until its own slice)

Metric on the steering slide:
  percent of order traffic served by net10
  not: percent of csproj files retargeted

First slice teaches the real cost of auth, EF, and the deploy.
The estimate for the rest comes after that slice is in production."""},
        {"t": "warn", "title": "What breaks", "text": "A status deck that counts projects instead of traffic hides the revenue path. A feature freeze that is not real means new Framework-only code lands while you migrate. A first slice that is 'the whole solution' teaches you nothing until the ninth month."},
        {"t": "lead", "title": "Say this", "text": "Inventory, one vertical slice behind the current URL, both runtimes live, delete the old slice when traffic, logs, and rollback are proven. I report traffic percent. A single number for eighty projects is fiction."},

        {"t": "h2", "text": "What usually blocks a Web API"},
        {"t": "p", "text": "HTTP modules and handlers quietly do auth, logging, or tenant resolution. They become middleware, and a missed one means the new host is missing a control. WCF clients generated from old references, binary serialization, and Remoting need an explicit contract. ConfigurationManager and web.config transforms become the options pattern. Static HttpContext.Current has no place in ASP.NET Core. The context is passed in, or read through IHttpContextAccessor sparingly. App-pool identity assumptions become a managed identity. Blocking synchronous IO that worked at low volume starves the new host under load. Packages that were never built for modern .NET stop the slice until you replace, wrap, or drop them."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// The module that used to run for every request. If you miss it,
// tenant resolution disappears and the new API reads the wrong rows.
public sealed class TenantMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context, ITenantAccessor tenant)
    {
        var id = context.User.FindFirstValue("tid");
        if (!int.TryParse(id, out var tenantId))
        {
            context.Response.StatusCode = StatusCodes.Status401Unauthorized;
            return;
        }
        tenant.Set(tenantId);
        await next(context);
    }
}"""},
        {"t": "p", "text": "Classify each blocker as replace, wrap for now, or stop the slice. Publish the list with an owner. A migration without that list becomes a long branch. The list is also how you say no to rewriting the reporting module that is not on the critical path."},
        {"t": "warn", "title": "What breaks", "text": "Porting [Authorize] and assuming the module still ran is how an endpoint ships anonymous. Copying HttpContext.Current into a static helper compiles nowhere and, if forced, captures the wrong request. A package with no modern build blocks the slice. Pretending otherwise blocks the program."},
        {"t": "lead", "title": "Say this", "text": "Modules become middleware I test. Configuration becomes options. The app-pool identity becomes a managed identity. I publish the blocker list with an owner and a decision: replace, wrap, or stop this slice."},

        {"t": "h2", "text": "Blockers you classify out loud"},
        {"t": "table", "headers": ["Blocker", "Classification", "Example of the decision"], "rows": [
            ["System.Web HttpModule", "Replace in the slice", "Tenant and auth modules become middleware with a test that fails closed."],
            ["WCF SOAP a partner still calls", "Bridge or leave that host", "CoreWCF for that contract only. The rest of the API does not wait."],
            ["EDMX", "New code model for the slice", "Map the migrated aggregate. Compare schema. Do not let EF create a second database."],
            ["Web Forms page", "Leave it", "A page is a product decision, not a class-library port."],
            ["web.config appSettings", "Options and Key Vault", "Secrets leave the file. The rest binds to a validated options class."],
            ["Windows service", "Worker or Function", "A queue or a schedule becomes a Function. A long co-located loop becomes a Worker Service."],
            ["COM or the registry", "Wrap and isolate", "That component may stay on Windows after the API moves. Say so in week one."],
            ["Shared SQL login as db_owner", "Split identities", "The first production slice introduces the runtime role and the migrator."],
        ]},
        {"t": "h3", "text": "Example of a wrap with an expiry"},
        {"t": "code", "text": """public interface ILegacyInvoicePdf
{
    byte[] Render(int invoiceId);
}

// The COM renderer stays on a Windows worker.
// The new API calls it over HTTP. The ADR names the removal date.
// New invoices do not take a dependency on COM beyond this interface."""},
        {"t": "lead", "title": "Say this", "text": "I classify each blocker in the first week. A wrap has an owner and an expiry. A Web Forms page and a partner SOAP endpoint do not block the rest of the API."},

        {"t": "h2", "text": "EF6 to EF Core without a production surprise"},
        {"t": "p", "text": "Treat it as a new data layer, not a namespace rename. Recreate the model in code. Map keys, required relationships, delete behaviors, and column types explicitly. Compare the schema EF Core wants with the schema that exists. Do not let it create a parallel database. Port the hot queries first and run them against a realistic dataset, because translation differences change plans. Lazy loading is opt-in and different. Prefer explicit loads and projections. EDMX does not come forward."},
        {"t": "p", "text": "During the strangler, EF6 stays in the old process and EF Core stays in the new process. Both may point at the same database only with strict rules: no silent model drift, and one owner of migrations. Spatial types, table-per-type inheritance, and some complex mappings need an explicit check against the EF Core documentation for the version you are on, not a memory of EF6. Test concurrency tokens and transactions, not only CRUD."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """// You write the model to match the existing table. You do not scaffold
// and then 'fix it in production'.
modelBuilder.Entity<Order>(b =>
{
    b.ToTable("Orders", "orders");
    b.HasKey(o => o.Id);
    b.Property(o => o.Total).HasColumnType("decimal(18,2)");
    b.Property(o => o.RowVersion).IsRowVersion();
    b.HasQueryFilter(o => o.TenantId == tenant.Id && !o.IsDeleted);
});

// One migration history. The pipeline's identity applies it.
// The Framework app does not call Database.SetInitializer and create tables.
// The new app does not call Database.Migrate at startup."""},
        {"t": "warn", "title": "What breaks", "text": "Two migration histories on one database drop a column the old app still reads. A rename EF Core inferred from a missing property ships as drop-and-add. Lazy loading that used to fill a grid becomes an N+1, or an empty collection, depending on what you forgot. The in-memory provider will not catch any of this."},
        {"t": "lead", "title": "Say this", "text": "I rebuild the model and compare it to the live schema. One side owns migrations. Hot queries are tested against SQL with realistic stats. I do not call it a port. I call it a new data layer beside the old one."},

        {"t": "h2", "text": "Authentication, cut over without an anonymous hour"},
        {"t": "p", "text": "Write down the current mechanism: Windows integrated, forms cookie, OWIN JWT, custom headers, or certificates. Map every audience: browser, partner, and internal job. For a new API, prefer Entra ID and bearer tokens, with policies that match today's roles. Run both authenticators during the overlap if clients cannot all move, and log which scheme succeeded. Test 401 and 403 on every moved route, plus one cross-tenant case. Do not trust a ported [Authorize] until a test fails closed."},
        {"t": "p", "text": "Secrets in web.config move to Key Vault references. Certificates get an owner and an expiry alert. A Windows-identity flow that impersonated the user down to SQL is a design change: the user's identity stays in the token, and the app's managed identity connects to SQL. Authorization stays in the API. You do not flow the Windows token into Azure SQL and call that a port."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.Authority = "https://login.microsoftonline.com/<tenant>/v2.0";
        o.Audience = "api://orders";
    });

builder.Services.AddAuthorization(o =>
{
    o.AddPolicy("orders.write", p => p.RequireClaim("roles", "orders.write"));
});

// The test that must fail before you celebrate the port:
// no token -> 401
// token without the role -> 403
// token for tenant A requesting tenant B's order id -> 404 or 403, as documented
// and the SQL login is the app identity, not the user's Windows account."""},
        {"t": "warn", "title": "What breaks", "text": "A route you forgot to authorize ships open. Impersonation to SQL silently stops, or worse, the new app connects as a powerful Windows account you copied into the connection string. A certificate with no expiry alert dies on a Saturday."},
        {"t": "lead", "title": "Say this", "text": "I map every audience, run both schemes only while clients move, and log which one succeeded. 401 and 403 are tests. The user token authorizes. The managed identity connects to SQL."},

        {"t": "h2", "text": "What you test when the old system has few tests"},
        {"t": "p", "text": "Start with characterization tests on the HTTP contract of the slice you are moving: status code, the headers that matter, and the JSON shape for the main success and the main failure. Add golden tests around billing calculations and any code that has caused an incident. Add an integration test that hits SQL for the migrated query. Do not stop the migration to unit-test the entire legacy solution. Do not accept a rewrite of a slice with no before-and-after contract check."},
        {"t": "p", "text": "For the proxy, test the routing rules: this path goes to the new host, that path stays, and a bad route fails in a way you can see. Put load on the migrated slice. Sync-over-async and a missing index show up there, not in a unit test. Sequence the tests by money and embarrassment. The payment path gets a characterization test before the admin dropdown does."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """[Fact]
public async Task Create_order_keeps_the_contract()
{
    var response = await client.PostAsJsonAsync("/orders", new
    {
        sku = "AB-1",
        quantity = 2,
        idempotencyKey = "k-1"
    });

    Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    var body = await response.Content.ReadFromJsonAsync<JsonElement>();
    Assert.Equal("Pending", body.GetProperty("status").GetString());
    Assert.True(response.Headers.Location is not null);
}

// Captured from the old host first. The new host must match.
// A field rename is a contract break, even if the new name is nicer."""},
        {"t": "warn", "title": "What breaks", "text": "A green suite of new unit tests that never saw the old JSON lets a renamed field break every partner. Skipping the proxy test sends /payments to the new host that does not own it yet. Load left until launch hides the blocking call."},
        {"t": "lead", "title": "Say this", "text": "I characterize the HTTP contract of the slice I am moving, and I hit SQL for the migrated query. I do not boil the ocean. I test payment before I test a dropdown."},

        {"t": "h2", "text": "How you estimate, and what you refuse to rewrite"},
        {"t": "p", "text": "Estimate the inventory and the first slice, not the whole estate. The first slice teaches the real cost of auth, EF, and deployment. After it is in production, estimate the rest in slices, with a range. Refuse to rewrite code you do not understand, code with no contract, and code the business is about to replace. Wrap those and put an expiry on the wrap. Refuse a second feature program that lands only on Framework while you migrate. New work goes to the new runtime unless there is a dated exception."},
        {"t": "p", "text": "Keep a risk register: shared database, an unknown module, key-person knowledge, a package with no modern build, and a rollback that requires schema compatibility. A single number for an eighty-project solution is fiction. A funded first slice, a risk register, and a cadence is an estimate you can defend."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Fund now:
  Week 0 inventory and the blocker list.
  Slice 1: POST and GET /orders, characterization tests, YARP route, pipeline migrate.

Explicitly not in slice 1:
  Rewriting the Web Forms admin.
  Splitting microservices.
  Replacing the reporting warehouse.

Risk register line:
  Shared database. Owner: the tech lead. Mitigation: one migration history,
  expand/contract, route rollback rehearsed before the slice takes traffic."""},
        {"t": "warn", "title": "What breaks", "text": "An estimate that includes a domain rewrite misses the support date. New features landing on Framework make the inventory stale every sprint. A wrap with no expiry is a permanent legacy host with a nicer name."},
        {"t": "lead", "title": "Say this", "text": "I estimate the first slice and the inventory. I refuse a rewrite of code we do not understand or the business is about to drop. New work goes to .NET 10 unless I write down a dated exception."},

        {"t": "h2", "text": "Rollback six weeks into a strangler"},
        {"t": "p", "text": "Routing rollback sends the slice's traffic to the old host. That works only if the old host can still read and write the current schema, which is why you expanded the schema and did not rename or drop in the same release. Data written by the new service must be readable by the old service, or you have a compensating job you have rehearsed. A feature flag can disable a new behavior without a deploy. You do not need to roll back a shared class library if it stayed compatible. Rehearse the route switch in a lower environment. If you cannot describe rollback, the slice is too big. The person on call should not invent it at midnight."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Week 1, expand:
  ALTER TABLE orders.Orders ADD Currency char(3) NULL;
  Old app ignores the column. New app writes it.

Week 6, incident on the new host:
  YARP sends POST /orders back to the Framework app.
  The old app still inserts. Currency stays null. That is acceptable
  because the column is nullable and the old app never read it.

Not reversible:
  Week 1 renamed Total to Amount and dropped Total.
  The old INSERT fails. Swap-back is a second incident.

The checklist line next to the migration script:
  'Route /orders returns to the Framework app in one config change.
   Rehearsed on staging on <date>.'"""},
        {"t": "warn", "title": "What breaks", "text": "A drop or rename in the same release as the route change removes the old host as a rollback. Data the new app wrote in a shape the old app rejects is stuck even if the route goes back. An unrehearsed proxy change is a guess at midnight."},
        {"t": "lead", "title": "Say this", "text": "Rollback is a route change plus a schema the old bits can still use. Expand, then contract later. I rehearse it. If I cannot describe it, the slice is too big."},

        {"t": "h2", "text": "What you adopt during the move, and what you postpone"},
        {"t": "p", "text": "Adopt the SDK-style project, nullable reference types on new code, generic hosting, the options pattern, structured logging, and EF Core migrations owned by the pipeline. Adopt managed identity if the app is moving to Azure as part of this work. Postpone a microservices split, a new UI framework, and a domain rewrite. The migration's job is a supported runtime, the same business behavior, and a safer deploy."},
        {"t": "p", "text": "A cleaner module boundary inside the new host is welcome when it falls out of the slice. A new architecture program disguised as a migration is how the date slips and Framework stays in production past support. .NET 8 and .NET 9 reach end of support in November 2026. New work targets .NET 10 LTS, supported through November 2028. Say the sentence to stakeholders: supported runtime first, structural improvement only where the slice already has to change."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """In the slice, because the code is already open:
  nullable enabled on the new projects
  options class for TaxUrl, ValidateOnStart
  structured log with trace id
  pipeline migration, runtime SQL role

Not in the slice, written down so the team stops relitigating:
  extracting a pricing microservice
  rewriting the admin UI
  introducing a generic repository 'while we are here'"""},
        {"t": "warn", "title": "What breaks", "text": "A migration that also replatforms to Kubernetes and splits six services misses the support window. Postponing nullable, logging, and the SQL role means you arrive on .NET 10 with the same operational scars."},
        {"t": "lead", "title": "Say this", "text": "Supported runtime first. I adopt hosting, options, logging, pipeline migrations, and managed identity because the slice already touches them. I postpone a new architecture. That sentence is how the date survives."},
        {"t": "break"},
    ]
