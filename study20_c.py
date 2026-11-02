# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 11 — ASP.NET Core MVC"},
        {"t": "p", "text": "Outcome: you can separate model, view, and controller on an orders admin site, and you can say why this is not the Web API you designed in the first ten days."},
        {"t": "h2", "text": "The three parts"},
        {"t": "p", "text": "The model is the data and the rules the view needs. Often that is a view model, a type shaped for the screen, not the EF entity. The view is the Razor markup that turns that model into HTML. The controller accepts the HTTP request, calls the application, chooses the view, and chooses the status. The controller is thin. A controller that calculates tax, queries five tables, and builds HTML in strings has eaten the other two parts."},
        {"t": "code", "text": """public sealed class OrderListViewModel
{
    public required IReadOnlyList<OrderRowViewModel> Orders { get; init; }
}

public sealed class OrdersController(IOrderQueries queries) : Controller
{
    [HttpGet("/admin/orders")]
    public async Task<IActionResult> Index(CancellationToken ct)
    {
        var rows = await queries.ListAsync(ct);
        return View(new OrderListViewModel { Orders = rows });
    }
}"""},
        {"t": "p", "text": "return View(model) renders Views/Orders/Index.cshtml by convention. The view declares its model type and does not inject a DbContext. A link uses tag helpers so the URL stays tied to the action name. If you rename the action, the helper fails the build instead of failing in the browser."},
        {"t": "code", "text": """@model OrderListViewModel
<table>
@foreach (var order in Model.Orders)
{
    <tr>
        <td>@order.Number</td>
        <td>
            <a asp-action="Detail" asp-route-id="@order.Id">Open</a>
        </td>
    </tr>
}
</table>"""},
        {"t": "h2", "text": "MVC, Razor Pages, and a Web API"},
        {"t": "p", "text": "MVC groups actions on a controller and views in a folder. Razor Pages group the page and its handler in one place, which fits simple forms. A Web API returns JSON and has no view. An admin site that humans click is a fair MVC or Razor Pages app. The partner integration stays a Web API. Do not add views to the partner API so the admin site can share a controller. Share the application service. Keep two hosts, or two endpoint groups, with two auth styles: cookie for the browser, bearer token for the partner."},
        {"t": "warn", "title": "What breaks", "text": "Returning an EF entity to the view. The view then walks navigation properties and you have an N+1 during render, or you leak a concurrency token you did not mean to edit. Putting business rules in the cshtml because the if was easy there. The rule is untested and the API cannot reuse it."},
        {"t": "lead", "title": "Say this", "text": "The controller chooses the action and the view model. The view renders. The entity stays out of the view. Browser UI and partner API share the application service, not the controller."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Name model, view, and controller for the orders list.",
            "Say why a view model is not an EF entity.",
            "Say which auth the browser uses and which the partner uses.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 12 — MVC details that show up in review"},
        {"t": "p", "text": "Outcome: you can post a form safely, explain model binding, and name the filter that runs. You can reject a form that trusts a hidden admin flag."},
        {"t": "h2", "text": "A form, binding, and antiforgery"},
        {"t": "p", "text": "A GET shows the empty form. A POST binds form fields onto a view model and checks ModelState. The form includes an antiforgery token. ASP.NET Core checks it on the POST so another site cannot submit the form with the user's cookie. Tag helpers add the token when the form uses the form tag helper. A hand-built HTML form that omits it fails closed if ValidateAntiForgeryToken is on. That is the setting you want."},
        {"t": "code", "text": """public sealed class CreateOrderViewModel
{
    [Required]
    public string Sku { get; set; } = "";

    [Range(1, 100)]
    public int Quantity { get; set; }
}

[HttpPost("/admin/orders")]
[ValidateAntiForgeryToken]
public async Task<IActionResult> Create(CreateOrderViewModel input, CancellationToken ct)
{
    if (!ModelState.IsValid)
        return View(input);
    var id = await handler.HandleAsync(input.ToCommand(), ct);
    return RedirectToAction(nameof(Detail), new { id });
}"""},
        {"t": "code", "text": """<form asp-action="Create" method="post">
    <input asp-for="Sku" />
    <span asp-validation-for="Sku"></span>
    <input asp-for="Quantity" />
    <button type="submit">Create</button>
</form>"""},
        {"t": "p", "text": "Redirect after a successful POST so a refresh does not submit again. If validation fails, return the same view with the model so the user sees the values and the messages. Do not put IsAdmin on the view model. A hidden field is still a field the browser can change. The user's role comes from the cookie claims. Over-posting is the same bug as on the API, with a friendlier UI."},
        {"t": "h2", "text": "Filters, areas, and TempData"},
        {"t": "p", "text": "An authorization filter runs before the action and can short-circuit with a challenge or a forbid result. An action filter runs around the action. A result filter runs around the view result. An exception filter is a local catch. Prefer the exception handler middleware for the site-wide error page so MVC and minimal endpoints share it. An area is a folder of controllers for a subsection, such as Admin, with its own route prefix. TempData survives one redirect, which is how you show 'Order created' after RedirectToAction. It is not a shopping cart. Session is the wrong place for the order total if you have more than one server and no distributed session."},
        {"t": "warn", "title": "What breaks", "text": "A POST without antiforgery on a cookie-authenticated site. Binding an entity directly, so a posted RowVersion or TenantId overwrites the database. Validation only in jQuery, bypassed by a raw POST. An exception filter that swallows the error and returns the form as if it saved."},
        {"t": "lead", "title": "Say this", "text": "GET shows the form. POST validates, then redirects. Antiforgery protects the cookie. The view model lists the fields the user may send, and privilege is not one of them."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Walk a failed validation and a successful create, including the redirect.",
            "Say what the antiforgery token is defending against.",
            "Point at one field you would remove from a posted entity.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 13 — MVVM"},
        {"t": "p", "text": "Outcome: you can draw model, view, and view model, and you can explain why an ASP.NET Core MVC view model is not, by itself, the MVVM pattern."},
        {"t": "h2", "text": "The shape"},
        {"t": "p", "text": "MVVM is a client pattern. The view is the screen. The model is the domain data. The view model sits between them. The view binds to properties on the view model. The view model exposes commands for save and cancel. The view does not call the database. The view model does not construct buttons. This is the usual shape in WPF, .NET MAUI, WinUI, and some mobile XAML apps. The binding engine pushes property changes to the screen when the view model raises a change notification."},
        {"t": "code", "text": """public sealed class CreateOrderViewModel : INotifyPropertyChanged
{
    private string _sku = "";
    private int _quantity = 1;

    public string Sku
    {
        get => _sku;
        set { _sku = value; OnPropertyChanged(); SaveCommand.RaiseCanExecuteChanged(); }
    }

    public int Quantity
    {
        get => _quantity;
        set { _quantity = value; OnPropertyChanged(); }
    }

    public RelayCommand SaveCommand { get; }

    public CreateOrderViewModel(OrderClient api)
    {
        SaveCommand = new RelayCommand(
            async () => await api.CreateAsync(Sku, Quantity),
            () => !string.IsNullOrWhiteSpace(Sku) && Quantity > 0);
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}"""},
        {"t": "p", "text": "The view binds Sku to a text box and SaveCommand to a button. The button disables itself when CanExecute is false. A unit test constructs the view model, sets Sku, and executes the command with a fake OrderClient. The test does not start the UI. That is the point of the pattern. INotifyPropertyChanged is the contract the binder listens to. Forgetting to raise it means the screen shows the old value after the code updates the field."},
        {"t": "h2", "text": "What MVC already has, and what it does not"},
        {"t": "p", "text": "An MVC type named OrderViewModel is a DTO for one request. The controller fills it, the view renders it, and the object dies at the end of the response. Nothing is observing property changes, because the HTML was already sent. Calling that MVVM confuses a panel. The honest sentence is: we use a view model so the view does not see the entity. The pattern of the server is still MVC. MVVM starts when a long-lived view binds to a long-lived object that raises change notifications and commands."},
        {"t": "warn", "title": "What breaks", "text": "Raising PropertyChanged for every keystroke that recalculates a huge order graph on the UI thread. The screen freezes. A view model that references a Window or a Button. You cannot test it, and you cannot reuse it on another client. Swallowing the API error inside the command so CanExecute stays true and the user thinks the order saved."},
        {"t": "lead", "title": "Say this", "text": "MVVM is a binding pattern for a live client. The view binds, the view model notifies and commands, the model is the domain. An MVC view model is a shape for one HTML response. I do not use the names as synonyms."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Draw view, view model, and model for a desktop create-order screen.",
            "Say what a unit test can call without a window.",
            "Say one sentence that keeps MVC and MVVM apart.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 14 — MVVM in front of ASP.NET Core"},
        {"t": "p", "text": "Outcome: you can place a MAUI or WPF client, a Blazor screen, and an Angular screen on the same API without forcing one pattern onto all three."},
        {"t": "h2", "text": "The API stays the API"},
        {"t": "p", "text": "POST /orders is the command. The client pattern does not change the idempotency key, the status codes, or the server-side price. The view model calls an OrderClient that uses HttpClient. The view model maps a 400 onto error properties the view already binds. It does not parse HTML. The API does not return a view model for WPF."},
        {"t": "code", "text": """public sealed class OrderClient(HttpClient http)
{
    public async Task<OrderDto> CreateAsync(string sku, int quantity, string key, CancellationToken ct)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "orders")
        {
            Content = JsonContent.Create(new { sku, quantity })
        };
        request.Headers.Add("Idempotency-Key", key);
        var response = await http.SendAsync(request, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<OrderDto>(ct))!;
    }
}"""},
        {"t": "h2", "text": "Blazor and Angular are cousins, not MVVM by slogan"},
        {"t": "p", "text": "A Blazor component has a view, the razor file, and state in the component class. If that state is a separate class with methods the markup calls, you are close to a view model. Blazor does not require INotifyPropertyChanged. It re-renders after an event or after you call StateHasChanged. An Angular component plus a service, from the Angular guide, is the same idea: the template binds, the class holds state, the service calls HTTP. Use those names with the team you are on. In a design review, say what is bound, what calls the API, and what you can test without the UI. That is the MVVM benefit even when the framework spells it differently."},
        {"t": "h2", "text": "Where the pattern earns its cost"},
        {"t": "p", "text": "A one-page internal tool does not need a relay command hierarchy. A desktop app with ten screens on one API does, or every screen will new up HttpClient and copy the error handling. Share the client and the auth handler. Keep each view model on one screen. A view model that is also a cache for the whole company catalog has become a service. Move the cache."},
        {"t": "warn", "title": "What breaks", "text": "Each view model creating its own HttpClient. Sockets run out, the same way they do on the server. Catching every exception and setting Error = ex.ToString(), which shows a stack to the user and may include a server path. Treating a 409 concurrency conflict as a generic failure, so the user retries and overwrites someone else."},
        {"t": "lead", "title": "Say this", "text": "The API contract stays MVC or minimal API on the server. The client holds a view model or a component and calls HttpClient through one typed client. I test the view model without the screen. I do not pretend Blazor, Angular, and WPF are the same pattern. I do say they share the split."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Place browser MVC, a Web API, and a MAUI view model in one diagram.",
            "Say which piece owns the idempotency key on a retry.",
            "Name the test that does not start a device.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 15 — ASP.NET Core, the parts after the first roadmap"},
        {"t": "p", "text": "Outcome: you can go past the pipeline sketch. You can place middleware, filters, and endpoint filters, and you can add caching and a background worker without capturing a DbContext."},
        {"t": "h2", "text": "Middleware, MVC filters, and endpoint filters"},
        {"t": "p", "text": "Middleware sees the HTTP request and runs for every endpoint that is downstream of it. MVC filters see an MVC action. Endpoint filters see a specific minimal API or a group. Use middleware for the correlation id, the exception page, and authentication. Use an MVC filter for an admin convention, such as a filter that adds a cache header on one controller. Use an endpoint filter for a validation check that belongs to one route group. A business rule in middleware is invisible to a queue consumer that calls the same handler later."},
        {"t": "code", "text": """var orders = app.MapGroup("/orders").RequireAuthorization("orders.write");
orders.MapPost("/", async (CreateOrderRequest body, CreateOrderHandler handler, CancellationToken ct) =>
{
    var result = await handler.HandleAsync(body.ToCommand(), ct);
    return result.Ok
        ? Results.Created($"/orders/{result.Value!.Id}", result.Value)
        : Results.ValidationProblem(new Dictionary<string, string[]> { ["body"] = [result.Error!] });
});"""},
        {"t": "h2", "text": "Output cache and rate limits"},
        {"t": "p", "text": "A reference list that changes hourly can be output-cached. An order the user just posted must not be cached for another user. Vary the cache by the tenant claim, or do not cache it. A public cache of a tenant-specific body is a data leak. Rate limiting protects the process from one client. It is not the only capacity plan. The SQL pool still has a limit. Return 429 with Retry-After. Do not rate-limit health checks or the site will mark itself unhealthy and restart."},
        {"t": "code", "text": """builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("orders", o =>
    {
        o.Window = TimeSpan.FromSeconds(1);
        o.PermitLimit = 20;
        o.QueueLimit = 0;
    });
});
app.UseRateLimiter();
app.MapGet("/catalog/categories", ListCategories).RequireRateLimiting("orders");"""},
        {"t": "p", "text": "The numbers are an example policy, not a platform quota. Set them from the real client and measure. OutputCache on a GET of categories is reasonable. OutputCache on POST /orders is a defect."},
        {"t": "h2", "text": "A background worker that owns a scope"},
        {"t": "p", "text": "IHostedService or BackgroundService is a singleton. It must not take DbContext in the constructor. Create a scope per pass, do one unit of work, dispose the scope. Pass the stopping token into the delay and into EF. Log the failure and continue the loop unless the process should stop. A worker that throws on the first SQL timeout takes the whole site down if the host is configured to stop when a background service faults."},
        {"t": "code", "text": """protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    while (!stoppingToken.IsCancellationRequested)
    {
        await using var scope = scopeFactory.CreateAsyncScope();
        var relay = scope.ServiceProvider.GetRequiredService<OutboxRelay>();
        await relay.PublishBatchAsync(stoppingToken);
        await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);
    }
}"""},
        {"t": "warn", "title": "What breaks", "text": "Caching a personalized response in a shared cache. A rate limit so low that a single office NAT looks like an attack and locks out a tenant. A hosted service that uses the root service provider for the life of the process and keeps one DbContext open. Middleware that reads the body and does not rewind it, so the action sees an empty body."},
        {"t": "lead", "title": "Say this", "text": "Middleware is for every request. Filters are for a route or an MVC action. I cache public reference data, varied by tenant if the body is private. A background worker opens a scope per batch. It does not capture DbContext."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Place correlation id, auth, and a single-route validator in middleware or filters.",
            "Say which GET you would cache and which you would not.",
            "Explain the scope inside the hosted service.",
        ]},
        {"t": "break"},
    ]
