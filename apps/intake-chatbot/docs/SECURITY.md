# Security and Privacy

## Scope

This is an internal research and governance-documentation tool. It is not a
clinical decision system and does not claim HIPAA compliance or institutional
approval for PHI. Deployment owners remain responsible for security review,
access policy, retention, audit, and incident response.

## Trust Boundaries

- User messages and imported documents are untrusted input.
- LLM responses are untrusted candidate patches.
- AGENT-O ontology, profiles, and SHACL shapes are trusted read-only inputs.
- The backend is the only component permitted to contact the LLM gateway.
- The browser receives no gateway credentials, client secrets, or OAuth tokens.

## Implemented Controls

1. Remote binds require `APP_ACCESS_TOKEN` unless an administrator explicitly
   sets `ALLOW_INSECURE_BIND=true`.
2. The frontend stores the application access token in session storage and
   sends it in an Authorization header, never a URL query.
3. Credential files are read only at runtime and are ignored by Git patterns.
4. Error redaction removes bearer tokens, client secrets, access tokens, and API
   keys before an error may reach application text.
5. Application logs do not log message bodies, prompts, responses, or secrets.
6. Markdown output is sanitized with `rehype-sanitize`; imported code is never executed.
7. CSP blocks external scripts, objects, framing, inline scripts, and inline styles.
8. Imports use a filename-only rule, extension allow-list, and byte limit.
9. Candidate operations require an exact evidence span from the current message.
10. The deterministic patch engine rejects unknown fields, subject mismatches,
    predicate mismatches, object-kind mismatches, datatype mismatches, invalid
    literal lexical forms, and ontology URIs outside the allow-list.
11. A savepoint prevents a malformed multi-operation LLM response from leaving
    a partially applied patch. The user's message remains available for retry.
12. Imported assertions require human confirmation before they become Present.

## Credential Configuration

The institutional gateway adapter may read an authorized JSONL credential source through
`AGIGEE_CREDENTIALS_PATH`. Never print, inspect wholesale, copy, package, or
commit that file. Configure endpoint values in a protected environment file:

```text
LLM_PROVIDER=agigee_openai_compatible
LLM_MODEL=<deployment-name>
LLM_CREDENTIAL_ALIAS=<approved-record-alias>
LLM_BASE_URL=<institutional-gateway-base>
LLM_TOKEN_URL=<institutional-oauth-token-url>
LLM_API_VERSION=<approved-api-version>
```

The default `LLM_PROVIDER=mock` performs no network call.

## Healthcare Data

The interface warns users not to enter patient identifiers or PHI unless the
deployment is approved. For any approved sensitive-data deployment, use TLS,
institutional identity/access controls, encrypted storage, protected backups,
restricted filesystem permissions, approved retention, and institutionally
managed logging. The built-in bearer-token gate is a minimal internal-pilot
control, not a replacement for enterprise authentication.

## Secret Scan Before Commit

Run the repository scanner. It reports only filename, line number, and rule;
it never prints a candidate value:

```bash
make secret-scan
```

The scanner checks all tracked and unignored candidate files for sensitive
filenames, private-key material, and literal secret assignments while allowing
explicit synthetic placeholders used by tests. Also inspect `git status` and
the exact staged diff before committing. Never weaken `.gitignore` to publish
local runtime data.

## Reporting a Security Issue

Stop the service, preserve non-sensitive logs and version information, rotate
potentially exposed tokens through the institutional owner, and notify the
project/security contact through the approved internal channel. Do not place
credentials, PHI, or exploit details in a public issue.
