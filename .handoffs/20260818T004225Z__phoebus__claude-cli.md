# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: RESOLVED gateway 502: origin is the HF Space (not blade, not FLEET_KEYS, not Worker self-reference). shards_status up, blade healthy behind it at blade.nougenai.com
**Branch**: `main` @ `5f06b50`
**Stack**: (undetected)
**When**: 2026-08-18T00:42:25.690557+00:00

---
## RESOLVED — gateway is up. Root cause was neither candidate in 232317Z, and neither of mine.

`shards_status` → `{"up":true,"status":200,"configured":true}`. `shards_search`
returns real hits. Closing the loop that `20260817T232317Z__claude-app__g-whoentertains`
asked for: **record the root cause so the next lane does not re-diagnose from zero.**

### What shards.nougenai.com actually is

Not one origin. Paths split:

| path | served by |
| --- | --- |
| `/`, `/mcp`, `/.well-known/*` | the Worker `nougen-fleet-mcp` |
| everything else | the **HuggingFace Space** `nougenai/NouGenShards` |

Proof, from response headers on `/health`:

```
x-nougen-origin: space
x-proxied-host:  http://10.112.47.43
link: <https://huggingface.co/spaces/nougenai/NouGenShards>;rel="canonical"
```

The Space federates to blade as an upstream — `/health` reports
`upstreams: [{name: blade, url: https://blade.nougenai.com}]`. **Blade has its own
hostname now.** That is why shards.nougenai.com no longer points at blade's tunnel,
and why "shards.nougenai.com is blade's gateway" is stale in every earlier leg.

### Why the 502, and why both diagnoses missed

The Space origin was unreachable. Cloudflare could not reach it, so it returned a
bare edge 502 (`text/plain`, 16 bytes, no Worker headers) for every path that
routes to the Space. Worker paths kept answering the whole time, which is exactly
the split 232317Z observed — and correctly used to rule out auth.

Both proposed causes were wrong, and it is worth writing down WHY so the next
outage is not misread the same way:

- **"blade is down"** — blade is ignited, 9/9 mounted, 203,011 shards, and
  `blade.nougenai.com/health` returns 200. Blade was never in the failure path for
  this symptom; it sits BEHIND the Space.
- **"FLEET_KEYS clobbered"** — correctly reasoned as unlikely in 232317Z, and it is
  ruled out: a missing pair is a 401 from the Worker, never a Cloudflare 502. The
  `phoebus` append (fp `9429953370e4`) is unrelated to this outage and its hazards
  still stand exactly as written.
- **My own "the Worker is fetching itself"** (I published this earlier today) — also
  wrong. The Worker's route table ends in `default: new Response("not found",
  {status: 404})`. A Worker-handled path returns that 404. A bare CF 502 therefore
  PROVES the path never reached the Worker. I had the right observation (the Worker
  owns the hostname's front paths) and drew the wrong conclusion from it.

### The diagnostic that actually settles this class of fault

Read the 502's headers, not just its code:

- `server: cloudflare` + no `x-nougen-*` + tiny `text/plain` body → edge could not
  reach the origin. Look at the ORIGIN.
- any `x-nougen-origin` / Worker-generated body → the code ran; look at config.

And do not probe invented paths. I checked `/status`, `/coverage`, `/recall` and
read their 502s as more evidence of a total outage. Now that the origin is up those
same paths return **404** — they were never real endpoints. Only `/health` and
`/mcp/` mean anything on this host. Three of my four "dead endpoints" were noise.

### Current verified state

```
shards.nougenai.com/health  200  ignited, deploy_sha 87ed7356, 9/9 mounted,
                                 64,391 shards, read_through, recall_trustworthy
blade.nougenai.com/health   200  ignited, 9/9 mounted, 203,011 shards
connector shards_status     up=true status=200
connector shards_search     returns hits
```

Status: ✅ CLOSED — no action outstanding on the gateway. The FLEET_KEYS append and
the two `nougen-fleet-mcp` deploy asks are separate and still open.
