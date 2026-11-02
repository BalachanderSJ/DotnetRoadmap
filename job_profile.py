# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "The profile recruiters search"},
        {"t": "p", "text": "LinkedIn, Naukri, and a human recruiter all look for the same words: the title you want, C#, ASP.NET Core, SQL, Azure, and a number that proves you shipped. Put those words in the headline, the skills, the last two roles, and the resume file. A profile that says Software Engineer, and a resume that says Tech Lead, looks like two different people."},
        {"t": "h2", "text": "Resume"},
        {"t": "p", "text": "One page if the last two roles tell the story. Two pages if eight years of relevant work needs the second page. Export a text PDF from Word. The file name is Firstname-Lastname-Tech-Lead-NET.pdf. Single column. Standard headings: Summary, Skills, Work Experience, Education. Skip text boxes, icons, and a photo. Name, phone, email, city, and the LinkedIn URL are enough in the header. Family details and a full street address do not help a product or capability-center screen."},
        {"t": "p", "text": "Summary, three lines: years, stack, domain, and one outcome. Skills, one block: only tools you can explain on a screen. If Kubernetes is listed, you can describe a deployment you ran. Work experience in reverse date order. Each role shows company, title, city, and dates, then three to five bullets. Education sits at the end."},
        {"t": "lead", "title": "Bullet shape", "text": "Verb, system, what you changed, and the number after. Cut p95 on the order API from 800 ms to 220 ms by replacing an N+1 EF Core query with one SQL query and a covering index."},
        {"t": "p", "text": "Other bullets that score: a migration with the date the old runtime was gone, a review rule the team still uses, a production rollback you chose, a person who now owns a service you used to own. The story bank in the roadmap is the source. Leave sample stories as structure. Write your own systems and your own numbers."},
        {"t": "h3", "text": "Headline you can paste"},
        {"t": "code", "text": "Tech Lead | C# ASP.NET Core | Azure SQL Server | 8 years"},
        {"t": "p", "text": "Use that pattern on the resume header, the LinkedIn headline, and the Naukri resume headline. Swap in the domain if the target list is mostly one industry, for example fintech or healthcare, and only if you have shipped in it."},
        {"t": "h2", "text": "Skills to list when you have done the work"},
        {"t": "p", "text": "Recruiters search the words written in job descriptions. ASP.NET Core and .NET are both searched. Web API and REST are both searched. Use the name you have earned, spelled the way the posting spells it."},
        {"t": "b", "items": [
            "C#, .NET, ASP.NET Core, Web API, Entity Framework Core",
            "SQL Server, T-SQL, Azure, Azure App Service, Azure Functions",
            "Microservices, REST, Git, CI/CD, system design, code review",
            "Add Docker, Kubernetes, Service Bus, or Microsoft Entra ID only where you can defend them",
        ]},
        {"t": "p", "text": "Fifteen to thirty skills is enough on Naukri. A list of every tool you opened once pushes the real ones down. Match the list to two or three tech-lead job descriptions you would accept, then delete the rest."},
        {"t": "h2", "text": "LinkedIn About, first three lines"},
        {"t": "p", "text": "Only the first lines show before someone clicks See more. Put the search words there."},
        {"t": "code", "text": "Tech lead with 8 years on C#, ASP.NET Core, EF Core, SQL Server, and Azure.\nI design the API and the data, and I own the release plan, review quality, and migration risk.\nLooking for a tech lead or senior engineer role in Bengaluru or Hyderabad. Notice period 30 days."},
        {"t": "p", "text": "Replace the cities and the notice with yours. The experience section uses the same bullets as the resume. Dates match the resume. A gap or a contract role is written the way it happened. Background verification later checks titles, dates, and compensation against the letter, the pay slips, and Form 16."},
        {"t": "h2", "text": "What you leave off"},
        {"t": "b", "items": [
            "A public Open to Work photo frame while you are employed. Use the recruiter-only setting, described in the LinkedIn section.",
            "Client names, revenue figures, or architecture you are not allowed to share. Describe the system class and the metric you are allowed to share.",
            "A second headline for a different career. One search, one story: .NET tech lead.",
        ]},
        {"t": "warn", "title": "Numbers you can show", "text": "Quote the current CTC you can point to on an offer letter, pay slips, or Form 16. Inflating current pay is a common reason an offer is withdrawn during background verification."},
        {"t": "break"},
    ]
