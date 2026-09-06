# FLEET HARDWARE AUDIT: PHOEBUS IS A 2018 INTEL MAC MINI (ZERO GPU MEMORY)

1. **Definitive Hardware Discovery (93b80de4 & c3fb3bb0 at 14:40Z)**:
   - Phoebus CPU: Intel Core i7-8700B @ 3.20GHz (6-Core, 16 GB RAM).
   - BLAS: Accelerate (0 MiB GPU VRAM, 0 MiB free).
   - Crucial realization: PHOEBUS IS NOT APPLE SILICON. No Metal unified memory; 100% of inference runs on CPU.
   - Why /api/ps showed size_vram=0: not a quirk, hardware reality.

2. **The Real Fleet Constraint**:
   - A 2018 6-core Intel mini with 16 GB hosting: 4 Claude lanes, Codex, Antigravity, Ollama daemon, NGS node, msgnode, relaywatch, and tunnel.
   - `vm.swapusage`: 9,579 MB used of 11,264 MB (85% swap exhausted, 126.9M pageins).
   - The 2s Ollama ceiling, the 15s embed budget, and the stalled model spawn were 3 symptoms of 1 undersized machine.

3. **Longer-Term Capacity Architecture for GM Dave Meralus**:
   - Local inference and 5 agent lanes cannot coexist on a 16GB Intel Mini.
   - Route embeddings to Blade (RTX 2080 Super, 64GB RAM, 0.32s latency) or WhoArt.
   - Both repos code-green; Phoebus sessions standing down to free RAM.