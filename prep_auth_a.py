# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Authentication and authorization"},
        {"t": "p", "text": "Authentication answers who called. Authorization answers whether that caller may do this. On the Orders API those are two steps in the pipeline, in that order. Authentication builds a ClaimsPrincipal, or it fails. Authorization reads that principal, the endpoint policy, and sometimes the order row. A missing token and a token that lacks orders.write are different outcomes, and the client behaves differently for each."},
        {"t": "p", "text": "The partner who POSTs an order presents a bearer token issued by Entra ID. A first-party Angular app, when you add one, talks to a BFF. The browser holds an HttpOnly cookie. The BFF holds the tokens. The Orders API still validates a bearer token on the call the BFF or the partner makes. Cookie authentication and bearer authentication solve two surfaces. One deployment does not have to enable both."},

        {"t": "h2", "text": "Handlers, schemes, and the default scheme"},
        {"t": "p", "text": "An authentication scheme is a name plus a handler type. The handler implements AuthenticateAsync, ChallengeAsync, and ForbidAsync. AuthenticateAsync inspects the request and returns a result: success with an AuthenticationTicket, failure when a credential was present and bad, or no result when this handler has nothing to read. The ticket carries the ClaimsPrincipal."},
        {"t": "p", "text": "AddAuthentication registers the services and the default scheme. The default scheme is the one the rest of the pipeline uses when a call does not name a scheme. You can split that into a default authenticate scheme, a default challenge scheme, and a default forbid scheme when they differ. A BFF often authenticates with a cookie and challenges with the OpenID Connect handler. A pure Orders API sets a single default: the JWT bearer scheme."},
        {"t": "p", "text": "UseAuthentication runs the default handler and assigns HttpContext.User. UseAuthorization runs after it. Authorization that runs before authentication sees an anonymous user. The endpoint then treats a missing token as a forbid, and the client shows access denied where it should have shown a sign-in."},
        {"t": "code", "text": """app.UseAuthentication();
app.UseAuthorization();

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Entra:Authority"];
        options.Audience = builder.Configuration["Entra:Audience"];
        options.MapInboundClaims = false;
    });"""},
        {"t": "p", "text": "Authority is the Entra metadata address, typically the v2.0 issuer for the directory that issues your tokens. The handler loads the signing keys from that document over HTTPS. Audience is the API's application ID URI, the value in the aud claim the partner requested. The full TokenValidationParameters sketch is in the JWT section. Leave it on. The four validation switches stay enabled."},
        {"t": "p", "text": "MapInboundClaims left at its historical default rewrites short claim names into long URI claim types. A policy that looks for scp or roles then fails on a token you already proved was signed. This guide sets MapInboundClaims to false and authorizes on the names Entra issued."},

        {"t": "h2", "text": "Challenge and Forbid"},
        {"t": "p", "text": "Challenge means the request has no usable identity. Forbid means the identity is known and the policy refused it. The bearer handler writes 401 and a WWW-Authenticate header for a challenge. It writes 403 for a forbid. The cookie handler's challenge redirects to the login path. That redirect is correct for a browser on the BFF. It is a bug on a partner API: the partner receives 302 and a login HTML page."},
        {"t": "p", "text": "The authorization middleware chooses for you on an [Authorize] endpoint. An anonymous user, or a handler failure such as a bad signature, becomes a challenge. An authenticated user who fails the policy becomes a forbid. Results.Challenge and Results.Forbid are the same pair when you decide inside a handler after you have loaded a resource. Match the scheme to the surface so challenge means the status code that surface expects."},
        {"t": "table", "headers": ["Situation", "Pipeline result", "Partner API status"], "rows": [
            ["No Authorization header", "Challenge", "401"],
            ["Token present, signature, issuer, audience, or lifetime fails", "Challenge", "401"],
            ["Token valid, scope or policy fails", "Forbid", "403"],
            ["Token valid, order id is outside the tenant", "Your action returns NotFound", "404"],
            ["Browser on the BFF, no session", "Cookie challenge", "Redirect to login"],
        ]},
        {"t": "p", "text": "404 for a cross-tenant id is a product choice. The query includes the tenant, so the row is absent in this caller's scope. The response does not confirm that some other tenant owns that id. Document it. A missing orders.write scope is still 403, because the middleware refused the route before a row was involved. A fresh token with the same claims fails the same way. 401 is the signal to sign in again."},

        {"t": "h2", "text": "Cookie, bearer, and the grant"},
        {"t": "p", "text": "A pure API validates Authorization: Bearer. The partner is a confidential client. It uses the client credentials grant when it acts as itself, and the token carries app roles. A human user uses the authorization code grant with PKCE. The client sends a code_challenge, method S256, on the authorize redirect. The token endpoint receives the code and the original code_verifier. Entra returns the access token and, when you asked for offline_access, a refresh token."},
        {"t": "p", "text": "The BFF is the confidential client for the Angular app. It redeems the code. It stores the access token and the refresh token on the server. It sets a cookie that is HttpOnly, Secure, and SameSite. The browser sends that cookie to the BFF. Script on the page cannot read it. The BFF attaches the access token when it calls the Orders API."},
        {"t": "code", "text": """builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Lax;
        options.LoginPath = "/bff/login";
    });"""},
        {"t": "p", "text": "A cookie is attached by the browser. A bearer header is attached by code that chose to attach it. The BFF therefore protects cookie-authenticated POSTs against cross-site request forgery: SameSite, and an antiforgery token on unsafe methods. The partner API does not take a session cookie, so it does not add a browser antiforgery token. It demands the bearer token instead."},
        {"t": "p", "text": "A public browser app can run authorization code with PKCE and redeem the code in the page. This system's choice is still the BFF, so the refresh token stays on the server. Two schemes in one process are a later option: cookie for the BFF routes, bearer for /partner. A policy scheme can forward to the handler whose credential is present. Build that when one host truly serves both. Ship the partner API on bearer first."},
        {"t": "warn", "title": "Interview trap", "text": "Implicit flow, response_type=token, puts the access token in the URL fragment. Leave it out of the design. An access token in localStorage or sessionStorage is readable by any script that runs on the origin. A long-lived token in the browser is a stolen credential with a wide window. The OAuth security guidance for a browser client is authorization code with PKCE, and this guide keeps those tokens on the BFF."},

        {"t": "h2", "text": "Policies, requirements, and handlers"},
        {"t": "p", "text": "A role is a claim. A policy is a named rule in the composition root. [Authorize(Roles = \"Admin,Support\")] scatters an OR-list of role strings across actions. Renaming a role means a sweep of controllers. A policy named orders.write is one registration, one test, and one attribute. The endpoint stays stable when the rule grows from a role to a scope plus a tenant claim."},
        {"t": "p", "text": "IAuthorizationRequirement is a marker. A handler is AuthorizationHandler of that requirement. Requirements on one policy are combined: every requirement must succeed. Several handlers for one requirement are alternate ways to succeed: the first success satisfies that requirement. context.Succeed records success. Returning without Succeed is an ordinary failure. context.Fail is an explicit deny that stops the remaining handlers. Use Fail when you mean deny even if another handler would have allowed the call."},
        {"t": "p", "text": "Entra puts delegated permissions in one scp claim, space-separated. It puts app roles in one or more roles claims, each value a single role. RequireClaim(\"roles\", \"orders.write\") matches an app role. RequireClaim(\"scp\", \"orders.read\") looks for a claim whose entire value is orders.read, so a token whose scp is \"orders.read orders.write\" fails it. Split scp in a handler."},
        {"t": "code", "text": """public sealed class ScopeRequirement : IAuthorizationRequirement
{
    public ScopeRequirement(string scope) => Scope = scope;
    public string Scope { get; }
}

public sealed class ScopeHandler : AuthorizationHandler<ScopeRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        ScopeRequirement requirement)
    {
        foreach (var claim in context.User.FindAll("scp"))
        {
            foreach (var scope in claim.Value.Split(' ', StringSplitOptions.RemoveEmptyEntries))
            {
                if (string.Equals(scope, requirement.Scope, StringComparison.Ordinal))
                {
                    context.Succeed(requirement);
                    return Task.CompletedTask;
                }
            }
        }
        return Task.CompletedTask;
    }
}

builder.Services.AddSingleton<IAuthorizationHandler, ScopeHandler>();
builder.Services.AddAuthorizationBuilder()
    .SetFallbackPolicy(new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build())
    .SetDefaultPolicy(new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build())
    .AddPolicy("orders.read", policy =>
    {
        policy.RequireAuthenticatedUser();
        policy.AddRequirements(new ScopeRequirement("orders.read"));
    })
    .AddPolicy("orders.write", policy =>
    {
        policy.RequireAuthenticatedUser();
        policy.AddRequirements(new ScopeRequirement("orders.write"));
        policy.RequireClaim("tenant_id");
    });"""},
        {"t": "p", "text": "The same registration exists as services.AddAuthorization(o => o.AddPolicy(...)). AddAuthorizationBuilder is the fluent form. Handlers that do not take scoped services are singletons. A handler that opens a DbContext is scoped, or it creates a scope inside the call."},
        {"t": "p", "text": "The default policy is what a bare [Authorize] applies. Here it requires an authenticated user. The fallback policy applies to endpoints that carry no authorization metadata. Here it requires an authenticated user, so a new minimal API you forgot to mark is still closed. AllowAnonymous is how you opt out. The liveness and readiness probes are anonymous because the platform has no user token. The probe body stays boring: a status, no order data."},
        {"t": "p", "text": "Partner app tokens often have roles and no scp. Add a second handler for the same requirement that succeeds when roles contains orders.write, or register a partner policy that uses RequireClaim(\"roles\", \"orders.write\"). Say which token shape each route accepts. A route that silently accepts either shape is a decision you write down."},
        {"t": "code", "text": """[Fact]
public async Task Write_scope_succeeds_when_scp_lists_several_values()
{
    var user = new ClaimsPrincipal(new ClaimsIdentity(
    [
        new Claim("scp", "orders.read orders.write"),
        new Claim("tenant_id", "10")
    ], authenticationType: "Bearer"));
    var context = new AuthorizationHandlerContext(
        [new ScopeRequirement("orders.write")], user, resource: null);
    await new ScopeHandler().HandleAsync(context);
    Assert.True(context.HasSucceeded);
}"""},

        {"t": "h2", "text": "Resource-based access to an order"},
        {"t": "p", "text": "The endpoint policy is the coarse gate: scope, and a tenant claim that parses. It runs before the action, so it cannot see the order. Resource-based authorization runs after you have the entity. You pass the order to IAuthorizationService.AuthorizeAsync. The handler receives the requirement and the resource."},
        {"t": "p", "text": "Load the order with the tenant predicate already applied. The handler is the second check, for a rule the predicate does not express. In this example a partner token may also carry customer_id. That partner may read only that customer's order. A staff token inside the tenant omits customer_id and may read any order the tenant query returned."},
        {"t": "code", "text": """public sealed class OrderAccessRequirement : IAuthorizationRequirement
{
}

public sealed class OrderAccessHandler
    : AuthorizationHandler<OrderAccessRequirement, Order>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OrderAccessRequirement requirement,
        Order resource)
    {
        var tenantClaim = context.User.FindFirst("tenant_id")?.Value;
        if (!int.TryParse(tenantClaim, out var tenantId) || tenantId != resource.TenantId)
            return Task.CompletedTask;

        var customerClaim = context.User.FindFirst("customer_id")?.Value;
        if (customerClaim is not null &&
            (!int.TryParse(customerClaim, out var customerId) || customerId != resource.CustomerId))
            return Task.CompletedTask;

        context.Succeed(requirement);
        return Task.CompletedTask;
    }
}

app.MapGet("/orders/{id:long}", async (
    long id,
    ClaimsPrincipal user,
    AppDbContext db,
    IAuthorizationService auth,
    CancellationToken ct) =>
{
    var tenantId = int.Parse(user.FindFirstValue("tenant_id")!);
    var order = await db.Orders.AsNoTracking()
        .SingleOrDefaultAsync(o => o.Id == id && o.TenantId == tenantId, ct);
    if (order is null)
        return Results.NotFound();

    var decision = await auth.AuthorizeAsync(user, order, "order.access");
    if (!decision.Succeeded)
        return Results.Forbid();

    return Results.Ok(OrderDto.From(order));
}).RequireAuthorization("orders.read");"""},
        {"t": "p", "text": "Register order.access with AddRequirements(new OrderAccessRequirement()), and register the handler. A global query filter on TenantId is a safety net for ordinary LINQ. IgnoreQueryFilters and a raw SQL path skip it. The test that matters sends tenant A's token and tenant B's order id, and expects 404."},

        {"t": "h2", "text": "Endpoint metadata"},
        {"t": "p", "text": "[Authorize(Policy = \"orders.write\")] on a controller action, and RequireAuthorization(\"orders.write\") on a minimal API, both add authorization metadata. [AllowAnonymous] and AllowAnonymous() add the opt-out. The middleware reads that metadata. It does not guess from a comment or from a folder name."},
        {"t": "p", "text": "Calling RequireAuthorization twice combines the policies. The endpoint must satisfy each one. A group that requires orders.read plus a POST that requires orders.write demands both. Put one policy on the route unless you mean the combination. A bare [Authorize] uses the default policy. With the fallback above, a route with neither attribute still requires a user."},
        {"t": "code", "text": """app.MapPost("/orders", CreateOrder).RequireAuthorization("orders.write");
app.MapGet("/orders/{id:long}", GetOrder).RequireAuthorization("orders.read");
app.MapHealthChecks("/health/live").AllowAnonymous();
app.MapHealthChecks("/health/ready").AllowAnonymous();"""},

        {"t": "h2", "text": "Tenant isolation and object-level access"},
        {"t": "p", "text": "Broken object level authorization, often called IDOR in older write-ups, is a guessable id and a query that loads by that id alone. The caller changes /orders/10 to /orders/11 and receives another tenant's order. The fix is a predicate: id and tenant together. The tenant value comes from the authenticated identity."},
        {"t": "p", "text": "Entra's tid claim is the directory id. Use it as the business tenant when one customer is one directory. When many customers share a directory, the business tenant is a custom claim this guide calls tenant_id, issued by your claims mapping, or it is a row you resolve from the client application id in azp or appid. That lookup is server-side. The JSON body is the wrong source in every one of those shapes. A field named TenantId on the create request is over-posting. Reject it in validation."},
        {"t": "p", "text": "The Day 3 sketch reads a claim it called tid because that sample token was shaped that way. In the room, say which claim is the directory and which claim is the customer. Then say the body cannot override either."},
        {"t": "code", "text": """int tenantId = user.FindFirst("tenant_id") is { Value: { } raw } && int.TryParse(raw, out var id)
    ? id
    : await tenants.RequireByClientIdAsync(user.FindFirstValue("azp")!, ct);

if (body.TenantId is not null)
    return Results.ValidationProblem(new Dictionary<string, string[]>
    {
        ["tenantId"] = ["TenantId is not accepted from the body."]
    });"""},
        {"t": "warn", "title": "Interview trap", "text": "A valid signature with the wrong audience accepts another API's token. A filter that hides rows in EF is not the boundary once someone calls IgnoreQueryFilters or FromSqlRaw. Returning 403 for a missing token sends the partner into an access-denied path. Returning the other tenant's order with 200 is the incident."},

        {"t": "h2", "text": "Where the secrets live"},
        {"t": "p", "text": "An Entra-signed token is validated with public keys from the metadata document. You do not put Entra's private key in the API, and you do not commit a copy of a signing key to stand in for metadata. An API that issues its own tokens loads the signing material from Key Vault through configuration at startup. The value is absent from appsettings.json in git."},
        {"t": "p", "text": "Downstream calls use the process identity. The App Service managed identity is the Azure SQL user, the Key Vault reader, and the Service Bus sender. The user's access token is the authorization decision for the human or the partner. It is a different identity from the login that opens SQL. Forwarding the raw user token to every internal hop is a choice you make when that hop must see the user. The Orders API's own data access uses the managed identity."},
        {"t": "p", "text": "RS256 is the usual shape for an IdP-signed access token: the issuer signs with a private key, and every API verifies with the published public key. A symmetric key, HMAC such as HS256, fits a small API that issues tokens to callers you control. The secret lives in Key Vault. Any service that holds that secret can mint tokens that the others will trust. A shared symmetric secret across many services is a poor boundary. Prefer the IdP and asymmetric verification when more than one service must accept the token."},

        {"t": "h2", "text": "Questions and answers"},
        {"t": "qa", "q": "What is the difference between authentication and authorization?",
         "a": "Authentication builds the ClaimsPrincipal: who called, from a bearer token or a BFF cookie. Authorization decides whether that principal may call this action or touch this order. On POST /orders the bearer handler validates the Entra token first. The orders.write policy runs next. The action then binds the tenant from the token and writes the order. A failure in the first step is 401 on the partner API. A failure in the second step is 403. A row that is outside the tenant is 404 because the query never sees it.",
         "lead": "I keep the words apart in review. A PR that checks a role before it has a principal, or that treats 403 as 'please log in', has mixed them up."},
        {"t": "qa", "q": "What is a scheme, a handler, and the default scheme?",
         "a": "A scheme is a name bound to a handler. The handler reads a credential and returns a ticket, a failure, or no result. AddAuthentication(JwtBearerDefaults.AuthenticationScheme) makes bearer the default for authenticate, challenge, and forbid on the partner API. A BFF can authenticate with a cookie and challenge with OpenID Connect, because those defaults are separate properties when you need them to differ. UseAuthentication assigns HttpContext.User. UseAuthorization reads it. The JWT section shows the handler options for issuer, audience, lifetime, and signature.",
         "lead": "I name the default scheme in the first minute. A partner API on the cookie scheme redirects to a login page, and the partner treats that as a broken contract."},
        {"t": "qa", "q": "When do you Challenge, and when do you Forbid?",
         "a": "Challenge when there is no usable credential: missing header, bad signature, wrong issuer, wrong audience, expired token. The bearer handler turns that into 401. Forbid when the principal is authenticated and the policy failed: the scope is absent, the tenant claim is absent, the resource handler did not succeed. That is 403. The cookie handler's challenge is a redirect, which belongs on the BFF. Inside a minimal API, Results.Challenge and Results.Forbid call the same handlers. The middleware already did this for [Authorize] before your delegate ran. You call them yourself for an imperative resource check.",
         "lead": "401 means the client should obtain a new token. 403 means a new token with the same claims will fail until someone grants access. I do not collapse those for a simpler client."},
        {"t": "qa", "q": "How do you choose cookie authentication versus JWT bearer?",
         "a": "The partner Orders API uses JWT bearer. The caller sends Authorization: Bearer, and the API validates it on every request. The first-party Angular app uses a BFF with a cookie session: HttpOnly, Secure, SameSite. The BFF stores the access token and the refresh token, and it attaches the access token when it calls the API. The browser never receives the access token. If one process later serves browser routes and partner routes, cookie and bearer are two schemes, forwarded by which credential is present. I ship them as two surfaces first.",
         "lead": "I can draw the browser, the BFF, and the partner as three boxes. The access token sits in the BFF or in the partner's secret store. It does not sit in the page."},
        {"t": "qa", "q": "Which OAuth grant do you use for the interactive user, and where do the tokens live?",
         "a": "Authorization code with PKCE, code_challenge_method S256. The user signs in at Entra. The BFF redeems the code with the code_verifier and a confidential client. The access token and the refresh token stay on the server. The browser gets the session cookie. offline_access is how you ask Entra for a refresh token. The partner application, when it has no user, uses client credentials and an app role. I keep implicit flow out of the design. I keep access tokens out of localStorage and sessionStorage.",
         "lead": "PKCE protects the code on the way back. The BFF protects the tokens after that. XSS that reads the page still cannot read an HttpOnly cookie."},
        {"t": "qa", "q": "What do you configure on AddJwtBearer, and what do you refuse to turn off?",
         "a": "Authority and audience, MapInboundClaims false, HTTPS metadata left on. Issuer, audience, lifetime, and signing key validation stay enabled. Clock skew is the library default of five minutes unless I set a smaller window on purpose and say why. I pin the algorithm to RS256 for Entra access tokens this API accepts, after I have seen a real token in the test directory. I do not install a SignatureValidator that returns success. I do not accept alg none. The self-issued sketch, when I am the issuer, loads a symmetric key from configuration that Key Vault filled, and it pins HMAC. That key is a different scheme from the Entra scheme.",
         "lead": "If a teammate disables issuer or signature validation to unblock a demo, the PR does not merge. The demo gets a correct authority instead."},
        {"t": "qa", "q": "Why is a policy a better gate than [Authorize(Roles = \"...\")] on each action?",
         "a": "The role string is a claim, and it is a blunt OR. Scattered role attributes drift: one action says Admin, the next says Admin,Support, the next forgot the attribute. orders.write lives in one AddPolicy call. The attribute only names it. The rule can require a scope, a tenant claim, and a handler, and a unit test can pass a principal through that handler. When the business word changes from a role to a scope, the endpoints stay. I still use a role when the token truly carries app roles. I reference it inside the policy.",
         "lead": "In review I look for a new route with no policy name. The fallback policy is the backstop. The named policy is the permission we meant."},
        {"t": "qa", "q": "What is the difference between the fallback policy and the default policy?",
         "a": "The default policy runs when the endpoint says [Authorize] or RequireAuthorization() with no name. The fallback policy runs when the endpoint has no authorization metadata at all. On this API both require an authenticated user. Named policies add the scope. Health checks are AllowAnonymous so the probe still works. Without a fallback, a new MapGet that nobody decorated is public. Without a thought-out default, a bare [Authorize] might mean something the author did not read.",
         "lead": "I would rather a forgotten endpoint return 401 than accept an anonymous POST. Public routes are an explicit AllowAnonymous I can see in the diff."},
        {"t": "qa", "q": "How do you implement resource-based authorization for an order?",
         "a": "The route policy orders.read runs first and checks the scope. The action loads the order with Where Id and TenantId, and returns 404 when that row is absent. It then calls AuthorizeAsync with the order and the order.access policy. The handler succeeds when tenant_id matches the row and, if customer_id is present, that matches too. Staff tokens omit customer_id. I register a handler of AuthorizationHandler<OrderAccessRequirement, Order>. The requirement has no place on the attribute alone, because the attribute runs before the order exists.",
         "lead": "Coarse policy on the route, tenant predicate in the query, resource handler for the extra rule. I can point at a test for each."},
        {"t": "qa", "q": "Where does the tenant id come from, and what is BOLA?",
         "a": "BOLA is access to an object by guessing or changing its id, when the server checks the id and skips the owner. The Orders query is Id plus tenant. The tenant is tenant_id on the token when many customers share one Entra directory. It is Entra's tid when one customer is one directory. It is a server-side map from azp when the partner token identifies an application and the claim is not on the token. It is never a property of the JSON body. A global query filter repeats the rule for ordinary LINQ. A test with tenant A's token and tenant B's id is the control.",
         "lead": "I reject TenantId on the create model in validation. The day someone binds the entity directly, that rejection is what saves us."},
        {"t": "qa", "q": "What do you mark [AllowAnonymous], and what does minimal API metadata change?",
         "a": "The live and ready probes are anonymous. Anything else on the Orders API needs a named policy. [Authorize] and RequireAuthorization write metadata the middleware reads. AllowAnonymous writes the opt-out, including an opt-out from the fallback policy. Two RequireAuthorization calls both apply. I put a single policy on each route so the scope is obvious in the endpoint list. Controller filters and minimal API metadata are two ways to attach the same decision.",
         "lead": "I can open the endpoint list and read the policy next to the verb. A route I cannot find in that list is the one I am worried about."},
        {"t": "qa", "q": "When would one app use more than one authentication scheme?",
         "a": "When one process really has two surfaces. The BFF routes authenticate the cookie. The partner routes authenticate bearer. A forwarding scheme picks the handler from the request: an Authorization bearer header selects JWT, otherwise the cookie. Challenge and forbid must follow the same choice, or a browser receives 401 and a partner receives a redirect. I do not add the second scheme on the first day of the partner API. I add it when the BFF moves into this host for a reason I can say.",
         "lead": "Two schemes are a host decision. They are not a requirement of Entra, and they are not a requirement of having both a web app and an API in the company."},
        {"t": "qa", "q": "Where do signing keys live, and when is RS256 the right story versus a symmetric key?",
         "a": "Entra tokens: the API trusts the metadata document and verifies with the published public key. RS256 is the pin for those tokens once I have confirmed the alg on a real access token. Tokens I issue myself: the symmetric secret or the private key is loaded from Key Vault, and the appsettings file in git does not contain it. HMAC is enough for a local issuer with a small set of callers. The moment several services share that secret, any one of them can mint tokens for the others. That is a poor boundary. Those services should validate an IdP-signed token instead. The managed identity, not the user token, is what opens Azure SQL.",
         "lead": "I can name three identities: the caller in the token, the app's managed identity, and the pipeline identity that runs DDL. The signing key is a fourth secret, and it stays in the vault."},
        {"t": "qa", "q": "What is clock skew, and what do you set it to?",
         "a": "Clock skew is the allowance for exp and nbf when the issuer's clock and the API's clock disagree. The library default is five minutes. I leave it there, or I set a smaller value when I know the hosts sync and I want a tighter expiry. A large skew extends every expired token by that much. A skew of zero fails tokens when the machines are a few seconds apart, which shows up as random 401s after deploy. I do not use skew to paper over a token that is expired by hours. That token needs a refresh.",
         "lead": "Skew is a clock tolerance. It is not a session length. The access token lifetime is the session length I chose with the identity team."},
        {"t": "break"},
    ]
