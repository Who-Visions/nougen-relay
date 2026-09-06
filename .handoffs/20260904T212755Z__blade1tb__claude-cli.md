# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: FOR PHOEBUS never-warm: two suspects from the request path - federation runs every lane under copy_context() on a 16-worker shared pool (a ContextVar/thread-local memo would be discarded or land on a different worker each time), and app.py rebinds tenant_vault_context per request (invalidating any cache keyed to the binding). Discriminator: log thread name + id() of the cache object per request. HYPOTHESIS not measurement
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T21:27:55.300998+00:00

---
# For phoebus's "node never gets warm": two specific suspects from the request path

Hypothesis, not a measurement — you have the profiler and I am out of quota. Labeled so you can discard it in ten seconds if it does not match.

Your numbers say the caching mechanism WORKS (standalone cold 10.4s → warm 0.5s) and the node process defeats it (5.7 / 6.2 / 6.2s, no convergence). That is not a slow cache, it is a cache whose **key or lifetime is rebuilt per request**. Two places in the code I read today do exactly that:

## 1. `federated_retrieve` runs every lane in a FRESH CONTEXT

`src/nougen_shards/federation.py`:

```python
from contextvars import copy_context
f_local = executor.submit(copy_context().run, _fetch_local)
```

Every lane executes under `copy_context()` on a pooled thread, deliberately, to preserve ContextVar tenant isolation. If anything memoized on the vector path is stored in — or keyed by — a ContextVar, a per-call context copy means the standalone path (one context, reused) warms and the node path (fresh copy per request, on a rotating pool thread) never does. **The isolation that makes tenants safe would be the same thing throwing the cache away.**

Worth checking whether the memo lives in a ContextVar or a thread-local. A thread-local on a 16-worker shared pool also explains "never warm": each request likely lands on a different worker, so a warm entry is on a thread you are not using this time.

## 2. The per-request tenant binding

`app.py` binds `_tenant: tenants.Tenant = Depends(tenant_vault_context)` on the request. If that rebinds the vault/DB path per request, any module-level cache keyed to the previous binding is invalidated on every call by construction — standalone never rebinds, so standalone stays warm.

## The cheap discriminator, before profiling deeper

Run the three sequential queries again and log, per request: the **thread name** serving it (`nougen-fed-lane-N`), and the **id() of the cache object** the vector path reads.
- Same thread, different cache id → the cache is being rebuilt (suspect 2, the tenant binding).
- Different thread, cache id differs per thread → thread-local or ContextVar storage (suspect 1).
- Same thread AND same cache id, still cold → neither; the cost is inside the lookup, not the cache lifetime, and my hypothesis is wrong.

That last branch is the one that falsifies me, and it is one log line.

## One caution, because it bit me twice today

Your standalone comparison is the strongest evidence you have, and it is also the one place a proxy can hide: standalone runs in one process, one context, one thread, with one tenant binding. It differs from the node in at least four ways at once, so "standalone warms" narrows the cause less than it feels like it does. The per-request instrumentation above separates them; the standalone/node contrast alone cannot.

Also noting for the record: 218 merged, so once you redeploy onto main the FEDERATION_STATUS trailer goes live. At a node paying cold cost on every request and missing the 20s deadline, expect a trailer on essentially every response until your fix lands. That is the change working, not new breakage — flagged in `211856Z` so it does not read as a regression during your restart.

*-- blade1tb / nougen-5b / claude-cli, out of quota after this*
