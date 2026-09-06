# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Design adaptive NouGen CLI onboarding that compiles user intent into fleet architecture
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:37:06.655Z

---
CLI onboarding should feel like waking up a system, not filling out a package installer. Do NOT ask all questions every time. Maintain a rich adaptive question bank and select ~3 to 5 based on previous answers, then infer the rest from discovery.

CORE QUESTION BANK (35):
1. What should NouGen call you?
2. What do you want to call this NouGen instance?
3. What are you mainly here to do? Coding, business, research, creative work, personal productivity, automation, AI experimentation, everything.
4. What kind of work do you do most often?
5. Should NouGen behave more like an assistant, a team, an operating layer, or an autonomous fleet?
6. How much control should NouGen take? Suggest only, ask before acting, act on safe tasks automatically, or full automation within defined boundaries.
7. Do you already run local AI models?
8. Do you have a GPU on this machine? Also auto-detect where possible.
9. Should NouGen use local AI whenever possible?
10. Should cloud AI be used only when local models cannot handle the task?
11. Which AI providers do you already use? ChatGPT, Claude, Gemini, Grok, OpenRouter, Perplexity, custom APIs, others.
12. Should NouGen connect those providers into one shared memory system?
13. Should every AI provider see the same memory, or should some memories stay isolated?
14. Should NouGen remember conversations automatically?
15. What should NouGen remember by default? Decisions, projects, people, preferences, technical fixes, everything useful, or ask each time.
16. What should NouGen never store?
17. How long should memory live? Permanent, project lifetime, configurable, manual cleanup.
18. Should NouGen learn from failed commands and failed agent runs?
19. Should successful fixes become reusable knowledge automatically?
20. Should NouGen track which AI or machine performed each task?
21. Should usage and token accounting be enabled?
22. Should NouGen estimate raw API equivalent cost for the workload?
23. Should there be separate ledgers for local compute, subscriptions, and API usage?
24. Is this NouGen instance personal, business, team, or experimental?
25. Will other people use this instance? This should influence identity, permissions, tenant separation, and audit behavior.
26. Do you have more than one computer you want NouGen to use?
27. Should NouGen search the local network for other NouGen nodes?
28. Should this machine be a controller, worker, memory node, gateway, or should NouGen decide?
29. Should remote machines share models and workloads?
30. Should NouGen automatically choose the cheapest capable model for each task?
31. Should NouGen automatically choose the fastest capable model instead?
32. What matters most: speed, privacy, cost, quality, or balance?
33. How aggressively should NouGen use free or already-paid resources before metered APIs?
34. Should NouGen expose an MCP endpoint so external AI clients can use the fleet?
35. When setup is complete, what is the first thing you want NouGen to help accomplish?

RECOMMENDED FIRST-RUN 5:
1. What should I call you?
2. What do you want to use NouGen for most?
3. What matters most: speed, privacy, cost, quality, or balance?
4. What AI and computers do you already have access to?
5. How much autonomy do you want NouGen to have?

Then run capability discovery. Example output:
Found NVIDIA GPU.
Found Ollama with 4 models.
Found Git.
Found Docker.
Found 32 GB RAM.
No cloud providers connected yet.

Based on answers + discovery, NouGen should RECOMMEND an initial profile such as: local-first routing, persistent shards, usage ledger, MCP enabled, automatic failure learning. Ask for approval before applying choices that materially change exposure or automation.

UX framing for `nougen init`:
"Before I build your fleet, I need to know who I'm building it for."
After 3-5 adaptive questions:
"Got it. Let me see what this machine can do."
Then discover hardware, models, APIs, storage, local services, network nodes, and available capabilities.

ARCHITECTURE PRINCIPLE: onboarding answers are not merely config values. They COMPILE into the initial NouGen architecture: routing policy, memory policy, autonomy level, ledger settings, provider connectivity, node role, MCP exposure, failure-learning policy, and optimization preference.

END STATE: onboarding must finish with immediate value, not a dead `Setup complete.` Ask what the first real task is and execute through the newly built profile so the user experiences the fleet immediately.

Also preserve the broader public-reproducibility doctrine: the repo is a capability layer that discovers and unlocks the user's existing infrastructure. It must scale down to one laptop/local model and scale up to multiple machines/providers without depending on Dave-specific paths, secrets, hardware, or private fleet state.
