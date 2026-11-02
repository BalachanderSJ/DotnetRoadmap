# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 9 — System design and the lead conversation"},
        {"t": "p", "text": "Day 9 turns the earlier days into a design you can finish in twenty minutes, and into a story that is yours. The samples below are scaffolds. They show the shape a panel can score. Replace the system, the number, and the decision with your own. A borrowed checkout story collapses on the first follow-up."},

        {"t": "h2", "text": "The design spine"},
        {"t": "p", "text": "Write this on the board in the first three minutes. It keeps you from jumping to Kubernetes, and it gives the interviewer a place to interrupt you with a better number."},
        {"t": "b", "numbered": True, "items": [
            "Clarify the user, the success metric, the scale you are assuming, and what is out of scope. State the assumption and let them correct you.",
            "Name the API: resources, verbs, sync versus async, status codes.",
            "Name the data: the aggregate, the key, the constraint, the index that matches the hot query.",
            "Name consistency: what is in one SQL transaction, what is a message, what may lag.",
            "Name failure: timeout, retry, duplicate, poison message, and what the user sees.",
            "Name operation: logs, the one dashboard, deploy and rollback, identities and SQL roles.",
            "Name the tradeoff you refused, and the first slice you would ship.",
        ]},
        {"t": "p", "text": "If they do not give numbers, assume some and say them. For this guide: about 50 requests a second at peak, about 2 million orders a year, p95 under 300 milliseconds for the read, email within a minute. Invite correction. The design changes when the number changes. A lead who designs for a million events a second without being asked overbuilds and runs out of time."},
        {"t": "h3", "text": "Example of the opening ninety seconds"},
        {"t": "code", "text": """"I am assuming a partner posts orders and retries, a customer reads an order,
and the confirmation email can finish after the response. Peak is about 50
requests a second, a couple of million orders a year, read p95 under 300
milliseconds, email inside a minute. I am not designing a million-event stream.
Tell me if those numbers are wrong.

I will keep one API on App Service, one database, and a Function for email.
I will not split a pricing service in the first slice." """},
        {"t": "lead", "title": "Say this", "text": "I state the user, the number, and the out-of-scope box before I name a product. Then I take correction. The rest of the design hangs off that number."},

        {"t": "h2", "text": "Design A — the Order API, worked"},
        {"t": "p", "text": "Prompt: design the backend for creating an order, viewing it, and emailing a confirmation. Partners retry. Two customers must not lose updates. You are the tech lead. The pieces below are Days 3, 4, 5, 6, and 7 in one design. Speak them in spine order, not as a tour of Azure."},
        {"t": "h3", "text": "API"},
        {"t": "code", "text": """POST /orders
  Header Idempotency-Key: <client guid>
  Body: sku, quantity, ship-to. Not Total. Not IsPriority. The server prices.
  201 Created, Location, body     first time
  200 with the stored body        same key, same request hash
  409                             same key, different body
  400                             validation
  401 / 403                       authn / authz
  503                             tax dependency exhausted, if tax is required

GET /orders/{id}
  200 projection, no tracking
  404 in the caller's tenant

GET /orders?cursor=&limit=
  keyset on (CreatedUtc, Id), limit capped

PATCH /orders/{id}
  If-Match or the rowversion in the body
  409 if a concurrent update won"""},
        {"t": "h3", "text": "Data and consistency"},
        {"t": "code", "text": """One SQL transaction:
  orders.Orders            rowversion column
  orders.OrderLines
  orders.IdempotencyKeys   unique (TenantId, KeyValue), stores response hash
  orders.Outbox            unpublished OrderConfirmed

Unique business key where the domain has one, such as partner reference.
Index (TenantId, CreatedUtc DESC, Id DESC) INCLUDE (Status, Total) for the list.

Outside the transaction:
  the Service Bus publish, done by the relay
  the email, done by the Function

The user does not wait on the mail provider.
Mail status is a column support can see."""},
        {"t": "h3", "text": "Failure, operation, and the slice"},
        {"t": "b", "items": [
            "Tax, if it is synchronous and required: a timeout inside the request, a small retry only because the tax call is safe to repeat, then 503. If the business would rather accept PendingTax, say that and store the state. Do not invent the policy in the interview without labeling it as a product choice.",
            "Duplicate email: the consumer dedupes on the message id. That unique key is in the first increment, not a follow-up story.",
            "Two writers: the rowversion WHERE clause changes zero rows, EF throws, the API returns 409. No blind retry.",
            "Host: App Service, slots, Always On, affinity off. Function on the isolated worker for email. Three identities: user token, API managed identity in app_orders_runtime, pipeline migrator.",
            "Dashboard: request latency, SQL duration, outbox age, dead-letter depth. Rollback is a swap, and only while the schema is still compatible.",
            "First slice: synchronous create, the outbox, and the email consumer. Pricing stays a module behind IPriceService. No pricing microservice.",
        ]},
        {"t": "p", "text": "Close with the week-one risk: a duplicate email from redelivery, which is why the message id is unique in the first ship. If they change the peak to a number that breaks one database, you revisit the read model. You do not revisit it at 50 requests a second."},
        {"t": "warn", "title": "What breaks", "text": "Accepting Total from the client lets the partner set the price. Publishing the email inside the transaction holds locks. A microservice split in the first twenty minutes spends the clock on boxes and never reaches the duplicate or the 409."},
        {"t": "lead", "title": "Say this", "text": "One transaction for the order, the idempotency row, and the outbox. Email after commit, deduped. 409 on a lost update. App Service and a Function, three identities. Pricing stays a module until a second team needs it."},

        {"t": "h2", "text": "Design B — a nightly file of a million rows, worked"},
        {"t": "p", "text": "Prompt: a partner drops a CSV in storage every night. You must validate, load, and report failures. The HTTP API must stay responsive. The mistake is to parse a million rows inside the blob trigger or on a request thread."},
        {"t": "h3", "text": "Flow"},
        {"t": "code", "text": """1. Blob created, or an Event Grid event.
   A function records the file and enqueues one control message.
   It does not parse the file.

2. A splitter reads ranges and enqueues chunk messages:
   { fileId, blobName, rowStart, rowCount }

3. Workers upsert a chunk.
   Each chunk commits with a unique (fileId, rowStart).
   A retry of the same chunk does not double-insert.
   A bad row goes to orders.FileErrors (fileId, lineNumber, reason).
   The file row moves Received -> Processing -> CompletedWithErrors or Failed.

4. The API serves status and the error page from SQL.
   It never parses the file.
   The partner can fetch an error CSV.

5. Alert if the file is not terminal by the business deadline.
   A poison chunk dead-letters without stopping the other chunks.
   The file state shows the gap."""},
        {"t": "h3", "text": "Why not EF per row"},
        {"t": "code", "text": """A million SaveChanges calls will miss the window and hold the API's database busy.
Use a staged table and a set-based merge, or a bulk copy into the stage.

INSERT into orders.FileChunks (FileId, RowStart) is the idempotency key.
The worker's managed identity can read the container and write the staging schema.
It cannot ALTER. The API's identity is not the worker's identity.

Prove chunk retry on a small file before you talk about scale.
Say the plan and the timeout as properties you would check, not as a memorized SKU."""},
        {"t": "warn", "title": "What breaks", "text": "One invocation that reads the whole file dies at the function timeout and retries from byte zero. SaveChanges per row holds locks and misses the window. A chunk retry without a range key double-inserts. A poison chunk that stops the orchestrator leaves the other 99 chunks unprocessed and the file looking idle."},
        {"t": "lead", "title": "Say this", "text": "The trigger only records the file. Workers own chunks, each chunk is idempotent, bad rows are queryable, and the API only reads status. I prove retry on a small file, and I show the error file the partner can fetch."},

        {"t": "h2", "text": "Design C — multi-tenant, if they ask"},
        {"t": "p", "text": "Default to one database. TenantId is on every tenant-owned row. A global query filter applies it. The unique index includes TenantId. The tenant id comes from the token, never from the body. The API authorizes the route, and a test proves tenant A cannot read tenant B's id. The filter is a safety net, not the only control."},
        {"t": "p", "text": "A noisy or regulated tenant can move to a separate database. The application resolves the connection by tenant. Migrations must apply to every database, which is an operational cost you name before you offer the option. You do not start with a database per tenant for hundreds of small customers. The migration and the connection story will dominate the team."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """CREATE UNIQUE INDEX UX_Orders_Tenant_Number
    ON orders.Orders (TenantId, Number);

-- Token claim "tid" = 10.
-- Body field tenantId = 11 is ignored, not trusted.
-- Test: token 10, GET /orders/{id of tenant 11} does not return the row.

Separate database, only when you can say why:
  a regulated tenant, or a tenant whose volume hurts the others.
  Cost you name first: every migration runs once per database,
  and a missed database is a drift incident."""},
        {"t": "warn", "title": "What breaks", "text": "Trusting tenant id from the body is a cross-tenant write. A unique index on Number alone collides across tenants or, worse, leaks that a number exists. A database per small tenant multiplies every operational mistake by the tenant count."},
        {"t": "lead", "title": "Say this", "text": "One database, TenantId from the token, a filter, a unique index that includes the tenant, and a test that crosses tenants. A separate database is a named exception with a migration cost, not the default."},

        {"t": "h2", "text": "How a lead story is shaped"},
        {"t": "p", "text": "Use situation, task, action, result, and a last line: what the team does now. Keep it under two minutes. I is for your decision. We is for the work the team did. Panels listen for whether you actually decided something. The three stories in the roadmap are scaffolds. Below, each one is annotated so you can hear what is doing the work. Then you throw the facts away and write yours."},

        {"t": "h3", "text": "Scaffold — production incident"},
        {"t": "p", "text": "Situation: a release went out at 11:00 and by 11:20 the order GET p95 was above four seconds. Task: you were the tech lead on call and had to choose rollback or fix-forward. Action: you checked the deploy marker against the latency chart, saw SQL dependency time jump, and swapped back within fifteen minutes because the migration had only added a nullable column. Then you looked at Query Store. A new screen was scanning Orders. The team added a covering index in a reviewed script and shipped it that afternoon. Result: latency returned to about 200 milliseconds after the swap, and the index kept the new screen. The team rule now is that a list-endpoint PR includes the filter, the index, and a sample plan, and rollback is pre-written on the release ticket."},
        {"t": "b", "items": [
            "The decision is the swap, and the minute you chose it. Without the minute, it is a war story.",
            "The number is the p95 before and after. A panel can score a number. It cannot score 'it was slow'.",
            "The safety condition is the nullable column. That is why swap-back was allowed. Say it.",
            "The lasting line is the PR rule. A lead changes the next review, not only tonight's graph.",
        ]},
        {"t": "warn", "title": "What breaks", "text": "Memorizing this checkout incident as your career fails when they ask which index and which table. Replace every fact. If you do not have a p95, use the number you did have: error count, tickets, or how long the swap took."},

        {"t": "h3", "text": "Scaffold — disagreement"},
        {"t": "p", "text": "Situation: a senior developer wanted a generic repository and a new microservice for pricing before a release. Task: you needed a data-access approach the team could review, and a date you could hit. Action: you asked what change you were protecting. You had one query shape and one team. You proposed pricing as a module behind IPriceService, and no generic repository, so the SQL stayed visible. You wrote a one-page note and asked them to own the module boundary. Result: you shipped on time, the query stayed tunable, and they kept real ownership. You would split pricing later if a second team needed to release it."},
        {"t": "b", "items": [
            "You disagreed with a person, not with 'the business'. Name the proposal.",
            "The question 'what change are we protecting?' is the technique. Use it on your own story.",
            "The relationship cost is in the story: they kept ownership. A lead who only wins the argument sounds expensive to work with.",
            "The consequence is a date you hit and a SQL statement you could still see.",
        ]},

        {"t": "h3", "text": "Scaffold — growing someone"},
        {"t": "p", "text": "Situation: a developer with two years of experience was copying controllers and calling SaveChanges from actions. Task: the next feature had to land in a shape the team could maintain. Action: you paired on one endpoint, moved the use case into a handler, and left them a checklist: cancellation token, a projection for the read, a test for the failure path, and a status code. You reviewed the rule, not the formatting. Result: they owned the returns API two months later and caught an over-posting bug in someone else's PR. The checklist is in the repo."},
        {"t": "b", "items": [
            "The action is a checklist another person can apply. Heroic pairing with no artifact does not scale.",
            "The result is what they own now, plus a bug they caught without you.",
            "I reviewed the rule. We shipped the endpoint. Keep those pronouns honest.",
        ]},
        {"t": "lead", "title": "Say this", "text": "My story has a decision, a number, and a rule the team still follows. I is the decision. The sample in the guide is the shape. The facts are mine."},

        {"t": "h2", "text": "A missed date"},
        {"t": "p", "text": "Pick a real date. Say the original commitment, the new risk you learned, and the day you told stakeholders, which should be early. Say what you cut: a report, an edge case, a non-critical admin screen. Say what you refused to cut: auth, a migration rollback, or the payment test. Say the new date you hit and the planning change, such as estimating the first slice only. Avoid a story where you worked a weekend and changed nothing about planning."},
        {"t": "h3", "text": "Example of the shape, not your career"},
        {"t": "code", "text": """Commitment: order slice in production on 12 March.
Learned on 20 February: the partner certificate path was a second audience
we had not inventoried.
Told stakeholders the same day.
Cut: the admin export.
Refused to cut: the 401 test and the route rollback rehearsal.
New date: 26 March. We hit it.
Planning change: the next slice starts with the audience list, not with code."""},
        {"t": "warn", "title": "What breaks", "text": "A story about quietly absorbing the slip is an individual-contributor story. A story that blames the stakeholder and cuts the payment test is a lead story in the wrong direction."},
        {"t": "lead", "title": "Say this", "text": "I re-planned in public, early. I cut scope that was not auth, data, or rollback. I changed how the next slice is estimated."},

        {"t": "h2", "text": "Technical debt"},
        {"t": "p", "text": "Name the debt in user or operator language: this list endpoint will time out at the next tenant's volume, or this Framework host is out of support in November 2026. Attach a cost to leave it and a cost to fix it. Put a slice of the fix in the same increment as a nearby feature when the code is already open. Spend a reserve on the item with the nearest incident, not on the rewrite you find interesting. Do not hide a migration inside an unrelated story. Also delete debt. A pattern you no longer need is a ticket with an owner."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Debt: GET /orders has no keyset and no covering index.
Cost to leave: the next large tenant pushes p95 through the 300 ms budget
and shows up as a support ticket, the way the last scan did.
Smallest fix: the index and the cursor, in the PR that is already adding
a column to that list.
Not the fix: a read-replica program, this quarter.
Owner and date go on the board. Vague passion about clean code does not."""},
        {"t": "lead", "title": "Say this", "text": "I name the incident the debt implies and the smallest fix. I attach it to work that is already open. I do not spend the reserve on the rewrite I find interesting."},

        {"t": "h2", "text": "Review without becoming the bottleneck"},
        {"t": "p", "text": "Publish the rules so people can apply them without you: cancellation, authorization, SQL shape, secrets, tests for the money path, and migration safety. Review the contract and the risk. Let the formatter own the braces. Be available at agreed times so reviews do not sit overnight. Ask the author to walk you through a design before a thousand-line PR exists. Two approvals for auth and for schema. A junior's first reviews are paired so the comments teach. If every PR waits for you, you have failed. Pick a second reviewer and a written rule that removes you from the middle."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """The comment that teaches, from the bad Create action on Day 3:

"We do not bind IsAdmin or TenantId from the body. Add a command type
that contains only sku and quantity. The tenant comes from the token.
Please apply the same split on the returns endpoint in this PR."

Not: "nit: brace on the next line." """},
        {"t": "lead", "title": "Say this", "text": "I publish the rule, I review the contract and the risk, and I make sure a second person can approve the ordinary PR. If everything waits for me, the review system has failed."},

        {"t": "h2", "text": "Disagreeing with your manager's technical direction"},
        {"t": "p", "text": "Restate their goal until they agree you understood it. Put your alternative in writing with the risk, the date, and the operational cost. Distinguish a reversible choice from a one-way door. On a reversible choice, disagree, commit, and watch the metric you named. On a one-way door, such as a shared database across a boundary you cannot undo, or a production login as db_owner, say that clearly and offer a smaller experiment. Do not relitigate in the team channel after the decision. If the decision is unsafe for customers or staff, escalate with the risk written down."},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """Goal I heard: ship the partner API this quarter.
Direction: one shared SQL login in db_owner so the new service can move faster.
That is a one-way door. The login will still be there after the quarter,
and so will every table it can drop.

Alternative: app_orders_runtime this week, migrator in the pipeline,
two extra days on the identity. I will not relitigate the choice of App Service
versus Functions for the email worker. That one is reversible. We can watch
the mail latency and move it."""},
        {"t": "warn", "title": "What breaks", "text": "Calling every disagreement a one-way door makes the phrase useless. Relitigating a reversible choice in public after you committed trains the team to ignore the decision. Staying silent on db_owner because the date is close is how the login survives for years."},
        {"t": "lead", "title": "Say this", "text": "I restate the goal, I write the risk, and I separate a reversible choice from a one-way door. I use that language once, on a real example, and then I stop."},

        {"t": "h2", "text": "Questions you ask them"},
        {"t": "p", "text": "A lead who asks about rollback, identity, and on-call sounds like they intend to live with the system. Ask two, not six, at the end of a round. Pick the two that match what you heard."},
        {"t": "b", "items": [
            "What is the first slice you would want me to lead in the first 90 days?",
            "Which systems are still on .NET Framework, and is there a funded plan before support ends?",
            "How does a change reach production, and who can roll it back at 21:00?",
            "What does on-call look like, and what woke the team up last month?",
            "Where should a tech lead spend time here: design, review, people, or still a large share of coding?",
            "How are SQL changes reviewed, and what rights does the application identity have today?",
        ]},
        {"t": "h3", "text": "Example"},
        {"t": "code", "text": """"You mentioned the Framework billing API.
Is there a funded slice onto a supported runtime, and who can roll a release
back at night if the new path mis-prices?"

Two questions. Then stop talking."""},
        {"t": "lead", "title": "Say this", "text": "I ask how a change reaches production and what the app's SQL login can do. I ask two questions, tied to something they already said."},
        {"t": "break"},
    ]
