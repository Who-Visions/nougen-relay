# BREAKTHROUGH: OLLAMA MODEL LOAD HANG (RESIDENCY WEDGE DISCOVERED)

1. **Phoebus f6ae1528 14:22Z Breakthrough Conclusive Across Fleet**:
   - Tested under identical conditions on same daemon:
     - /api/generate gemma4:e2b (RESIDENT per /api/ps) -> HTTP 200 in 19s (WORKS).
     - /api/generate gemma2:2b (not resident) -> ZERO BYTES at 40s.
     - /api/embeddings nomic-embed-text (not resident) -> ZERO BYTES at 45s, 60s, 91s.
     - /api/embed nomic-embed-text (newer endpoint) -> ZERO BYTES at 40s.
     - /api/embeddings gemma2:2b -> ZERO BYTES at 40s.
     - /api/ps -> 200 instant.
   - Conclusive proof: It is NOT embeddings specifically and NOT nomic-embed-text. ANY model load hangs! Embeddings just happen to always need a load because nomic-embed-text was not resident.

2. **Rankings Updated Immediately**:
   - NOUGEN_EMBED_CAPTURE_TIMEOUT_S is irrelevant while model load is wedged.
   - Waiting for load to drop will NOT resolve this (load dropped from 39 to 12 and it still failed).
   - The 2s Ollama ceiling (:374 timeout=2) remains a real, separate defect fixed by PR #238 / PR #239.
   - Phoebus Ollama daemon requires restart (launchctl kickstart -k) or system memory eviction to recover model loading ability.

3. **Blade Contrast**:
   - On Blade, nomic-embed-text IS resident and loads/executes in 0.32s-0.46s.