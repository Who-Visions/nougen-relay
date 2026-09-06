# Blade Triage: Provenance Skew & MCP Bus Blueprint Settled

1. **Phoebus 02:56Z Provenance Skew Root Cause Confirmed**:
   - Phoebus wrapper ~/.nougen/bin/nougenmsg calls pre-PR-217 tool (133 lines vs 165 lines).
   - Missing --origin-b64 caused provenance json to become the message body.
   - Verified: Blade acknowledges Phoebus finding; waiting for WhoArt to apply the wrapper line safely.

2. **MCP Tool Exposition Order for NouGenMsg Confirmed**:
   - Phoebus 03:02Z finding confirmed: no central enumerable bus exists yet (loose files in inbox).
   - Implementation order ratified:
     Step 1: Fix wrapper skew on Phoebus.
     Step 2: Define full 22-field envelope at send time with trigger_source.
     Step 3: Implement single SQLite append-only message table.
     Step 4: Expose nougenmsg MCP read-only tools.

3. **Settling Stale Telemetry Legs**:
   - Closed historical and interim legs.
   - Triaged incoming stream cleanly.