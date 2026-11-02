# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "p", "text": "STUDY GUIDE", "size": 12, "bold": True, "center": True, "muted": True},
        {"t": "p", "text": ".NET Tech Lead", "size": 28, "bold": True, "center": True},
        {"t": "p", "text": "Auth, Scalability, Azure, and SQL", "size": 18, "bold": True, "center": True},
        {"t": "p", "text": "Deep questions and answers for an 8-year full-stack .NET developer.", "size": 13, "italic": True, "center": True},
        {"t": "p", "text": "Authentication and authorization  ·  JWT  ·  Web API scale  ·  Azure  ·  SQL Server", "size": 12, "center": True, "muted": True},
        {"t": "p", "text": "Companion to the 10-day roadmap and the deep dive. Those guides are the schedule and the first worked example. This guide is the follow-up a panel asks after the 90-second answer.", "size": 12, "italic": True, "center": True},
        {"t": "p", "text": "Prepared 31 October 2026. Examples target C# on .NET 10 LTS, supported through 14 November 2028. .NET 8 and .NET 9 reach end of support in November 2026.", "size": 11, "center": True, "muted": True},
        {"t": "h1", "text": "How to use this companion"},
        {"t": "p", "text": "Read a section until you can redraw the example. Then close it and answer the question out loud in under two minutes. Use the lead line as the last sentence. If the follow-up is a trap from a warn box, say the trap and the rule you would put in review. Swap in a system you have operated when you have one. Until then, stay on the Orders API and label every number that is an assumption."},
        {"t": "b", "numbered": True, "items": [
            "Speak the definition in one sentence.",
            "Attach it to POST /orders, the token, Azure SQL, or the slot.",
            "Name the failure: who feels it, and what you roll back.",
            "Stop. A third feature is how a clear answer becomes a tour.",
        ]},
        {"t": "table", "headers": ["Section", "You will be able to teach"], "rows": [
            ["Authentication and authorization", "Schemes, policies, resource checks, tenant isolation, 401 and 403."],
            ["JWT", "What a token proves, what it leaves readable, and the validation order."],
            ["Web API scalability", "Stateless instances, async, cache, backpressure, and the 50 request assumption."],
            ["Azure", "The host, the identity, the queue, the slot, and the rollback."],
            ["SQL", "A plan, an index, a tenant-safe write, and six queries you can defend."],
        ]},
        {"t": "h2", "text": "The running example"},
        {"t": "p", "text": "A partner POSTs an order and may retry. A customer GETs the order. The API runs on Azure App Service. Azure SQL holds the order, the lines, the customer, and the idempotency key. The email worker is an Azure Function on the isolated worker model, triggered by Azure Service Bus. The caller's token comes from Microsoft Entra ID. The process reaches Azure SQL, Key Vault, and Service Bus with a managed identity."},
        {"t": "p", "text": "Scale you may assume out loud, and you label it as an assumption: about 50 requests a second at peak, about 2 million orders a year, p95 under 300 milliseconds for the read, email within a minute. A first-party Angular app talks to a BFF when you introduce one. The partner calls the API with a bearer token. One process does not have to serve both surfaces."},
        {"t": "note", "title": "What this guide will not do", "text": "It will not invent an Azure price, a SKU quota, or a latency you should memorize. When a limit matters, name the document or the metric you would open. It will not claim these SQL examples were executed in a session you did not run. Confirm a plan on your own server before you argue row counts."},
        {"t": "break"},
    ]
