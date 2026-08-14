# Joining the relay from Antigravity (agy CLI / IDE / SDK)

A Claude session can be *made* to check the registry — a SessionStart hook runs
whether the agent wants it or not. Antigravity lanes are configured differently,
so they join through two pieces that have to both be present:

| piece | supplies | without it |
|---|---|---|
| **MCP server** | the relay verbs as callable tools | the lane has nothing to call |
| **Skill** | *when* to call them | the lane has tools and never uses them |

Both ship in one plugin, so a machine installs them together or not at all.

## Install

```bash
pip install -e "path/to/NouGenRelay[mcp]"
cp -r plugins/nougen-relay ~/.gemini/config/plugins/     # global, all workspaces
```

Workspace-only instead: copy it to `<repo>/.agents/plugins/`.

Verify — this should list eight `relay_*` tools and describe the pre-work
sequence:

```bash
agy -p "List your MCP tools starting with relay_, and what the nougen-relay skill says to do before editing a file."
```

## Why a plugin and not two edits

Antigravity reads a global `~/.gemini/config/mcp_config.json` (60+ servers on a
working box) and a global `skills/` directory. Registering there directly works,
but it means every machine hand-edits a large shared registry and the two halves
can drift apart — a lane with tools and no skill will never call them, and a
lane with the skill and no tools produces errors.

A plugin bundles `plugin.json` + `mcp_config.json` + `skills/` into one
directory that is copied, versioned in this repo, and removed in one step.

## Not done yet: hooks.json

Antigravity plugins also support `hooks.json`, which is the piece that would
make this enforced rather than advisory — the same role the SessionStart hook
plays for Claude lanes. It is deliberately absent here: the schema was not
confirmed at the time of writing, and a fabricated hook file that silently fails
is worse than none. Add it once the format is verified against the docs.

Until then an Antigravity lane follows the protocol because the skill tells it
to, not because anything stops it. That is a real difference in enforcement
strength and worth remembering when a record goes missing.

## Naming the lane

The plugin sets `NOUGEN_AGENT=agy-cli` so records from this lane are
distinguishable from `claude-cli` on the same box. The machine name still comes
from the hostname unless `NOUGEN_MACHINE` overrides it.
