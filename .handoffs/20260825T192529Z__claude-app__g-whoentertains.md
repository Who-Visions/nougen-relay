# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Muse-matching platform concept — product mechanics, payment rails, competitive teardown (FetLife + Tinder Sparks 2026)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-25T19:25:29.286Z

---
## Situation
Concept session for a photographer↔model recurring-collaborator platform. Positioning locked: **muse matching**, not dating. Existing boards (ModelMayhem, PurplePort) treat it as one-off transactional gigs; nobody serves the recurring-collaborator relationship.

## Core mechanic — Terms Declaration
Both sides declare before match. Doubles as compatibility filter AND timestamped pre-shoot consent record. This is the moat.
- Cadence: one-off / recurring / standing monthly
- Exclusivity: open collab vs exclusive to one shooter for a body of work
- Comp: paid / TFP / licensing rev-split
- Content limits: clothed / implied / art nude / no
- Location: studio / on-location / private residence y-n
- Third party welcome: assistant, MUA, chaperone

## Lifted from FetLife
- Into / Curious / Not-Into checklist taxonomy → makes terms searchable, not prose in a bio
- Social network structure (profiles, groups, events) — NOT swipe. Retains women; kills the dating-app read.
- Munch pattern → public group shoots / workshops / meetups before anyone is in a studio alone
- Visible connection graph (who has worked with whom) instead of star ratings, which get gamed
- WARNING: FetLife lost Visa/MC in 2017 and had to strip content. Also refused to adjudicate abuse reports because adjudicating created liability — that trap is inherited automatically if we brand as "dating."

## Lifted from Tinder Sparks 2026 (Mar 12 2026 keynote, LA)
- **Face Check** — mandatory liveness verification. Ship as mandatory for BOTH sides at signup, day one, no free tier bypass.
- **Modes** navigation (Music/Astrology/College/Double Date) → our version = Editorial / Fine Art / Commercial / Fitness modes
- **Events beta** (LA-first: trivia, pottery) → validates the munch pattern at scale. Geographic-single-market launch is the play; ours = West Palm / Palm Beach County.
- **Chemistry** AI recommendation layer + **Camera Roll Scan** (opt-in photo analysis for personality/interest signals) — expanded to US/Canada Mar 2026. Our version reads the PORTFOLIO, not the camera roll: style-match photographer aesthetic to model look. Do NOT touch private camera rolls — privacy backlash is already attached to that feature.
- **Learning Mode** — real-time recommendation adaptation
- **"Are You Sure?"** (pre-send harmful-language warning) + **"Does This Bother You"** (receiver-side detection, now with auto-blur) — both upgraded to LLM. Cheap to replicate, high safety signal.
- Video speed dating (3-min live video, photo-verified users only) → our version = pre-shoot video vibe-check, verified only. Strong safety layer.
- Context: Match Group is fighting 9+ straight quarters of paying-subscriber decline and swipe fatigue. The whole industry is pivoting AWAY from swipe toward curation + IRL. Confirms the thesis.

## Payment rails — DECIDED
Platform NEVER touches shoot money.
- Revenue = SaaS subscription only. Photographer $19-39/mo (search, outreach, publish terms). Models always free. Optional: workshop tickets, verification fee, portfolio hosting.
- Shoot comp arranged directly between parties, off-platform. Stated explicitly in ToS.
- Platform deliverable = generated model release + terms sheet PDF, dual signature, timestamped. That is the artifact and the evidence file.
- NO ESCROW. Escrow converts directory → marketplace overnight. Resist even when users request it.
- Entity separation: platform entity owns subscription revenue. Who Visions Productions books talent as a normal USER of the platform, 1099s contractors. Do not blur — platform-owner-as-biggest-booker weakens the directory defense.
- Stripe primary + a second processor account live from day one. Merchant descriptor and public copy stay boring: "creative-professional directory / collaborator matching / production services."

## Done-when
- Competitive scan of what is currently live in muse/collab matching (not yet run)
- Domain + name decision
- Terms Declaration schema v1
- Single-market launch scope: Palm Beach County
