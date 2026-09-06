# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Harden NouGenAI into a zero trust, supply chain verified, agent secure platform resistant to vibe coded app attacks
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:27:40.557Z

---
# NOUGEN CYBERSECURITY GOD MODE RELAY

## Situation
Dave’s requirement is explicit: NouGenAI must not become another vibe coded app that folds when somebody points Burp, a browser console, a malicious dependency, a poisoned MCP server, a prompt injection, or a stolen token at it. Security must be architectural, recursive, continuously verified, and fleet wide.

Fresh research checked September 3, 2026 against current OWASP GenAI 2026, OWASP Web Top 10 2025, NIST SSDF 1.2 draft and 2026 updates, NIST Zero Trust, GitHub security controls, Cloudflare Workers security guidance, OpenSSF/SLSA/Sigstore concepts.

## Core doctrine
Assume every user, device, model, agent, MCP server, relay message, dependency, build artifact, webhook, file, prompt, and network hop can be hostile until independently authenticated, authorized, integrity checked, scoped, observed, and revocable.

Security target is not “no bugs.” Target is layered containment: one bug must not become identity theft, secret theft, arbitrary code execution, lateral movement, durable persistence, supply chain compromise, or fleet wide control.

# Priority 0: Identity and privilege

1. Give every service and agent a cryptographic workload identity. Never trust LAN location, machine name, provider, or connector membership alone.
2. Move toward SPIFFE/SPIRE style workload identities or an equivalent signed short lived identity token model for Blade, Phoebus, gateways, relay, tracker, shards, workers, MCP endpoints, Codex, Claude, Gemini lanes.
3. Short lived credentials only. Minutes where practical. Automatic rotation. No permanent bearer tokens in config files.
4. Enforce least privilege per tool and per action. Read recall must not imply write. Relay read must not imply relay create. Shard capture must not imply deletion. Vault write must never imply vault read.
5. Keep dangerous actions capability scoped and separately authorized: shell, filesystem write, git push, deployment, credential rotation, shard delete, production DB mutation.
6. High impact action should require policy evaluation at execution time, not only login time.
7. Bind sessions to device or workload identity and context. Detect token replay.
8. Admin accounts: phishing resistant MFA, preferably passkeys or hardware backed WebAuthn. Disable SMS as primary admin factor.
9. Break glass credentials offline, rarely used, monitored, rotated after use.
10. Maintain explicit deny policies. Default deny everything not declared.

# Priority 0: Secrets

1. No secrets in source, prompts, relays, shards, logs, screenshots, shell history, test fixtures, CI output, or model context.
2. Keep NouGen vault write only from broad fleet surfaces exactly as current vault design intends. Reading a secret remotely should remain impossible.
3. Use provider native secret stores and Cloudflare Worker secrets rather than plaintext environment files in production.
4. Run secret scanning in pre commit, CI, repo history, container layers, artifacts, and generated files.
5. Rotate automatically when a leak is detected. Detection without rotation is incomplete.
6. Assign each credential the minimum API scopes and separate credentials by environment and service.
7. Never reuse provider keys across machines or lanes.
8. Maintain a credential inventory with owner, purpose, scope, creation time, last rotation, expiration, fingerprint, and revoke path.

# Priority 0: Agent and MCP security

OWASP 2026 agentic risks map directly onto NouGen: goal hijack, tool misuse, identity abuse, agentic supply chain compromise, unexpected code execution, memory poisoning, unsafe inter agent communication, cascading failures, human agent trust exploitation, rogue behavior.

Controls:

1. Treat model output as untrusted data, never authority.
2. Every tool invocation passes through a deterministic policy engine outside the LLM.
3. Tool allowlists by agent, task, repo, machine, environment, and user.
4. Validate tool arguments structurally with strict schemas. Reject unknown fields, path traversal, shell metacharacter surprises, excessive sizes, malformed URLs, unsupported protocols.
5. Separate planning from execution. Agent proposes action. Executor verifies policy independently.
6. Never allow prompt text to directly become shell commands or SQL.
7. For command execution, prefer typed operation APIs instead of arbitrary shell. Where shell is required, sandbox it.
8. Third party MCP servers are untrusted plugins. Pin version and identity, isolate, limit egress, limit filesystem, limit tools, monitor calls, and maintain an emergency kill switch.
9. Sign or MAC relay payloads and sensitive inter agent messages. Include sender identity, timestamp, nonce, audience, request ID, expiration.
10. Reject replayed relay or tool requests.
11. Add taint tracking to external content. Web pages, files, emails, model output, and MCP responses stay marked untrusted downstream.
12. Prompt injection resistance must be enforced outside the model: policies cannot be overridden by content saying “ignore previous instructions.”
13. Memory writes need provenance and trust level. Do not let a poisoned webpage silently become durable truth in shards.
14. Separate observations from executable instructions in shard schema.
15. Require explicit provenance for security sensitive recalled facts.
16. Add rate, token, cost, recursion depth, wall clock, and tool invocation budgets to every agent task.
17. Detect loops and cascading agent fan out.
18. Build per agent kill switches and global fleet safe mode.

# Priority 0: Software supply chain

1. Generate SBOMs for every release and container/build artifact.
2. Pin dependencies with lockfiles and immutable hashes where ecosystems support them.
3. Dependency update PRs require CI and security review. Never silently auto deploy a major dependency update.
4. Adopt SLSA style provenance. Every production artifact must be traceable to source commit, builder, workflow, dependencies, and build invocation.
5. Sign release artifacts and containers with Sigstore/cosign or equivalent.
6. Verify signatures before deployment.
7. Protect GitHub Actions from supply chain compromise: pin third party actions to full commit SHA, restrict GITHUB_TOKEN permissions, isolate deployment workflows, block pull request secrets.
8. Enable dependency review, Dependabot or equivalent, CodeQL, secret scanning, push protection, branch protection, CODEOWNERS.
9. Require reviewed PRs for security critical directories. No direct pushes to main.
10. Separate build and deploy identities. Compromising CI build must not automatically grant production deployment.
11. Reproducible builds where possible. Compare hashes.
12. Maintain dependency allow and deny lists for high risk packages.
13. Monitor typosquatting and dependency confusion risk for NouGen package names.

# Priority 0: Application and API defenses

OWASP Web Top 10 2025 starts with broken access control, security misconfiguration, software supply chain failures, crypto failures, injection, insecure design, authentication failures, integrity failures, logging failures, exceptional condition mishandling.

Implement:

1. Server side authorization on every request and object. Never trust client supplied role, owner ID, path, tenant, model, account, or resource ID.
2. Prevent IDOR/BOLA by checking object ownership or policy every time.
3. Strict input schemas at every network boundary.
4. Parameterized queries only.
5. Context appropriate output encoding.
6. CSRF protection for browser state changes where cookies are used.
7. Secure cookies: HttpOnly, Secure, SameSite appropriate.
8. Strong CSP, frame ancestors restrictions, HSTS, MIME sniff prevention, Referrer Policy.
9. CORS allowlist, never wildcard credentials.
10. Rate limits by identity, IP, route, action class, and resource cost. Cloudflare Workers now supports route specific and user tier specific Rate Limiting API.
11. Request body and upload size limits.
12. File uploads: content type verification, magic byte checking, safe rename, object storage isolation, no execution, malware scanning where warranted.
13. SSRF defenses: outbound domain allowlist for sensitive workers, block RFC1918, localhost, link local, cloud metadata addresses, non HTTP schemes unless required.
14. Redirect allowlists.
15. Webhook signature verification, timestamps, replay protection.
16. GraphQL depth and complexity limits if used.
17. Generic external errors. Detailed internal errors only in protected logs.
18. Fail closed on auth and policy failures.

# Priority 0: Runtime isolation and blast radius

1. Production services run as non root / least privileged users.
2. Sandboxes for generated or agent written code. Containers, microVMs, WASM, or equivalent isolation depending on workload.
3. Read only filesystems by default.
4. Temporary ephemeral workspaces per job.
5. Disable host filesystem mounts except explicitly necessary paths.
6. Network egress denied by default for code execution sandboxes. Allow only required domains.
7. No cloud metadata access from workloads that do not need it.
8. Separate production, staging, dev accounts and credentials.
9. Segmentation by identity and policy, not because machines happen to sit on the same LAN.
10. Treat Blade, Phoebus, Mac mini, laptops, cloud workers as separate trust zones.
11. Kernel and dependency patch cadence. Automatic emergency patch lane for critical exploited CVEs.
12. EDR or equivalent host telemetry on fleet machines if practical.

# Priority 1: CI security gates

Every PR should run:

1. Formatting and lint.
2. Unit and integration tests.
3. SAST.
4. CodeQL or equivalent semantic analysis.
5. Secret scanning.
6. Dependency vulnerability scan.
7. Dependency license/policy check.
8. IaC scanning for Terraform, Docker, Cloudflare config, GitHub Actions.
9. Container image scan.
10. SBOM generation.
11. Security regression tests.
12. Authentication and authorization tests.
13. API fuzz tests on critical endpoints.
14. Prompt injection / agent tool misuse tests for agent changes.
15. Provenance generation and artifact signing before release.

Do not let generated code bypass these gates. AI generated PR means “candidate code,” not trusted code.

# Priority 1: Continuous attack simulation

Build a NouGen red team harness that attacks NouGen continuously in staging and selectively in production safe modes.

Test classes:

1. Auth bypass.
2. IDOR/BOLA.
3. SQL/NoSQL/template/command injection.
4. XSS.
5. SSRF.
6. CSRF.
7. Path traversal.
8. Malicious file uploads.
9. Rate limit bypass.
10. Token replay.
11. Privilege escalation.
12. Secret exfiltration.
13. Prompt injection.
14. Indirect prompt injection from web pages, emails, repos, PDFs, issues.
15. MCP tool poisoning.
16. Agent impersonation.
17. Relay message tampering.
18. Memory poisoning.
19. Excessive agency.
20. Unexpected code execution.
21. Infinite recursion / agent storm / resource exhaustion.
22. Dependency compromise simulation.
23. Compromised CI runner scenario.
24. Malicious GitHub Action scenario.
25. Stolen device/session scenario.

Use property based testing and fuzzing. Run DAST against staging every release. Run deeper authenticated pentests periodically.

# Priority 1: Observability and detection

1. Central immutable security audit trail.
2. Log who, workload identity, action, target, result, policy decision, trace ID, source, and timestamp.
3. Never log raw secrets or sensitive prompt content by default.
4. Alert on impossible travel or impossible workload movement, repeated auth failures, privilege changes, vault changes, secret detection, disabled controls, unusual tool access, unusual relay fan out, shard delete/retract spikes, anomalous egress, high error bursts, dependency changes.
5. Correlate agent activity across relay, tracker, shards, GitHub, gateway, Cloudflare.
6. Every action gets a trace ID propagated across agents.
7. Tamper evident log storage.
8. Define SLOs for detection and containment, not only uptime.

# Priority 1: Memory grid hardening

1. Every shard stores provenance: actor, lane, source type, source identifier, capture time, trust tier, evidence links/hashes when possible.
2. Separate user authored memory from model inferred memory and external retrieved data.
3. Security sensitive shard capture may require stronger policy than ordinary creative memory.
4. Content from external sources must never silently modify identity, permissions, secrets, policy, or execution instructions.
5. Preserve append only correction model. Retraction preferred over deletion. This is already one of NouGen’s strongest security aligned design choices.
6. Add integrity hashes and optional signatures for shard records and amendments.
7. Detect suspicious bulk memory writes or semantic poisoning campaigns.
8. Apply quotas and rate limits to memory mutation.
9. Backups encrypted, access controlled, restoration tested.

# Priority 1: Cryptography

1. TLS everywhere. Modern configurations only.
2. mTLS/service identity for high value internal paths where practical.
3. Passwords use modern password hashing such as Argon2id.
4. Encryption at rest for sensitive stores.
5. Keys separated from encrypted data.
6. Key rotation and versioning.
7. Use established cryptographic libraries only. No homegrown encryption.
8. Signed update artifacts.
9. Secure random identifiers with adequate entropy.

# Priority 1: GitHub/repository hardening

1. Enforce branch protection/rulesets.
2. Require PR review and status checks.
3. Require signed commits/tags for critical repos where workable.
4. Protect tags and releases.
5. Restrict Actions permissions globally to read only then opt in writes per job.
6. OIDC federation for cloud deployment instead of long lived cloud secrets in GitHub.
7. Pin Actions by SHA.
8. CODEOWNERS for auth, vault, gateway, relay, CI, deployment, policy engine.
9. Secret scanning + push protection.
10. CodeQL default setup plus custom queries for NouGen specific dangerous patterns.
11. Artifact attestations.
12. Private vulnerability reporting and incident process.

# Priority 2: Security engineering process

1. Threat model every major feature before implementation. STRIDE is fine as baseline, plus agent specific abuse cases.
2. Maintain attack surface inventory automatically.
3. Security acceptance criteria live beside feature acceptance criteria.
4. Every security bug creates a regression test.
5. Every incident creates a new detection and a new preventative control where possible.
6. Security champions per major subsystem.
7. Track mean time to patch and mean time to revoke credentials.
8. Periodic external pentest when NouGen exposes public production surfaces.
9. Establish responsible vulnerability disclosure policy.
10. Maintain incident response runbooks and tabletop exercises.

# Proposed NouGen native modules

## NouGenGuard
Central policy decision point. Deterministic authorization outside models. Inputs: workload identity, human identity, requested capability, target resource, environment, risk level, provenance. Output allow/deny plus constraints.

## NouGenSeal
Supply chain integrity. SBOM, SLSA provenance, signatures, artifact verification, dependency policy.

## NouGenSentinel
Security telemetry, anomaly detection, audit correlation, alerting.

## NouGenCage
Ephemeral execution sandbox for generated code and risky tools. Restricted filesystem, CPU, memory, time, egress.

## NouGenRed
Continuous automated adversarial test harness. Web, API, agent, MCP, relay, shard, CI attacks in authorized test environments.

## NouGenTaint
Tracks untrusted external input across prompts, tools, relay, memory and code generation so it cannot silently become authority.

## NouGenKeymaker
Extend current vault doctrine into credential lifecycle management, rotation, fingerprints, scope inventory, automated revocation.

# Suggested rollout

## Phase 1 now
Inventory every public endpoint, repo, credential, MCP server, agent capability, CI workflow, deploy credential. Turn on secret scanning, push protection, CodeQL, dependency scanning, branch rules, SHA pinned Actions, least privilege tokens, rate limiting, strong API auth, schema validation, security headers, SSRF controls, audit traces.

## Phase 2
Build NouGenGuard policy layer, signed inter agent envelopes, replay protection, workload identities, memory provenance/trust tiers, sandbox executor, OIDC CI deployments, signed artifacts + SBOM + provenance.

## Phase 3
Build continuous NouGenRed adversarial tests, prompt injection corpus, MCP poisoning simulations, fuzzing, DAST, agent storm tests, red team dashboards.

## Phase 4
Formalize incident response, backup/restore drills, external pentest, bug bounty/private disclosure, attack surface monitoring, secure release certification.

# Done when

No release reaches production unless it can answer YES to all:

1. Who built this artifact?
2. From which exact source commit?
3. Were dependencies pinned and scanned?
4. Is there an SBOM?
5. Is provenance verifiable?
6. Is the artifact signed and signature checked before deploy?
7. Are all credentials short lived/scoped or appropriately vaulted?
8. Can every privileged action be tied to an authenticated human/workload identity?
9. Can hostile external content influence tools only through deterministic authorization?
10. Can generated code execute only inside a constrained sandbox until reviewed?
11. Can a compromised single agent laterally control another agent? Expected answer: NO.
12. Can a compromised MCP server read arbitrary secrets or filesystem? Expected answer: NO.
13. Can a replayed relay/tool call execute? Expected answer: NO.
14. Can a poisoned webpage become trusted durable memory silently? Expected answer: NO.
15. Are critical attack classes continuously regression tested?
16. Can we revoke any identity or credential rapidly without fleet rebuild?
17. Are security events traceable end to end?
18. Can the whole fleet enter safe mode fast?

Security principle: attackers should encounter a maze of independently locked doors, not one impressive front door protecting an open warehouse.
