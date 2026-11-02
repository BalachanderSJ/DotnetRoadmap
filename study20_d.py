# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 16 — ASP.NET Core in production and in tests"},
        {"t": "p", "text": "Outcome: you can show logging, health, versioning, and one integration test that boots the real pipeline without a production database."},
        {"t": "h2", "text": "Logs, health, and versioning"},
        {"t": "p", "text": "Log the correlation id, the route, the status, and the elapsed time. Do not log the body when it can contain a name, an address, or a card. Health has two endpoints. Liveness is the process. Readiness includes a cheap SQL check. The App Service health probe uses readiness. API versioning for an enterprise partner is a URL segment, /v1/orders, until you have a reason to hide it in a header. Run v1 and v2 together. Measure calls on v1 before you delete it. The pipeline deploys both. A version is a contract, not a folder you rename on Friday."},
        {"t": "code", "text": """builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("sql", tags: ["ready"]);

app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});"""},
        {"t": "h2", "text": "WebApplicationFactory"},
        {"t": "p", "text": "An integration test constructs the host with WebApplicationFactory, replaces the database or the auth handler, and sends HTTP through the test client. The test proves routing, auth, and model validation together. It does not replace a SQL test of the query. Use it for the contract: an anonymous POST is 401, a body without a SKU is 400, a valid body with a test double for the handler returns 201. Dispose the factory. Do not point it at the production connection string in appsettings."},
        {"t": "code", "text": """public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    public OrdersApiTests(WebApplicationFactory<Program> factory) => _factory = factory;

    [Fact]
    public async Task Post_without_a_token_is_unauthorized()
    {
        var client = _factory.CreateClient();
        var response = await client.PostAsJsonAsync("/orders", new { sku = "AB-1", quantity = 1 });
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }
}"""},
        {"t": "p", "text": "Program must be visible to the test project. The usual approach is a public partial Program in the API project. The test replaces authentication with a handler that always fails, or always succeeds with a tenant claim, depending on the case. Two tests are more honest than one test that disables auth for the whole class and then claims to have tested auth."},
        {"t": "h2", "text": "Configuration and options, at release time"},
        {"t": "p", "text": "appsettings.json is the default. The environment name selects appsettings.Production.json. Environment variables override both. Azure App Service settings become environment variables. Key Vault references land in configuration before the host finishes starting, when the identity can read them. ValidateOnStart throws if Pricing:Rate is missing, and the slot fails before swap if the health check starts the process. A secret in appsettings.Production.json that is copied to the repo is still a secret in Git, whatever the file name says."},
        {"t": "warn", "title": "What breaks", "text": "A liveness probe that calls SQL, so a brief database blip restarts every instance. A factory test that uses the real startup connection and deletes rows. Versioning by copying the controller and forgetting the authorization policy on v2. Logging the request body in Development and leaving that switch on in Production."},
        {"t": "lead", "title": "Say this", "text": "Readiness checks SQL. Liveness does not. Versions overlap. WebApplicationFactory proves the HTTP contract, including 401. Secrets come from the environment or Key Vault, not from a json file in Git."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Write the two health URLs and what each may touch.",
            "Name the assertion of the anonymous POST test.",
            "Say the order of configuration overrides in one sentence.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 17 — Microservices past the first sketch"},
        {"t": "p", "text": "Outcome: you can go beyond the outbox drawing from the first roadmap. You can say who owns the service, how it deploys, and how a client discovers a contract without sharing the EF project."},
        {"t": "h2", "text": "A boundary you can staff"},
        {"t": "p", "text": "A service is a deployable with its own data, its own pipeline, and a team that can be on call for it. A project folder is a module. If orders and catalog still ship in one pull request every week, they are one team and should stay one deployable until that stops being true. The extra pieces you accept on the day you split are: a contract, a dashboard, an on-call rotation, and a way to roll the service back without rolling the other one back."},
        {"t": "h2", "text": "Contracts without a shared database model"},
        {"t": "p", "text": "Publish an OpenAPI document or a small message schema. The consumer writes a test against that contract. The provider's CI runs the contract. A shared Orders.Domain project referenced by the email service and the API is a distributed monolith: one entity change forces two deploys. The message OrderCreated carries an id, a version, a correlation id, and the fields the email needs. It does not carry the EF entity."},
        {"t": "code", "text": """public sealed record OrderCreated(
    Guid MessageId,
    string CorrelationId,
    int OrderId,
    string Number,
    DateTimeOffset OccurredUtc);"""},
        {"t": "h2", "text": "A gateway in front, not a shared database behind"},
        {"t": "p", "text": "YARP, or the platform gateway, routes /orders to the orders service and /catalog to the catalog service. The browser still sees one host. Each service still has its own database and its own login. The gateway authenticates once if that is the product choice, and forwards the tenant claim. It does not open SQL. A gateway that also contains tax rules becomes the new monolith. Keep rules in the service that owns the data."},
        {"t": "code", "text": """{
  "ReverseProxy": {
    "Routes": {
      "orders": {
        "ClusterId": "orders",
        "Match": { "Path": "/orders/{**catch-all}" }
      }
    },
    "Clusters": {
      "orders": {
        "Destinations": {
          "a": { "Address": "https://app-orders.internal" }
        }
      }
    }
  }
}"""},
        {"t": "p", "text": "The address is an example. Production uses the name your network actually has, and the gateway's identity is allowed to call the service. Internal services still authenticate the forwarded user or the gateway identity. A network rule alone is not authorization if the network is wide."},
        {"t": "warn", "title": "What breaks", "text": "Splitting the deploy and keeping one database with cross-schema joins. Two pipelines that must run in a fixed order every release. A shared NuGet of entities that versions in lockstep. A gateway timeout longer than the service timeout, so the user waits on a dead call the service already abandoned."},
        {"t": "lead", "title": "Say this", "text": "I split when a team can own the deploy, the data, and the on-call. The contract is a message or OpenAPI, not the EF model. The gateway routes. It does not own the business rule or the database."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Name the four things you add on the day you split catalog from orders.",
            "Say what the email service is allowed to reference.",
            "Explain why the gateway is not the place for tax.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 18 — One service, one pipeline, one failure"},
        {"t": "p", "text": "Outcome: you can describe a single orders service as it would exist after the split, including the pipeline path filter, the health check, and the user-visible failure."},
        {"t": "h2", "text": "The slice"},
        {"t": "p", "text": "The orders service is an ASP.NET Core API on App Service. Its pipeline builds on every change under src/Orders and deploys only that artifact. Catalog has a path filter of its own. A change to email does not recycle orders. The database is orders, with the runtime role and the migration identity from the first roadmap. The outbox and the idempotency table stay in that database. Inventory is not a table in this database. It is a call or a message."},
        {"t": "code", "text": """trigger:
  branches:
    include: [main]
  paths:
    include:
      - src/Orders/**
      - pipelines/orders.yml

pr:
  branches:
    include: [main]
  paths:
    include:
      - src/Orders/**"""},
        {"t": "h2", "text": "Failure the product can see"},
        {"t": "p", "text": "If inventory is down and the business said the customer may still place an order, the API writes Pending and the outbox. The user sees 201 and a status. If tax is required to price the order, the API returns 503 after a short timeout and does not write a wrong price. The pipeline did not cause that choice, but the dashboard the pipeline deploys with must show outbox age and the 503 rate. A service without those two numbers is not ready to be on its own pager."},
        {"t": "h2", "text": "Rollback of one service"},
        {"t": "p", "text": "Swap the orders slot back. Catalog stays. That works when the message contract was compatible. Adding an optional field is compatible. Changing the meaning of Number is not, and then a rollback of orders with a new catalog still in production is a lie. Contract changes use the same expand habit as database columns: add, deploy consumers that tolerate both, then remove. The pipeline does not deploy two services as one atomic release unless you have a reason you can say out loud."},
        {"t": "warn", "title": "What breaks", "text": "A path filter that forgets the shared library, so orders keeps running an old copy of the money type until someone notices. A health check that always returns 200 while the outbox is an hour old. Rolling back orders when the new event field was required and catalog already depends on it."},
        {"t": "lead", "title": "Say this", "text": "One service, one artifact, one path filter, one database, one slot rollback. The user either gets a 201 with a pending status or a short 503. I do not deploy the estate to change a line in orders."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Write the path filter for orders and say what it must also include.",
            "Choose 201 or 503 for a down tax service and justify it.",
            "Say when a single-service rollback is unsafe.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 19 — AIPDLC, the AI-assisted lifecycle"},
        {"t": "p", "text": "Outcome: you can place Cursor and Copilot inside the lifecycle without handing them the release. AIPDLC here means the AI-assisted product development life cycle: the same discover, design, build, test, release, and operate loop, with a model allowed to draft and a human required to sign."},
        {"t": "h2", "text": "Where a draft is useful"},
        {"t": "table", "headers": ["Stage", "The model may draft", "A human still signs"], "rows": [
            ["Discover", "A first cut of stories and questions", "The problem, the metric, and what is out of scope"],
            ["Design", "An ADR outline, a sequence, threats to consider", "The boundary, the data owner, and the rollback"],
            ["Build", "A method, a test, a YAML step, a Razor field", "The diff, the auth, the SQL, the migration"],
            ["Review", "A list of risks to look at", "The approval, especially on schema and identity"],
            ["Test", "Extra cases around the ones you named", "The assertion that protects money or a tenant"],
            ["Release", "A release-ticket draft from the diff", "The approval and the swap"],
            ["Operate", "A summary of logs you paste, with secrets removed", "Rollback versus fix-forward"],
        ]},
        {"t": "p", "text": "The model is a fast colleague who has not been on call for your system. It will invent a reasonable Azure setting. You check the current document or you do not ship the number. It will satisfy the test you asked for and miss the tenant test you forgot to mention. Your prompt is a specification. A vague prompt produces a vague edit across fifty files."},
        {"t": "h2", "text": "What you do not put in the prompt"},
        {"t": "p", "text": "Production connection strings, tokens, customer rows, and private keys do not go into chat. A stack trace is useful after you remove the connection string it printed. A failing test and the method under test are the right context. An entire repo paste is not. If the tool offers a privacy mode or a business agreement that keeps prompts out of training, the company decides that. You still do not paste a secret, because the secret is now in a log you do not control."},
        {"t": "h2", "text": "A worked pass on one story"},
        {"t": "p", "text": "Story: a partner retry must not create a second order. You write the acceptance test yourself, or you ask the tool to draft it and you fix the assertion until a missing unique index would fail it. You ask for the smallest change: a key column, a unique index, a check in the handler, and the migration as expand. You read the migration SQL. You ask for the pipeline impact only if the project file changed. You do not ask the tool to also split a microservice in the same session. The pull request stays reviewable. The tool does not approve it."},
        {"t": "code", "text": """Prompt shape that stays small:

Context: src/Orders.Api/CreateOrderHandler.cs and the test project.
Task: store an Idempotency-Key with a hash of the body in the same transaction as the order.
Do: unique (TenantId, Key). Same key and same body returns the first result.
Same key and a different body returns 409.
Do not: add a new service, change auth, or edit the pipeline.
Tests: one retry test must fail if the second insert happens."""},
        {"t": "warn", "title": "What breaks", "text": "Accepting a green diff you did not read. The tool added a catch that returns 200. A generated test that asserts true. A prompt that includes a customer export so the model can 'use realistic data'. A release pipeline edited by an agent and merged because the build passed. Generated code is still your code when it ships."},
        {"t": "lead", "title": "Say this", "text": "AI drafts inside the lifecycle. I sign the boundary, the test that protects money, the migration, and the release. I keep the prompt small, I keep secrets out, and I read the diff."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "For each lifecycle stage, say one thing you would let a model draft.",
            "Rewrite the idempotency prompt so it forbids a drive-by refactor.",
            "Name three things that never go into the chat box.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 20 — Cursor and GitHub Copilot"},
        {"t": "p", "text": "Outcome: you can use both tools as a senior uses a junior: clear tasks, a diff you read, and a refusal when the change is too wide. The habits overlap. The files they read for project rules do not."},
        {"t": "h2", "text": "What each tool is for"},
        {"t": "p", "text": "GitHub Copilot sits in the editor and in GitHub. Inline suggestions complete the line or the method you are already typing. Chat answers a question about the selection. A coding agent can open a pull request. You review that pull request with the same CODEOWNERS rules as a human colleague. Cursor is the editor you can ask to change several files, run a focused command, and show a diff. Agent mode edits. Plan mode is for a change you want designed before files move. Ask, or a read-only pass, is how you learn a pipeline file without rewriting it. Use plan when the task touches the pipeline, auth, or the data model. Use a direct edit when the task is one method and one test."},
        {"t": "h2", "text": "Context is the trick"},
        {"t": "p", "text": "Name the files. In Cursor, attach the handler and the test. In Copilot, point the chat at the selection or the file. A question with no file becomes a generic lecture. A question with the failing test and the method becomes a patch. Close the mental scope the same way: one bug, one acceptance check. If the answer wanders into a new architecture, stop and restate the boundary."},
        {"t": "code", "text": """Cursor, agent, after you have the test:

Open CreateOrderHandler and IdempotencyTests.
Make the retry test pass.
Keep the unique key in the same SaveChanges as the order.
Do not change the YAML or the auth handler.
Show me the migration SQL before you add more files.

Copilot, in the test file, with the method selected:

Write a test where the same Idempotency-Key and a different body returns 409.
Use the existing test host. Do not add a new framework."""},
        {"t": "h2", "text": "Project rules the tools can see"},
        {"t": "p", "text": "Copilot reads .github/copilot-instructions.md for the repository, and path-specific files under .github/instructions when the file you are editing matches. Cursor rules live with the project and tell the agent how this repo builds, tests, and reviews. Write the rules you already believe: cancellation tokens go to EF, the client does not send the price, migrations are expand-only, do not commit secrets, do not edit the pipeline unless asked. A rule you do not follow yourself trains the tool to be ignored. Keep the file short. A 40-page rule file is a novel. The tool will not hold it all."},
        {"t": "code", "text": """# .github/copilot-instructions.md
This is an ASP.NET Core orders API on .NET 10.
Pass CancellationToken into EF and HttpClient.
Do not bind price, tenant, or roles from the request body.
Schema changes are expand then contract.
Do not add a new project or a new package unless the prompt asks.
Tests use the existing test project. Prefer one behavior per test."""},
        {"t": "h2", "text": "Tricks that save a review"},
        {"t": "b", "items": [
            "Ask for the test first, watch it fail, then ask for the implementation. A test written after a green implementation often encodes the bug.",
            "Ask the tool to explain a YAML stage or a Razor form before you ask it to rewrite one. Understanding is cheaper than reverting.",
            "When the edit is wrong, say what is wrong in one sentence and point at the line. Do not start a new chat that has forgotten the constraint.",
            "Reject a suggestion that catches Exception and returns success, that logs a token, or that uses a SQL password.",
            "For a pipeline change, read the trigger and the environment before you run it. A suggested on: push with a deploy job is a production change.",
            "For MVVM, ask for a view model test with a fake client. Reject a suggestion that new's a window.",
            "For MVC, ask the form to include antiforgery and a view model. Reject a posted EF entity.",
            "Let formatters fix braces. Do not spend a session on style the editor already owns.",
            "If you cannot explain the diff, do not commit it. That rule is older than these tools and still decides the interview.",
        ]},
        {"t": "h2", "text": "A week of practice after the 20 days"},
        {"t": "p", "text": "Repeat one pipeline file until you can mark trigger, test, artifact, environment, and rollback without notes. Repeat one MVC form and one view model until the difference is boring. Then take a real story from your backlog and run it through the AIPDLC table: what the tool drafted, what you changed, and what you refused. That story is more useful in an interview than a list of product names."},
        {"t": "warn", "title": "What breaks", "text": "Trusting an inline completion in a migration or an auth handler because it looked fluent. Giving an agent permission to push to main. Pasting a production log with a connection string into chat to get a quicker diagnosis. A rule file that says 'be careful' and never mentions tenant, price, or secrets. The tool cannot invent your invariants if you hide them."},
        {"t": "lead", "title": "Say this", "text": "I point the tool at the file and the test. I keep the task small. Copilot instructions and Cursor rules state the invariants. I read the diff, I refuse secrets and drive-by architecture, and I still own the release."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Write five lines of copilot-instructions for the orders API.",
            "Rewrite a vague prompt, 'make orders better', into a bounded one.",
            "Say which tool mode you want before a schema change, and why.",
        ]},
        {"t": "h2", "text": "The map back to the first 10 days"},
        {"t": "p", "text": "Days 1 to 10 of the first roadmap are still the language, the API, SQL, Azure hosts, and the lead conversation. These 20 days are how that system is built with other people and with these tools. If a panel asks only one question from this set, answer with a pull request, a pipeline environment, a rollback, and the line you would not let a model merge. That is the same lead signal as the first guide: a decision, a cost, and a way back."},
    ]
