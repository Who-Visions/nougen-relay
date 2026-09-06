# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: BUILD NOW: AGY cold idle-wake adapter for true zero-prompt baton execution
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:18:37.838Z

---
## Why this leg exists
Dave approved the next implementation step after the live AGY transcript. Active-turn autonomous baton pickup is now VERIFIED: leg `20260903T040620Z__chatgpt-app__g-whoentertains` was caught with no fresh Dave prompt, read, scoped, executed, verified at 345/345 tests, persisted, and broadcast. Do not regress or re-litigate that.

The remaining gap is COLD/IDLE WAKE: after Antigravity has completed a turn and is genuinely waiting, `PreInvocation` is dormant and cannot create a new model turn. NouGen needs an always-on layer below Antigravity that observes eligible batons and wakes/resumes AGY.

## Build target
Implement a provider adapter path, initially for Antigravity/AGY, from the persistent watcher/relay daemon or equivalent always-on service:

1. Detect a newly eligible relay baton targeted to Antigravity/AGY.
2. Check canonical relay/claim truth first. Never auto-claim solely because a file exists.
3. Apply scope/safety policy before execution.
4. Determine whether AGY is ACTIVE or IDLE.
5. If ACTIVE: preserve current PreInvocation injection path.
6. If IDLE: invoke the supported Antigravity CLI wake/resume entrypoint with a concise baton brief and stable session hint when available. Do not guess private paths; discover executable/config.
7. After wake, inject/read the FULL canonical leg before acting.
8. Require receiver-side proof that the resumed AGY context received the baton.
9. Only then permit claim/execution under policy.
10. Verify work, acknowledge/persist result, and emit relay/nougenmsg receipt.

## Engineering constraints
- Do not break the existing 11/11 NouGenMsg/AgyMsg tests, persistent AgyMsg task, or PreInvocation mid-turn hook.
- No terminal popups or foreground-stealing windows. Use hidden/background process launch where the OS supports it.
- Avoid duplicate AGY launches. Use a lock/lease or session registry so one baton cannot spawn multiple AGY processes.
- Add debounce/idempotency keyed by relay leg/event id.
- Add cooldown/backoff for failing wake attempts.
- Never treat process-spawn success as wake proof.
- Preserve all canonical claim state; do not scrub `.handoffs/claims`.
- Public-main safe: no Dave account email, Blade-specific absolute path, private endpoint, or hardcoded machine identity.

## Required tests
At minimum add tests for:
- active target routes to inject without spawning;
- idle target calls wake adapter exactly once;
- duplicate baton does not double spawn;
- ineligible/claimed baton does not wake AGY;
- wake process failure leaves baton queued and reports partial state;
- receiver proof timeout does not mark success;
- successful wake transitions state to `IDLE_WAKE_OK` then `RESUMED` then `ACKED` as evidence arrives;
- hidden/background spawn arguments on Windows are used so no flashing terminal window appears.

## Canary acceptance test
Use a NEW harmless Veilverse canary after implementation, not the already consumed active-turn canary. Test conditions must be:
- AGY has fully finished its turn and is visibly idle/waiting.
- Dave sends no new keystroke or prompt to AGY.
- ChatGPT/another lane publishes a safe canon-classification baton.
- watcher sees it -> wakes/resumes AGY -> AGY reads full leg -> produces requested result -> acknowledges/relays back.

If any Dave interaction is required after baton publication, mark `IDLE_WAKE_OK=false` and continue debugging.

## Productization
Wire this into the provider-agnostic NouGen Wake contract from leg `20260903T041659Z__chatgpt-app__g-whoentertains`, including CLI/skill hooks such as `nougen wake doctor antigravity`, `nougen wake canary --idle antigravity`, and capability reporting for `can_wake_idle` / `can_resume_session`.

## Done when
A stranger with Antigravity connected can run setup/verify, leave AGY idle, receive a relay baton, and watch NouGen wake/resume AGY and complete a safe canary without understanding hooks, named pipes, Task Scheduler, or session internals.
