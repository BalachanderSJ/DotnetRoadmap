# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Day 6 — The CI gate"},
        {"t": "p", "text": "Outcome: a pull request cannot merge when the tests fail, the solution does not build, or a migration was not reviewed. You can name the checks and the ones you will not pretend are security."},
        {"t": "h2", "text": "What the gate actually proves"},
        {"t": "p", "text": "Restore proves the packages resolve. Build proves the code compiles, including nullable warnings if you treat them as errors. Test proves the checks you wrote. It does not prove the ones you forgot. A formatting check proves whitespace. A dependency scan proves known vulnerable package versions, not a logic bug. A required reviewer on the migration folder proves a human saw the SQL. Stack those. Do not call the unit test job a security review."},
        {"t": "code", "text": """dotnet test Orders.sln -c Release --no-build ^
  --collect:"XPlat Code Coverage" ^
  --logger "trx;LogFileName=results.trx"

# Treat warnings as errors on the API project once the backlog is clear.
# A new warning fails the pull request. An old warning is a ticket, not a silent ignore."""},
        {"t": "p", "text": "Coverage is a conversation, not a trophy. A lead asks which money path is untested, not whether the number is 80. The idempotency test and the tenant isolation test are required. A test that only asserts the controller returns 200 with a fake that never touches the rule is not. Integration tests that need SQL run in CI against a container or a dedicated database, not against production."},
        {"t": "h2", "text": "Pull request policies"},
        {"t": "p", "text": "On Azure DevOps, a branch policy on main requires a build validation, a minimum number of reviewers, and optionally a comment resolution. On GitHub, a ruleset does the same with a required check. The build validation uses the YAML. The policy lives in the project settings, which is a gap: the YAML is reviewed in Git, the policy is clicked in the portal. Write the policy down in the repo README or a pipeline doc so a new project copies it. Reset votes when the source changes, or an approval survives a later commit that adds the token log."},
        {"t": "warn", "title": "What breaks", "text": "A pipeline that uses continueOnError on the test step. The check is green and the tests failed. A path filter that excludes the test project, so production code changes and the tests do not run. Commenting out a failing test to merge. That is a lead conversation, not a style nit."},
        {"t": "lead", "title": "Say this", "text": "The required check builds and tests. Reviewers cover auth, schema, and workflows. Coverage points me at the untested money path. A green build with continueOnError is not a gate."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "List four checks you would require on main, and one you would not call security.",
            "Say what you do when a test fails and the release is today.",
            "Find continueOnError in a sample and say what the board will show.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 7 — Continuous delivery to App Service"},
        {"t": "p", "text": "Outcome: you can deploy the artifact from Day 5 to a staging slot, smoke-test it, swap, and swap back. The schema change in the same release is still expand-only."},
        {"t": "h2", "text": "Build once, promote the artifact"},
        {"t": "p", "text": "The build stage publishes the API. Staging downloads that artifact and deploys it to the staging slot. Production swaps, or deploys the same artifact to the production slot after an approval. Nobody rebuilds between staging and production. A rebuild can pick up a newer package or a different commit if the trigger moved. The artifact name and the build id are what you write on the release ticket."},
        {"t": "code", "text": """- task: AzureWebApp@1
  displayName: Deploy to staging slot
  inputs:
    azureSubscription: sc-orders-nonprod
    appType: webApp
    appName: app-orders
    deployToSlotOrASE: true
    resourceGroupName: rg-orders
    slotName: staging
    package: $(Pipeline.Workspace)/orders-api/**/*.zip"""},
        {"t": "p", "text": "The task name and inputs drift by major version. The decision does not. The service connection is the Azure identity of the pipeline. The slot is staging. The package is the artifact, not a fresh publish. After deploy, hit /health/ready on the slot hostname. Then swap. Sticky settings stay with the slot. A staging connection string marked sticky by mistake means the smoke test hit the wrong database, or production starts using the staging database after the swap."},
        {"t": "h2", "text": "Approvals and the order of operations"},
        {"t": "p", "text": "The order is: migration as an expand, deploy to the slot, readiness, smoke, approval if a human must look, swap, watch the chart, leave the old bits on the other slot. The migration identity is not the App Service identity. The pipeline identity that deploys the zip is not automatically the identity that should run DDL. Split them. A manual approval on the production environment is how you stop a Friday deploy when the check is optional. It is not a substitute for the test gate."},
        {"t": "warn", "title": "What breaks", "text": "Swap before the migration, so the new bits read a column that does not exist. Swap after a destructive migration, so swap-back is a lie. Deploying the zip to production with no slot because slots felt like extra work, and then having no previous bits to return to. A smoke test that only checks that the process started, and never calls a real authenticated route."},
        {"t": "lead", "title": "Say this", "text": "One artifact, staging slot, readiness, then swap. Rollback is swap-back, and it is real only when the previous bits understand the current schema. Approvals sit on the environment. They do not replace tests."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Write the six steps from merge to swap, in order.",
            "Say which identity runs DDL and which identity the site uses.",
            "Name a smoke check that would catch a missing auth policy.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 8 — Functions, containers, and a small Bicep change"},
        {"t": "p", "text": "Outcome: the email function and the API do not share one pipeline stage by accident. You can show a small infrastructure change in source control."},
        {"t": "h2", "text": "A second artifact"},
        {"t": "p", "text": "The API zip and the function zip are different publish outputs. They can be two jobs in one pipeline or two pipelines with path filters. Path filters are how a README change avoids a production deploy, and how an email-only change avoids recycling the API. Each deploy uses its own identity. The function app's identity can send mail and complete Service Bus messages. It cannot alter the orders schema."},
        {"t": "code", "text": """- script: dotnet publish src/Orders.Email -c Release -o $(Build.ArtifactStagingDirectory)/email
- publish: $(Build.ArtifactStagingDirectory)/email
  artifact: orders-email

# Deploy with the function app task your org standardizes on.
# The decision: a different app, a different identity, the same build id."""},
        {"t": "h2", "text": "Containers when the host is not a zip"},
        {"t": "p", "text": "If the platform standard is Container Apps or App Service for containers, the artifact is an image, not a zip. The pipeline builds the image, pushes it to Azure Container Registry, and deploys the digest. A tag such as latest is not a version. The digest is. The same rule holds: build once, deploy that digest to staging, then to production. A Dockerfile that runs as root and copies secrets into a layer fails review even when the app starts."},
        {"t": "h2", "text": "Bicep for the change you can review"},
        {"t": "p", "text": "Clicking a slot in the portal does not show up in the pull request. A small Bicep file does. You do not need a full landing zone on this day. You need one resource the team can diff: the app, the staging slot, and the identity. What-if, or a plan, runs before the apply. Production apply sits on the production environment approval. Application code and infrastructure can be the same pipeline or a separate one. Separate is clearer when infrastructure changes are rare and dangerous. The application pipeline should not be able to delete the resource group."},
        {"t": "code", "text": """resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-orders'
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: true
      ftpsState: 'Disabled'
    }
  }
}"""},
        {"t": "p", "text": "The API version on the resource type changes. The properties you mean are httpsOnly, Always On, and a managed identity. Check the current template reference before you copy a year-old snippet into a real subscription. Bicep does not replace the expand/contract rule. An infrastructure change that renames the site is a new site, not a deploy."},
        {"t": "warn", "title": "What breaks", "text": "One pipeline that deploys the API, the function, and a full subscription template on every commit. A container tag latest moving under you after you thought production was frozen. A Bicep apply from a pull request build, so a fork or a feature branch edits production. Infrastructure apply belongs on main, behind the environment."},
        {"t": "lead", "title": "Say this", "text": "The API and the function are different artifacts and different identities. Images are deployed by digest. Infrastructure is a reviewed template, applied from main, and it cannot delete the estate because a developer pushed a branch."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Draw two artifacts from one build id.",
            "Say why latest is not a release.",
            "Name the pipeline permission you would refuse: contributor on the whole subscription.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 9 — Identity for pipelines"},
        {"t": "p", "text": "Outcome: you can draw the pipeline identity separately from the app identity, and you can explain OIDC so the workflow does not store a client secret."},
        {"t": "h2", "text": "Three identities, again, plus the pipeline"},
        {"t": "p", "text": "The user has a token. The API has a managed identity in the runtime SQL role. The migration has a different identity. The pipeline is a fourth. It must be allowed to deploy the app and, if it migrates, to apply DDL. Those can be two pipeline identities. Combining them means every build can change the schema. The deploy identity does not need to read customer tables."},
        {"t": "h2", "text": "Service connection and workload identity"},
        {"t": "p", "text": "In Azure DevOps, a service connection of type Azure Resource Manager is how the AzureWebApp task logs in. Workload identity federation uses a federated credential. There is no client secret to rotate in the variable group. The older service principal with a secret still works and still leaks when someone prints the variable or copies the connection. Prefer federation. Limit the connection to the resource group of the orders app, not the subscription, when the product allows that scope."},
        {"t": "h2", "text": "GitHub Actions and OIDC"},
        {"t": "p", "text": "GitHub requests a token for the job. Azure trusts that token when the subject matches the repository and the environment. The workflow asks for id-token: write. The login action exchanges the token. The federated credential subject includes the environment name when you bind it that way, so a pull request job that is not in the production environment cannot mint the production identity."},
        {"t": "code", "text": """permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}"""},
        {"t": "p", "text": "client-id is the application id, not a secret, though many teams still mask the tenant and subscription. The secret you eliminated is the client secret. Store nothing you can avoid. The federated credential's subject must match environment: production. A typo in either name fails closed, which is the failure you want."},
        {"t": "warn", "title": "What breaks", "text": "A client secret in a GitHub secret that every workflow in the repo can read. OIDC bound to the whole repository with no environment, so any branch workflow can deploy. Logging the Azure token to debug a 401. A service connection shared by every project in the organization, so a test app can deploy the orders API."},
        {"t": "lead", "title": "Say this", "text": "The pipeline has its own identity, federated, scoped to the resource group. Production deploy requires the production environment. There is no SQL password and no client secret in the YAML."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Name the four identities: user, API, migration, pipeline.",
            "Say what the federated subject checks.",
            "Explain why a pull request must not satisfy that subject.",
        ]},
        {"t": "break"},

        {"t": "h1", "text": "Day 10 — Release safety"},
        {"t": "p", "text": "Outcome: you can refuse a release that cannot roll back, and you can write the ticket a person on call can follow."},
        {"t": "h2", "text": "The release ticket"},
        {"t": "p", "text": "The ticket is short. Build id, artifact, schema change, smoke command, rollback, and who is watching. If any line is empty, the release waits. A dashboard link belongs on the ticket. A novel belongs in the pull request."},
        {"t": "code", "text": """Build: 2026.10.31.4
Artifact: orders-api from that build
Schema: add ExternalRef nvarchar(64) null
Smoke: GET /health/ready on the staging slot, then one authenticated GET /orders
Watch: p95 and SQL dependency for 20 minutes
Rollback: swap back to the previous slot
Blocked if: the migration drops or renames a column"""},
        {"t": "h2", "text": "Gates that are not theater"},
        {"t": "p", "text": "An approval from the person who wrote the change is a weak gate. An approval from the on-call owner, or a second team for schema, is a real one. An automated gate can query the health check after deploy and stop the swap. A manual approval with no checklist becomes a click. Write the checklist next to the environment. A lead removes a gate that everyone bypasses, or fixes the gate so it asks a question a human can answer."},
        {"t": "h2", "text": "When production is wrong after the swap"},
        {"t": "p", "text": "Look at the deploy marker and the chart before you read code. If the swap lines up and swap-back is safe, swap back. Then find the plan or the exception. This is the same sequence as the Azure day in the first roadmap. The new part is the pipeline evidence: the build id on the slot, the migration log, and the approval record. If you cannot find which bits are on the slot, the release process is not finished, even if today's incident ends."},
        {"t": "warn", "title": "What breaks", "text": "Hotfixing on the server and not committing it, so the next deploy restores the bug. Editing production app settings during the incident and forgetting they are not sticky, or that they are sticky and staging is now wrong. Declaring rollback impossible and then spending an hour on a forward fix while the error rate stays high."},
        {"t": "lead", "title": "Say this", "text": "The ticket names the artifact, the schema, the smoke check, and the rollback. If rollback is not real, the release is too big. After a bad swap I return to the previous bits first, then I diagnose."},
        {"t": "h2", "text": "Evening drill"},
        {"t": "b", "numbered": True, "items": [
            "Fill the release ticket for a nullable column and a slot swap.",
            "Say the first action when p95 jumps at the deploy marker.",
            "Name one gate you would delete because nobody can fail it honestly.",
        ]},
        {"t": "break"},
    ]
