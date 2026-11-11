package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
)

// ClaimRecord matches `.handoffs/claims/*.json` written by Python `cmd_claim` + optional lease fencing.
type ClaimRecord struct {
	Machine         string  `json:"machine"`
	Agent           string  `json:"agent"`
	Goal            string  `json:"goal"`
	Scope           string  `json:"scope"`
	Status          string  `json:"status"`
	Session         string  `json:"session,omitempty"`
	Branch          string  `json:"branch,omitempty"`
	SHA             string  `json:"sha,omitempty"`
	CreatedUTC      string  `json:"created_utc"`
	ReleasedUTC     string  `json:"released_utc,omitempty"`
	TTLHours        float64 `json:"ttl_hours"`
	ExecutionStatus string  `json:"execution_status,omitempty"`
	FirstActionUTC  string  `json:"first_action_utc,omitempty"`
	ClaimedAtUTC    string  `json:"claimed_at_utc,omitempty"`
	LegID           string  `json:"leg_id,omitempty"`
	LeaseID         string  `json:"lease_id,omitempty"`
	FencingToken    int     `json:"fencing_token,omitempty"`
	IdempotencyKey  string  `json:"idempotency_key,omitempty"`
	File            string  `json:"-"`
}

// ClaimConflict describes an active foreign claim overlapping a requested scope.
type ClaimConflict struct {
	Claim   ClaimRecord `json:"claim"`
	Overlap []string    `json:"overlap"`
}

// ClaimOptions configures `gorelay claim take`.
type ClaimOptions struct {
	Root         string
	Scope        string
	Goal         string
	Machine      string
	Agent        string
	Session      string
	LegID        string
	TTLHours     float64
	Force        bool
	FencingToken *int
	Now          time.Time
}

// ReleaseOptions configures `gorelay claim release`.
type ReleaseOptions struct {
	Root         string
	Scope        string
	Machine      string
	Session      string
	LegID        string
	AllSessions  bool
	FencingToken *int
	Now          time.Time
}

func resolveClaimTTLHours() float64 {
	if raw := strings.TrimSpace(os.Getenv("NOUGEN_CLAIM_TTL_HOURS")); raw != "" {
		if v, err := strconv.ParseFloat(raw, 64); err == nil && v > 0 {
			return v
		}
	}
	return defaultClaimTTLHours
}

// ClaimIsActive mirrors core.claim_is_active (status == "active" && age <= ttl_hours).
func ClaimIsActive(rec ClaimRecord, now time.Time) bool {
	if rec.Status != "active" {
		return false
	}
	t, ok := parseRFC3339OrISO(rec.CreatedUTC)
	if !ok {
		return true
	}
	ttl := rec.TTLHours
	if ttl <= 0 {
		ttl = resolveClaimTTLHours()
	}
	return now.UTC().Sub(t).Hours() <= ttl
}

// ReadClaims reads `.handoffs/claims/*.json`, normalizing legacy JSON list scopes to strings.
func ReadClaims(claimsDir string) ([]ClaimRecord, error) {
	paths, err := filepath.Glob(filepath.Join(claimsDir, "*.json"))
	if err != nil {
		return nil, err
	}
	sort.Strings(paths)
	out := make([]ClaimRecord, 0, len(paths))
	for _, p := range paths {
		raw, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		var doc map[string]any
		if err := json.Unmarshal(raw, &doc); err != nil {
			continue
		}
		// Normalize legacy list-typed `scope` before struct unmarshaling.
		doc["scope"] = NormalizeScopeValue(doc["scope"])
		normalized, err := json.Marshal(doc)
		if err != nil {
			continue
		}
		var rec ClaimRecord
		if err := json.Unmarshal(normalized, &rec); err != nil {
			continue
		}
		rec.File = filepath.Base(p)
		out = append(out, rec)
	}
	return out, nil
}

// CheckClaims returns active foreign claims whose scope overlaps `scope`.
func CheckClaims(root, scope, selfMachine string, now time.Time) ([]ClaimConflict, error) {
	if strings.TrimSpace(scope) == "" {
		return nil, fmt.Errorf("--scope is required")
	}
	claims, err := ReadClaims(ClaimsDir(root))
	if err != nil {
		return nil, err
	}
	type key struct {
		machine string
		scope   string
	}
	latest := map[key]ClaimRecord{}
	order := []key{}
	for _, rec := range claims {
		if rec.Machine == selfMachine || !ClaimIsActive(rec, now) {
			continue
		}
		k := key{machine: rec.Machine, scope: rec.Scope}
		if _, exists := latest[k]; !exists {
			order = append(order, k)
		}
		latest[k] = rec
	}
	var conflicts []ClaimConflict
	for _, k := range order {
		rec := latest[k]
		if overlap := ScopesOverlap(scope, rec.Scope); len(overlap) > 0 {
			conflicts = append(conflicts, ClaimConflict{Claim: rec, Overlap: overlap})
		}
	}
	return conflicts, nil
}

// UniqueRecordName mirrors core.unique_record_name (`<utc>__<machine>__<agent>` with -2, -3 suffix).
func UniqueRecordName(dir string, now time.Time, machine, agent string) string {
	base := now.UTC().Format("20060102T150405Z")
	suffix := ""
	n := 2
	for {
		stem := fmt.Sprintf("%s%s__%s__%s", base, suffix, machine, agent)
		_, errJSON := os.Stat(filepath.Join(dir, stem+".json"))
		_, errMD := os.Stat(filepath.Join(dir, stem+".md"))
		if os.IsNotExist(errJSON) && os.IsNotExist(errMD) {
			return stem
		}
		suffix = fmt.Sprintf("-%d", n)
		n++
	}
}

// TakeClaim writes a claim record with idempotent self-reuse, overlap checks, and optional lease fencing.
func TakeClaim(opts ClaimOptions) (*ClaimRecord, []ClaimConflict, bool, error) {
	if strings.TrimSpace(opts.Scope) == "" {
		return nil, nil, false, fmt.Errorf("--scope is required")
	}
	root := ResolveRoot(opts.Root)
	machine := ResolveMachine(opts.Machine)
	agent := ResolveAgent(opts.Agent)
	session := ResolveSession(opts.Session)
	now := opts.Now
	if now.IsZero() {
		now = time.Now().UTC()
	}

	unlock, err := AcquireWriterLock(root)
	if err != nil {
		return nil, nil, false, err
	}
	defer unlock()

	conflicts, err := CheckClaims(root, opts.Scope, machine, now)
	if err != nil {
		return nil, nil, false, err
	}
	if len(conflicts) > 0 && !opts.Force {
		return nil, conflicts, false, fmt.Errorf("%d active foreign claim(s) overlap scope %q", len(conflicts), opts.Scope)
	}

	idemSubject := opts.LegID
	if idemSubject == "" {
		idemSubject = machine + "/" + agent + ":" + strings.Join(NormalizeScope(opts.Scope), " ")
	}
	idemKey := ComputeIdempotencyKey(idemSubject, opts.Goal)

	existingClaims, err := ReadClaims(ClaimsDir(root))
	if err != nil {
		return nil, nil, false, err
	}
	for _, c := range existingClaims {
		if c.Machine == machine && c.Agent == agent && (session == "" || c.Session == session) &&
			ClaimIsActive(c, now) && c.IdempotencyKey == idemKey {
			if opts.LegID != "" {
				lease, err := AcquireLease(root, opts.LegID, machine, agent, session, opts.Goal, 0, opts.Force, now)
				if err != nil {
					return nil, nil, false, err
				}
				c.LeaseID = lease.LeaseID
				c.FencingToken = lease.FencingToken
				_ = WriteJSONAtomic(filepath.Join(ClaimsDir(root), c.File), &c)
			}
			return &c, nil, true, nil
		}
	}

	if opts.FencingToken != nil && opts.LegID == "" {
		return nil, nil, false, fmt.Errorf("--fencing-token requires --leg")
	}
	var lease *LeaseRecord
	if opts.LegID != "" {
		if opts.FencingToken != nil {
			if err := CheckLeaseFencing(root, opts.LegID, opts.FencingToken, "claim:take", now); err != nil {
				return nil, nil, false, err
			}
		}
		lease, err = AcquireLease(root, opts.LegID, machine, agent, session, opts.Goal, 0, opts.Force, now)
		if err != nil {
			return nil, nil, false, err
		}
	}

	ttl := opts.TTLHours
	if ttl <= 0 {
		ttl = resolveClaimTTLHours()
	}
	dir := ClaimsDir(root)
	name := UniqueRecordName(dir, now, machine, agent)
	stamp := now.UTC().Format(time.RFC3339Nano)
	rec := &ClaimRecord{
		Machine:         machine,
		Agent:           agent,
		Goal:            opts.Goal,
		Scope:           opts.Scope,
		Status:          "active",
		Session:         session,
		CreatedUTC:      stamp,
		TTLHours:        ttl,
		ExecutionStatus: "executing",
		FirstActionUTC:  stamp,
		ClaimedAtUTC:    stamp,
		LegID:           opts.LegID,
		IdempotencyKey:  idemKey,
		File:            name + ".json",
	}
	if lease != nil {
		rec.LeaseID = lease.LeaseID
		rec.FencingToken = lease.FencingToken
	}
	if err := WriteJSONAtomic(filepath.Join(dir, rec.File), rec); err != nil {
		return nil, nil, false, err
	}
	return rec, nil, false, nil
}

// ReleaseClaims releases active local claims matching machine/scope/session and optional fenced lease.
func ReleaseClaims(opts ReleaseOptions) (int, int, error) {
	root := ResolveRoot(opts.Root)
	machine := ResolveMachine(opts.Machine)
	session := ResolveSession(opts.Session)
	now := opts.Now
	if now.IsZero() {
		now = time.Now().UTC()
	}

	unlock, err := AcquireWriterLock(root)
	if err != nil {
		return 0, 0, err
	}
	defer unlock()

	if opts.LegID != "" {
		if err := ReleaseLease(root, opts.LegID, "released", opts.FencingToken, "claim:release", now); err != nil {
			return 0, 0, err
		}
	}

	dir := ClaimsDir(root)
	claims, err := ReadClaims(dir)
	if err != nil {
		return 0, 0, err
	}
	released := 0
	skippedOther := 0
	stamp := now.UTC().Format(time.RFC3339Nano)
	for _, c := range claims {
		if c.Machine != machine || c.Status != "active" {
			continue
		}
		if opts.Scope != "" && len(ScopesOverlap(opts.Scope, c.Scope)) == 0 {
			continue
		}
		if c.Session != "" && session != "" && c.Session != session && !opts.AllSessions {
			skippedOther++
			continue
		}
		if opts.LegID != "" && c.LegID != "" && c.LegID != opts.LegID {
			continue
		}
		c.Status = "released"
		c.ReleasedUTC = stamp
		if err := WriteJSONAtomic(filepath.Join(dir, c.File), &c); err != nil {
			return released, skippedOther, err
		}
		released++
	}
	return released, skippedOther, nil
}
