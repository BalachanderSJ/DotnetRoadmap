# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 1 — The seat you are taking"},
        {"t": "p", "text": "Outcome: you can say what a technical architect owns, what you leave with the tech lead, and who else must agree before a decision is real. You write your positioning line in your own words and a stakeholder map for Harbor."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: this day, including the comparison table, out loud.",
            "30 min: Fundamentals of Software Architecture, the chapters on the architect's role and expectations. Stop at 30 minutes.",
            "70 min: positioning line plus the Harbor stakeholder map.",
            "30 min: speak. 30 min: AI critic. 10 min: rewrite the positioning line from memory.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A senior full-stack developer owns a change through code, tests, and a pull request. A tech lead owns that plus the team's plan: review quality, the release, mentoring, and the design of the service the team ships. A technical architect owns decisions that more than one team will live with for a year or more: where the boundaries are, who owns the data, how identity works, which qualities you will actually pay for, and which standards are written down. You still read code. You stop being the fastest person to take every story."},
        {"t": "p", "text": "A solution architect, especially in a services firm, spends more of the week in a workshop and a written proposal: scope, integrations, assumptions, risks, and a shape the client can fund. The engineering underneath is the same. If you cannot explain the failure mode, you are writing a brochure. An enterprise architect sets principles across many products and rarely designs one accept path. That is a later career, not day 30."},
        {"t": "p", "text": "Decision rights are the part people skip. You recommend. You do not secretly own the budget, the residual security risk, or the business priority. For Harbor, a typical split is: you recommend modular monolith over microservices; the engineering manager accepts the staffing consequence; security accepts the residual risk of one database; the product owner accepts that email is not in the 400 millisecond budget. Write the names of the roles even if you do not yet have the people. A decision with no owner is a slide."},
        {"t": "p", "text": "Influence without authority is the job on the weeks you do not manage the team. You earn it with a short document, a real alternative, and time in the other team's problem. You lose it by announcing a target architecture in week one, by reviewing style instead of boundaries, and by using AI output you cannot explain."},
        {"t": "table", "headers": ["Situation", "Tech lead does", "Technical architect does"], "rows": [
            ["A module wants a new NuGet package", "Reviews the license and the call site in the PR", "Writes nothing, unless the package sets a platform standard"],
            ["Two squads both want to write orders", "Runs the design conversation", "Names the single writer and records the decision"],
            ["Production is down", "Leads the incident for their service", "Joins if the boundary or the data owner is the cause. Does not take the keyboard by rank."],
            ["A director asks for a rewrite", "Estimates the team's slice", "Says which slice, which risk, and what will not be rewritten"],
        ]},
        {"t": "h2", "text": "Stakeholder map for Harbor"},
        {"t": "p", "text": "List eight roles and one sentence each: what they need from the architecture, and what they can veto. Buyer admin, warehouse lead, product owner, two squad leads, security, the person who pays the Azure bill, and the reporting analyst who already runs SQL against something. That last person is how modernization projects die. Put them on the map on day 1, not as a surprise on day 23."},
        {"t": "lead", "title": "Say this", "text": "I recommend the shape and I record the tradeoff. The budget owner accepts cost, security accepts residual risk, and the tech lead owns the team's release. If I cannot name those people, the decision is not made yet."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my positioning line and my Harbor stakeholder map.
Attack them.
Tell me where I still sound like the person who will implement every story myself.
Tell me which stakeholder can veto a decision, and which line I wrote that pretends they cannot.
Do not improve my tone. Improve the decision rights."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "Positioning line, six lines or fewer, in docs/reviews/positioning.md.",
            "Stakeholder map with vetoes.",
            "Three sentences: work you will stop doing in the first month of the role so the tech leads still own delivery.",
        ]},
        {"t": "qa", "q": "What is the difference between a tech lead and a technical architect?", "a": "The tech lead owns one team's delivery: design of their service, review, release, and people. The technical architect owns decisions that cross teams or last long enough to be expensive to undo: boundaries, data ownership, identity, quality attributes, and written standards. I still read code. I do not take every story.", "lead": "On Harbor I would let the squad lead own the Orders module release. I would own the decision that Ordering is the only writer of an order, and I would write that down."},
        {"t": "break"},

        {"t": "h1", "text": "Day 2 — Quality attributes you can test"},
        {"t": "p", "text": "Outcome: you can turn 'fast, secure, and scalable' into three scenarios a team could accept or reject. You can say what you are giving up."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: scenarios and tradeoffs below.",
            "30 min: Richards and Ford on architecture characteristics. Or Microsoft's Well-Architected overview if the book is not here.",
            "70 min: write three Harbor scenarios in the template.",
            "30 min speak, 30 min AI, 10 min redraw one scenario from memory.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A quality attribute is a property the system must have, expressed so you can argue about it. 'Scalable' is not one. A scenario is. The form used at the Software Engineering Institute is: source, stimulus, artifact, environment, response, response measure. You do not need the jargon in the room. You do need all six parts on the page."},
        {"t": "p", "text": "Source: who or what starts it. Stimulus: the event. Artifact: the part of the system that must respond. Environment: normal load, peak, or already failing. Response: what the system does. Response measure: a number, a window, and how you would observe it."},
        {"t": "p", "text": "Harbor accept-path example. Source: a buyer user. Stimulus: submits an order. Artifact: the Ordering module. Environment: peak, about 40 submits a second, assumption. Response: the order and its outbox row are committed, and the API returns the order id. Response measure: p95 under 400 milliseconds over a calendar month, excluding the payment provider's time if payment is asynchronous. If you include the provider, say so, and do not promise 400 milliseconds for their outage."},
        {"t": "p", "text": "Percentiles matter. An average of 200 milliseconds can hide a p95 of two seconds. Availability is a different promise from latency. 99.9 percent of a 30-day month is about 43 minutes of unavailability. 99.99 percent is about 4 minutes. Do not offer 99.99 percent for Harbor in one region with one database. You have not paid for it."},
        {"t": "p", "text": "Tradeoffs you should be able to say without a slide. Consistency against availability: if Azure SQL is down, Harbor rejects the submit. You do not accept orders you cannot store. Latency against freshness: the catalog page may be a few minutes old; the stock check on submit may not. Coupling against duplication: a read model copies order status into a search store; that copy can be stale. Cost against resilience: a second region doubles a class of bill and forces a data story you do not have yet. Speed of change against uniformity: two squads in one deployable wait for each other sometimes; two deployables without a platform team wait for incidents instead."},
        {"t": "p", "text": "A fitness function is an automated check that an architectural choice still holds. Examples you can actually build later this month: a test that the Catalog project does not reference Ordering infrastructure; a unique index on the idempotency key; an accessibility scan on the order route; a pipeline check that fails a new public HTTP client with no timeout. A fitness function without a decision is just a test. Day 18 comes back to this. Today, name two you would want for Harbor."},
        {"t": "p", "text": "ISO/IEC 25010 lists qualities such as reliability, security, performance efficiency, maintainability, and compatibility. Use it as a checklist so you notice the one you ignored. Do not recite the standard in the interview. Speak the scenario."},
        {"t": "h2", "text": "Template"},
        {"t": "code", "text": """Quality:
Source:
Stimulus:
Artifact:
Environment:
Response:
Response measure (number, window, how observed):
Assumption or measurement:
What we give up to get this:
Revisit when:"""},
        {"t": "lead", "title": "Say this", "text": "Fast is not a requirement. For Harbor, the buyer submit at peak commits the order and returns in under 400 milliseconds at p95. That number is an assumption until we measure it. Mail is outside that budget. If SQL is down we fail the submit, because we will not take an order we cannot store."},
        {"t": "warn", "title": "Interview trap", "text": "Listing twelve qualities with no priority. An architect ranks them for this system. Harbor ranks integrity of the order and tenant isolation above a beautiful catalog animation. Say the rank."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here are three quality attribute scenarios for Harbor.
For each one, tell me if the response measure can be observed, or if I used a vague word.
Point at the measure that fights another measure.
Do not add new Azure services. Do not invent a benchmark."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "Scenario: latency of order submit.",
            "Scenario: a buyer must not read another company's order.",
            "Scenario: a Catalog change ships without an Ordering code change. Say what 'without' means for a modular monolith (no Ordering pull request, not a separate deployable).",
        ]},
        {"t": "qa", "q": "How do you handle non-functional requirements?", "a": "I write them as scenarios: who triggers what, against which part of the system, under which conditions, with a response and a measure. I rank them for this product. I label numbers as assumptions until we have a measurement. I name the quality we are spending less on so the tradeoff is visible.", "lead": "On Harbor, durability of the order beats a second region. I would rather fail a submit than accept an order we cannot store."},
        {"t": "break"},

        {"t": "h1", "text": "Day 3 — Draw the system at the right altitude"},
        {"t": "p", "text": "Outcome: you can draw Harbor's context and containers in one sitting, and you can say which diagram you refused to draw."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "60 min: C4 levels below.",
            "30 min: c4model.com, the levels page only.",
            "90 min: draw context and containers on paper, then write them in markdown.",
            "30 min speak, 30 min AI, 10 min redraw containers with the laptop closed.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The C4 model, from Simon Brown, is four levels of zoom. Context: Harbor and the people and systems outside it. Container: the applications and data stores that run, in the Docker sense of a container only by coincidence. A container here is the Angular app, the BFF, the database, the bus. Component: the major parts inside one container, drawn only when you are discussing that container. Code: classes, which do not belong in an architecture review unless someone asks how a specific module is shaped."},
        {"t": "p", "text": "A diagram that does not change a decision is decoration. Every box needs a responsibility you can say in one sentence. Every arrow needs a protocol or a 'why'. If two boxes always deploy together and fail together, they are probably one box at container level."},
        {"t": "p", "text": "Harbor context, in sentences. Buyers use Harbor to place wholesale orders. Ops staff use Harbor to manage credit and exceptions. Harbor uses Microsoft Entra to authenticate both, in two different directories or configurations. Harbor uses a payment provider to authorize payment and does not store card numbers. Harbor sends mail through an email provider. A reporting analyst is a person, not a system, until they have a warehouse. If they query SQL directly, draw that arrow and label it 'legacy, painful, explicit'."},
        {"t": "p", "text": "Harbor containers, the default you will attack on later days. Buyer Angular app. Ops Angular app, or a second area if day 19 says so. BFF, ASP.NET Core, the only thing the browser calls. Harbor API, the modular monolith. Azure SQL. Azure Service Bus. Notification worker on Functions. Key Vault. The telemetry sink, named as Azure Monitor or Application Insights, not as 'logging'. Entra sits outside, already on the context diagram. Do not draw a Kubernetes cluster. You have not earned it."},
        {"t": "code", "text": """Buyer ---- HTTPS ----> Buyer Angular ---- HTTPS/cookie ----> BFF
Ops user ---- HTTPS ----> Ops Angular ---- HTTPS/cookie ----> BFF
BFF ---- HTTPS + app identity ----> Harbor modular monolith
Harbor monolith ---- TDS/managed identity ----> Azure SQL
Harbor monolith ---- Service Bus ----> Notification worker ----> Email provider
Harbor monolith ---- HTTPS ----> Payment provider
Buyer and ops ---- OIDC ----> Entra (two audiences)"""},
        {"t": "p", "text": "arc42 is a fuller template: goals, constraints, context, solution strategy, building blocks, runtime view, deployment view, crosscutting concepts, decisions, quality, risks, glossary. For Harbor you will fill a short form of goals, constraints, context, building blocks, a runtime view of submit order, decisions, quality scenarios, and risks. You will not write a 40-page arc42 this month. Bloated documentation is a risk. So is a diagram with no decisions next to it."},
        {"t": "lead", "title": "Say this", "text": "Context shows who is outside Harbor and what we refuse to store, which includes card numbers. Containers show the Angular apps, the BFF, one modular monolith, SQL, Service Bus, and a worker. I will draw components only for the accept path, and I will not draw classes in a review."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my Harbor context list and container list.
Which box has no responsibility I could say out loud?
Which arrow has no reason to be synchronous?
Where did I draw a technology instead of a container responsibility?
Do not add services I did not list."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/context.md with actors, external systems, and one sentence on what Harbor will not do.",
            "docs/c4/containers.md with the boxes and arrows above, edited to match your wording.",
            "A note of the first component diagram you will need: submit order only.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 4 — Write a decision someone can revisit"},
        {"t": "p", "text": "Outcome: you can write an architecture decision record that a squad lead can follow without you in the room. You finish ADR-001: Harbor stays a modular monolith for this stage."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "50 min: the ADR rules below.",
            "30 min: Nygard's ADR article or adr.github.io, the template only.",
            "100 min: write ADR-001 yourself. The sample further down is a reference, not your file. Write yours first, then compare.",
            "30 min speak, 30 min AI, 10 min restate the decision and the revisit trigger with the page turned over.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "An architecture decision record is a short document with a status, a context, a decision, and consequences. Michael Nygard described that shape. The point is not the headings. The point is that the next person can see what you chose, what you refused, and what would make the choice obsolete. A wiki page titled 'Architecture' that is edited forever is not a decision. A decision has a date and a status: proposed, accepted, superseded."},
        {"t": "p", "text": "Write options as real alternatives, including the one you reject. 'Microservices versus monolith' is too coarse. For Harbor the options are: one modular monolith with module boundaries enforced in code; a handful of independently deployed services on day one; a monolith with no internal boundaries. The third option is how you get a rewrite in two years. The second option is how a team of ten spends the half on pipelines, distributed debugging, and data that no longer shares a transaction."},
        {"t": "p", "text": "Consequences are both good and bad. Good: one deployable, one database transaction for an order and its outbox, simpler local development. Bad: a faulty Catalog change can still take down Ordering if you share a process. You mitigate that with module boundaries, tests, and a separate worker for mail, not with a speech about discipline. Also bad: you cannot scale the catalog read path by giving it its own replica count. You accept that until measurement says the accept path or the catalog is the saturated part."},
        {"t": "p", "text": "A revisit trigger is mandatory. Examples: a module must be owned by a team that cannot share the release train; a measured hotspot needs independent scale; a compliance boundary forbids shared hosting; the process fails its SLO because of a neighbor module and isolation inside the process is not enough. 'When we feel ready' is not a trigger."},
        {"t": "h2", "text": "Reference ADR, read only after you draft yours"},
        {"t": "code", "text": """ADR-001: Harbor ships as a modular monolith
Status: Accepted
Date: (today)

Context:
Two squads, about 8 to 12 engineers, one product, one Azure region.
Peak submit is assumed at about 40 requests a second.
Ordering and the outbox row must commit together.
We have no platform team that runs Kubernetes.

Decision:
One ASP.NET Core deployable with modules Catalog, Ordering, and Billing.
Each module owns its schema. Code may not query another module's tables.
Mail leaves the process through Service Bus to a Functions worker.
We do not create independently deployed business services yet.

Options rejected:
Separate services for Catalog, Ordering, and Billing now.
A single project with no module boundaries.

Consequences:
We keep a local transaction for the order and the outbox.
A bad deploy can still couple the modules at runtime.
Catalog cannot scale on its own until we split it on purpose.

Revisit when:
A squad must release on a different cadence, or a measured resource limit sits inside one module and cannot be fixed in-process."""},
        {"t": "lead", "title": "Say this", "text": "I chose a modular monolith for Harbor because the team is still one release conversation and the order needs a local transaction. I rejected microservices until a module has a different cadence, a different scale problem we measured, or a compliance boundary. The cost is that one bad deploy can affect the whole API. The worker for mail is already separate because it fails differently."},
        {"t": "warn", "title": "Interview trap", "text": "Calling it a monolith as an apology, or calling it microservices because there are three class libraries. Deployment independence and data ownership are the test. A class library is not a service."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Review ADR-001, which I wrote myself.
Quote the revisit trigger. If it is vague, say so.
Name a consequence I treated as only positive.
Give me the strongest case for splitting Ordering out now, then say whether my constraints defeat that case.
Do not rewrite the ADR."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/adr/001-modular-monolith.md in your words.",
            "Status, context, decision, options rejected, consequences, revisit trigger.",
            "One sentence a director can read, copied into the top of the file.",
        ]},
        {"t": "qa", "q": "Monolith or microservices?", "a": "For Harbor, a modular monolith. The team is small enough to share a release, and the order plus the outbox need one transaction. Microservices would add network failures and data split before we have a platform team or a measured hotspot. I would split a module out when its cadence, scale, or compliance boundary is actually different. Mail is already a separate worker because its failure domain is different.", "lead": "I would enforce the modules with a test that forbids cross-schema reads, not with a meeting."},
        {"t": "break"},

        {"t": "h1", "text": "Day 5 — Boundaries, language, and the teams who own them"},
        {"t": "p", "text": "Outcome: you can name Harbor's bounded contexts, who is allowed to write each piece of data, and which team shape matches ADR-001."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: contexts and team types below.",
            "40 min: Team Topologies, the four team types and the interaction modes. Skip the rest today.",
            "70 min: a one-page context map.",
            "30 min speak, 30 min AI, 10 min redraw the map.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A bounded context is a boundary inside which a word means one thing and a model is consistent. In Harbor, 'order' in Ordering means the commercial commitment: buyer, lines, price as copied at submit time, status. 'Order' in the warehouse's language might mean a pick list. If you use one class for both, you will leak warehouse fields into the buyer API. Catalog owns products and list prices. Ordering owns the order, copying the price at submit so a later catalog edit does not rewrite history. Billing owns invoices and credit. Notification owns delivery of messages, not the business fact that an order exists. Identity owns who the user is; it does not own what the user may do to an order. That authorization rule lives next to the order."},
        {"t": "p", "text": "A context map describes the relationship between contexts. Shared kernel: a tiny model both sides change together. Dangerous if it grows. Customer-supplier: Ordering needs something from Catalog and can ask for a change. Conformist: you take an external model as-is, which is how you should treat the payment provider. Anti-corruption layer: a translation at the edge so the provider's names never enter your domain. Harbor's payment adapter is that layer. Published language: the message schema on Service Bus."},
        {"t": "p", "text": "Conway's law is the observation that the system copies the communication structure of the organization. Use it as a design input, not a joke. If you create four services and one team, you have given one team four operational surfaces. If you create two squads and forbid them to speak, a modular monolith will still rot at the boundary. Team Topologies gives you four team types. Stream-aligned teams own a flow of work, here the buyer journey and the ops journey, or one team per journey if you split later. A platform team provides a paved path: pipeline, observability, a service template. An enabling team teaches a skill, such as threat modeling, and then leaves. A complicated-subsystem team owns a rare specialty. Harbor does not have that problem yet. Do not invent a platform department for twelve people. A thin shared pipeline owned by a rotating pair is the honest platform."},
        {"t": "p", "text": "Interaction modes: collaboration is two teams working together for a defined period, expensive and sometimes necessary at a new boundary. X-as-a-service is a clear API with a small waiting time. Facilitating is the enabling team. Harbor's two squads collaborate on the monolith's boundary rules, then treat modules as an internal contract. They are not two companies."},
        {"t": "p", "text": "Cognitive load is the reason you still draw boundaries inside one deployable. A person should be able to change Catalog without holding the Ordering state machine in their head. The Angular app mirrors this. Feature areas or libraries follow the same words: catalog, ordering, billing. A shared UI kit is not a bounded context. It is a dependency with a different rule: visual consistency, no business decisions inside a button."},
        {"t": "lead", "title": "Say this", "text": "Catalog owns the product and the list price. Ordering copies the price onto the order at submit and is the only writer of order status. The payment provider's model stops at an anti-corruption layer. Two squads share one deployable until a revisit trigger in ADR-001 fires. I will not create a platform team to look mature."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my Harbor context map: contexts, who writes which data, and the team shape.
Find a word I used to mean two things.
Find data with two writers.
Tell me if my team shape contradicts ADR-001.
Do not propose a new vendor."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "One page: Catalog, Ordering, Billing, Notification, Identity. Writer, data, and what is copied rather than shared.",
            "Mark the payment adapter as anti-corruption.",
            "One paragraph on team shape that matches ADR-001.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 6 — The shape of Angular in front of .NET"},
        {"t": "p", "text": "Outcome: you can walk the path from a button click to a committed order, and you can say where the token is allowed to live."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "80 min: BFF, cookies, and PKCE below. Sketch the sequence on paper.",
            "30 min: Microsoft identity docs, authorization code flow with PKCE, skim only.",
            "70 min: write the runtime view of submit order in docs/c4/submit-order.md.",
            "30 min speak, 30 min AI, 10 min redraw the sequence.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The browser is an untrusted client. Anything you ship in JavaScript can be read by a script that should not be there, and anything the buyer posts can be rewritten. Prices, roles, and tenant ids in the request body are hints at most. The server recomputes the price from Catalog data, takes the tenant from the authenticated session, and ignores a client-supplied role."},
        {"t": "p", "text": "For a first-party Angular app, the default architecture in this plan is a backend for frontend. The Angular app calls only the BFF, same site. The BFF runs the OpenID Connect authorization code flow with PKCE against Entra, keeps the tokens on the server, and gives the browser an HttpOnly, Secure, SameSite cookie. The Angular app does not see the access token, so it cannot put one in localStorage. That removes a common theft path. The cost is a BFF you must operate, and you must handle CSRF because the browser will send the cookie."},
        {"t": "p", "text": "CSRF: SameSite=Lax or Strict stops many cross-site posts. For cookie-authenticated writes, also use an anti-forgery token. CORS is not your authorization model. CORS decides which browser origins may read a response. A non-browser client ignores it. Do not describe CORS as 'locking the API'."},
        {"t": "p", "text": "The pure SPA alternative is still valid: authorization code plus PKCE in the browser, tokens in memory, refresh done carefully, nothing in localStorage. Use it when a BFF is truly unjustified, for example a temporary app or a host that cannot run the cookie site. Say the threat you accepted: any XSS can act as the user while the token is in memory, and a mistake in storage becomes a lasting theft. The BFF moves that bar to the cookie and the BFF's own session store."},
        {"t": "p", "text": "Downstream, prefer the BFF or the monolith to reach Azure SQL and Service Bus with managed identity. Do not forward the user's raw token to every internal API by habit. The on-behalf-of flow exists when a downstream API must independently see the user and enforce its own delegated permission. It is more moving parts. For Harbor, the monolith enforces authorization itself using the user id, the tenant, and the roles the BFF established. Internal calls use the app's identity. Revisit on-behalf-of when a downstream team refuses to trust the monolith."},
        {"t": "p", "text": "Buyer identity and staff identity are different trust zones. Staff live in the workforce tenant. Buyers, for a new build, live in Entra External ID. Do not mix them in one Angular app with a boolean. Two app registrations, two audiences, and the ops app is not deployed to the public buyer host if you can avoid it. A buyer token must fail on ops endpoints even if someone copies the URL."},
        {"t": "p", "text": "The BFF is not a place to hide business rules. It authenticates, applies a few client-specific shapes, and calls the monolith. If price calculation starts living in the BFF, you have two Ordering models. Aggregation of a read screen is fair. A decision about whether an order is valid is not."},
        {"t": "code", "text": """Sequence: submit order
1. Angular POSTs /api/orders with the cookie and an Idempotency-Key.
   Body has sku and quantity. It does not have a price the server trusts.
2. BFF authenticates the cookie, rejects a missing anti-forgery token, calls Harbor.
3. Ordering loads the buyer tenant from the session, loads prices from Catalog's public method or a copied price list, rejects a tampered tenant.
4. Ordering inserts the order and the outbox row in one SQL transaction.
5. API returns 201 and the order id.
6. A relay publishes the outbox row to Service Bus.
7. The worker sends mail. The user is not waiting on step 7."""},
        {"t": "p", "text": "A thin code sketch is enough if you want your hands in the tools today. Cookie authentication plus the OpenID Connect handler in ASP.NET Core, and an Angular app that calls a relative /api URL with credentials included and has no token interceptor. If the sketch grows past an hour, stop. The sequence above is the day's real output."},
        {"t": "lead", "title": "Say this", "text": "The Angular app talks only to a BFF. Tokens stay on the server. The browser gets an HttpOnly cookie, and writes carry an anti-forgery token. The server ignores any price or tenant id in the body. Mail is after the commit. I would put tokens in the SPA only if I had rejected the BFF on purpose and accepted the XSS exposure."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my submit-order sequence.
Where could a malicious buyer change the price or the tenant?
Where is the token, exactly?
What happens if the process dies after the SQL commit and before the message is published?
Do not add an API gateway unless you can show why the BFF is not enough."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/c4/submit-order.md, the sequence in your words.",
            "A short note: token location, cookie flags, what the client is not allowed to decide.",
            "One rejected option: access token in localStorage, and the sentence that says why.",
        ]},
        {"t": "qa", "q": "Where do you store the token in an Angular app?", "a": "For Harbor I do not store it in the Angular app. The BFF holds the tokens and the browser holds an HttpOnly Secure cookie. localStorage is readable by any script on the page, so I will not put a bearer token there. If we had no BFF, I would keep the token in memory and say out loud that XSS can still act as the user until the page closes.", "lead": "Authorization still happens on the server. The UI hiding a button is not a control."},
        {"t": "break"},

        {"t": "h1", "text": "Day 7 — Principles, then a hostile read"},
        {"t": "p", "text": "Outcome: a one-page principles document that ADR-001 and the submit path already obey. You can spot a sentence that is only a slogan."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "40 min: read the principle rules below.",
            "80 min: write eight principles or fewer, each with a consequence.",
            "40 min: check ADR-001 and the submit sequence against them. Fix either the principle or the decision.",
            "40 min: speak a five-minute briefing: who Harbor is, the decision, the quality you ranked first.",
            "30 min: AI critic on the principles. 10 min: recite them without the page.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A principle is a rule you are willing to enforce. 'We build quality in' is not a principle. 'The browser is untrusted; prices and tenant ids are taken from the server session and the database' is a principle, because a pull request can violate it and a reviewer can point at the sentence. Each principle needs a consequence that can hurt. If there is no case where the principle makes you slower, it is a poster."},
        {"t": "p", "text": "Start from these eight, then rewrite them until they sound like you. One owner per data set. The browser is an untrusted client. A synchronous call has a timeout. A message may be delivered more than once, so the consumer is idempotent. Prefer a module boundary before a network boundary. An accepted decision names a revisit trigger. We measure a promise we make about latency or availability. Standards are written, and an exception is an ADR, not a hallway agreement."},
        {"t": "p", "text": "Add a non-principle list so you do not pretend taste is architecture. Formatting, folder names inside a feature, and whether a component is signals or a local observable are team conventions. They can be written. They are not why you were hired as an architect, unless they break a boundary."},
        {"t": "p", "text": "The week review is a spoken briefing, five to ten minutes. Shape: who the users are; the container picture; ADR-001 in four sentences; the accept-path measure; the threat you designed against; what would make you reopen the decision. Record yourself on the phone. If you hear 'basically' and 'just', cut those sentences and say the tradeoff again."},
        {"t": "lead", "title": "Say this", "text": "Our principles are short because we intend to enforce them. The one I will argue hardest this month is a single writer per data set, and the one that will slow us down is the timeout on every synchronous call, including the ones that 'usually return quickly'."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here are my principles, ADR-001, and the submit-order sequence.
List contradictions.
List principles that cannot be violated in a pull request because they are too vague to enforce.
Do not add principles to make the list look complete."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/principles.md, one page.",
            "A five-minute recording, deleted after you note three sentences you will change.",
            "A score of the week using the front-matter rubric. Write the weakest artifact. Day 29 will thank you.",
        ]},
        {"t": "break"},
    ]
