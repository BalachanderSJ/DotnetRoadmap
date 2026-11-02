# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 22 — Case: design Harbor from a blank page"},
        {"t": "p", "text": "Outcome: in 90 minutes on paper you can produce a design another architect can attack. You do this before you reread your own documents."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "15 min: read only the brief below. Do not open your docs.",
            "90 min: paper. Context, containers, data owners, accept path, one failure. No laptop.",
            "40 min: compare with your week 1 and week 2 docs. Note what you forgot, not what you would add.",
            "30 min: speak the design.",
            "30 min: AI as a hostile reviewer of the paper, typed in after.",
            "15 min: one-page writeup in docs/reviews/case-harbor.md.",
        ]},
        {"t": "h2", "text": "The brief"},
        {"t": "p", "text": "Harbor Wholesale wants a portal. About 2,000 buyer companies, about 15,000 users, a peak you may assume at about 40 order submits a second. Eight to twelve engineers, two squads. One Azure region. Card data stays at a payment provider. Buyers and staff must not share one identity pile. Ops staff release credit holds. Confirmation mail can be a minute late. Reporting today is a person with SQL scripts, and they will exist on day one of the new system only as a stakeholder you must not surprise. The business wants 'microservices and Angular' in the first sentence of the proposal. You may tell them no."},
        {"t": "h2", "text": "What a strong paper includes"},
        {"t": "b", "items": [
            "Actors and the two identity zones.",
            "Containers you can operate, and a short reject list: no AKS, no token in the browser, no shared database with the warehouse.",
            "Ordering as the only writer, price copied at submit, outbox in the same transaction.",
            "The SLO as an assumption, with the 43 minute translation if you offered three nines.",
            "One failure: SQL down rejects the submit; mail down does not. Or payment timeout is not retried.",
            "The sentence you would say to the person who asked for microservices.",
        ]},
        {"t": "p", "text": "A weak paper lists Azure products, draws five services because the brief said microservices, and never says what happens when the bus is down. If that is what you drew, that is the finding. Write it at the top of the notes. Do not quietly correct the paper and pretend the first hour went well."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """You are a principal engineer reviewing a hiring exercise.
Here is my paper design for Harbor, transcribed.
Ask me six follow-up questions, one at a time is not required, all six now.
At least two questions must attack data ownership, identity, or failure.
Then score decision, tradeoff, and operability from 0 to 2 each, with one sentence of evidence.
Do not redesign it for me."""},
        {"t": "lead", "title": "Say this", "text": "I drew a modular monolith, a BFF, and a separate mail worker. I rejected a microservice per module because the team is twelve people and the order needs a local transaction. The design is operable in one region, and I said what the buyer sees when SQL is down."},
        {"t": "break"},

        {"t": "h1", "text": "Day 23 — Case: the legacy system and the person who funds it"},
        {"t": "p", "text": "Outcome: a one-page modernization plan a director can fund, including what you will not rewrite this half."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "20 min: the brief only.",
            "80 min: the plan on paper, then typed.",
            "40 min: a spoken version in four minutes for a non-engineer.",
            "40 min: compare with day 18 and fix the plan, not the story you wish you had.",
            "30 min: AI critic. 10 min: recite the rollback.",
        ]},
        {"t": "h2", "text": "The brief"},
        {"t": "p", "text": "The current Harbor is ASP.NET on .NET Framework, plus an Angular app several majors behind, on one SQL Server database. A reporting analyst runs weekly scripts against dbo. Orders, invoices, and catalog live in the same tables the UI writes. Revenue cannot stop. You have one team of eight and two quarters, not a blank check. A director has asked for a rewrite on .NET 10 and the current Angular, 'so we are future-proof', and wants a date when the old system is off."},
        {"t": "h2", "text": "Study material: the plan that gets funded"},
        {"t": "p", "text": "Lead with the risk they already feel, not with the framework version. Orders are hard to change because the UI, the reports, and another team's extracts share one set of tables. The rewrite pays for itself only if a slice of order-taking becomes safe to change. Future-proof is not a date."},
        {"t": "p", "text": "Scope of the first half: new buyer submit on the new stack, one writer of those orders, old system still does invoices and the rest. Reporting gets a view or a copy with a named owner and a date, because their scripts are a production dependency. Schema change is expand and contract. The route back to the old submit stays until the new path has lived through a peak week. The flag expires at the end of the second quarter, at which point you either cut over or you write a new ADR. The old runtime does not get a fantasy shutdown date in month one. It gets a condition: no remaining writer, reports moved, rollback no longer required."},
        {"t": "p", "text": "Cost language a director can use: one team, no second product, no Kubernetes, a thin slice, a rollback. The thing you need from them is cover when someone asks why invoices are still old, and an introduction to the person who owns the reporting scripts. The thing you will not do is freeze features for six months to rebuild the catalog."},
        {"t": "lead", "title": "Say this", "text": "I can put new buyer orders on .NET 10 and a current Angular app in two quarters without stopping revenue. Invoices stay on the old system on purpose. We keep a way back until a peak week goes well. I need the reporting scripts treated as a consumer with a date. I will not give you a shutdown date for the whole legacy estate until nothing important writes to it."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Read this as a director who wants a shutdown date and hates risk.
Where is the date I asked for, and did the architect replace it with a condition I can understand?
What still takes revenue down if it fails?
What am I being asked to decide, in one sentence?
Point at jargon I would not repeat to my board."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/case-legacy.md, one page, no framework lecture.",
            "The condition that replaces the shutdown date.",
            "The ask of the director, two sentences.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 24 — Case: mail, audit, and search are not one database"},
        {"t": "p", "text": "Outcome: you can separate three needs that teams often smash into SQL Server or into 'the logs'."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "30 min: the brief.",
            "90 min: three stores, three writers, three failure modes.",
            "40 min: speak it.",
            "40 min: AI critic.",
            "20 min: write docs/reviews/case-mail-audit-search.md.",
        ]},
        {"t": "h2", "text": "The brief"},
        {"t": "p", "text": "After submit, Harbor must email the buyer, keep an audit that can answer 'who accepted this order' six years from now, and let ops search last year's orders by company name and sku. A teammate proposes: write it all to the application log, and add three more indexes to the orders table for search. Another proposes event sourcing the entire order history because they read a blog. You have Azure SQL, Service Bus, and the option of a search index if you can justify it."},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Mail is a notification. It can fail, it can be retried, it can be late. It is the outbox and the worker you already designed. It is not the source of truth. If the mail says Accepted and the database says Rejected, the database wins, and you have a bug in the worker to fix."},
        {"t": "p", "text": "Audit is a business record. It answers who did what to which order, when, from which tenant. It must survive a log-retention policy that deletes debug logs after 30 days. Store it on purpose: a table Ordering appends to in the same transaction as the state change, or a dedicated audit store with a retention rule the business signed. Six years is a business requirement. Write it down and ask legal or the director if you invented the number. Do not invent six years in the interview if they did not say it. The brief said six. In real life you ask. The audit row is not an application insight log. Different access control, different retention, different reason."},
        {"t": "p", "text": "Search is a read model. The orders table serves the transaction: get by id, enforce uniqueness, keep the state machine honest. Searching a year of text across company name and sku with a pile of indexes will fight the writes. A copy, filled from the outbox, can sit in a search index or in a table shaped for the query. It can be seconds or minutes behind. Ops must see a 'as of' time, or they will argue with a buyer about a phantom status. The search store is not a writer of the order. If someone 'fixes' a row only in search, the next event will overwrite it, or worse, you now have two writers."},
        {"t": "p", "text": "Event sourcing replaces the order row with a fold of every event. It is justified when you truly need to reconstruct past states as a product feature and you accept the operational cost. Harbor needs the current state, an audit trail, and a search copy. That is an order row plus an audit append plus a projection. Selling full event sourcing here is a different system. Say no, and say what you would revisit: a requirement to answer arbitrary historical questions that an audit table cannot, measured, not imagined."},
        {"t": "table", "headers": ["Need", "Store", "If it is down or stale"], "rows": [
            ["Truth of the order", "ordering.Orders", "Submit fails. We do not accept what we cannot store."],
            ["Who did it", "Audit table, long retention, same transaction as the change", "The state change should fail too, if you required them in one transaction. Do not rely on logs."],
            ["Find last year's orders", "Read model fed by the outbox", "Search is stale or unavailable. The buyer can still open a known order id. Show the lag."],
            ["Email", "Worker and the provider", "Order stands. Alert on the dead letter. Do not roll back the order because mail failed."],
        ]},
        {"t": "lead", "title": "Say this", "text": "The order row is the truth, the audit row is the legal memory, the search index is a copy that may lag, and the log is for diagnosis. I will not search by adding every reporting index to the transactional table, and I will not event-source the order because we need an audit."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my split of mail, audit, and search.
Where did I still use the log as a system of record?
Can the audit row commit if the order rolls back? It must not.
What does ops see if search is ten minutes behind?
Is event sourcing actually required? If I included it, attack it."""},
        {"t": "break"},

        {"t": "h1", "text": "Day 25 — Write the decision for someone who will not read the ADR"},
        {"t": "p", "text": "Outcome: a one-page memo that recommends staying a modular monolith this half, in language a director can repeat."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "30 min: read the sample structure, not to copy the sentences.",
            "80 min: write the memo from your ADR-001.",
            "40 min: read it aloud. Cut adjectives.",
            "40 min: AI plays the director.",
            "30 min: a second memo, half a page, on a decision from your real career, with names removed.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "A director memo has five parts. The decision in two sentences. The problem that made it necessary. The options, including the one they hope you will pick. The consequence in cost, risk, and calendar, without a fake precision. The ask: what you need them to say yes to. Put the ask at the top or the bottom, not in the middle of a diagram."},
        {"t": "p", "text": "Sample shape, compress and replace. 'Decision: Harbor stays one application with hard module boundaries this half. We will not split Catalog, Ordering, and Billing into separately deployed services. Problem: we have two squads and one database transaction that must stay intact, and we have no team whose job is a cluster. Options: split now, stay one deployable with enforced modules, or keep one project with no boundaries. Splitting now spends the half on pipelines and partial failures instead of on the buyer journey. No boundaries means the next rewrite is already scheduled. Consequence: a bad release can still affect the whole API, and we cannot scale one module by itself. We accept that until a measurement or a team split says otherwise. Ask: agree that microservices is not a success metric for this half, and that a module split needs a new decision when a trigger fires.'"},
        {"t": "p", "text": "Disagreement is part of the job. You do not win by a longer document. You restate their goal, you show the cost of their option, and you offer the trigger that would make you join them. If they overrule you, you record the decision, the risk you named, and who accepted it. You do not sabotage the split after the fact, and you do not pretend it was your idea. An overruled architect who keeps a private 'real architecture' is a source of shadow systems."},
        {"t": "lead", "title": "Say this", "text": "I recommend we stay one deployable this half. Splitting services is the option I rejected because it spends the team on failure modes before we have a separate owner for any module. If a squad must release alone, I will bring back a split decision. I need you to treat that as the plan, not as a delay."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """You are the director who asked for microservices.
Read my one-page memo.
What am I deciding?
What do you need from me?
Which sentence sounds like I am protecting my preference instead of the deadline?
Reply in plain language. Do not rewrite the memo."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/memo-no-microservices.md.",
            "A half-page memo from your own eight years, sanitized.",
            "The sentence you will use when you are overruled.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 26 — Run the review instead of winning it"},
        {"t": "p", "text": "Outcome: a 60-minute agenda and a list of questions that expose a missing quality attribute without humiliating the author."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "40 min: the agenda and the question list below.",
            "80 min: review a design. Use a teammate's real design if you may, or review your own day 22 paper as if a colleague wrote it. Write comments in the form of questions.",
            "40 min: practice the opening and the closing out loud.",
            "40 min: AI role-plays a defensive author. You only ask questions.",
            "20 min: save the agenda and the questions.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The review exists so the next incident is cheaper. It does not exist so the architect is the smartest person in the room. The author presents. You facilitate. If you take the pen in minute five, you have stolen the design and the learning."},
        {"t": "p", "text": "Sixty minutes. Five: context and the decision they want. Ten: options they rejected. Fifteen: the quality scenarios and the failure they are willing to show the user. Ten: data ownership, identity, and what the client is allowed to decide. Ten: cost drivers and who is on call. Ten: the decision sentence, the revisit trigger, and the open risks. If the definition-of-ready page is missing, you spend five minutes saying so and you stop. Reschedule. Do not design it for them in the remaining time."},
        {"t": "p", "text": "Questions that work. What happens to the buyer if this dependency times out? Who is the only writer of this row? What did we reject, and who is unhappy? What number is an assumption? What will page someone? What is the rollback if we are wrong on Thursday? Which principle does this exception bend? What would make you revisit this in six months? Where is the tenant taken from? You can run a whole review on those sentences."},
        {"t": "p", "text": "Questions that waste the hour. Why not Kafka? Have you considered a pattern I like? Can we rename this class? Why is this not using the library I wrote? Save those for a conversation that is not this meeting."},
        {"t": "p", "text": "Close by reading back the decision, the risk, and the owner. Send the notes the same day. An undocumented review is a conversation the team will relitigate next sprint."},
        {"t": "lead", "title": "Say this", "text": "I will keep the review to an hour and send you back if the options and the failure mode are not on the page. I will ask who writes the data and what the user sees when the dependency dies. I will not redesign it in the meeting. I will read the decision back before we leave."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Role-play a senior developer who designed five microservices for Harbor and is proud of it.
I will only ask questions. After my questions below, answer in character, then tell me which of my questions was an attack instead of a question.
My questions:
What fails for the buyer if service three is down?
Who writes the order row?
What did you reject?
What is the rollback on Thursday?"""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/agenda.md.",
            "Ten questions in your own words.",
            "Notes from the practice review, including one question you would rephrase.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 27 — The portfolio and the stories only you can tell"},
        {"t": "p", "text": "Outcome: a README a hiring manager can read in ten minutes, and five stories from your career written as decisions."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "40 min: the README structure below.",
            "70 min: write the README so it links your real artifacts.",
            "80 min: five stories. System, decision, alternative, consequence, what you would reopen.",
            "30 min: AI checks that each story has a tradeoff. It must not invent metrics.",
            "20 min: read one story aloud in two minutes.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The portfolio is the harbor-architecture repository plus a README. The README says who you are in six lines, then links: principles, context, containers, three ADRs, SLO, threat model, the legacy memo, the briefing script. A manager will open two of those. An architect interviewer will open the ADRs and try to break them. Make the links true. A link to an empty file is worse than no link."},
        {"t": "p", "text": "Do not put your employer's private diagrams, customer names, or revenue in the repo. Say 'a wholesale portal' or 'a line-of-business app' and change the numbers if the real numbers are confidential. You can still tell the truth about the decision."},
        {"t": "p", "text": "Stories from eight years beat Harbor, because Harbor is a case and they know it. Write five. A production incident and the minute you chose rollback or fix-forward. A design you pushed back on. A migration slice, even a small framework upgrade, and what you refused to rewrite. A data or query problem where you changed the shape, not just an index. A person you grew, and what they now decide without you. Each story is one short page. If you do not have a number, do not create one. 'It was slow enough that support saw it every morning' is honest. 'We improved latency by 63 percent' without a measurement is how panels lose trust."},
        {"t": "p", "text": "The architect version of a story is not 'I worked hard'. It is 'we had two options, I recommended this, the cost was that, and the signal I watched afterward was this'. Practice stopping. Two minutes is enough. The follow-up is where depth shows."},
        {"t": "lead", "title": "Say this", "text": "The repository is how I make architecture decisions visible: context, ADRs, and the quality I would measure. The stories are from systems I actually shipped. I will tell you the option I rejected. I will not invent a percentage."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here are five stories. For each, say whether you can find: a decision, a rejected option, a consequence, and a way I would know it failed.
Flag any number that looks invented.
Flag any story that is really a list of technologies.
Do not improve the prose. Do not add achievements I did not write."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "README.md at the root of the architecture repo.",
            "docs/reviews/stories.md with five stories.",
            "One story you will tell if you are asked for only one.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 28 — Mock panel"},
        {"t": "p", "text": "Outcome: a scored 45-minute design and a 20-minute story conversation, with notes of what broke."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "20 min: set up. Paper, a timer, the scoring sheet. Phone on record if you can stand to hear it.",
            "45 min: design, laptop closed, AI silent.",
            "20 min: two stories, timed.",
            "30 min: transcribe the design enough for the critic.",
            "40 min: run the panel prompt. Write the scores it gives and, more important, the scores you give yourself where you disagree.",
            "25 min: a repair list of at most three items for day 29. More than three means you are avoiding the worst one.",
        ]},
        {"t": "h2", "text": "The design prompt, unseen until the timer starts"},
        {"t": "p", "text": "A regional distributor wants a portal for their retailers to place replenishment orders. About 500 retailers, peak of about 10 submits a second, a team of six, Azure, .NET and Angular. They also fax orders today and want that to stop. Warehouse staff must see today's orders. Design the system. Call out what you will not build in the first release."},
        {"t": "p", "text": "This is Harbor with the numbers changed on purpose. If you cannot redraw it under new numbers, you memorized a diagram. The fax line matters: it is a legacy input, an anti-corruption problem, and a temptation to keep a shared spreadsheet forever. Say what happens to fax in release one. A reasonable answer: release one is the portal for the largest retailers, fax remains as a manual entry screen for staff, and you do not build optical character recognition as architecture."},
        {"t": "h2", "text": "Panel prompt"},
        {"t": "code", "text": """You are a technical architect interviewing a candidate with eight years of .NET and Angular.
You have their transcribed design and two stories below.
Score 0, 1, or 2 on each: decision quality, tradeoff, operability, security and data ownership, communication.
Ask eight follow-up questions they did not answer.
Name the single gap that would stop you hiring them as a technical architect this quarter.
Do not coach warmly. Do not redesign the system.
Be specific. Quote their words.
DESIGN:
(paste)
STORIES:
(paste)"""},
        {"t": "p", "text": "Services-firm panels often add a workshop: assumptions, risks, and a rough phase plan. Product-firm panels often stay on the whiteboard and then ask how you would roll it back. If you know which room you are walking into, add ten minutes in that style after the 45. Do not skip the failure mode in either room."},
        {"t": "h2", "text": "How you score yourself"},
        {"t": "b", "items": [
            "2: you named the decision, the rejected option, and the user-visible failure.",
            "1: you named the decision, and the tradeoff arrived only when pressed.",
            "0: you listed technologies, or you agreed with every interruption.",
            "A total of 7 or more out of 10, with no zero on data ownership, is a pass for this mock. A beautiful diagram with a zero on security is not.",
        ]},
        {"t": "warn", "title": "What the model must not decide", "text": "Whether you are 'ready for Google' or any other brand. Whether your stories are good enough to claim a title. Use the model to find holes. You decide what to repair. If the model flatters you, the prompt was too soft. Run it again with the line 'be specific' and a demand to quote you."},
        {"t": "break"},

        {"t": "h1", "text": "Day 29 — Repair, then a different case"},
        {"t": "p", "text": "Outcome: the worst gap from the mock is smaller, and you can design a partner API that must not reuse the browser session."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "70 min: repair only the top gap. If it was data ownership, rewrite that page. If it was speaking, record the briefing again. Do not 'lightly review everything'.",
            "20 min: the partner brief.",
            "70 min: paper design.",
            "30 min: speak.",
            "30 min: AI scores only the partner case.",
            "20 min: note what changed since day 22.",
        ]},
        {"t": "h2", "text": "The brief"},
        {"t": "p", "text": "A large buyer wants to place Harbor orders from their own ERP, not from your Angular app. They can call an API. They cannot be given a staff password. They must not see another tenant. You expect tens of calls a second from them at peak, in bursts. They will get the contract wrong at least once in the first month. Decide what you add, what you reuse, and what the Angular BFF must not become."},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "Reuse Ordering, the idempotency store, the tenant rules, and the outbox. Do not reuse the cookie session. A partner uses an application identity: client credentials or a similar OAuth client flow against Entra, their own app registration, a credential they can rotate. Authorization says which tenant that client may act for. One client must not submit for every tenant because it knows an id. That mapping is server-side."},
        {"t": "p", "text": "This is the moment API Management, or a carefully limited gateway, earns a box. You want a key or a token you can revoke, a quota so a bug in their ERP does not consume the accept path, and a versioned contract. The BFF stays the browser's door. If you route the partner through the BFF's cookie endpoints, you will invent a service account password in a hurry. Write the no."},
        {"t": "p", "text": "Version the partner contract with a URL version from the start, because you cannot deploy their ERP. Expand and contract still applies inside a version. Give them Problem Details and a request id. Rate-limit with 429 and a documented retry they can honor. Their retries must send the same idempotency key or they will duplicate orders and blame you."},
        {"t": "p", "text": "The Angular app does not get a special bypass around the new rules. If both doors write orders, they write through the same Ordering module. Two doors, one writer."},
        {"t": "lead", "title": "Say this", "text": "The partner gets their own client credentials, a tenant mapping we control, a versioned contract, and a quota. They use the same Ordering module and the same idempotency rules. They do not get a browser cookie, and the BFF does not grow a back door for them. API Management is justified now because a partner exists."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Score my partner-API design from 0 to 2 on decision, tradeoff, and security.
Did I reuse the cookie?
Is there still one writer of the order?
What happens when they retry without an idempotency key, and did I say it?
Quote the weakest sentence."""},
        {"t": "break"},

        {"t": "h1", "text": "Day 30 — The first 90 days in the seat"},
        {"t": "p", "text": "Outcome: a personal operating plan for the job, not another diagram. You know what you will not redesign in the first month."},
        {"t": "h2", "text": "Time box (4 hours)"},
        {"t": "b", "items": [
            "40 min: read the 90-day shape below and edit it to the company you are actually joining or targeting.",
            "80 min: write your plan, including a listening list and the first fitness function.",
            "40 min: speak the 30-day briefing one last time, from memory.",
            "40 min: AI critic on the plan, looking for heroics.",
            "40 min: close the portfolio. Fix broken links. Write the date.",
        ]},
        {"t": "h2", "text": "Study material"},
        {"t": "p", "text": "The failure mode of a new technical architect is a target architecture in week two. The system you just joined has scars, political owners, and a release train. Your first job is to see it. Days 1 to 30 of the role, not of this course: read the last five incident reports, read the deploy pipeline, draw the real containers from the repositories rather than from the old slide, and have eight conversations. The tech leads, the person on call, the person who pays the bill, security, the product owner, support, the analyst with the scripts, and one engineer who is quietly holding a module together. Ask what they are afraid to change. Do not present Harbor."},
        {"t": "p", "text": "Days 31 to 60: one decision the teams already asked for, written as an ADR, small enough to merge. One fitness function in CI that would have caught a real incident or a real boundary violation. One review forum that actually happened, with notes. If you cannot get a fitness function merged, you do not have the relationships yet. Go back to listening. Do not add a second initiative to hide that."},
        {"t": "p", "text": "Days 61 to 90: the forum has happened twice. The radar has fifteen items or fewer and at least one Hold that annoyed someone, which means it is real. You have declined a rewrite or a platform in writing, with a revisit trigger. You can point to a decision someone else used without calling you. That is the job. A diagram nobody used is a hobby."},
        {"t": "p", "text": "Keep a depth spike so you do not become a person who only reviews. For you that spike is ASP.NET Core, data access, and Angular. One day a week you read a pull request properly or you pair on a hard defect. The 10-day tech lead guide remains the refresher when a panel or a production bug drops below architecture altitude. Use it. Do not spend the first month rebuilding it."},
        {"t": "p", "text": "AI in the job: the same rules as this course. The model may attack an ADR you wrote. It may draft a threat-model skeleton you then correct against the real system. It may not set the SLO, choose the region strategy, or write a performance number into a customer proposal. Paste constraints. Ask for the objection. Redraw from memory. Do not paste your employer's secrets into a personal account."},
        {"t": "lead", "title": "Say this", "text": "In the first month I will draw the system that exists and listen to the people who run it. In the second month I will land one decision they already need and one check in the pipeline. In the third month I will have declined something expensive in writing. I will not arrive with a target architecture named after a reference diagram."},
        {"t": "h2", "text": "AI session"},
        {"t": "code", "text": """Here is my 90-day plan for the architect role.
Find the heroic goal that a new person cannot finish.
Find a week where I am presenting instead of listening.
Find where I took implementation work away from a tech lead.
Tell me the smallest fitness function that would still count."""},
        {"t": "h2", "text": "Evening artifact"},
        {"t": "b", "numbered": True, "items": [
            "docs/reviews/first-90-days.md.",
            "The listening list, eight conversations, with the question you will ask each.",
            "The first fitness function, described so a tech lead could add it without you.",
            "A note of the mock scores from day 28 and what day 29 changed.",
        ]},
        {"t": "qa", "q": "What would you do in your first 90 days?", "a": "I would not announce a new architecture. I would spend the first month on the real system and on the people who are afraid to change it. In the second month I would ship one ADR the teams already need and one automated fitness check. By the third month the review forum should have met twice, and I should have declined at least one expensive rewrite in writing, with a trigger that would reopen it.", "lead": "I would still review code one day a week. An architect who cannot read the pull request will not see the boundary break."},
        {"t": "break"},

        {"t": "h1", "text": "Appendix A — Prompt library"},
        {"t": "p", "text": "Use these on your own artifacts. Replace the angle brackets. Keep the session prompt from the front of this document as the first message when the chat has forgotten the constraints."},
        {"t": "h2", "text": "Critique an ADR"},
        {"t": "code", "text": """Constraints: <team size, scale assumption, region, data store, identity>.
ADR below. Do not rewrite it.
1. Decision in one sentence, as you read it.
2. The strongest objection.
3. A consequence I listed as positive that is also a cost.
4. Whether the revisit trigger is observable.
5. Sentences I should delete because they are slogans.
ADR:
<paste>"""},
        {"t": "h2", "text": "Missing quality attribute"},
        {"t": "code", "text": """Here is a design. Name the quality attribute I did not cover.
Write the missing scenario as source, stimulus, environment, response, and measure.
If the measure cannot be observed, say so.
Do not add a product to fill the gap.
DESIGN:
<paste>"""},
        {"t": "h2", "text": "Threat model starter, then you delete the nonsense"},
        {"t": "code", "text": """Threat-model this flow with STRIDE.
For each threat: one sentence, one control that is a server-side check or a test, and one control that is only a UI convenience.
Flag anything you are unsure about instead of inventing a CVE or a compliance claim.
FLOW:
<paste>"""},
        {"t": "h2", "text": "Mock interviewer, short"},
        {"t": "code", "text": """Interview me for a technical architect role on .NET and Angular.
Ask one question. Wait. I will answer in a later message.
After my answer, score 0 to 2 for decision, tradeoff, and consequence.
Then ask a follow-up that attacks the weakest of the three.
Do not lecture. Do not move to a new topic until I ask."""},
        {"t": "h2", "text": "Director translation"},
        {"t": "code", "text": """Turn this ADR into a decision a director can read in two minutes.
Keep my decision. Do not soften a risk I named.
Cut product names that are not required to understand the cost.
End with the ask.
ADR:
<paste>"""},
        {"t": "h2", "text": "Boundary check in Cursor"},
        {"t": "code", "text": """Look at principles.md and the ADR I have open.
List contradictions only.
For each: quote both files.
Do not edit the files.
Do not propose a new architecture."""},
        {"t": "p", "text": "If you use Cursor for that last prompt, open the two files so the tool can see them. Then you still edit by hand. A clean contradiction list is the value. An automatic rewrite is how the principles drift to match the latest draft."},
        {"t": "h2", "text": "Stop prompts"},
        {"t": "b", "items": [
            "Do not ask which cloud is best.",
            "Do not ask for a full production code base for Harbor. A sketch that proves the boundary is enough. A generated solution you have not run is a liability in the portfolio.",
            "Do not ask the model to score you 'ready' or 'not ready' for a job. Ask it to quote the missing tradeoff.",
            "Do not paste an employer repository into a personal tool. Bring the shape, not the source, unless the company tool is approved.",
        ]},

        {"t": "h1", "text": "Appendix B — Templates"},
        {"t": "h2", "text": "ADR"},
        {"t": "code", "text": """# ADR-000: <decision in the title>
Status: Proposed | Accepted | Superseded by ADR-000
Date:

## Context
<constraints, not a history essay>

## Decision
<what we will do>

## Options rejected
<why each lost>

## Consequences
<good and bad>

## Revisit when
<observable trigger>"""},
        {"t": "h2", "text": "Quality scenario"},
        {"t": "code", "text": """Quality:
Source:
Stimulus:
Artifact:
Environment:
Response:
Response measure:
Assumption or measurement:
What we give up:
Revisit when:"""},
        {"t": "h2", "text": "One-page decision"},
        {"t": "code", "text": """Decision:
Problem:
Options:
Consequence and risk:
Ask:"""},
        {"t": "h2", "text": "Review notes"},
        {"t": "code", "text": """Date:
Author:
Decision requested:
Options rejected:
Failure the user sees:
Data owner:
Open risk:
Revisit trigger:
Who accepted:"""},

        {"t": "h1", "text": "Appendix C — Rapid answers"},
        {"t": "p", "text": "Speak the answer, then stop. Add the lead sentence only if they ask why."},
        {"t": "qa", "q": "What is your default for a new .NET and Angular product with one team?", "a": "A modular monolith for the domain, a BFF in front of the Angular app, and a separate worker only for work that must fail independently, such as mail. One database with schema ownership. Managed identity. One region until the SLO and the business say otherwise.", "lead": "I write the revisit trigger at the same time, or the default becomes a religion."},
        {"t": "qa", "q": "When do you split a service out?", "a": "When a team must release on its own cadence, when a measured hotspot cannot be fixed inside the process, or when a compliance boundary forbids sharing the host. Not because the diagram has too few boxes.", "lead": "Mail can be a worker earlier, because the failure domain is already different and the user is not waiting."},
        {"t": "qa", "q": "How do you handle a double submit?", "a": "An idempotency key, unique per tenant, stored with the order. The same key and body return the same order. The same key and a different body return 409. The UI generates the key once per attempt.", "lead": "The outbox consumer uses the same idea for messages, because the broker is at least once."},
        {"t": "qa", "q": "Where does authorization live?", "a": "On the server, on every read and write, using the tenant and the user from the session or token. The Angular app can hide a button. That is not the control. A cross-tenant test is part of the definition of done.", "lead": "I use 404 when the id is outside the tenant so we do not confirm it exists."},
        {"t": "qa", "q": "What do you put in the browser?", "a": "An HttpOnly Secure cookie issued by the BFF, plus an anti-forgery token on writes. Not the access token, and not a secret in the Angular environment file.", "lead": "If we skip the BFF, the token stays in memory and I state the XSS risk instead of pretending localStorage is fine."},
        {"t": "qa", "q": "How do you choose between App Service, Functions, Container Apps, and AKS?", "a": "App Service for the request API, Functions for the event worker, Container Apps when we need containers without operating a cluster, AKS when a platform team already runs one and the workload needs it. Harbor does not start on AKS.", "lead": "Every choice is a pager. I can say who answers it."},
        {"t": "qa", "q": "What is your availability target?", "a": "I do not pick nines from a hat. For a single-region Harbor I would discuss 99.9 percent on the accept path, about 43 minutes a month, as a starting SLO, and I would label it an assumption until we measure. I would not offer 99.99 percent without a second region and a data strategy.", "lead": "Mail is a different, looser SLO. I do not hide it inside the accept number."},
        {"t": "qa", "q": "What is a fitness function?", "a": "An automated check that an architecture decision still holds. A test that one module cannot reference another's tables, a contract check on the order event, a timeout required on new HTTP clients, an accessibility scan on the submit route.", "lead": "I would rather have two that match real incidents than a dashboard of twenty nobody owns."},
        {"t": "qa", "q": "Would you use NgRx?", "a": "Not by default. Signals for feature state, RxJS at the HTTP boundary. A global store when distant parts of a long workflow go stale and we can name that bug. The store is a cost.", "lead": "The larger Angular decision is the boundary between buyer and ops, and between catalog and ordering, not the state library."},
        {"t": "qa", "q": "How do you work with AI as an architect?", "a": "I write the decision. The model attacks it: missing quality, weakest objection, fictional numbers. I do not paste secrets, I do not accept a price it invented, and I redraw the design from memory. If I cannot, I do not understand it yet.", "lead": "Cursor is useful when it can see the ADR next to the principles and only report contradictions."},

        {"t": "h1", "text": "Appendix D — Glossary"},
        {"t": "table", "headers": ["Term", "Meaning in this document"], "rows": [
            ["BFF", "Backend for frontend. The only API the Angular app calls. Holds tokens. The browser gets a cookie."],
            ["Bounded context", "A boundary where a word means one thing. Ordering's order is not the warehouse's pick list."],
            ["ADR", "Architecture decision record. Context, decision, consequences, revisit trigger."],
            ["C4", "Context, container, component, code. Most reviews stop at container, plus one component view of a hard path."],
            ["SLI / SLO", "The measurement, and the target for that measurement over a window."],
            ["Error budget", "The failure the SLO still allows. For 99.9 percent of a 30-day month, about 43 minutes."],
            ["Outbox", "A row written in the same transaction as the business change, later published to a bus."],
            ["Saga", "Several local transactions with a compensation or a retry. Not a synonym for 'we use events'."],
            ["Fitness function", "An automated check that a design decision still holds."],
            ["Strangler", "Replace a legacy system one journey at a time, with a way back, until the old path has no writers."],
            ["Anti-corruption layer", "A translation at the edge so a foreign model does not leak into yours."],
            ["Modular monolith", "One deployable, with module and data boundaries you enforce. Not 'a monolith we are ashamed of'."],
            ["Well-Architected", "Microsoft's five pillars: reliability, security, cost, operations, performance. A review should say which one you are spending."],
            ["Managed identity", "An Azure identity for the app itself, so SQL and Key Vault do not need a password in a config file."],
            ["Idempotency key", "A client-supplied key that makes a retried create return the original order instead of a second one."],
        ]},

        {"t": "h1", "text": "Appendix E — What this month will not make you"},
        {"t": "p", "text": "You will not be an enterprise architect, a security consultant, or a person who has operated a multi-region system through a real failover. You will not have read Kleppmann or the Hard Parts cover to cover. You will not have a right to a title. You will have a portfolio you can defend, a way of speaking in decisions, and a 90-day plan that does not start with a rewrite."},
        {"t": "p", "text": "If a week collapses because of work or family, do not quit the sequence and do not double the hours the next day. Keep the artifact and the spoken answer. Slide the external reading to the weekend or drop it. The calendar is a scaffold. The ADRs are the point."},
        {"t": "p", "text": "When you finish day 30, book a conversation with the strongest architect you know and ask them to spend 45 minutes trying to break ADR-001 and the partner API. A human who has carried a pager will find things this document and the model both missed. That conversation is the start of the job, not a graduation."},
        {"t": "note", "title": "A last rule about numbers", "text": "Every peak, latency, retention, and availability figure in this document is a teaching assumption for Harbor, except the calendar arithmetic on a 30-day month and the published .NET support window. If you say them in a real review, label them. Then replace them with the measurement, the bill, or the official limit."},
    ]
