# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 15 — Promises you can burn"},
        {"t": "p", "text": "Outcome: you can write an SLO for Harbor's accept path, and you can say where retries help and where they make an incident worse."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: SLI, SLO, error budget, and stability patterns below.",
            "40 min: the SLO chapter in Google's SRE book, or Release It! on timeouts and retries.",
            "70 min: Harbor SLO sheet.",
            "30 min speak, 30 min AI, 10 min restate the error budget in minutes.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "An SLI is the measurement. An SLO is the target you promise for that measurement over a window. An error budget is the amount of failure the SLO allows. For availability, 99.9 percent over 30 days leaves about 43 minutes. That number is 30 days times 24 hours times 60 minutes times 0.001. If you cannot compute it on a whiteboard, do not quote the nines. 99.95 percent is about 22 minutes. 99.99 percent is about 4 minutes. Harbor's accept path, one region, one database, is a 99.9 conversation if the business needs a number at all. It is not a 99.99 conversation."},
        {"t": "p", "text": "Separate the indicators. Availability of POST /orders: the fraction of requests that were not server failures, defined carefully so a 400 validation error is not downtime. Latency: p95 and maybe p99 of successful submits. Correctness: duplicate orders per thousand submits, which your idempotency key should drive toward none. Freshness of mail is a different SLO, looser, because you already decided mail is off the request. Do not average them into one green light."},
        {"t": "p", "text": "An error budget policy is a human rule. When the budget is gone, you stop shipping changes that add risk, and you spend the time on the reliability work that burned it. Without a person who can say no, the policy is a paragraph. The architect writes the policy. The engineering manager enforces it. Name both."},
        {"t": "p", "text": "Timeouts are how you stop waiting forever. Every outbound HTTP call has one. The timeout is lower than the user-facing budget if the call is on the request. Retries are how you survive a blip. Retry only when the operation is idempotent or you have a key that makes it so. Use a small number of tries and jitter so all callers do not stampede back at the same millisecond. Never retry a payment authorization because the response timed out. You do not know if the provider took the money. You reconcile. A circuit breaker opens when a dependency is failing, so you fail fast instead of filling the server with waiting requests. A bulkhead keeps a noisy dependency from using every thread. In Harbor the mail worker is already a bulkhead because it is another process. Inside the API, the payment client gets its own limit if payment stays on the request."},
        {"t": "p", "text": "Polly, and the .NET HTTP resilience handler, are the tools. The interview does not need the pipeline syntax. It needs the policy: timeout, retry with jitter for idempotent GETs, no blind retry for payment, circuit breaker around a provider that is already returning errors."},
        {"t": "p", "text": "The Angular side of the same decision: the submit button disables after the first click, the Idempotency-Key is generated once per attempt, and a failed read of the order list can show the last list with the time it was fetched. Do not clear the cart on a timeout until you know whether the 201 happened. Offer 'check latest orders' when the response is lost. That is the user-facing half of idempotency."},
        {"t": "lead", "title": "Say this", "text": "The accept path SLO I would start from is 99.9 percent availability and p95 under 400 milliseconds, both assumptions until measured, over a month. That is about 43 minutes of budget. Mail has a looser SLO. I retry idempotent reads. I do not retry a payment call that timed out. The UI keeps one idempotency key for the click so a timeout does not become two orders."},
        {"t": "warn", "title": "Interview trap", "text": "Promising 99.99 percent because it sounds serious, or putting a retry loop around every HttpClient including charges. Nines without a region and a data strategy are fiction. Retries without idempotency are duplication."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my SLO sheet and retry policy.
Did I mix mail latency into the accept-path SLO?
Which retry can double-charge or double-order?
Is the error budget in minutes, and did I name a person who can stop risky releases?
Do not raise the nines."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/quality/slo.md with two SLOs, the budget in minutes, and what you will not promise.",
            "A five-line retry policy.",
            "The Angular behavior when the submit response is lost.",
        ]},
        {"t": "qa", "q": "What SLO would you set, and how do retries fit?", "a": "I set an SLI first: success and p95 latency of the accept path, not of mail. A starting SLO for this one-region system is 99.9 percent and a p95 target we label as an assumption until we measure. The budget is about 43 minutes a month, and someone has to be allowed to stop risky releases when it is gone. Retries are for idempotent calls, with jitter. A timed-out payment is reconciled, not clicked again by a loop.", "lead": "The Angular client uses one idempotency key per submit so the user's double-click is safe too."},
        {"t": "break"},

        {"t": "h1", "text": "Day 16 — See the request from the browser to SQL"},
        {"t": "p", "text": "Outcome: you can say what you trace, what you count, what you log, and which three conditions page a human."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: signals, cardinality, and correlation below.",
            "30 min: ASP.NET Core OpenTelemetry overview, skim.",
            "80 min: observability map for submit order.",
            "30 min speak, 30 min AI, 10 min list the three pages from memory.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Logs, metrics, and traces are three different questions. A log is a discrete event you can read, such as 'order 123 accepted' with a trace id, not a novel. A metric is a number you aggregate over time: request count, error count, latency histogram, CPU. A trace is the path of one request across BFF, monolith, and SQL, made of spans. You need all three. A trace without metrics does not tell you if the error is rare. A metric without a trace does not tell you why this order was slow."},
        {"t": "p", "text": "Cardinality is how you drown the bill and the tool. A metric label may be the route template, the status code, the tenant tier if you have a handful of tiers. A metric label must not be the order id, the user id, or the raw URL. Those belong on a trace or a log, sampled if volume demands it. Log ingestion is a cost driver. Logging the body of every submit will include customer data and a large bill. Log the ids, the decision, and the trace id."},
        {"t": "p", "text": "Correlation: ASP.NET Core can emit OpenTelemetry traces and metrics, exported OTLP to Azure Monitor or another backend you already operate. W3C traceparent is the header that ties spans together. From the browser, you have two honest options. A real user-monitoring tool starts a trace in the page and propagates traceparent to the BFF. Or the BFF starts the trace and returns a request id header the UI can show in an error dialog. The second is enough for Harbor. Do not claim the Angular app is fully traced if you have not built the first."},
        {"t": "p", "text": "The RED signals for the API are rate, errors, and duration. The USE signals for the App Service plan and SQL are utilization, saturation, and errors. Google's four golden signals are latency, traffic, errors, and saturation. You do not need three dashboards that say the same thing. You need one page a tired person can read: submits per minute, error ratio, p95, SQL CPU or DTU saturation, Service Bus dead-letter depth, outbox lag."},
        {"t": "p", "text": "Page a human when the SLO is burning fast, when the payment provider or SQL is failing the accept path, or when the dead-letter depth or outbox lag crosses a line you set. Do not page on a single 500. Do not page on mail delay inside its looser SLO. The alert should link to the dashboard and say what 'good' looks like. An alert with no owner is a log."},
        {"t": "lead", "title": "Say this", "text": "Submit is traced from the BFF through SQL with OpenTelemetry, and the UI shows a request id when we fail. Metrics use the route and the status, not the order id. I page on SLO burn, on the database or payment path being down, and on dead-letter or outbox lag. I do not page on one exception, and I do not log the request body."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my observability map and my paging list.
Which signal has unbounded cardinality?
Which alert will fire every night and get ignored?
What can I not see if the outbox relay stops?
Do not add a second observability vendor."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/quality/observability.md: logs, metrics, traces, the three pages.",
            "A line on what you will not log.",
            "How a support person uses the request id.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 17 — Cost is an architecture constraint"},
        {"t": "p", "text": "Outcome: you can name Harbor's cost drivers and the assumptions a bill would test, without inventing a price."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "60 min: drivers and questions below.",
            "30 min: Well-Architected cost pillar, the principles page only.",
            "80 min: assumption and cost-driver page.",
            "30 min speak, 30 min AI, 10 min recite the drivers.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Architects lose trust by quoting a monthly figure they computed from memory. They gain trust by naming what moves the bill and what assumption the figure depends on. For Harbor the drivers are: the App Service plan's instance count and SKU, because it runs all month; Azure SQL's tier, because it also runs all month; Service Bus, which is usually smaller until you do something chatty; egress, if you move data out of the region; and log ingestion, which surprises teams who turn on verbose logging in production. The Functions worker is consumption-shaped and should not dominate unless mail volume is huge."},
        {"t": "p", "text": "The unit of scale is an order, and behind it a tenant. A question you ask: what does one extra tenant cost if they submit ten orders a day versus ten thousand? If you cannot sketch the shape, you do not understand which tier is flat and which is per request. App Service and a provisioned SQL tier are mostly flat until you scale out or up. A per-request AI feature or a per-GB log pipeline is not flat. Call the difference out before someone adds 'AI recommendations' to the catalog page."},
        {"t": "p", "text": "Degrade on purpose. If SQL is the cost center and the reliability center, you do not save money by running it too small to meet the SLO. You save money by not running a second region you cannot use, not keeping APIM for a partner who does not exist, not retaining debug logs for 90 days, and not sizing for a peak you have not measured. After launch, you read the bill and the metrics together and you right-size. Reserved capacity and savings plans are a finance conversation once the shape has been stable. Mention them as a follow-up, not as the design."},
        {"t": "p", "text": "The Azure pricing calculator and the actual invoice are the sources. In a review you say: 'I would price this from the calculator with these assumptions, then check the bill after a month.' Then you list the assumptions: instance count, SQL tier family without a fake dollar amount, log volume in GB if you have a guess and the word assumption next to it, region, and no multi-region."},
        {"t": "p", "text": "A cost decision is still an ADR when it changes the shape. 'We will not add a second region this year' is a cost and reliability decision. 'We will sample traces above this rate' is a cost and operability decision. Put the big ones in writing."},
        {"t": "lead", "title": "Say this", "text": "The bill will be mostly App Service and Azure SQL, plus whatever we log. I will not quote a price in the room. I will list the assumptions, open the calculator with the person who pays, and refuse a second region and a spare API gateway until a requirement forces them. Verbose logs are a cost incident as much as a security incident."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my cost-driver page. I did not include prices on purpose.
Which driver did I miss for this design?
Which assumption, if wrong by ten times, changes the host or the tier?
Where did I optimize cost by weakening the SLO without saying so?
Do not fill in dollar amounts."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/quality/cost.md: drivers, assumptions, what you will not run.",
            "One degrade decision: what you turn off or delay when cost or load forces a choice.",
            "Who signs the bill, from your day 1 stakeholder map.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 18 — Change the system without betting the company"},
        {"t": "p", "text": "Outcome: you can describe a strangler slice from a legacy .NET and Angular app, including the shared database and the rollback."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: fitness functions, expand and contract, and the slice below.",
            "40 min: Building Evolutionary Architectures, the fitness-function idea. Fowler's strangler fig article if you want the original metaphor.",
            "70 min: one migration slice with a rollback.",
            "30 min speak, 30 min AI, 10 min restate the rollback.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "An evolutionary architecture is one you can change with a guided set of checks. A fitness function is that check, automated where you can. For Harbor's future modular monolith, a fitness function is a test that Catalog does not reference Ordering's infrastructure project. NetArchTest is one way to write it. A contract test that the order message still has the fields mail needs is another. A pipeline check that new HTTP clients set a timeout is another. You do not need twenty. You need the two that would have caught the last painful incident."},
        {"t": "p", "text": "The legacy you should be able to discuss looks like this. An ASP.NET application on .NET Framework, a UI that is old Angular or a mix of MVC pages and Angular, and one SQL database in dbo that a reporting analyst queries with saved scripts. The business cannot stop taking orders. A rewrite-in-a-room for nine months is how this fails. A strangler moves one slice of behavior to the new system, leaves the rest, and routes only that slice."},
        {"t": "p", "text": "Pick a slice that earns its keep and has an edge you can intercept. Example: new orders from the buyer portal go to the new Ordering module, while invoices remain on the old app. The old UI gets a link, or the new BFF routes that path. You do not migrate 'the customer entity' in the abstract. You migrate a journey."},
        {"t": "p", "text": "An anti-corruption layer translates the old row into the new model at the edge, in one direction, until the old writer is dead. Old column names do not enter the new domain. If the old and new systems both write the same order row, you do not have a slice. You have a race. During the overlap, only one writer is allowed. The other reads."},
        {"t": "p", "text": "Expand and contract is how columns change. Add the new column. Deploy code that can read it. Deploy code that writes it. Backfill. Switch readers. Remove the old column in a later release. Dropping the column in the same release as the new code is how you remove rollback."},
        {"t": "p", "text": "The reporting analyst is a stakeholder, not an obstacle you route around. If they query dbo directly, they are a second consumer of the schema. You either support a view with a contract, or you give them a copy, and you do not drop their columns until they have moved. Put that in the plan or the plan is fiction."},
        {"t": "p", "text": "Rollback: a feature flag or a route sends submits back to the old writer, which still works because you did not drop its columns and you did not let the new system change a row the old system cannot read. A flag that lives for a year is a permanent branch. Give it an expiry in the ADR. Data written only by the new system during the trial must be readable by the old system or explicitly in scope to discard. Say which."},
        {"t": "lead", "title": "Say this", "text": "I would strangle one journey, new buyer submits, and leave invoices on the old app. One writer of an order during the overlap. Expand and contract on the table so we can route back. The reporting scripts are a consumer I schedule, not a surprise. The flag expires. I do not fund a nine-month freeze to rewrite the whole estate."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my strangler slice.
Who writes the order during the overlap?
What breaks for the reporting analyst?
What do I do with rows the new system wrote if we flip the route back on Friday?
Point at any step that drops a column too early."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/strangler-orders.md, the slice, the single writer, the rollback, the analyst.",
            "Two fitness functions you would put in CI after the new module exists.",
            "An expiry for the route flag.",
        ]},
        {"t": "qa", "q": "How would you modernize a legacy .NET and Angular system?", "a": "I would not rewrite it in one cut. I would move one journey, such as buyer submit, to the new ASP.NET Core module, keep a single writer, and leave the rest on the old app until that slice is proven. Schema changes expand and contract so the route can flip back. Anyone who queries the old database, especially reporting, is in the plan. A feature flag has an expiry.", "lead": "I would add a fitness test so the new module cannot grow a dependency back onto the old web project."},
        {"t": "break"},

        {"t": "h1", "text": "Day 19 — Angular at architect altitude"},
        {"t": "p", "text": "Outcome: ADR-003 chooses how the buyer and ops UI are structured, and you can say when microfrontends are the wrong spend."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "80 min: boundaries, state, performance, and accessibility below.",
            "30 min: angular.dev pages on standalone components and signals, only to confirm the vocabulary you will use.",
            "70 min: ADR-003 in your words.",
            "30 min speak, 30 min AI, 10 min redraw the library boundaries.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "At this altitude you do not debate a single component's change detection first. You decide what is allowed to depend on what, who releases the UI, and which budgets are real. The buyer portal and the ops portal are different audiences and different threat zones. Default in this plan: two Angular applications, so a buyer bundle does not contain ops screens, and a buyer host does not serve the ops app. The cost is two pipelines and a shared library to keep the visual language. The alternative, one app with lazy routes and a route guard, is acceptable when the team is small and the ops screens are not sensitive enough to force a separate host. That alternative is a decision, not a default you forget to mention. Pick one in the ADR and name the security consequence."},
        {"t": "p", "text": "Inside an app, boundaries follow the domain. Feature areas or libraries for catalog, ordering, and billing. A shared UI library has no business rules. A data-access library owns HTTP to the BFF and the types in the contract. Feature code does not hand-build URLs in random components. Enforce it. In a single CLI workspace, a written rule and review may be enough. Nx, or another workspace tool, earns its place when several teams and many libraries make the graph too hard to see. Do not adopt Nx as identity. Adopt it when the boundary is already breaking."},
        {"t": "p", "text": "State: signals are the default for state the component or the feature owns. RxJS stays at the edge where you truly have a stream: HTTP composition, typeahead, a socket. Do not convert every observable in a working app because the style guide moved. Do not introduce NgRx, or any global store, until you can name a bug that local state cannot fix, usually distant screens sharing a long workflow and going stale. A store is a cost in boilerplate and in concepts the next developer must learn."},
        {"t": "p", "text": "Microfrontends, including module federation or native federation, let two teams release UI independently. They also split the design system, the auth story, the performance budget, and the local developer experience. Choose them when two release trains cannot share a repository and that pain is already here. Harbor's two squads can share a repo. The ADR says no. The revisit trigger is a team that must ship a portal area on a cadence the others block, and a platform person who will own the shell."},
        {"t": "p", "text": "Performance is a budget, not a Lighthouse screenshot on your laptop. Set a target you will measure for the buyer home: transferred JavaScript on first load, and largest contentful paint on a throttled profile. An example target you may write as a target, not as a law: a shell that stays under a couple of hundred kilobytes compressed, then measure and adjust. Lazy-load ordering and billing. Do not lazy-load so aggressively that the submit path pays the delay. Server-side rendering helps a public catalog that must paint fast or be indexed. The authenticated order flow can stay client-rendered. Do not SSR the whole authenticated app as a slogan."},
        {"t": "p", "text": "Accessibility is a quality attribute. WCAG 2.2 AA is the usual bar. The fitness function is an automated scan on the order path in CI, plus one keyboard pass a human still does on the submit flow. A button that only works with a mouse is a failed accept path for a class of users, not a polish item for later."},
        {"t": "p", "text": "Zone.js and zoneless change detection: many production apps still run with Zone.js. Zoneless is a migration you schedule when change detection cost shows up in a profile, or when you are starting a new app and the current Angular documentation marks the path as supported for your major. Check angular.dev the week you write the ADR. Do not make zoneless the headline of your architecture review."},
        {"t": "lead", "title": "Say this", "text": "I split buyer and ops when the threat zone differs, and I keep domain libraries aligned with Catalog, Ordering, and Billing. Signals for local state, RxJS at the HTTP edge, no global store until we can name the stale-state bug. No microfrontends while two squads can share a repo. A performance budget and an accessibility check are fitness functions, not slides."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Review ADR-003, my Angular composition decision.
Does the security boundary match the deployable boundary?
Where did I add Nx, NgRx, SSR, or microfrontends without a trigger?
Which budget can a pipeline enforce?
Do not upgrade the Angular version in the answer."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/adr/003-frontend-composition.md.",
            "A sketch of apps and libraries, one page.",
            "The performance target and the accessibility check, each labeled as a target until measured.",
        ]},
        {"t": "qa", "q": "Would you use microfrontends?", "a": "Not for Harbor. The two squads can share a repository, and microfrontends would split auth, the design system, and the performance budget. I would split buyer and ops into two apps if we need a hard security and deployment boundary, and keep domain libraries inside each. I would revisit federation only when a team must release on a cadence the shared repo is blocking, and someone owns the shell.", "lead": "I would rather enforce a library boundary with a review rule than add a runtime composition framework."},
        {"t": "break"},

        {"t": "h1", "text": "Day 20 — Governance people will still talk to you about"},
        {"t": "p", "text": "Outcome: you can say which decisions must come to a review, what the forum is for, and what is on your technology radar."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "60 min: forum, triggers, and radar below.",
            "30 min: Accelerate, the four metrics only: deployment frequency, lead time, change fail rate, time to restore.",
            "80 min: write the triggers and a 15-item radar.",
            "30 min speak, 30 min AI, 10 min recite the triggers.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Governance fails in two directions. A committee that must approve every library, which teaches people to route around you. An absence of decisions, which teaches every squad to pick a different serializer, a different auth library, and a different logging shape. The architect's forum is a short meeting on a fixed rhythm, one hour every two weeks, with a written page in advance. It is not a gate on the sprint."},
        {"t": "p", "text": "Bring a topic when it matches a trigger: a new integration or a new data store; a new API that another team or a partner will call; an exception to a written principle; a step-change in cost; a new identity boundary; a production incident that was an architecture miss. Do not bring formatting, a single component, or a NuGet update that follows the existing standard. Those live in code review with the tech lead."},
        {"t": "p", "text": "Definition of ready for the forum, one page: the context, at least two options, a recommendation, the quality scenario you are serving, the risk, and the revisit trigger. If the page is missing, the forum does not invent the design live. You send it back. That feels strict and it saves the hour."},
        {"t": "p", "text": "A technology radar, in the Thoughtworks sense, has four rings. Adopt: the default, use it. Trial: use it in one place and learn. Assess: study it, do not put it in production yet. Hold: do not start new work with it. Harbor's radar should have about fifteen blips, not a catalog of the industry. Examples you should edit into your own voice. Adopt: modular monolith, BFF with cookie session, outbox, OpenAPI check in CI, managed identity. Trial: .NET Aspire for local orchestration. Assess: microfrontends, multi-region active-passive. Hold: new Azure AD B2C tenants, token in localStorage, AKS without a platform team, shared database as an integration style for new work."},
        {"t": "p", "text": "The four Accelerate measures tell you whether the governance is hurting delivery. If lead time explodes after you introduce the forum, the forum is too heavy. If change fail rate is high because nobody reviews boundaries, the forum is too light or the fitness functions are missing. You do not need a metrics program this month. You need to know the four names and what a bad movement would mean."},
        {"t": "p", "text": "Standards you write: principles, ADRs, API error shape, auth, logging. Standards you do not pretend are architecture: brace style, which an analyzer owns. Spending political capital on braces is how architects become irrelevant while the data model rots."},
        {"t": "lead", "title": "Say this", "text": "The forum is one hour every two weeks for new integrations, new stores, identity, cost steps, and principle exceptions. It is not a gate on every story. The radar has a few items we will actually enforce. Adopt the outbox and the BFF. Hold localStorage tokens and a cluster we cannot operate. If the forum slows delivery without reducing failed changes, I shrink the forum."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here are my review triggers and my 15-item radar.
Which trigger will fire on ordinary sprint work and annoy the team?
Which radar item contradicts ADR-001, ADR-002, or ADR-003?
Which Hold item has no reason a skeptic can read?
Do not add tools to look current."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/principles/review-forum.md: cadence, triggers, definition of ready.",
            "docs/principles/radar.md: fifteen items or fewer, four rings.",
            "One sentence on which Accelerate metric would tell you the forum is too heavy.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 21 — Say the architecture in ten minutes"},
        {"t": "p", "text": "Outcome: a spoken briefing that covers the decision, the tradeoff, the risk, and the revisit trigger. No slides required."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "40 min: read the script below, then close it.",
            "90 min: write your own script from your artifacts, not from the sample.",
            "50 min: record two takes. Watch one. Cut every sentence that does not contain a decision or a risk.",
            "30 min: AI listens only as a critic of the script text.",
            "30 min: third take, from memory, ten minutes or under.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A briefing is not a tour of Azure. Use this shape. One minute: who the buyer and the ops user are, and the scale assumption. Two minutes: the containers, including what you refused to add. Two minutes: ADR-001 and ADR-003, the monolith and the UI boundary. Two minutes: the accept path, the outbox, and the SLO with the number of minutes in the budget. Two minutes: the threat you designed for, tenant isolation and no token in the browser. One minute: the biggest risk and the revisit trigger. Stop. If they ask nothing, you are done. If they ask something, answer with a tradeoff, not a new product."},
        {"t": "p", "text": "Sample, to be replaced by yours. 'Harbor lets about two thousand buyer companies submit wholesale orders, with a peak we are treating as about forty submits a second until we measure it. Staff and buyers are different identity tenants. The Angular apps talk only to a BFF. Tokens stay on the server. One ASP.NET Core application holds Catalog, Ordering, and Billing, with separate schemas, because two squads can still release together and the order must commit with its outbox. Mail is a Functions worker off Service Bus. We are in one region on App Service and Azure SQL, so I will not promise more than three nines, about forty-three minutes a month. The risk I watch is the shared process: a bad catalog deploy can hurt submit. I split a module out only if cadence, measured scale, or compliance says so. I would not put the token in localStorage, and I would not start on Kubernetes.'"},
        {"t": "lead", "title": "Say this", "text": "That whole sample is the target length. If your version needs a diagram the audience cannot see, the words are still weak. Practice until the containers and the revisit trigger survive without the page."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my ten-minute script.
Mark every sentence that is a tool name without a decision.
Mark every number I did not label as an assumption or a measurement.
Tell me the question a skeptical director will ask at the end.
Do not rewrite the script. I will."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/briefing.md, your script.",
            "Three cuts you made after the first recording.",
            "Week score: SLO, observability, cost, migration, frontend, governance. Name the weakest.",
        ]},
        {"t": "break"},
    ]
