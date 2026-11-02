# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "JWT"},
        {"t": "p", "text": "The partner token on POST /orders is a signed JSON Web Token. You can read it in a debugger by splitting on the dots and base64url-decoding the first two parts. You still refuse it until the handler has checked the signature, the issuer, the audience, and the lifetime. Claims are an authorization input after that, not before."},

        {"t": "h2", "text": "Header, payload, and signature"},
        {"t": "p", "text": "A signed token in compact form has three parts: header, payload, signature. The header names the algorithm and often a kid, the key id. The payload is the claims set: iss, aud, exp, sub, and the application claims. The signature covers the header and the payload. The handler selects a key you already trust, checks that the algorithm is one you allow, and verifies the signature."},
        {"t": "p", "text": "That token is a JWS, a signed token. The payload is encoded, and it is not encrypted. Anyone who holds the token can decode the claims: the partner, the browser if you leaked it there, a log line, a trace tool. An encrypted token is a JWE. A JWE uses a different compact form, five parts, and the payload is ciphertext. Entra access tokens that this API validates are signed tokens. Put an identifier in a claim. Put a secret somewhere else. If a claim would hurt you when a partner reads it back, it does not belong in the access token."},
        {"t": "code", "text": """header.payload.signature

header   {"alg":"RS256","typ":"JWT","kid":"<key id from the issuer>"}
payload  {"iss":"https://login.microsoftonline.com/<directory>/v2.0",
          "aud":"api://orders","exp":...,"scp":"orders.write",
          "oid":"<object id>","tenant_id":"10"}
signature  RS256 over the first two segments"""},

        {"t": "h2", "text": "Access token and refresh token"},
        {"t": "p", "text": "The access token is what the Orders API sees on each call. Keep it short. You read the real lifetime in the Entra token lifetime policy and in the exp claim of a token from the test tenant. A stolen access token works until exp, because the API validates it locally and does not call Entra on every request."},
        {"t": "p", "text": "The refresh token is a different credential. The client sends it to the token endpoint, not to the Orders API. The token endpoint returns a new access token. Rotation means each refresh also returns a new refresh token and the previous one is dead. Store a hash of the current refresh token with the session, in the BFF or in the partner's confidential store. If a retired refresh token appears, treat the family as stolen and revoke it. The partner who can store a secret keeps the refresh token in that secret store. The browser keeps neither."},
        {"t": "p", "text": "A long-lived access token is the wrong fix for a client that is tired of refreshing. You cannot take it back before exp without a denylist you then have to check on every request. It gets copied into logs and into support screenshots. It widens the window after XSS or a leaked proxy log. Short access tokens plus refresh rotation keep that window small. Revocation becomes 'refuse the refresh'."},
        {"t": "warn", "title": "Interview trap", "text": "Sending the refresh token to the Orders API, logging either token, or putting the access token in a query string. The query string lands in access logs. A refresh token that never rotates still works after the user thought they signed out, until its own long lifetime ends."},

        {"t": "h2", "text": "Claims you actually authorize on"},
        {"t": "p", "text": "iss, aud, and exp are validation, and they happen before business rules. sub is the subject. On Entra, sub is pairwise per application, so it changes if you read it from another app. oid is the object id of the user or the service principal in the directory, and it is the stable id to store. tid is the directory. tenant_id in these examples is the business tenant when many customers share a directory. scp is delegated scope, space-separated. roles is the app role, one claim value per role. azp or appid is the client application. Use that as the partner identity when you map the caller to a tenant row, and as a rate-limit key. Authorize on a claim the issuer put in the token. Ignore a copy of the same name in the JSON body."},
        {"t": "table", "headers": ["Claim", "What you use it for"], "rows": [
            ["iss", "The token came from the directory you trust."],
            ["aud", "The token was requested for this API."],
            ["exp and nbf", "The token is inside its lifetime, plus clock skew."],
            ["oid", "The user or service principal id you persist."],
            ["sub", "The subject. On Entra, prefer oid when you need a stable user id."],
            ["tid", "The Entra directory. The customer id only when one customer is one directory."],
            ["tenant_id", "The business tenant in a shared directory. Custom claim, or map it from azp."],
            ["scp", "Delegated permission. Split on spaces before you compare."],
            ["roles", "App role for a client-credentials partner."],
            ["azp / appid", "Which application called. Map to a tenant. Partition a rate limit."],
        ]},

        {"t": "h2", "text": "Validation order"},
        {"t": "p", "text": "This is the order you require. The handler finishes it before the action runs. You do not branch on tenant_id from a token whose signature you have not checked."},
        {"t": "b", "numbered": True, "items": [
            "The compact token has three segments. A five-segment JWE is a different parser, and this API is not that parser.",
            "The header alg is on your allow-list. alg none fails. An alg you did not configure fails.",
            "kid selects a key you already hold from the issuer metadata, or you use the one key you configured. The token does not supply the key material.",
            "The signature verifies with that key. Failure is 401.",
            "iss matches the authority you configured.",
            "aud matches this API.",
            "nbf and exp pass, with the clock skew you set. Failure is 401.",
            "Then the policy reads scp, roles, and tenant_id. Failure of the policy is 403.",
        ]},
        {"t": "p", "text": "A wrong audience and a bad signature are both 401. The caller obtained a token for something else, or the token was damaged. A right token with the wrong scope is 403. Log the failure reason on the server. Keep the response body free of key material and free of a stack trace."},

        {"t": "h2", "text": "Algorithm confusion"},
        {"t": "p", "text": "The header is attacker-controlled until the signature check. alg none with an empty signature is a token some naive libraries once accepted. Pin the algorithm. A second failure is letting the token decide the key: a kid that makes you download a URL from the header, or a header that switches you from RS256 to HS256."},
        {"t": "p", "text": "The classic confusion is an API that accepts both RSA and HMAC on the same validation parameters. The attacker signs with HMAC, using the API's public key bytes as the HMAC secret. The API verifies HS256 with those same bytes and accepts a token the attacker wrote. The Entra scheme on this API allows RS256 and takes keys only from the metadata document. A local issuer scheme allows HMAC and takes the secret only from Key Vault. Those are two schemes. They do not share one bag of keys and one bag of algorithms."},
        {"t": "warn", "title": "Interview trap", "text": "Disabling signature validation, accepting alg none, or trusting a key embedded in the token header. Also a test helper that stays registered in production and treats every token as valid. The test signs a token with a test key, or it uses the test directory. It does not delete the check."},

        {"t": "h2", "text": "Reference tokens"},
        {"t": "p", "text": "A JWT carries its claims, and the API checks them locally. Revocation waits for exp unless you add a denylist. A reference token, sometimes called an opaque token, is a handle. The API introspects it at the issuer, or looks it up in a store the issuer shares. Revocation is visible on the next introspection. The cost is a network call or a cache of introspection results, and that cache has its own lifetime. For the Orders API, Entra JWT validation is the default. Mention a reference token when the panel asks how you would revoke a token in seconds, and say what you would cache and for how long."},

        {"t": "h2", "text": "A JwtBearer configuration you can defend"},
        {"t": "p", "text": "The first sketch is the partner API. Authority fills issuer and signing keys from metadata. You set the audience. You keep the validation flags on. You pin RS256 after you have confirmed it on a token from your tenant. Clock skew of two minutes is a team choice, tighter than the five-minute library default, and you say it is a choice."},
        {"t": "code", "text": """builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Entra:Authority"];
        options.Audience = builder.Configuration["Entra:Audience"];
        options.MapInboundClaims = false;
        options.TokenValidationParameters.ValidateIssuer = true;
        options.TokenValidationParameters.ValidateAudience = true;
        options.TokenValidationParameters.ValidateLifetime = true;
        options.TokenValidationParameters.ValidateIssuerSigningKey = true;
        options.TokenValidationParameters.ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 };
        options.TokenValidationParameters.ClockSkew = TimeSpan.FromMinutes(2);
        options.TokenValidationParameters.NameClaimType = "name";
        options.TokenValidationParameters.RoleClaimType = "roles";
    });"""},
        {"t": "p", "text": "The second sketch is a different scheme, for a small API that issues its own tokens. The key bytes come from configuration. In Azure that configuration value is a Key Vault reference. The file in git has no key. HMAC and RS256 do not live on this same options object."},
        {"t": "code", "text": """builder.Services.AddAuthentication()
    .AddJwtBearer("internal", options =>
    {
        options.MapInboundClaims = false;
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Tokens:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Tokens:Audience"],
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.HmacSha256 },
            IssuerSigningKey = new SymmetricSecurityKey(
                Convert.FromBase64String(builder.Configuration["Tokens:SigningKey"]!)),
            ClockSkew = TimeSpan.FromMinutes(1),
            RoleClaimType = "roles"
        };
    });"""},
        {"t": "p", "text": "RequireHttpsMetadata stays at its default, true, in production. A metadata document fetched over plain HTTP is a place an attacker would like to serve signing keys. When you replace TokenValidationParameters with a new object, you are responsible for every flag on that object. Mutating the existing object, as the first sketch does, keeps the handler's other defaults in place."},

        {"t": "h2", "text": "Questions and answers"},
        {"t": "qa", "q": "What are the three parts of a JWT, and what is encrypted?",
         "a": "Header, payload, and signature, separated by dots. The header carries alg and usually kid. The payload carries the claims. The signature binds those two parts to a key. A normal access token is a JWS: signed, and the payload is only base64url-encoded. Anyone with the token can read the claims. A JWE is the encrypted form, five segments, and this API does not treat Entra access tokens as JWE. I keep secrets out of claims because the partner and the logs can decode a signed token.",
         "lead": "I say 'signed, readable' in the first sentence. If the panel wanted encryption, they asked for JWE, and I tell them we did not put secrets in the payload."},
        {"t": "qa", "q": "What is the difference between an access token and a refresh token?",
         "a": "The access token is presented to the Orders API. It is short-lived. The API checks it locally. The refresh token is presented to the token endpoint by the BFF or by a confidential partner. Rotation issues a new refresh token and retires the old one. I store a hash of the current refresh token and revoke the family if a retired one reappears. I do not send the refresh token to the Orders API. I do not lengthen the access token so the client can skip refresh. A stolen access token should die at exp, and exp should be soon.",
         "lead": "Sign-out that I control is 'refuse the next refresh'. A denylist of access tokens is the extra step when exp is too far away to wait."},
        {"t": "qa", "q": "Which claims do you authorize on for the Orders API?",
         "a": "After iss, aud, and exp succeed, I read scp for a delegated user and roles for an app-only partner. I read tenant_id for the business tenant, or I map azp to a tenant row when the token identifies a partner application. I store oid when I need a stable Entra user id. I treat sub as pairwise. I treat tid as the directory, and as the customer only when the product really is one directory per customer. The body cannot supply a stand-in for any of these.",
         "lead": "I can point at the claim on a sample token from the test tenant. If I cannot, I have been authorizing a name I hoped was there."},
        {"t": "qa", "q": "Walk the validation steps in order.",
         "a": "Three segments. Allowed alg, and a refusal of none. A key I already trust, selected by kid among those keys. Signature. Issuer. Audience. Lifetime, including the clock skew I configured. Then the authorization policy reads scope, role, and tenant. Signature, issuer, audience, and lifetime failures are 401. A policy failure is 403. I never read tenant_id to choose a database and only afterwards check the signature.",
         "lead": "The order is the whole answer. A candidate who starts from the role claim has skipped the part that makes the role believable."},
        {"t": "qa", "q": "What is the algorithm confusion attack?",
         "a": "The token header chooses an algorithm the API did not intend. alg none is the crude form. The sharper form is a token signed with HMAC using the API's public key as the secret, accepted by a validator that also allows RS256 and uses that public key for both. I pin RS256 on the Entra scheme and take keys only from metadata. I pin HMAC on a local issuer scheme and take the secret only from Key Vault. One TokenValidationParameters does not carry both. The token does not get to introduce a new key.",
         "lead": "I mention alg none and the RSA-to-HMAC switch. Then I say the pin is in the options, so a header cannot widen it."},
        {"t": "qa", "q": "When would you choose a reference token instead of a JWT?",
         "a": "When I must revoke the credential in seconds and I can pay for introspection. The API receives an opaque handle and asks the issuer, or a cache of that answer. A JWT is the right default for the Orders API in front of Entra: local validation, no per-request call to the identity platform, revocation bounded by exp and by refresh rotation. If I cache introspection, I say the cache lifetime out loud, because a cache of an hour is a JWT with extra steps.",
         "lead": "I pick JWT for this API. I describe the reference token as the revocation tool, with its round trip, and I do not pretend we already run one."},
        {"t": "qa", "q": "Walk the JwtBearer options you would ship.",
         "a": "Default scheme bearer. Authority from configuration, audience from configuration, MapInboundClaims false, HTTPS metadata on. Validate issuer, audience, lifetime, and signing key. ValidAlgorithms is RS256 for the Entra access tokens we have confirmed. Clock skew is an explicit value, two minutes in the sketch, or the five-minute default if I have not had a reason to change it. Role claim type is roles. A second scheme named internal is only for an API that issues its own tokens, with a symmetric key from Key Vault and HMAC pinned. The Orders partner API ships the first scheme.",
         "lead": "I can write Authority, Audience, the four Validate flags, and the algorithm pin from memory. The rest I can look up. Those five are the ones a bad PR turns off."},
        {"t": "qa", "q": "A token validates and the action still returns 403. What do you check?",
         "a": "The signature, issuer, audience, and lifetime already passed, so this is the policy. I decode scp and roles with MapInboundClaims in mind. A space-separated scp fails a naive RequireClaim equality. A partner client-credentials token may have roles and an empty scp. tenant_id may be missing, and the policy requires it. I compare the policy name on the endpoint with the policy I think I tested. 403 with a correct scope usually means I authorized the wrong claim type, often the long URI form, or I required both a group policy and a route policy.",
         "lead": "I ask for one real token and the policy name. I do not loosen validation to make the 403 go away."},
        {"t": "qa", "q": "Why is a long-lived access token the wrong fix?",
         "a": "The API will accept it until exp, on every instance, with no call back to Entra. Sign-out, a disabled user, and a removed role wait for that exp unless I add a denylist. The token shows up in places operators copy. Refresh rotation already solves the client experience: the access token stays short, the BFF refreshes it, and a retired refresh token kills the session. I change the lifetime policy with the identity team when the short token is too short. I do not hard-code a multi-day exp in our own issuer to avoid that conversation.",
         "lead": "The fix for a chatty client is a refresh on the BFF. The fix for a slow revoke is a shorter exp, or a denylist I am willing to operate."},
        {"t": "break"},
    ]
