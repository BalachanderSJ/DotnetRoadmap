# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "p", "text": "FURTHER STUDY", "size": 12, "bold": True, "center": True, "after": 4, "muted": True},
        {"t": "p", "text": ".NET Tech Lead", "size": 28, "bold": True, "center": True, "after": 2},
        {"t": "p", "text": "Next 20 days", "size": 18, "bold": True, "center": True, "after": 8},
        {"t": "p", "text": "Azure Pipelines  ·  TFS and Azure DevOps  ·  GitHub Actions", "size": 12, "center": True, "after": 2, "muted": True},
        {"t": "p", "text": "ASP.NET Core MVC  ·  MVVM  ·  Microservices  ·  AI-assisted delivery", "size": 12, "center": True, "after": 10, "muted": True},
        {"t": "p", "text": "This follows the 10-day interview roadmap and the deep dive. Those days taught the API, SQL, Azure hosts, and a first pass at microservices. These 20 days teach how the change reaches production, how MVC and MVVM differ, and how to use Cursor and GitHub Copilot without skipping review.", "size": 12, "italic": True, "center": True, "after": 6},
        {"t": "p", "text": "Prepared 31 October 2026. Examples stay on .NET 10, ASP.NET Core, Azure App Service, and Azure Pipelines or GitHub Actions. Do not memorize a price or a quota. Name the document you would check.", "size": 11, "center": True, "after": 6, "muted": True},
        {"t": "h1", "text": "How the next 20 days fit"},
        {"t": "p", "text": "Each day is about 3.5 to 4 hours. Read the explanation, type the example, then say the short answer out loud. Days 1 to 10 are delivery. Days 11 to 16 are the UI patterns and a deeper ASP.NET Core pass. Days 17 and 18 extend microservices past the interview sketch. Days 19 and 20 are the AI-assisted product development life cycle, called AIPDLC here: where a model may draft, and where a human still signs."},
        {"t": "table", "headers": ["Days", "You will be able to teach"], "rows": [
            ["1-3", "Git on a team, GitHub pull requests, and a GitHub Actions build for the orders API."],
            ["4-6", "What TFS means now, an Azure Pipelines YAML file, and a CI gate that fails a bad pull request."],
            ["7-10", "Deploy to a slot, identity without a password in the pipeline, and a rollback you have named."],
            ["11-14", "ASP.NET Core MVC, and MVVM as a different shape used by a client, not a rename of MVC."],
            ["15-16", "Middleware, filters, caching, background work, and an integration test."],
            ["17-18", "A service boundary you can deploy on its own, with its own pipeline and data."],
            ["19-20", "Where AI sits in the lifecycle, and the Cursor and Copilot habits that survive review."],
        ]},
        {"t": "note", "title": "Names you will hear in the same conversation", "text": "TFS is the old name. The on-premises product is Azure DevOps Server. The cloud product is Azure DevOps Services. People still say TFS when they mean either. GitHub is a different host. Azure Pipelines is the CI and CD engine inside Azure DevOps. GitHub Actions is the CI and CD engine inside GitHub. A team picks one engine for a service. Running both without a reason is two places to look during an incident."},

        {"t": "h1", "text": "Day 1 — Git the way a team uses it"},
        {"t": "p", "text": "Outcome: you can explain a branch, a pull request, a merge, and a rebase with the orders API as the example, and you can repair a conflict without rewriting history that other people already pulled."},
        {"t": "h2", "text": "Time box (3.5 hours)"},
        {"t": "b", "items": [
            "40 min: commit, branch, and remote. Say each in one sentence.",
            "80 min: type the example flow on a scratch repo.",
            "50 min: merge versus rebase, then a conflict.",
            "40 min: speak the Say this boxes.",
        ]},
        {"t": "h2", "text": "The objects that matter"},
        {"t": "p", "text": "A commit is a snapshot plus a pointer to its parent. A branch is a movable name for a commit. HEAD is the commit you have checked out. origin is the usual name of the remote. main is the branch you protect. A feature branch is where the orders change lives until review. A pull request is the conversation and the policy gate. It is not a Git object. GitHub and Azure DevOps add it on top of the commits."},
        {"t": "code", "text": """git switch -c feature/order-idempotency
# edit CreateOrder, add the test
git add src/Orders.Api tests/Orders.Tests
git commit -m "Store the idempotency key with the order"
git push -u origin feature/order-idempotency
# open the pull request into main"""},
        {"t": "p", "text": "The commit message says why. The diff says what. A message such as 'updates' fails review because the history becomes useless at midnight. One commit can be several files when they are one decision. Two unrelated fixes are two commits, or two pull requests."},
        {"t": "h2", "text": "Merge and rebase"},
        {"t": "p", "text": "Merge joins two lines and can create a merge commit with two parents. History keeps the branch shape. Rebase replays your commits on top of a new base, so the feature looks like it started from today's main. Rebase rewrites commit ids. That is safe on a branch only you use. It is hostile on a branch other people have pulled, because their next pull must reconcile two histories of the same work."},
        {"t": "code", "text": """git switch feature/order-idempotency
git fetch origin
git rebase origin/main
# conflict in CreateOrder.cs
# edit the file, keep both the new token check and your key storage
git add src/Orders.Api/CreateOrder.cs
git rebase --continue
git push --force-with-lease"""},
        {"t": "p", "text": "force-with-lease refuses the push if someone else added a commit you have not seen. A plain force push can delete that commit. After the rebase, the pull request updates to the new commits. Squash merge on the server turns the feature into one commit on main. That is a team rule. Pick squash or merge and stay with it. Mixing them makes git bisect harder."},
        {"t": "warn", "title": "What breaks", "text": "Rebasing main, or rebasing a shared release branch, rewrites the commits the pipeline and other developers already built. Committing secrets, even in one commit you later delete, leaves them in the object database until history is rewritten and every clone is replaced. A conflict resolved by taking 'ours' without reading both sides drops the idempotency check."},
        {"t": "lead", "title": "Say this", "text": "A branch is a name for a commit. A pull request is the review gate. I rebase only the branch I own, and I push it with force-with-lease. I do not rewrite main."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Draw main, your branch, and the pull request. Mark which commits the build runs.",
            "Explain why force-with-lease is the push you use after a rebase.",
            "Name one file that must never be committed: appsettings with a password, a .pfx, a user secret file.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 2 — GitHub for the orders API"},
        {"t": "p", "text": "Outcome: you can set the repository rules a two-year developer should expect, and you can review a pull request for the contract, not the brace style."},
        {"t": "h2", "text": "Time box (3.5 hours)"},
        {"t": "b", "items": [
            "30 min: repository, fork, and clone.",
            "70 min: branch protection and CODEOWNERS.",
            "70 min: a pull request review of a bad orders change.",
            "40 min: secrets, environments, and what does not belong in the repo.",
        ]},
        {"t": "h2", "text": "What GitHub adds on top of Git"},
        {"t": "p", "text": "GitHub hosts the remote, the pull request, the review comments, the checks, and the permissions. A fork is a separate repository used when you do not have write access. Inside a company, developers usually push branches to the same repository and open a pull request. Collaborators get a role: read, write, or admin. Admin is rare. Write does not mean permission to push to main if branch protection is on."},
        {"t": "code", "text": """# .github/CODEOWNERS
/src/Orders.Api/Auth/        @contoso/api-security
/src/Orders.Api/**/*.cs      @contoso/orders-api
/.github/workflows/          @contoso/platform
/infra/                      @contoso/platform"""},
        {"t": "p", "text": "CODEOWNERS names who must review a path. Auth and workflow files should not be approvable by the author alone. Branch protection on main requires a pull request, requires the CI check to pass, and dismisses a stale approval when new commits arrive. A ruleset is the newer GitHub form of the same idea. The lead answer is the rule, not the screen name."},
        {"t": "h2", "text": "A review that catches the bug"},
        {"t": "p", "text": "The diff adds a client-supplied total and logs the bearer token. The build is green. Green means it compiled and the existing tests passed. It does not mean the change is safe."},
        {"t": "code", "text": """[HttpPost("/orders")]
public async Task<OrderDto> Create(OrderDto input, CancellationToken ct)
{
    logger.LogInformation("Token {Token}", Request.Headers.Authorization);
    var order = new Order { Total = input.Total, Sku = input.Sku };
    await db.SaveChangesAsync(ct);
    return input;
}"""},
        {"t": "b", "items": [
            "The token in the log is a secret in production logs. Delete that line.",
            "Total from the body is the client setting the price. The server prices the order.",
            "There is no idempotency key, so a retry creates a second order.",
            "The method returns the client object, not the stored order.",
            "Ask for a test that a second POST with the same key does not insert again.",
        ]},
        {"t": "warn", "title": "What breaks", "text": "Approving because the author is senior. A required check that is not the test job, so a skipped workflow still looks green. A secret committed in appsettings.Production.json. GitHub secret scanning may catch it later. The pipeline already cloned it."},
        {"t": "lead", "title": "Say this", "text": "Main requires a pull request and a passing build. CODEOWNERS covers auth, workflows, and infrastructure. I review the contract and the secrets, not the indentation."},
        {"t": "h2", "text": "Secrets and environments"},
        {"t": "p", "text": "A GitHub Actions secret is encrypted and masked in logs. An environment such as production can require a reviewer before a job that names that environment runs. Variables are for values that are not secret, such as an Azure client id if your org treats it as public. Subscription and tenant ids are often stored as secrets so logs stay masked. The application secret, the SQL password, does not live in the workflow file. Production should not have a SQL password at all. The app uses a managed identity. The workflow uses OpenID Connect, which Day 9 covers."},
        {"t": "lead", "title": "Say this", "text": "Secrets stay in the host's secret store. Environments gate production. I do not print a token to prove the header arrived."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "List the three paths you would put in CODEOWNERS for the orders system.",
            "Review the bad Create method out loud in under two minutes.",
            "Say where a production SQL password must not be stored.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 3 — GitHub Actions for a .NET API"},
        {"t": "p", "text": "Outcome: you can read a workflow and point at the trigger, the permissions, the job, and the step that would deploy. You can explain why a pull request workflow does not deploy to production."},
        {"t": "h2", "text": "The shape of a workflow"},
        {"t": "p", "text": "A workflow file lives in .github/workflows. on says when it runs. permissions says what the GITHUB_TOKEN may do. jobs run in parallel unless one needs another. steps run in order on a runner. uses pulls an action. run executes a shell command. A pull request runs the build and the tests. A push to main may deploy, and only through an environment that has a reviewer."},
        {"t": "code", "text": """name: orders-ci
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "10.0.x"
      - run: dotnet restore Orders.sln
      - run: dotnet build Orders.sln -c Release --no-restore
      - run: dotnet test Orders.sln -c Release --no-build"""},
        {"t": "p", "text": "Pin third-party actions. A moving tag such as @v4 can still change. A commit SHA is stricter. Use the major your security team has approved if they have not moved to SHAs yet, and say that. timeout-minutes stops a hung test from holding a runner. contents: read is enough for a test job. A job that pushes a package or comments on a pull request needs a narrower extra permission, not write on everything."},
        {"t": "h2", "text": "Cache, path filters, and artifacts"},
        {"t": "p", "text": "setup-dotnet can cache NuGet. A path filter stops a docs-only change from deploying the API. An artifact is the published output you pass to a later job. Build once. Deploy that output. Do not build again on the production runner, or the bits can differ."},
        {"t": "code", "text": """on:
  push:
    branches: [main]
    paths:
      - "src/Orders.Api/**"
      - "tests/Orders.Tests/**"
      - ".github/workflows/orders-ci.yml"

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "10.0.x"
      - run: dotnet publish src/Orders.Api -c Release -o "$RUNNER_TEMP/api"
      - uses: actions/upload-artifact@v4
        with:
          name: orders-api
          path: ${{ runner.temp }}/api"""},
        {"t": "warn", "title": "What breaks", "text": "A workflow with on: pull_request and a deploy step will try to deploy every fork's code if you are not careful. Deploy jobs belong on a protected environment, on main, or on a manual workflow_dispatch. pull_request_target runs in the base repository and can see secrets. Do not check out the pull request head and run its scripts in that context. That is a secret leak."},
        {"t": "lead", "title": "Say this", "text": "Pull requests build and test. Main deploys the artifact those tests already built. Permissions start at read. I do not give a pull request workflow the production secret."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Point at trigger, permissions, job, and step in the workflow above.",
            "Say why the deploy is not in the pull request job.",
            "Name the risk of pull_request_target plus a checkout of the untrusted head.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 4 — TFS, Azure DevOps, and the words people mix"},
        {"t": "p", "text": "Outcome: you can translate TFS language into the current product, and you can say whether the team is on Git or TFVC, YAML or classic releases, Azure Repos or GitHub."},
        {"t": "h2", "text": "The family tree"},
        {"t": "p", "text": "Team Foundation Server was the on-premises server: work items, TFVC or Git, and XAML or classic builds. Microsoft renamed the server product to Azure DevOps Server. Azure DevOps Services is the same ideas, hosted by Microsoft, at dev.azure.com. A project contains boards, repos, pipelines, test plans, and artifacts. An organization contains projects. GitHub is not inside that box. A company can use GitHub for code and Azure DevOps for boards, or Azure Repos for code and Azure Pipelines for the build. Ask which combination they run before you design a second one."},
        {"t": "table", "headers": ["They say", "They usually mean", "What you prefer now"], "rows": [
            ["TFS", "Azure DevOps Server, or old habits", "Name the version. Do not assume the cloud."],
            ["TFVC", "Centralized version control, check-in", "Git, unless a tool still requires TFVC."],
            ["Gated check-in", "Build must pass before the check-in lands", "A pull request policy with a required build."],
            ["Build definition", "Classic visual build", "A YAML file in the repo."],
            ["Release definition", "Classic stages across environments", "YAML stages and an Azure DevOps environment with approvals."],
            ["VSTS", "The old cloud name", "Azure DevOps Services."],
        ]},
        {"t": "h2", "text": "Boards and the work the pipeline deploys"},
        {"t": "p", "text": "A work item is a user story, a bug, or a task. The pull request links to the work item so the board shows what shipped. That link is not a test. A story can move to Done while the slot swap failed. The lead habit is: the pipeline stage that deploys production is the moment the work is done, and the board follows that, or you will report features the customer cannot call."},
        {"t": "code", "text": """# Pull request description
AB#1842 Idempotent POST /orders

The unique key is (TenantId, IdempotencyKey).
Rollback: slot swap, schema change is a nullable column only."""},
        {"t": "p", "text": "AB#1842 is the Azure Boards link form many teams use. GitHub issues use a different link. The content that matters is the same: the work id, the decision, and how to undo it."},
        {"t": "h2", "text": "TFVC versus Git, in one minute"},
        {"t": "p", "text": "TFVC has one server history. A check-in is immediate on the server path. Branches are server folders and merges are heavier. Gated check-in shelves the changes and builds them before they become a changeset. Git clones the history. The pull request is the gate. New .NET work goes to Git. If the interview is about a TFS estate that is still TFVC, the migration plan is the same shape as the Framework strangler: one team, one repo, a date, and a freeze on new TFVC branches. You do not convert 80 repositories in a weekend."},
        {"t": "warn", "title": "What breaks", "text": "Calling Azure DevOps 'GitHub' in a design review and then writing a workflow file the server cannot run. A classic release that only one person can edit, with no file in the repo, so the deploy steps are invisible in the pull request that changed the app. TFVC cloaking and workspace mappings that omit the new test project, so CI is green because it never compiled the tests."},
        {"t": "lead", "title": "Say this", "text": "TFS is the old name for Azure DevOps Server. I ask whether code is Git or TFVC and whether the pipeline is YAML or a classic release. New work is Git and YAML, reviewed like application code."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Translate gated check-in, build definition, and release definition into Git words.",
            "Say which host you would pick if the company already pays for GitHub Enterprise, and what you would not rebuild.",
            "Write the three lines you want on every pull request: work id, decision, rollback.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 5 — Azure Pipelines YAML"},
        {"t": "p", "text": "Outcome: you can walk a multi-stage pipeline from pull request to a staging slot, and you can say which parts are not allowed to run on a fork."},
        {"t": "h2", "text": "Stages, jobs, and steps"},
        {"t": "p", "text": "A pipeline is the file, usually azure-pipelines.yml. A stage is a boundary you can approve, such as Build and then DeployStaging. A job is a unit of work on an agent. Steps are tasks or scripts inside the job. Jobs in a stage run in parallel unless you set dependsOn. Stages run in order when you set dependsOn. A deployment job is the kind that records a deployment to an environment. An ordinary job does not."},
        {"t": "code", "text": """trigger:
  branches:
    include: [main]
pr:
  branches:
    include: [main]

pool:
  vmImage: ubuntu-latest

variables:
  buildConfiguration: Release
  dotnetVersion: "10.x"

stages:
  - stage: Build
    jobs:
      - job: BuildTest
        steps:
          - task: UseDotNet@2
            inputs:
              packageType: sdk
              version: $(dotnetVersion)
          - script: dotnet restore Orders.sln
          - script: dotnet build Orders.sln -c $(buildConfiguration) --no-restore
          - script: dotnet test Orders.sln -c $(buildConfiguration) --no-build
          - script: dotnet publish src/Orders.Api -c $(buildConfiguration) -o $(Build.ArtifactStagingDirectory)/api
          - publish: $(Build.ArtifactStagingDirectory)/api
            artifact: orders-api

  - stage: DeployStaging
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: Slot
        environment: orders-staging
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: orders-api"""},
        {"t": "p", "text": "The pull request runs the Build stage because of the pr trigger. DeployStaging's condition requires main, so a pull request does not deploy. The environment orders-staging is where you attach an approval check if staging is shared. Production gets a stricter environment. The YAML in the repo is the review surface. A classic release edited in the browser is not in the pull request diff."},
        {"t": "h2", "text": "Variables, templates, and who can change them"},
        {"t": "p", "text": "A variable in the YAML is visible to anyone who can read the file. A secret variable or a variable group marked secret is masked. A variable group linked to Key Vault reads the secret at run time. Templates keep three services from copying the same build steps. A template is code. Review it like code. A parameter is the input. A variable is the value. Do not put the production connection string in a parameter default."},
        {"t": "code", "text": """# template: pipelines/dotnet-test.yml
parameters:
  solution: Orders.sln
steps:
  - script: dotnet test ${{ parameters.solution }} -c Release

# caller
steps:
  - template: pipelines/dotnet-test.yml
    parameters:
      solution: Orders.sln"""},
        {"t": "warn", "title": "What breaks", "text": "A condition that checks Build.SourceBranchName against main while the real value is refs/heads/main. The deploy never runs, or a looser check lets a pull request deploy. A template parameter inserted into a script without care becomes command injection if the value comes from a pull request title. Checkout of a pull request plus a secret variable on the same job publishes the secret if the PR can change the script."},
        {"t": "lead", "title": "Say this", "text": "Build on every pull request. Deploy only from main, as a deployment job, into an environment. The YAML is in the repo. Secrets are in a variable group or Key Vault, not in the file."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Mark the stage a pull request is allowed to run.",
            "Say what an environment approval is for.",
            "Explain why you publish the API in Build and download it in Deploy.",
        ]},
        {"t": "break"},
    ]
