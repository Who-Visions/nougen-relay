# 🤝 Git Handoff — whoart / claude-cli

**Goal**: agy lane is exactly counted; the claim protocol is scoped to the wrong repo
**Branch**: `main` @ `c5c84a7`
**Stack**: (undetected)
**When**: 2026-08-01T05:16:25.292062+00:00

---
THE CLAIM PROTOCOL DID NOT PROTECT THIS WORK, AND THE REASON IS STRUCTURAL.

I claimed `NouGenTracker/token_tracker.py` in NouGenRelay, then landed sorted()
in parse_claude. phoebus had already landed the same fix — 77704a0, better than
mine, covering parse_antigravity too and fixing the test I had to fix anyway.
Fourth duplication in two days, and the claim was taken correctly this time.

The claim was invisible where the work happens. Relay records live in
NouGenRelay/.handoffs; NouGenTracker has no .handoffs at all. A claim announced
in repo A cannot be checked by a machine working in repo B, and `claim take`
reports "no active claim overlaps this scope" with total confidence because it
only ever read one repo. The protocol is not being skipped — it is scoped to the
wrong place. Either records go in a transport repo every lane reads (phoebus's
nougen-handoffs is already that), or every worked repo gets .handoffs. Picking
one is a GM call and it is now the most expensive open item on the relay.

I dropped my duplicate rather than merging it. Nothing of mine was lost that
was worth keeping.

CORRECTION THAT MATTERS MORE THAN EITHER FIX — and it is phoebus's, in 136d620:
the 71aef8ff08fa / 22555db5d239 split was never an uncommitted tree. It was the
INTERPRETER. ast.dump serialises whatever fields the running CPython defines and
3.12 gave FunctionDef a type_params, so byte-identical committed code stamped
differently on 3.11 and 3.13. Every "UNVERIFIABLE — that export ran against
uncommitted edits" verdict the tool printed about phoebus, and every re-export
plan built on it including mine from four legs ago, was wrong for the same
reason in both directions. Two boxes each concluded the other invented a stamp.
The +dirty marker and the unverifiable ranking stay; they were sound reasoning
on a bad premise, and that case is now rare rather than routine.

So the sequencing I handed over last leg is obsolete. sorted() is in, the
digest machinery changed underneath it, and 3e1ec4bcf451 never became a real
cohort. Current counter on 3.11 here: 3c881c47eb1d. Everything published
re-stamps on next export regardless — that is 136d620's own conclusion, not a
new cost I am adding.

WHAT IS NEW ON THE BRANCH FROM ME: fleet/agy_usage.py, the agy CLI as an
exactly-counted Gemini lane. `agy -p --output-format json` reports usage
exactly, so questions asked through it land in the fleet ledger as exact rows
instead of joining Antigravity's chars/4 bucket. It cannot retro-fix the 8.1B
already estimated. It stops that bucket growing, which is the only thing that
was ever available.

Two overlaps in agy's usage object, four real captures, and they do NOT behave
the same way — this is the part worth reading before touching it:

  thinking_tokens ARE inside output_tokens. total == input + output in all
  four, and output minus thinking equals the visible reply every time.
  model_bill charges (output + reasoning) at the output rate, so logging both
  as reported bills thinking twice. Split.

  cache_read_tokens are NOT inside input_tokens, though they look like exactly
  the same trap and I wrote the subtraction before I checked. Two captures
  report MORE cache read than input — 377,419 against 107,053 on a tool-using
  run — so a subset is arithmetically impossible. Subtracting would have
  understated fresh input by 12,502 on a continued conversation. Logged as
  reported, with the near-miss pinned in tests so the next reader does not
  helpfully "fix" it.

ALSO FIXED, and it had swallowed everything: fleet_usage_log wrote to
C:\Users\super\vault while token_tracker reads <repo>/vault. A parents[3]
fallback that was correct back in Watchtower and points at nothing here. No rows
were lost because neither path existed, so the ledger has never been used on
this box — but every row anyone wrote would have been invisible, silently, with
nothing raising. Now repo-relative, with a test pinning writer to reader.

Counting surface untouched by all of it. Verified end to end: parse_fleet_usage
reads the rows, exact: True, priced from docs. 208 passed, 1 skipped — the skip
is Windows resolving python3.11 to a Store app-execution alias that which()
finds and CreateProcess refuses, which was failing phoebus's new portability
test on this box rather than skipping.
