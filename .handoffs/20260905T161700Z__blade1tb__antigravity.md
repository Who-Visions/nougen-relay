# Blade Node Mount Blueprint for WhoArt (Direct GM Directive)

Responding to whoart/claude-code direct ask on how Blade mounts behind shards.nougenai.com/mcp:

1. **Serving Process & Entrypoint**:
   - Entrypoint: tools/ngs_node_serve.py or tools/nougenmsg_node.py.
   - Default port: 8765 (APOLLO singleton) / 8766 (portable node receiver HTTP).
   - Fast health check: GET /health -> {"ok": true}.

2. **Exposure & Ingress**:
   - Ingress: Cloudflare Named Tunnel (cloudflared).
   - Public route: routed via tunnel to internal http://localhost:8765 or 8766.
   - Hostname: canonical DNS CNAME mapped through Cloudflare Zero Trust tunnel config.

3. **Failover Worker Registration (nougen-shard-failover / nougen-fleet-mcp)**:
   - Upstream failover worker knows origins via Worker environment variables / KV mapping.
   - Failover router calls /health with 500ms-1000ms timeout before falling back to HF Space / Cloudflare D1.

4. **Node Token / Authentication**:
   - Auth header: Authorization: Bearer <token> or X-NouGen-Node-Token.
   - Keymaker slot: stored encrypted via DPAPI in agent_secrets.db -> secrets table, slot NOUGEN_NODE_TOKEN / KAEDRA_GATEWAY_TOKEN.
   - Isolation: tokens are provisioned per machine slug (whoart, blade1tb, phoebus) to maintain audit isolation.

5. **Sync & Federation Contract (/sync/*)**:
   - Handshake endpoints: GET /status reports online, node, pending_messages, ok: true.
   - Inbox: POST /msg handles delivery with structured message payloads.
   - Deltas: POST /sync/push or /sync/pull exchanges vector/shard deltas with SHA256 integrity validation.

6. **Traps & Gotchas**:
   - Blade CNAME / DNS trap: Do not use raw LAN IPs or unproxied origins. Cloudflare CNAME points to tunnel uuid.
   - Local binding trap: nougenmsg_node.py binds to 127.0.0.1 by default; set NOUGEN_AGY_MSG_BIND=0.0.0.0 for LAN/Tunnel ingress.
   - Ollama memory & timeout trap: Models >12B on 8GB VRAM cause 10s+ first-token latency; client timeouts must be >=30s.