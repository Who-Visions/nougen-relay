package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// HistoryEntry mirrors Python nougen_relay.core._append_history records.
type HistoryEntry struct {
	UTC      string `json:"utc"`
	Actor    string `json:"actor"`
	From     string `json:"from,omitempty"`
	To       string `json:"to"`
	Evidence string `json:"evidence,omitempty"`
}

// RejectedOp captures a stale-token attempt on a fenced lease.
type RejectedOp struct {
	UTC   string `json:"utc"`
	Op    string `json:"op"`
	Token *int   `json:"token"`
}

// LeaseRecord matches `.relay/leases/<leg_id>.lease.json` written by Python core.py.
type LeaseRecord struct {
	LegID          string         `json:"leg_id"`
	LeaseID        string         `json:"lease_id"`
	FencingToken   int            `json:"fencing_token"`
	Machine        string         `json:"machine"`
	Agent          string         `json:"agent"`
	Session        string         `json:"session,omitempty"`
	Status         string         `json:"status"`
	State          string         `json:"state,omitempty"`
	Goal           string         `json:"goal"`
	IdempotencyKey string         `json:"idempotency_key"`
	LeasedUTC      string         `json:"leased_utc"`
	HeartbeatUTC   string         `json:"heartbeat_utc"`
	UpdatedUTC     string         `json:"updated_utc,omitempty"`
	ReleasedUTC    string         `json:"released_utc,omitempty"`
	HeartbeatCount int            `json:"heartbeat_count"`
	TTLMinutes     float64        `json:"ttl_minutes"`
	RetryCount     int            `json:"retry_count"`
	AttemptCount   int            `json:"attempt_count"`
	MaxRetries     *int           `json:"max_retries,omitempty"`
	History        []HistoryEntry `json:"history,omitempty"`
	Rejected       []RejectedOp   `json:"rejected,omitempty"`
}

var statusToLeaseState = map[string]string{
	"active":        "LEASED",
	"released":      "RELEASED",
	"complete":      "COMPLETE",
	"failed":        "RETRY_WAIT",
	"retry_pending": "RETRY_WAIT",
	"dead_letter":   "DEAD_LETTER",
	"expired":       "CLAIMABLE",
	"blocked":       "BLOCKED",
	"abandoned":     "RELEASED",
	"superseded":    "SUPERSEDED",
}

func resolveLeaseTTLMinutes() float64 {
	if raw := strings.TrimSpace(os.Getenv("NOUGEN_LEASE_TTL_MINUTES")); raw != "" {
		if v, err := strconv.ParseFloat(raw, 64); err == nil && v > 0 {
			return v
		}
	}
	return defaultLeaseTTLMinutes
}

func parseRFC3339OrISO(stamp string) (time.Time, bool) {
	s := strings.TrimSpace(stamp)
	if s == "" {
		return time.Time{}, false
	}
	for _, layout := range []string{time.RFC3339Nano, time.RFC3339, "2006-01-02T15:04:05.999999-07:00", "2006-01-02T15:04:05"} {
		if t, err := time.Parse(layout, s); err == nil {
			return t.UTC(), true
		}
	}
	return time.Time{}, false
}

// LeaseIsActive mirrors core.lease_is_active evaluated at `now`.
func LeaseIsActive(rec *LeaseRecord, now time.Time) bool {
	if rec == nil || rec.Status != "active" {
		return false
	}
	stamp := rec.HeartbeatUTC
	if stamp == "" {
		stamp = rec.LeasedUTC
	}
	t, ok := parseRFC3339OrISO(stamp)
	if !ok {
		return true
	}
	ttl := rec.TTLMinutes
	if ttl <= 0 {
		ttl = resolveLeaseTTLMinutes()
	}
	return now.UTC().Sub(t).Minutes() <= ttl
}

// FencingOK mirrors core.fencing_ok: nil token allows legacy callers unless enforced explicitly.
func FencingOK(rec *LeaseRecord, token *int) bool {
	if token == nil {
		return true
	}
	if rec == nil {
		return false
	}
	return rec.FencingToken == *token
}

func readLease(root, legID string) (string, *LeaseRecord, error) {
	safe, err := SafeLegID(legID)
	if err != nil {
		return "", nil, err
	}
	path := filepath.Join(LeasesDir(root), safe+".lease.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return path, nil, nil
		}
		return path, nil, err
	}
	var rec LeaseRecord
	if err := json.Unmarshal(raw, &rec); err != nil {
		return path, nil, nil // treat corrupt lease file as reclaimable, matching core.py
	}
	return path, &rec, nil
}

func appendLeaseHistory(rec *LeaseRecord, actor, fromState, toState, evidence string, now time.Time) {
	if len(evidence) > 300 {
		evidence = evidence[:300]
	}
	stamp := now.UTC().Format(time.RFC3339Nano)
	rec.History = append(rec.History, HistoryEntry{
		UTC:      stamp,
		Actor:    actor,
		From:     fromState,
		To:       toState,
		Evidence: evidence,
	})
	if len(rec.History) > defaultLeaseHistoryMax {
		rec.History = rec.History[len(rec.History)-defaultLeaseHistoryMax:]
	}
	rec.State = toState
	rec.UpdatedUTC = stamp
}

// AcquireLease acquires or renews an exclusive fenced lease with monotonic fencing_token.
func AcquireLease(root, legID, machine, agent, session, goal string, ttlMinutes float64, force bool, now time.Time) (*LeaseRecord, error) {
	safeLeg, err := SafeLegID(legID)
	if err != nil {
		return nil, err
	}
	path, existing, err := readLease(root, safeLeg)
	if err != nil {
		return nil, err
	}
	if ttlMinutes <= 0 {
		ttlMinutes = resolveLeaseTTLMinutes()
	}
	stamp := now.UTC().Format(time.RFC3339Nano)

	var (
		priorToken      int
		priorRetryCount int
		priorMaxRetries *int
		priorHistory    []HistoryEntry
		acquireEvidence = "acquire"
	)

	if existing != nil {
		priorToken = existing.FencingToken
		priorHistory = append([]HistoryEntry(nil), existing.History...)
		if !force {
			if LeaseIsActive(existing, now) {
				sameHolder := existing.Machine == machine &&
					existing.Agent == agent &&
					(session == "" || existing.Session == session)
				if sameHolder {
					existing.LeasedUTC = stamp
					existing.HeartbeatUTC = stamp
					existing.TTLMinutes = ttlMinutes
					curState := existing.State
					if curState == "" {
						curState = "LEASED"
					}
					appendLeaseHistory(existing, machine+"/"+agent, curState, curState, "renew", now)
					if err := WriteJSONAtomic(path, existing); err != nil {
						return nil, err
					}
					return existing, nil
				}
				return nil, fmt.Errorf("active lease held by %s/%s (token %d)", existing.Machine, existing.Agent, existing.FencingToken)
			}
			if existing.Status == "dead_letter" || existing.Status == "complete" {
				return nil, fmt.Errorf("lease %s is %s and cannot be reclaimed without --force", safeLeg, existing.Status)
			}
			if existing.MaxRetries != nil && existing.RetryCount >= *existing.MaxRetries {
				return nil, fmt.Errorf("lease %s exhausted max retries (%d)", safeLeg, *existing.MaxRetries)
			}
			priorRetryCount = existing.RetryCount
			priorMaxRetries = existing.MaxRetries
			acquireEvidence = fmt.Sprintf("reclaim: %s lease from %s/%s token %d", existing.Status, existing.Machine, existing.Agent, priorToken)
		} else {
			priorRetryCount = existing.RetryCount
			priorMaxRetries = existing.MaxRetries
			acquireEvidence = fmt.Sprintf("force: took over %s lease token %d", existing.Status, priorToken)
		}
	}

	leaseID, err := randomHexID(6) // 12 lowercase hex chars, matching core.new_lease_id()
	if err != nil {
		return nil, err
	}
	rec := &LeaseRecord{
		LegID:          safeLeg,
		LeaseID:        leaseID,
		FencingToken:   priorToken + 1,
		Machine:        machine,
		Agent:          agent,
		Session:        session,
		Status:         "active",
		Goal:           goal,
		IdempotencyKey: ComputeIdempotencyKey(safeLeg, goal),
		LeasedUTC:      stamp,
		HeartbeatUTC:   stamp,
		HeartbeatCount: 0,
		TTLMinutes:     ttlMinutes,
		RetryCount:     priorRetryCount,
		AttemptCount:   priorRetryCount + 1,
		MaxRetries:     priorMaxRetries,
		History:        priorHistory,
	}
	appendLeaseHistory(rec, machine+"/"+agent, "CLAIMABLE", "LEASED", acquireEvidence, now)
	if err := WriteJSONAtomic(path, rec); err != nil {
		return nil, err
	}
	return rec, nil
}

// HeartbeatLease updates heartbeat_utc if active and fencing_token matches.
func HeartbeatLease(root, legID string, token *int, state string, now time.Time) error {
	path, rec, err := readLease(root, legID)
	if err != nil {
		return err
	}
	if rec == nil || !LeaseIsActive(rec, now) {
		return fmt.Errorf("no active lease for %q", legID)
	}
	if !FencingOK(rec, token) {
		rec.Rejected = append(rec.Rejected, RejectedOp{
			UTC:   now.UTC().Format(time.RFC3339Nano),
			Op:    "heartbeat",
			Token: token,
		})
		_ = WriteJSONAtomic(path, rec)
		return fmt.Errorf("stale fencing token %v (current %d)", *token, rec.FencingToken)
	}
	if state == "" {
		state = "RUNNING"
	}
	rec.HeartbeatUTC = now.UTC().Format(time.RFC3339Nano)
	rec.HeartbeatCount++
	if rec.State != state {
		appendLeaseHistory(rec, rec.Machine+"/"+rec.Agent, rec.State, state, "heartbeat", now)
	}
	return WriteJSONAtomic(path, rec)
}

// ReleaseLease closes an execution lease if fencing_token matches.
func ReleaseLease(root, legID, status string, token *int, evidence string, now time.Time) error {
	path, rec, err := readLease(root, legID)
	if err != nil {
		return err
	}
	if rec == nil {
		return fmt.Errorf("lease not found for %q", legID)
	}
	if status == "" {
		status = "released"
	}
	if !FencingOK(rec, token) {
		rec.Rejected = append(rec.Rejected, RejectedOp{
			UTC:   now.UTC().Format(time.RFC3339Nano),
			Op:    "release:" + status,
			Token: token,
		})
		_ = WriteJSONAtomic(path, rec)
		return fmt.Errorf("stale fencing token %v rejected (current %d)", *token, rec.FencingToken)
	}
	rec.Status = status
	rec.ReleasedUTC = now.UTC().Format(time.RFC3339Nano)
	toState := statusToLeaseState[status]
	if toState == "" {
		toState = strings.ToUpper(status)
	}
	if evidence == "" {
		evidence = "release:" + status
	}
	appendLeaseHistory(rec, rec.Machine+"/"+rec.Agent, rec.State, toState, evidence, now)
	return WriteJSONAtomic(path, rec)
}

// CheckLeaseFencing validates an explicit fencing token against any stored lease, logging rejections.
func CheckLeaseFencing(root, legID string, token *int, op string, now time.Time) error {
	if token == nil {
		return nil
	}
	path, rec, err := readLease(root, legID)
	if err != nil {
		return err
	}
	if rec == nil {
		return fmt.Errorf("fencing token %d rejected: no lease found for %q", *token, legID)
	}
	if !FencingOK(rec, token) {
		rec.Rejected = append(rec.Rejected, RejectedOp{
			UTC:   now.UTC().Format(time.RFC3339Nano),
			Op:    op,
			Token: token,
		})
		_ = WriteJSONAtomic(path, rec)
		return fmt.Errorf("stale fencing token %d rejected on %s (current %d)", *token, op, rec.FencingToken)
	}
	return nil
}

func decodeJSONPreservingNumbers(raw []byte) (map[string]any, error) {
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	var m map[string]any
	if err := dec.Decode(&m); err != nil {
		return nil, err
	}
	return m, nil
}
