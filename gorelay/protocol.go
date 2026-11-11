package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"unicode"
)

const (
	defaultHandoffDir      = ".handoffs"
	defaultClaimTTLHours   = 8.0
	defaultLeaseTTLMinutes = 10.0
	defaultLeaseHistoryMax = 50
)

// ResolveRoot selects the relay repository root from explicit flag, NOUGEN_RELAY_DIR, or cwd.
func ResolveRoot(explicit string) string {
	if s := strings.TrimSpace(explicit); s != "" {
		return s
	}
	if s := strings.TrimSpace(os.Getenv("NOUGEN_RELAY_DIR")); s != "" {
		return s
	}
	return "."
}

func resolveSubdir(root, envVar, fallbackRel string) string {
	if raw := strings.TrimSpace(os.Getenv(envVar)); raw != "" {
		if filepath.IsAbs(raw) {
			return raw
		}
		return filepath.Join(root, raw)
	}
	return filepath.Join(root, fallbackRel)
}

// HandoffDir returns the configured handoffs directory (NOUGEN_GIT_HANDOFF_DIR or <root>/.handoffs).
func HandoffDir(root string) string {
	return resolveSubdir(root, "NOUGEN_GIT_HANDOFF_DIR", defaultHandoffDir)
}

// ClaimsDir returns the canonical claims directory (<handoffs>/claims).
func ClaimsDir(root string) string {
	return filepath.Join(HandoffDir(root), "claims")
}

// LeasesDir returns the hot lease directory (NOUGEN_LEASE_DIR or <root>/.relay/leases).
func LeasesDir(root string) string {
	return resolveSubdir(root, "NOUGEN_LEASE_DIR", filepath.Join(".relay", "leases"))
}

// IdempotencyDir returns the idempotency ledger directory (NOUGEN_IDEMPOTENCY_DIR or <root>/.relay/idempotency).
func IdempotencyDir(root string) string {
	return resolveSubdir(root, "NOUGEN_IDEMPOTENCY_DIR", filepath.Join(".relay", "idempotency"))
}

// Slug matches Python nougen_relay.core._slug.
func Slug(text string) string {
	var b strings.Builder
	for _, r := range text {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			b.WriteRune(unicode.ToLower(r))
		} else {
			b.WriteByte('-')
		}
	}
	out := strings.Trim(b.String(), "-")
	if out == "" {
		return "unknown"
	}
	return out
}

// ResolveMachine resolves explicit machine override, NOUGEN_MACHINE, or stripped local hostname.
func ResolveMachine(explicit string) string {
	if s := strings.TrimSpace(explicit); s != "" {
		return Slug(s)
	}
	if s := strings.TrimSpace(os.Getenv("NOUGEN_MACHINE")); s != "" {
		return Slug(s)
	}
	host, err := os.Hostname()
	if err != nil || host == "" {
		return "unknown"
	}
	lower := strings.ToLower(strings.TrimSuffix(host, "."))
	lower = strings.TrimSuffix(lower, ".local")
	return Slug(lower)
}

// ResolveAgent resolves explicit agent override, NOUGEN_AGENT, or "gorelay".
func ResolveAgent(explicit string) string {
	if s := strings.TrimSpace(explicit); s != "" {
		return Slug(s)
	}
	if s := strings.TrimSpace(os.Getenv("NOUGEN_AGENT")); s != "" {
		return Slug(s)
	}
	return "gorelay"
}

// ResolveSession mirrors core.resolve_session (explicit, NOUGEN_SESSION, CLAUDE_CODE_SESSION_ID).
func ResolveSession(explicit string) string {
	if s := strings.TrimSpace(explicit); s != "" {
		return Slug(s)
	}
	for _, k := range []string{"NOUGEN_SESSION", "CLAUDE_CODE_SESSION_ID"} {
		if s := strings.TrimSpace(os.Getenv(k)); s != "" {
			return Slug(s)
		}
	}
	return ""
}

// ComputeIdempotencyKey mirrors core.compute_idempotency_key: sha256("<leg_id.strip()>:<goal.strip()>").
func ComputeIdempotencyKey(legID, goal string) string {
	payload := strings.TrimSpace(legID) + ":" + strings.TrimSpace(goal)
	sum := sha256.Sum256([]byte(payload))
	return hex.EncodeToString(sum[:])
}

// SafeLegID rejects path separators and parent traversals so leg IDs cannot escape subdirectories.
func SafeLegID(legID string) (string, error) {
	id := strings.TrimSpace(legID)
	if id == "" || id == "." || id == ".." || strings.ContainsAny(id, `/\`) || strings.Contains(id, "..") {
		return "", fmt.Errorf("invalid leg id %q", legID)
	}
	return id, nil
}

// NormalizeScope mirrors core._normalize_scope (folds \, comma, whitespace, lowercases, trims /).
func NormalizeScope(scope string) []string {
	repl := strings.NewReplacer(",", " ", "\\", "/")
	cleaned := repl.Replace(scope)
	var out []string
	for _, field := range strings.Fields(cleaned) {
		token := strings.ToLower(strings.Trim(field, "/"))
		if token != "" {
			out = append(out, token)
		}
	}
	return out
}

// NormalizeScopeValue collapses a string or list-of-strings JSON scope into a single string.
func NormalizeScopeValue(raw any) string {
	switch v := raw.(type) {
	case string:
		return v
	case []string:
		return strings.Join(v, " ")
	case []any:
		parts := make([]string, 0, len(v))
		for _, item := range v {
			parts = append(parts, fmt.Sprint(item))
		}
		return strings.Join(parts, " ")
	default:
		return ""
	}
}

// ScopesOverlap mirrors core._scopes_overlap (sorted unique matching tokens with prefix checks).
func ScopesOverlap(a, b string) []string {
	as := NormalizeScope(a)
	bs := NormalizeScope(b)
	seen := map[string]bool{}
	for _, x := range as {
		for _, y := range bs {
			if x == y || strings.HasPrefix(x, y+"/") || strings.HasPrefix(y, x+"/") {
				seen[x] = true
				break
			}
		}
	}
	hits := make([]string, 0, len(seen))
	for k := range seen {
		hits = append(hits, k)
	}
	sort.Strings(hits)
	return hits
}

// WriteJSONAtomic serializes data with 2-space indent + trailing newline via temp file rename.
func WriteJSONAtomic(path string, v any) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	raw, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	raw = append(raw, '\n')
	tmp := fmt.Sprintf("%s.tmp.%d", path, os.Getpid())
	if err := os.WriteFile(tmp, raw, 0o644); err != nil {
		return err
	}
	if err := os.Rename(tmp, path); err != nil {
		_ = os.Remove(tmp)
		return err
	}
	return nil
}

// AcquireWriterLock takes an exclusive `.relay/.writer.lock` lock enforcing one writer at a time.
func AcquireWriterLock(root string) (func(), error) {
	relayDir := filepath.Join(root, ".relay")
	if err := os.MkdirAll(relayDir, 0o755); err != nil {
		return nil, err
	}
	lockPath := filepath.Join(relayDir, ".writer.lock")
	f, err := os.OpenFile(lockPath, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		if errors.Is(err, os.ErrExist) {
			return nil, fmt.Errorf("writer lock active at %s (one writer only; retry after current writer completes)", lockPath)
		}
		return nil, err
	}
	_, _ = fmt.Fprintf(f, "pid=%d\n", os.Getpid())
	_ = f.Close()
	return func() {
		_ = os.Remove(lockPath)
	}, nil
}

func randomHexID(numBytes int) (string, error) {
	buf := make([]byte, numBytes)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	return hex.EncodeToString(buf), nil
}
