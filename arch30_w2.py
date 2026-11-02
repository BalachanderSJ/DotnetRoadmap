# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 8 — How Harbor talks to the rest of the world"},
        {"t": "p", "text": "Outcome: for each Harbor flow you can say whether it is a method call, an HTTP call, or a message, and what the user sees when the other side is slow or down."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: integration styles and the timeout budget below.",
            "30 min: Azure Architecture Center page on communication in a microservices or distributed system, the styles section only. Or Hohpe's Enterprise Integration Patterns overview if you already know the Microsoft page.",
            "80 min: a table of Harbor flows: sync, async, or in-process, with the failure the user sees.",
            "30 min speak, 30 min AI, 10 min redraw the table.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "There are four classic ways two parts of a business exchange data. A shared database, which couples them forever and is the legacy you will meet on day 23. A file drop, which is still how some warehouses work and is acceptable when the latency is hours and the contract is a documented file. A remote call, HTTP or gRPC, where the caller waits. A message, where the caller records the fact and someone else reacts. Pick the style from who is waiting and who owns the data, not from a preference for events."},
        {"t": "p", "text": "Inside the Harbor modular monolith, Catalog and Ordering talking in-process is a method call, not a network call. Do not put HTTP between two modules that deploy together just so the diagram looks like services. That pays for failure modes you do not get independence in return for. The method is still a boundary: Ordering calls a public method on Catalog, or reads a price list Catalog published into Ordering's schema on purpose. It does not join Catalog tables."},
        {"t": "p", "text": "Use a synchronous call when a person is waiting and you need the answer to finish their action. Harbor's payment authorization is the example, and only if the product insists the buyer sees 'paid' before the screen returns. Then the payment call has a timeout that is part of the architecture, not a default of 100 seconds buried in HttpClient. If the provider is slower than the page should be, change the product shape: accept the order as payment pending, return 201, and let a worker finish the authorization. Do not hold an ASP.NET request open to look reliable."},
        {"t": "p", "text": "Use a message when the work can finish after the user has a response, or when the receiver is down and the fact must not be lost. Mail, search indexing, and a warehouse pick list are messages. Azure Service Bus is the broker in this plan because you want a durable queue, a dead-letter queue, and competing consumers. A message is at least once. Duplicate detection on Service Bus is a time window, not a business guarantee that the mail sends once. The consumer must be safe to run twice."},
        {"t": "p", "text": "A contract is part of the architecture. For HTTP, OpenAPI is the contract, checked so a breaking change fails CI. For messages, a schema with a version field is the contract. Add fields. Do not change the meaning of an existing field. Do not use a topic as a shared database that every service queries by replaying from the dawn of time unless you have actually designed for that. Harbor does not need event sourcing to ship."},
        {"t": "p", "text": "Timeouts compose. If the user-facing budget is 400 milliseconds at p95, the calls inside that request must be shorter, and you need a number for each. An assumption you may write down: catalog price lookup inside the process, a few milliseconds; SQL commit, the bulk of the budget; payment, not on this request if you chose pending. Say the assumption. A timeout with no retry policy is unfinished, and a retry policy on a non-idempotent payment call is a double charge. Day 15 goes deeper. Today, name the timeout owner."},
        {"t": "table", "headers": ["Flow", "Style", "User impact if the other side is down"], "rows": [
            ["Buyer loads a product", "Read, in-process or a replica", "Catalog page fails or shows a stale snapshot you labeled"],
            ["Buyer submits an order", "Local transaction in Ordering", "Submit fails. No half-saved order."],
            ["Payment authorization, if on the request", "Sync HTTPS with a short timeout", "Order stays pending or the submit fails. Never a silent double charge."],
            ["Confirmation mail", "Outbox then Service Bus", "Order is already accepted. Mail is late. A dead-letter is an alert, not a lost order."],
            ["Warehouse pick", "Message or a file, their contract", "Order is accepted. Pick is delayed. Their outage is visible as a status, not as an HTTP 500 to the buyer."],
        ]},
        {"t": "lead", "title": "Say this", "text": "I keep Catalog and Ordering in-process until they deploy separately. I use HTTP when the user is waiting and I own the timeout. I use Service Bus after the order is durable, for mail and for partners who must not be on the buyer's request. The broker can deliver twice. The handler is idempotent. I do not share the database with the warehouse as the integration."},
        {"t": "warn", "title": "Interview trap", "text": "Saying 'we are event-driven' and then describing a chain of synchronous calls with a bus in the middle. A bus does not remove coupling if the user still waits for every consumer."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my Harbor integration table.
Which synchronous call will blow the 400 millisecond assumption if the dependency stalls?
Which message did I use where the user actually needs the answer on the request?
Where did I imply exactly-once delivery?
Do not add Kafka unless you can say why Service Bus fails the requirement."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/integrations.md with the table in your words.",
            "One sentence on the payment choice: on the request, or pending. Pick one and name the product consequence.",
            "The timeout you would set on that payment call, labeled as an assumption.",
        ]},
        {"t": "qa", "q": "REST or messaging?", "a": "Both, for different waiting times. Submit commits in SQL and returns. Mail and the warehouse are messages because the buyer should not wait on them, and those systems fail independently. I would not put HTTP between Catalog and Ordering while they are the same deployable. I would not claim the bus gives me exactly-once delivery.", "lead": "If payment must be known before the button finishes, that call is synchronous, it has a timeout, and it is not blindly retried."},
        {"t": "break"},

        {"t": "h1", "text": "Day 9 — Who owns the data"},
        {"t": "p", "text": "Outcome: you can point at every important table family and name one writer. You can explain the outbox and a tenant filter without drawing a second database you do not need."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: ownership, outbox, and tenancy below.",
            "40 min: Software Architecture: The Hard Parts, the data-ownership chapters, or this document again if the book is not here.",
            "70 min: schema sketch and the outbox transaction in words.",
            "30 min speak, 30 min AI, 10 min redraw who writes an order.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Data ownership is the architecture. Service boundaries that do not match write ownership are fiction. In Harbor one Azure SQL database is acceptable because ADR-001 kept one deployable. Ownership is still split by schema: catalog, ordering, billing. Application code in Catalog does not query ordering tables. A report that needs both is an explicit read model or a reporting schema fed by a copy, not an ad-hoc join hidden in a controller."},
        {"t": "p", "text": "The transaction boundary is the module's own change. Ordering can insert the order row and the outbox row in one transaction. Ordering cannot, in the same transaction, update a table Billing owns and a table in an external warehouse. If you need that, you have a saga, which is day 10, or you have the wrong boundary and the two facts are actually one module."},
        {"t": "p", "text": "The transactional outbox solves a specific failure: the order commits, the process dies, the message never leaves. You insert the message payload into an outbox table in the same commit as the order. A relay reads unpublished rows and sends them to Service Bus, then marks them published. The relay can crash after the send and before the mark, so the message can appear twice. That is allowed. Consumers dedupe. Do not 'solve' this by publishing to the bus before the commit. A crash then announces an order that does not exist."},
        {"t": "p", "text": "Price is copied onto the order line at submit. Catalog can change the list price a minute later. The order keeps the price the buyer accepted. That copy is deliberate duplication. The alternative, reading Catalog live for every historical invoice, rewrites history."},
        {"t": "p", "text": "Multi-tenant means every buyer company is a tenant. The tenant id comes from the authenticated session, never from a hidden field the client can edit. Every order query includes the tenant. A cross-tenant test tries to read company B's order with company A's session and must fail. SQL row-level security can be a backstop so a missed filter still returns nothing. It is not a substitute for the filter you can see in code review. A unique idempotency key is unique per tenant, not globally, unless you designed global keys on purpose."},
        {"t": "p", "text": "CQRS means the write model and the read model are different shapes. Use it when the screen fights the transaction. Order history search across a year, with free text, does not belong on the orders table as a pile of LIKE queries. A search index fed by the outbox is a read model. Getting one order by id is not CQRS. It is a query. Do not split read and write databases on day one to sound advanced."},
        {"t": "code", "text": """One transaction in Ordering:
  insert into ordering.Orders (...)
  insert into ordering.Outbox (Id, Type, Payload, PublishedAt null)
commit
Relay, separate loop:
  read a batch where PublishedAt is null
  send to Service Bus
  set PublishedAt
Consumer:
  if this event id was already applied, return
  else apply and record the event id"""},
        {"t": "lead", "title": "Say this", "text": "Ordering is the only writer of an order. The price on the order is a copy taken at submit. The outbox row commits with the order, and the publisher is allowed to send twice. Every query is scoped by the tenant on the session. A search screen can have its own copy. It does not become a second writer of the order."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my schema ownership sketch and outbox description.
Find any data with two writers.
Find a query that reaches into another module's tables.
Tell me what the buyer sees if the relay is down for an hour.
Do not invent a second database."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/data.md: schemas, writer, what is copied.",
            "The outbox steps in your own words, including the duplicate.",
            "The cross-tenant test you expect the team to keep.",
        ]},
        {"t": "qa", "q": "How do you keep the write and the message consistent?", "a": "I write the order and an outbox row in the same SQL transaction. A relay publishes the row and can publish it twice if it crashes at the wrong time. Consumers are idempotent. I do not publish to Service Bus before the commit, because the message would outrun the data.", "lead": "Search and mail read copies. They are not allowed to update the order."},
        {"t": "break"},

        {"t": "h1", "text": "Day 10 — Consistency without fairy tales"},
        {"t": "p", "text": "Outcome: you can draw the order states, say what happens when a message is delivered twice or out of order, and choose orchestration or choreography for one Harbor saga."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: duplicates, ordering, sagas, and CAP below.",
            "40 min: Kleppmann chapter 8, the failure modes, skim. Or Hard Parts on sagas.",
            "70 min: state machine and one compensation.",
            "30 min speak, 30 min AI, 10 min redraw the states.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Distributed systems fail in boring ways: the message arrives twice, the acknowledgement is lost, the receiver is slow, clocks disagree, a process dies between two writes. Harbor does not need a theorem to respect that. It needs a state machine and handlers that can run twice."},
        {"t": "p", "text": "At-least-once delivery is the contract you should design for on Service Bus with peek-lock. The lock expires, another worker gets the message, both might have done the work if the first one finished and then failed to complete the message. Exactly-once is a phrase vendors use for a narrow mechanism. The effect you want, one mail and one invoice, is something you build with an idempotency key or a processed-event table. Say that plainly. Duplicate detection on the broker reduces accidents inside a window. It is not the design."},
        {"t": "p", "text": "Ordering is not free. If two events for the same order must be applied in order, use Service Bus sessions keyed by order id, and accept less parallelism for that order. If the events commute, or if each event carries the full new status, you do not need sessions. A 'set status to Accepted' event that arrives after 'set status to Cancelled' is a bug unless the handler ignores a stale status. Prefer a state machine that refuses illegal transitions over a hope that the bus stays ordered."},
        {"t": "p", "text": "Harbor order states you can defend: Draft is optional and local to the UI. Submitted means we have a durable row. Accepted means it passed credit and any reservation you decided was in the transaction. Rejected means credit or validation failed and the row exists so support can see it. Cancelled means an accepted order was undone by a deliberate compensation. Do not delete the row. Deleting destroys the audit and breaks idempotency."},
        {"t": "p", "text": "A saga is a sequence of local transactions with a compensation or a retry when a later step fails. Two styles. Orchestration: one component, here Ordering, tells the next step what to do and stores the saga state. Choreography: each module reacts to events and emits the next. Orchestration is easier to see for two or three steps and one team. Choreography spreads the process across teams and makes the overall state harder to find. For Harbor, if inventory reservation is a second step outside the order transaction, orchestrate it from Ordering. If reservation fails, compensate: mark the order Rejected or Cancelled, release anything you held, and do not send the buyer a success mail. If Billing only needs to hear that an order was accepted, that is choreography of a notification, not a saga. A reaction with no compensator is not a saga. It is a subscriber."},
        {"t": "p", "text": "CAP, said carefully: when a network partition happens, a distributed data system cannot give you both perfect availability and perfect linear consistency. It is not a daily slogan and it is not 'you can only pick two of consistency, availability, and partition tolerance' as a product feature matrix. Partitions happen. Harbor's order write chooses consistency: if the database cannot be reached, the submit fails. The catalog read might choose a stale replica and be more available. Say which path chose which. Do not say 'we are AP' for the whole company."},
        {"t": "code", "text": """Submit (orchestrated):
  commit order as Submitted, with outbox OrderSubmitted
  ask inventory (sync or a waited reply with a timeout)
  if reserved: set Accepted, outbox OrderAccepted
  if not: set Rejected, release nothing that was not held, outbox OrderRejected
Mail worker:
  on OrderAccepted, send once per (order id, Accepted)
  ignore duplicates
  do not mail on OrderRejected"""},
        {"t": "lead", "title": "Say this", "text": "The order has states, and illegal jumps are refused. The bus can deliver twice, so the mail worker records the event id. I orchestrate reservation from Ordering because there are two steps and one team, and I can show the saga row. I do not call that exactly-once. If SQL is partitioned away from the API, the submit fails rather than accepting an order we cannot store."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my order state machine and the reservation saga.
Find a transition that loses an audit.
Find a step that charges or reserves twice if the message is replayed.
Say whether this is orchestration or choreography, and whether I hid the state.
Do not add a new broker."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/order-states.md with states, who may move them, and one compensation.",
            "A sentence on what duplicate delivery does to mail.",
            "A sentence on CAP that names only the submit path.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 11 — Identity and the ways an order submit is attacked"},
        {"t": "p", "text": "Outcome: you can threat-model submit order with STRIDE, and you can say which Entra setup Harbor uses for buyers and for staff."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "80 min: STRIDE, OWASP API notes, and identity zones below.",
            "30 min: OWASP API Security Top 10, the object-level authorization entry. And the Entra authorization-code page if day 6's skim was thin.",
            "70 min: a threat model page for POST /orders.",
            "30 min speak, 30 min AI, 10 min redraw the trust zones.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "STRIDE is a checklist, not a ceremony. Spoofing: someone pretends to be a buyer. Tampering: they change the payload, especially price, quantity of a sku they should not see, or tenant id. Repudiation: a buyer denies they placed the order, and you have no durable record of who was on the session. Information disclosure: company A reads company B's order, or a log line prints a personal email into a shared sink without retention rules. Denial of service: a script submits huge carts or hammers the route. Elevation of privilege: a buyer token calls an ops endpoint, or a viewer role updates an order."},
        {"t": "p", "text": "The OWASP API list changes editions. The item you must be able to discuss by its meaning is broken object level authorization. The call is GET /orders/{id}. You load the order by id and return it. The attacker uses their own valid token and someone else's id. The fix is the tenant and the user scope on every read and write, tested with a cross-tenant case. Hiding the id in a GUI is not the fix. A 404 for both 'missing' and 'not yours' avoids confirming that the other id exists."},
        {"t": "p", "text": "Identity zones. Staff authenticate against the workforce Entra tenant. Buyers on a new system authenticate against Entra External ID. Existing products may still be on Azure AD B2C. Do not start a new B2C tenant in 2026 unless a control you require is missing from External ID; check Microsoft's current comparison the week you decide, and record it in the ADR. Two app registrations. The ops API rejects buyer tokens by audience, not by a role string the client sent."},
        {"t": "p", "text": "Secrets. Managed identity for Azure SQL, Service Bus, and Key Vault. The Angular environment file is public. It may contain a public client id. It must not contain a client secret, a connection string, or an API key that grants data. User secrets and Key Vault references are for the server. Rotating a secret that was shipped in JavaScript means you already lost; assume it was copied."},
        {"t": "p", "text": "A content security policy and a dependency audit belong in the same conversation as the token story. XSS is how a cookie session is ridden and how an in-memory token is stolen. The architect names the control: strict CSP, no secret in the bundle, HttpOnly cookie, anti-forgery on writes. npm audit and NuGet audit are signals. A failing audit on a transitive test package is not the same as a failing audit on the authentication library. The team needs a written rule for which severity blocks a release."},
        {"t": "table", "headers": ["Threat", "Harbor control"], "rows": [
            ["Spoofing", "Entra, BFF session, cookie flags. No long-lived token in JavaScript."],
            ["Tampering", "Server-side price. Tenant from the session. Anti-forgery on cookie writes."],
            ["Repudiation", "Order row stores user id, tenant, timestamp. Audit is separate from logs. Day 24."],
            ["Information disclosure", "Tenant filter and a cross-tenant test. 404 when the order is not in the tenant."],
            ["Denial of service", "A rate limit on submit, a max page size, and a timeout on payment."],
            ["Elevation", "Buyer audience cannot call ops routes. Authorization checked on the server, per action."],
        ]},
        {"t": "lead", "title": "Say this", "text": "I threat-model the submit with a checklist, and the control I care about most is object-level authorization: a real buyer token must not read another tenant's order. Staff and buyers are different identity tenants and different audiences. Secrets stay off the Angular bundle. Managed identity reaches SQL."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my STRIDE table for POST /orders and GET /orders/{id}.
Which control is actually a UI convenience?
Which threat has no test a developer could automate?
Where did I trust a value from the browser?
Do not invent compliance certifications."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/security/threat-model-order-submit.md using the table, rewritten.",
            "Identity note: workforce tenant, external tenant, what a buyer token cannot call.",
            "One pipeline rule: the severity that blocks a release, and who may waive it.",
        ]},
        {"t": "qa", "q": "How do you secure a multi-tenant API?", "a": "The tenant comes from the token or the server session, not the body. Every query is filtered by that tenant, and a test proves company A cannot read company B. Authorization is per action on the server. I return 404 when the id is outside the tenant. Row-level security in SQL is a backstop. The Angular app hiding a button is not a control.", "lead": "I keep buyer identity and staff identity in separate Entra configurations so a buyer token fails the ops audience check."},
        {"t": "break"},

        {"t": "h1", "text": "Day 12 — An Azure shape you can operate"},
        {"t": "p", "text": "Outcome: you can choose a host for each Harbor container and map the choice to the Well-Architected pillars without quoting a price."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: hosts and pillars below.",
            "40 min: Azure Well-Architected Framework, the five pillar overviews. Skim the Architecture Center 'choose a compute' guidance if time remains.",
            "70 min: host decision table for Harbor.",
            "30 min speak, 30 min AI, 10 min redraw the hosts.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The five pillars are reliability, security, cost optimization, operational excellence, and performance efficiency. A design review that only names products misses the pillar it is spending. Harbor in one region spends reliability: you will have downtime when the region or the database has downtime, and you accepted that in exchange for cost and operational simplicity. Write that down. Do not discover it in an incident."},
        {"t": "p", "text": "App Service is the default host for the BFF and the modular monolith. You get slots for a swap, a simple scaling model, and a place for managed identity. Choose it when the workload is request and response and the team does not want to run a cluster. Azure Functions, isolated worker, is the default for the notification worker: an event starts it, it can scale separately, and a poison message should not exhaust the API's threads. Container Apps is the step when you need a container, a scale rule, or several processes, and you still do not want to operate Kubernetes. AKS is justified when a platform team already runs a cluster and the workload needs those controls. Twelve people and a wholesale portal do not justify AKS as a learning project."},
        {"t": "p", "text": "API Management sits in front of APIs that external partners call, when you need keys or OAuth for those partners, quotas, and a product catalog of APIs. The first-party Angular app does not need APIM on day one. The BFF is its facade. Adding APIM 'for the future' is a component you must patch, secure, and explain at 2 a.m. Revisit when a partner must call you without the BFF cookie. That is the day 29 case."},
        {"t": "p", "text": "Azure Front Door and a WAF matter when the app is on the public internet and you want a global entry, TLS at the edge, and a filter for obvious abuse. They do not fix broken object-level authorization. One region still means the data is in one region. Front Door does not turn Harbor into a multi-region system."},
        {"t": "p", "text": "Identity to Azure resources is managed identity. The App Service and the Function have identities. Those identities have roles on SQL, Service Bus, and Key Vault. No SQL password in a setting. Slots: production and staging. You deploy to staging, you smoke-test, you swap. Swap is not a data migration strategy. A bad migration still needs its own rollback, which is day 18."},
        {"t": "p", "text": ".NET Aspire orchestrates the local run: the API, the worker, dependencies, and OpenTelemetry defaults. It does not choose your production host and it is not a cloud. Say that in one sentence so you do not get marked as someone who thinks Aspire replaces Azure."},
        {"t": "p", "text": "Multi-region is a new ADR, not a checkbox. Active-passive with a recovery point and a recovery time you can say out loud is the honest upgrade. Active-active needs a write strategy for orders so two regions do not accept conflicting submits. You do not have that strategy. Do not draw two regions 'for resilience' and leave the database as a single node with a dotted line."},
        {"t": "table", "headers": ["Container", "Host", "Pillar you are being honest about"], "rows": [
            ["BFF and monolith", "App Service, slots, managed identity", "Operations stay simple. Reliability is one region."],
            ["Mail worker", "Functions isolated", "A poison message is isolated from the API process."],
            ["Data", "Azure SQL, one region", "Consistency of the order. Availability capped by that region and that service."],
            ["Messages", "Service Bus", "Durability of mail and integration, not of the order itself. The order is already in SQL."],
            ["Partner API, later", "APIM only when a partner exists", "Do not pay the operational cost on day one."],
            ["Cluster", "Not AKS", "Cost and operations. Revisit with a platform team and a need."],
        ]},
        {"t": "lead", "title": "Say this", "text": "Harbor runs the API on App Service and the mail worker on Functions. One region, one Azure SQL, managed identity, slots for the app deploy. I am explicit that this is not 99.99 percent and not multi-region. API Management waits for a real partner. AKS waits for a platform team. Aspire is how we run it locally, not where it runs in production."},
        {"t": "warn", "title": "Interview trap", "text": "A diagram of twenty Azure icons for a team of ten. Every icon is a pager. If you cannot say who operates it, take it off the diagram."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my Harbor host table.
Which service has no operator?
Where did I imply multi-region without a data strategy?
Which pillar did I ignore?
Do not add prices or SKU names you cannot tie to a requirement."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/azure.md, the host table and the one-region statement.",
            "A revisit trigger for APIM and a separate one for a second region.",
            "One sentence on what Aspire is for.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 13 — The API is a contract, not a controller"},
        {"t": "p", "text": "Outcome: you can specify submit order's status codes, idempotency, and versioning rule so two teams would build the same behavior."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: errors, idempotency, pagination, and versioning below.",
            "30 min: ASP.NET Core Problem Details documentation, skim.",
            "80 min: write the contract for POST /orders and GET /orders.",
            "30 min speak, 30 min AI, 10 min restate the status codes.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "First-party Angular and a public partner do not get the same versioning story. The Angular app ships with the API. You can evolve with expand and contract: add a field, deploy the reader, deploy the writer, remove the old field later. You do not need /v1 in the URL until a client you do not deploy must keep working. When that partner exists, a URL version is the blunt tool they can actually use. Header versioning is easier to get wrong in caches and gateways. Pick URL versioning for the partner API and write it down."},
        {"t": "p", "text": "Idempotency on create is an architecture decision because the buyer will double-click and the BFF will retry a lost response. The client sends an Idempotency-Key. Ordering stores it, unique per tenant, with the request hash and the order id. The same key and the same body return the same order and the same status. The same key and a different body return 409. A retry is not a second order. This is the same idea as the outbox consumer, applied to HTTP."},
        {"t": "p", "text": "Status codes are a vocabulary. 201 when the order is stored, body includes the id. 400 when the input is invalid. 401 when there is no session. 403 when the session is real but the action is not allowed. 404 when the order is missing or not in this tenant. 409 for an idempotency conflict or an illegal state change. 429 when the rate limit trips. 503 when a dependency you chose to surface is down, with a retry hint only if the client can retry safely. Do not return 200 with an error field for these cases. The Angular client will treat 200 as success."},
        {"t": "p", "text": "Error bodies use Problem Details, the shape ASP.NET Core already produces. A type, a title, a status, and a trace id the support person can paste. Do not return a stack trace. Do not return a SQL error. Validation errors can list fields. A payment decline is a domain result the UI can explain, and you decide whether it is 422 or a 201 with a Rejected order. Pick one. The rejected-order choice keeps an audit row. The 422 choice is simpler and easier to lose. Harbor keeps the row. Say so."},
        {"t": "p", "text": "Pagination: offset pages lie when new orders insert above the cursor the user is walking, and large offsets get slow. A continuation token or a keyset on (created time, id) is the adult choice for an order list. Cap the page size. Sorting by an unindexed column is a performance incident waiting for a client."},
        {"t": "p", "text": "OpenAPI is generated from the API and compared in CI. A breaking change is a failed check, or an explicit ADR if you truly must break a partner. The Angular data-access library is generated or handwritten against that contract, not against a controller you happened to read."},
        {"t": "code", "text": """POST /api/orders
Idempotency-Key: required
Body: lines[{sku, quantity}]   # price and tenant ignored if present
201: order id, status Submitted or Accepted
409: key reused with a different body
400: validation, Problem Details
401 / 403 / 429: as above

GET /api/orders?pageSize&continuation
GET /api/orders/{id}  # 404 if other tenant"""},
        {"t": "lead", "title": "Say this", "text": "The first-party app versions by expand and contract. A partner gets a URL version when they exist. Create order requires an idempotency key, and the same key returns the same order. We keep a rejected order as a row so support can see it. List endpoints use a continuation token, not a page number we cannot honor."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my POST /orders contract.
Find a case where the client retries and creates two orders.
Find a status code that will make Angular show success when the order failed.
Find a field I accept from the client and should ignore.
Do not redesign the BFF."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/api-orders.md with codes, idempotency, and pagination.",
            "The versioning rule in one paragraph.",
            "The Problem Details fields you will actually return.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 14 — Messaging decision and a red team"},
        {"t": "p", "text": "Outcome: ADR-002 is accepted in your portfolio, the threat model matches it, and you can survive a hostile reading."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "30 min: re-read your integration table, outbox notes, and threat model. Fix contradictions before you write.",
            "90 min: ADR-002, why Service Bus and an outbox, what you rejected.",
            "40 min: speak the week: data owner, saga, identity, host, API contract.",
            "40 min: AI red team, then edit the ADR.",
            "20 min: redraw the path from button to mail with the laptop closed.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "ADR-002 should be narrower than 'we use messaging'. The decision is: after the order commits, integration and mail go through an outbox to Azure Service Bus. Consumers are idempotent. Sessions are used only where order matters, named per flow. You rejected calling the email provider inside the submit request. You rejected a second database as a bus. You rejected claiming exactly-once. Consequences: mail can lag, and someone must watch the dead-letter queue. The revisit trigger: a consumer needs a million messages a second, an ordering guarantee Service Bus sessions do not give you, or a retention and replay story you measure and Service Bus cannot meet. Do not name Kafka as the revisit unless you can say which of those triggers fired."},
        {"t": "p", "text": "The red team is the AI session plus you. A useful objection sounds like: the outbox relay is now a critical component and you have no SLO for lag. Or: the threat model says the tenant comes from the session, but the message payload also contains a tenant id that a bad relay could forge. The consumer must not trust the message blindly if the message can be published by more than the outbox. For Harbor, only the monolith's managed identity can send to that topic. The worker checks the order exists before it mails. A message alone is not proof."},
        {"t": "code", "text": """ADR-002: Integrate after commit, through an outbox and Service Bus
Decision:
Mail and partner notifications are published from ordering.Outbox after the order transaction commits.
Consumers dedupe on event id.
Submit does not call the email provider.

Rejected:
Send mail inside the HTTP request.
Publish to the bus before commit.
Exactly-once as a broker setting.

Revisit when:
Dead-letter or lag breaks an SLO you have written, or a measured volume or replay need Service Bus cannot meet."""},
        {"t": "lead", "title": "Say this", "text": "ADR-002 says the order is true when SQL commits, and the bus is how other parts hear about it. Duplicates are normal. The dead-letter queue has an owner. I will not put Kafka on the diagram until a revisit trigger is real."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Red-team ADR-002 against my principles, threat model, and submit sequence.
Find one place I can lose an order.
Find one place I can send two emails that the business would call a defect, and whether my dedupe actually stops it.
Find one alert I named and one I forgot.
Do not rewrite the ADR. List the edits I should make."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/adr/002-outbox-and-service-bus.md.",
            "Threat model updated if the red team found a real hole.",
            "Week score. Note the weakest of: data ownership, consistency, security, Azure shape, API contract.",
        ]},
        {"t": "break"},
    ]
