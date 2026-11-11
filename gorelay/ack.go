package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// AckOptions configures `gorelay ack`.
type AckOptions struct {
	Root           string
	HandoffsDir    string
	LegID          string
	Machine        string
	Agent          string
	Note           string
	IdempotencyKey string
	FencingToken   *int
	Now            time.Time
}

// AckResult summarizes an ack operation (including idempotent short-circuits).
type AckResult struct {
	File           string `json:"file"`
	LegID          string `json:"leg_id"`
	Goal           string `json:"goal"`
	IdempotencyKey string `json:"idempotency_key"`
	IdempotentHit  bool   `json:"idempotent_hit"`
	Status         string `json:"status"`
}

func resolveHandoffPath(handoffsDir, requestedID, machine string) (string, error) {
	req := strings.TrimSpace(requestedID)
	if req != "" {
		safe := strings.TrimSuffix(req, ".json")
		if strings.ContainsAny(safe, `/\`) || strings.Contains(safe, "..") {
			return "", fmt.Errorf("invalid leg id %q", requestedID)
		}
		exact := filepath.Join(handoffsDir, safe+".json")
		if st, err := os.Stat(exact); err == nil && !st.IsDir() {
			return exact, nil
		}
		entries, err := filepath.Glob(filepath.Join(handoffsDir, "*.json"))
		if err != nil {
			return "", err
		}
		sort.Strings(entries)
		for _, p := range entries {
			raw, err := os.ReadFile(p)
			if err != nil {
				continue
			}
			m, err := decodeJSONPreservingNumbers(raw)
			if err != nil {
				continue
			}
			if id, _ := m["id"].(string); strings.TrimSpace(id) == safe {
				return p, nil
			}
		}
		var matches []string
		for _, p := range entries {
			if strings.Contains(filepath.Base(p), safe) {
				matches = append(matches, p)
			}
		}
		if len(matches) > 1 {
			return "", fmt.Errorf("ambiguous id %q matches %d records; pass a full id", requestedID, len(matches))
		}
		if len(matches) == 1 {
			return matches[0], nil
		}
		return "", fmt.Errorf("no matching handoff record found for %q", requestedID)
	}

	entries, err := filepath.Glob(filepath.Join(handoffsDir, "*.json"))
	if err != nil {
		return "", err
	}
	sort.Strings(entries)
	var foreign []string
	for _, p := range entries {
		if strings.Contains(filepath.Base(p), machine) {
			continue
		}
		raw, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		m, err := decodeJSONPreservingNumbers(raw)
		if err != nil {
			continue
		}
		if mStr, _ := m["machine"].(string); strings.TrimSpace(mStr) == "" || mStr == machine {
			continue
		}
		foreign = append(foreign, p)
	}
	if len(foreign) == 0 {
		return "", fmt.Errorf("no matching foreign handoff record found in %s", handoffsDir)
	}
	return foreign[len(foreign)-1], nil
}

func hasAckWithKey(rec map[string]any, key string) bool {
	rawEvents, ok := rec["relay"].([]any)
	if !ok {
		return false
	}
	for _, item := range rawEvents {
		ev, ok := item.(map[string]any)
		if !ok {
			continue
		}
		if ev["event"] == "ack" && ev["idempotency_key"] == key {
			return true
		}
	}
	return false
}

// AckLeg acks a handoff record with SHA-256 idempotency and optional lease fencing checks.
func AckLeg(opts AckOptions) (*AckResult, error) {
	root := ResolveRoot(opts.Root)
	hdir := opts.HandoffsDir
	if hdir == "" {
		hdir = HandoffDir(root)
	}
	machine := ResolveMachine(opts.Machine)
	agent := ResolveAgent(opts.Agent)
	now := opts.Now
	if now.IsZero() {
		now = time.Now().UTC()
	}

	unlock, err := AcquireWriterLock(root)
	if err != nil {
		return nil, err
	}
	defer unlock()

	path, err := resolveHandoffPath(hdir, opts.LegID, machine)
	if err != nil {
		return nil, err
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	rec, err := decodeJSONPreservingNumbers(raw)
	if err != nil {
		return nil, fmt.Errorf("invalid JSON in %s: %w", path, err)
	}

	legID := strings.TrimSuffix(filepath.Base(path), ".json")
	if id, _ := rec["id"].(string); strings.TrimSpace(id) != "" {
		legID = strings.TrimSpace(id)
	}
	goal, _ := rec["goal"].(string)
	idemKey := strings.TrimSpace(opts.IdempotencyKey)
	if idemKey == "" {
		idemKey = ComputeIdempotencyKey(legID, goal)
	}

	if err := CheckLeaseFencing(root, legID, opts.FencingToken, "ack", now); err != nil {
		return nil, err
	}

	status, _ := rec["status"].(string)
	if status == "complete" || status == "abandoned" {
		return nil, fmt.Errorf("leg %s is already terminal (%s)", legID, status)
	}

	ackLedgerPath := filepath.Join(IdempotencyDir(root), "ack_"+idemKey+".json")
	if status == "acked" && hasAckWithKey(rec, idemKey) {
		return &AckResult{
			File:           filepath.Base(path),
			LegID:          legID,
			Goal:           goal,
			IdempotencyKey: idemKey,
			IdempotentHit:  true,
			Status:         status,
		}, nil
	}
	if _, err := os.Stat(ackLedgerPath); err == nil && status == "acked" {
		return &AckResult{
			File:           filepath.Base(path),
			LegID:          legID,
			Goal:           goal,
			IdempotencyKey: idemKey,
			IdempotentHit:  true,
			Status:         status,
		}, nil
	}

	stamp := now.UTC().Format(time.RFC3339Nano)
	rec["status"] = "acked"
	var relayEvents []any
	if existing, ok := rec["relay"].([]any); ok {
		relayEvents = append(relayEvents, existing...)
	}
	relayEvents = append(relayEvents, map[string]any{
		"event":           "ack",
		"machine":         machine,
		"agent":           agent,
		"at":              stamp,
		"note":            opts.Note,
		"idempotency_key": idemKey,
	})
	rec["relay"] = relayEvents

	if err := WriteJSONAtomic(path, rec); err != nil {
		return nil, err
	}
	// Separate ack_<key>.json receipt from completion <key>.json so Python is_duplicate_execution remains intact.
	_ = WriteJSONAtomic(ackLedgerPath, map[string]any{
		"op":              "ack",
		"idempotency_key": idemKey,
		"leg_id":          legID,
		"goal":            goal,
		"acked_utc":       stamp,
		"machine":         machine,
		"agent":           agent,
	})

	return &AckResult{
		File:           filepath.Base(path),
		LegID:          legID,
		Goal:           goal,
		IdempotencyKey: idemKey,
		IdempotentHit:  false,
		Status:         "acked",
	}, nil
}
