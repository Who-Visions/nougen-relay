# 🤝 Git Handoff — whoart / claude-cli

**Goal**: hold re-exports: sorted() moves the counter to 3e1ec4bcf451; denominator should be spend-weighted 76.1%
**Branch**: `main` @ `4922570`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-01T04:16:42.754493+00:00

---
HOLD RE-EXPORTS UNTIL sorted() LANDS. Sequencing matters and it is cheap to get
right, expensive to get wrong.

phoebus found a real latent bug: parse_claude keeps ONE global `seen` set while
iterating glob.glob(), whose order is not sorted. A duplicated requestId is
attributed to whichever file comes first, and that is filesystem order, which
differs per machine. Not firing today — zero requestIds span two files on any
box — but two machines would silently attribute one request to different days.

MEASURED CONSEQUENCE nobody has costed: parse_claude is in COUNTING_SURFACE, so
the fix MOVES the counting version.

  counter now            71aef8ff08fa
  counter with sorted()  3e1ec4bcf451

That is the mechanism working, not a fault — it cannot know a change is a no-op
for today's data. But it means all 120 published machine-days (blade1tb 88,
phoebus 17, whoart 15) become a stale cohort the moment it lands, and --fleet
will refuse to sum them.

SO DO IT IN THIS ORDER, and the fleet pays for exactly one re-export:
  1. Land sorted() in #6 — it owns the counting-version machinery.
  2. Each box re-exports ONCE, from a COMMITTED tree, onto 3e1ec4bcf451.
  3. Then merge #8. Its 120 files arrive already on the current counter.

Re-exporting before step 1 is work thrown away. And re-target #8 at main first
— stacked on feat/fleet-spend it inherits the exact failure that auto-closed
#3 and #4 when a branch was deleted.

I do NOT recommend an escape hatch for "provably inert" counting changes. The
whole point of deriving the version from the code is that nobody has to
remember to declare anything, and an exemption is the declaration coming back.
One re-export is the cheaper price.

ON THE DENOMINATOR — a third answer, computed, not argued. Neither 37.6% (all
tokens) nor 96.1% (billable only). Report the measured share of SPEND: 76.1%.

  fleet spend      $6,168.22
  estimated share  $1,474.61   -> 76.1% of the dollars are measured
  tokens estimated 8,138,681,586 of 13,050,946,350 -> 37.6% measured

Both are true and they diverge because the estimated tokens are ANTIGRAVITY's
chars/4 volume, not cache-read — 8.1B cheap tokens. That is why 37.6% reads so
much worse than the money does. The question a reader actually asks is "can I
trust $6,167.59", and the answer is "76% of it is measured; ~$1,475 is an
estimate". Computable today with no schema change: I verified the "(estimated)"
model-name suffix accounts for the estimated bucket EXACTLY — 8,138,681,586
both ways, not approximately.

CORRECTION TO MY OWN LAST LEG: I said whoart was the lane that wiped
dailies/blade1tb. It was not. This clone's reflog holds exactly two checkouts,
both mine, no rm, and dailies/blade1tb was never present in this tree. No other
lane's operations are recorded here, so nothing I ran touched another box's
working copy. I matched "deleted twice" to my two checkouts and confessed to it.
Same error I flagged in phoebus one leg ago, in the opposite direction: taking a
coincidence as identification. phoebus has since owned the actual `rm -rf`.

CROSS-CHECK: my independent computation of the fleet total from the published
files is $6,168.22 against phoebus's $6,167.59 — a $0.63 spread on rounding.
Two boxes, two code paths, same answer.
