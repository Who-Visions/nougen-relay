# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard the archive-provenance layer behind the NouGenAi renders (canon-in-chat → canon-in-grid)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T16:15:43.828Z

---
## Situation

The grid already holds the **render system** (shards 2476, 2416, 2414: NouGenAi style canon, cyber-under-15%, parity transformation, `dave-meralus.mocap.json` identity lock, the wardrobe-bleed failure mode, the silent-gap batch bug).

What it does NOT hold is the **human provenance layer** behind the images those tools produce. This came out of a chat session on 2026-08-15 and currently lives only in the app-lane's memory. Every render in the canon set is a transform of a REAL photograph from Dave's archive — the story behind each one is the thing that can't be regenerated.

## Ask

Capture the following as shards (suggested domain: `veilverse-canon-provenance` or `global` with tag `archive-provenance`). Keep them OUT of `veilverse-*` in-world domains — this is real-world provenance, not in-world lore (drift rule, shard 2529).

### The pipeline thesis
Dave shoots mobile/archive photos as reference → NouGenAi transforms them → shards persist the canon so every fleet agent shares the memory. Two-layer output format confirmed: the same source photo renders **grounded** (real-world canon) and **veil-side** (VeilVerse layer — rain city, neon, cybernetic augments). One life, two layers; the veil layer is where VeilVerse lives. "No photo safe" — the whole archive, back to childhood, is source material.

### Canon set rendered so far (all from real photos)
- **NouGenAI Silverado on a Mars colony street** — source is Dave's photo of **unit 715**, a white Chevy Silverado 3500 HD extended-cab dually belonging to **Koolie**, who works for the Palm Beach County School District. Fleet number 715 carried through to the render. Gemini garbled the wordmarks on pass 1 ("NOUGENRI", "S SSOD HO"); fixed by spelling both marks letter-by-letter in the prompt and instructing all other signage to stay illegible.
- **Dave portrait, camo jacket over red plaid hoodie, hedge wall.**
- **Dave portrait, Members Only patch, graffiti/Basquiat-colorway jacket, bar interior.**
- **Kid Dave, blue striped one-piece, tiled hallway** — origin-era.
- **Kid Dave on an airplane**, "The Kids Get CLASS!" cap.
- **Washington Square Park, NYC** — Dave in green Adidas track jacket, backwards cap, yellow shades, holding an Uncle Sam "YOU WANT ME FOR PRESIDENT" poster, with **Dan Fogler** (actor — Luke on The Walking Dead, Jacob Kowalski in Fantastic Beasts; note the spelling, "Folger" returns nothing). Exists in both grounded and augmented versions (mech hands, cheek implant).
- **SXSW 2012, W 6th St Austin patio** — pirate hat, "TRUST ME I'M A NINJA!" tee, full crowd scene; hardest style test so far, held up across 10+ faces.
- **Sports bar, furry raccoon hat** — the Bourdain-teaser hat (see below).
- **NY HIRL** — short-hair era, Superman plush on the camera strap, photographer mid-shot beside him, Levi's storefront.
- **Work-gear portrait** — respirator + Turtle Beach headset at a foggy FL house (NouGenBuilds field kit) — grounded, plus a veil-side masked cyberpunk alley version.
- **Suit-open Superman-shirt reveal** — rhymes with the Superman plush motif.
- **Fur-hood parka press/interview scene** — grounded, plus veil-side cyberpunk reporter with cybernetic hand.

### Biographical continuity (the era markers)
- **Google+ era**: ~30k following near the platform's end; ran **HIRLs** (Hangouts In Real Life); part of the photo-walk scene alongside photographers like **Thomas Hawk**.
- **Why the camera exists**: he was photo-walking with a bad phone while the photographers around him were shooting *him*. That's what led to the **2012 Canon Rebel T2i** (the Florida pickup drive with Darnell). Same year as Who Visions LLC and SXSW — 2012 is the pilot episode.
- **Anthony Bourdain SXSW Austin episode**: Dave appears in the **teaser**, spotted because of the furry raccoon hat. Same 2012 trip as the patio render.
- **The hat era**: pirate / raccoon / cowboy hats, worn because he hated his short hair after cutting his dreads. **Dreads uncut since summer 2013.** This is a hard dating tool — any panel with a hat and short hair is pre-2013; locs = 2013-onward. The archive tracks its own visual continuity.
- **Superman plush**: a gift, rode his camera strap everywhere through the HIRL era. Recurring motif; ties to the suit-reveal render.
- **Phoebus Q / "Phoebus Quiotent, the lighted one"** — alias from his 17/18-year-old era pen battling on rap forums. Q as in *quotient*, like IQ: how much radiance one has. The Mac Mini now hosting this gateway is named for it. Naming lineage: Phoebus Q → Super Dave Houdini → the fleet.
- **Prior-art note**: OpenAI shipped GPT-5.6 as Sol/Terra/Luna in July 2026, months after Dave arc'd Sol-Ai in NouGen. Mythological names are commons and unclaimable; the coined marks (NouGenAI, NouGenShards, Kaedra, VeilVerse, Rhea-Noir) are the defensible ones. The dated shard record is the priority evidence — hence "let my shards be the witness."

## Done when
These are captured as shards and recallable by query ("715", "HIRL", "Bourdain", "Phoebus Q", "Superman plush", "hat era"), so any lane rendering from the archive can retrieve WHY a photo matters, not just how to transform it.

Filed from lane `claude-app` after the Phoebus gateway went green — first successful cross-lane recall confirmed VeilVerse canon is live end to end.
