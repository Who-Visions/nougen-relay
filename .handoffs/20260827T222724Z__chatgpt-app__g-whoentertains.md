# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add timeout hardening code to Kayanna shard persistence fix
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T22:27:24.531Z

---
Follow-up to relay `20260827T222624Z__chatgpt-app__g-whoentertains`.

Need to fix shard write/retrieval timeout behavior, then persist and verify the Kayanna meal chronology:

Ground truth:
* 2026-08-24 Monday, after spontaneous Palm Beach shoot: O'Shea's.
* 2026-08-26 Wednesday, after Norton Museum: Bull Top Taste, jerk chicken context.

Observed failure:
* `shards_search`, `shards_window`, `ask_griot`, `shards_capture`, and Dav1d attempts have intermittently aborted due to timeout.
* This creates a dangerous split where conversational working memory is correct but durable memory is not confirmed.

Implement timeout hardening rather than simply increasing one global timeout. Suggested pattern below.

```ts
// TypeScript: bounded retries + exponential backoff + jitter + per-attempt AbortController
async function withRetry<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  opts = { attempts: 3, timeoutMs: 12_000, baseDelayMs: 350 }
): Promise<T> {
  let lastErr: unknown;

  for (let i = 0; i < opts.attempts; i++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), opts.timeoutMs);

    try {
      return await fn(controller.signal);
    } catch (err) {
      lastErr = err;
      if (i === opts.attempts - 1) break;

      const exp = opts.baseDelayMs * 2 ** i;
      const jitter = Math.floor(Math.random() * 250);
      await new Promise(r => setTimeout(r, exp + jitter));
    } finally {
      clearTimeout(timer);
    }
  }

  throw lastErr;
}
```

```ts
// Retrieval: keep each arm independent so one slow arm does not abort the whole Griot gather.
const results = await Promise.allSettled([
  withRetry(signal => recall(query, { signal })),
  withRetry(signal => keywordSearch(query, { signal })),
  withRetry(signal => windowSearch({ query, since, until, signal }))
]);

const usable = results
  .filter((r): r is PromiseFulfilledResult<any> => r.status === 'fulfilled')
  .map(r => r.value);

// Return partial provenance-marked results and explicit failure metadata.
// Do not throw away successful arms because one backend timed out.
```

```ts
// Capture: make writes idempotent and retry-safe.
const idempotencyKey = sha256(`${title}\n${content}`);

await withRetry(signal =>
  shardCapture({
    title,
    content,
    idempotencyKey,
    signal
  })
);
```

```python
# Python equivalent for internal gateway callers
import asyncio, random

async def with_retry(fn, attempts=3, timeout=12.0, base_delay=0.35):
    last = None
    for i in range(attempts):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout)
        except Exception as exc:
            last = exc
            if i == attempts - 1:
                raise
            await asyncio.sleep(base_delay * (2 ** i) + random.uniform(0, 0.25))
    raise last
```

Also recommended:
1. Separate connect timeout, first-byte timeout, and total request timeout.
2. Bound result set early, especially semantic recall and date-window scans.
3. Add DB/query timing telemetry per arm: queue_ms, connect_ms, db_ms, serialize_ms, total_ms.
4. Add circuit breaker after repeated backend failures, with degraded partial-result mode instead of hanging the whole MCP request.
5. For Griot, fan out concurrently with independent deadlines and merge whatever succeeds.
6. For capture, acknowledge only after durable commit. If the client times out after commit, idempotency must make the retry a safe no-op.
7. Never report a shard write as successful unless the returned commit/capture result is confirmed.
8. After fix, run a read-after-write verification for the Kayanna meal shard using exact terms `O'Shea's`, `Bull Top Taste`, `Kayanna`, and the Aug 24/Aug 26 dates.

Done when:
* capture returns confirmed success,
* exact search and semantic recall both retrieve the new shard,
* bounded Griot query returns it without timing out,
* telemetry identifies which stage was responsible for previous timeout events.
