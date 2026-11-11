package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"
)

type vectorsFixture struct {
	ReferenceNowUTC     string   `json:"reference_now_utc"`
	OpenLegsSelfMachine string   `json:"open_legs_self_machine"`
	ExpectedOpenFiles   []string `json:"expected_open_files"`
	IdempotencyKeys     []struct {
		LegID          string `json:"leg_id"`
		Goal           string `json:"goal"`
		ExpectedSHA256 string `json:"expected_sha256"`
	} `json:"idempotency_keys"`
	ScopeNormalization []struct {
		Raw    string   `json:"raw"`
		Tokens []string `json:"tokens"`
	} `json:"scope_normalization"`
	ScopeOverlap []struct {
		A               string   `json:"a"`
		B               string   `json:"b"`
		ExpectedOverlap []string `json:"expected_overlap"`
	} `json:"scope_overlap"`
}

func loadVectors(t *testing.T) vectorsFixture {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("testdata", "protocol", "vectors.json"))
	if err != nil {
		t.Fatal(err)
	}
	var v vectorsFixture
	if err := json.Unmarshal(raw, &v); err != nil {
		t.Fatal(err)
	}
	return v
}

func copyFixture(t *testing.T, relSrc, dstPath string) {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("testdata", "protocol", relSrc))
	if err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Dir(dstPath), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(dstPath, raw, 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestPhase0VectorsAndOpenLegs(t *testing.T) {
	v := loadVectors(t)
	for _, tc := range v.IdempotencyKeys {
		got := ComputeIdempotencyKey(tc.LegID, tc.Goal)
		if got != tc.ExpectedSHA256 {
			t.Fatalf("idempotency(%q, %q) = %s, want %s", tc.LegID, tc.Goal, got, tc.ExpectedSHA256)
		}
	}
	for _, tc := range v.ScopeNormalization {
		got := NormalizeScope(tc.Raw)
		if !reflect.DeepEqual(got, tc.Tokens) {
			t.Fatalf("normalize(%q) = %v, want %v", tc.Raw, got, tc.Tokens)
		}
	}
	for _, tc := range v.ScopeOverlap {
		got := ScopesOverlap(tc.A, tc.B)
		want := tc.ExpectedOverlap
		if want == nil {
			want = []string{}
		}
		if len(got) == 0 && len(want) == 0 {
			continue
		}
		if !reflect.DeepEqual(got, want) {
			t.Fatalf("overlap(%q, %q) = %v, want %v", tc.A, tc.B, got, want)
		}
	}

	legs, err := OpenLegs(filepath.Join("testdata", "protocol", "handoffs"), v.OpenLegsSelfMachine)
	if err != nil {
		t.Fatal(err)
	}
	var gotFiles []string
	for _, l := range legs {
		gotFiles = append(gotFiles, l.File)
	}
	if !reflect.DeepEqual(gotFiles, v.ExpectedOpenFiles) {
		t.Fatalf("open legs = %v, want %v", gotFiles, v.ExpectedOpenFiles)
	}
}

func TestAckIdempotencyFencingAndFieldPreservation(t *testing.T) {
	v := loadVectors(t)
	now, _ := parseRFC3339OrISO(v.ReferenceNowUTC)
	root := t.TempDir()
	hdir := filepath.Join(root, ".handoffs")
	legFile := "20261111T172801Z__node-b__worker.json"
	copyFixture(t, "handoffs/open_explicit.json", filepath.Join(hdir, legFile))
	copyFixture(t, "handoffs/complete.json", filepath.Join(hdir, "complete.json"))

	// Acquire lease so fencing token 1 is active.
	lease, err := AcquireLease(root, "20261111T172801Z__node-b__worker", "node-a", "runner", "sess-1", "Add ack and claim to gorelay", 10, false, now)
	if err != nil {
		t.Fatal(err)
	}
	if lease.FencingToken != 1 || len(lease.LeaseID) != 12 {
		t.Fatalf("unexpected lease: %+v", lease)
	}

	// Stale fencing token must be rejected and recorded in lease.Rejected.
	badTok := 99
	if _, err := AckLeg(AckOptions{Root: root, LegID: "20261111T172801Z__node-b__worker", Machine: "node-a", Agent: "runner", FencingToken: &badTok, Now: now}); err == nil {
		t.Fatal("expected stale fencing token error")
	}
	_, updatedLease, err := readLease(root, "20261111T172801Z__node-b__worker")
	if err != nil || updatedLease == nil || len(updatedLease.Rejected) != 1 {
		t.Fatalf("expected rejected attempt persisted on lease, got %+v err=%v", updatedLease, err)
	}

	// Valid fencing token acks cleanly and preserves unknown fields (`branch`, `sha`, `dirty`, `stack`).
	goodTok := 1
	res, err := AckLeg(AckOptions{Root: root, LegID: "20261111T172801Z__node-b__worker", Machine: "node-a", Agent: "runner", Note: "taking leg", FencingToken: &goodTok, Now: now})
	if err != nil {
		t.Fatal(err)
	}
	if res.IdempotentHit || res.IdempotencyKey != v.IdempotencyKeys[0].ExpectedSHA256 {
		t.Fatalf("unexpected ack result: %+v", res)
	}

	raw, err := os.ReadFile(filepath.Join(hdir, legFile))
	if err != nil {
		t.Fatal(err)
	}
	doc, err := decodeJSONPreservingNumbers(raw)
	if err != nil {
		t.Fatal(err)
	}
	if doc["status"] != "acked" || doc["branch"] != "feat/example" || doc["sha"] != "abc1234" {
		t.Fatalf("ack lost fields or failed status update: %v", doc)
	}
	if evs, ok := doc["relay"].([]any); !ok || len(evs) != 1 {
		t.Fatalf("expected 1 relay event, got %v", doc["relay"])
	}

	// Idempotent replay with same key must short-circuit without duplicating relay[].
	replay, err := AckLeg(AckOptions{Root: root, LegID: "20261111T172801Z__node-b__worker", Machine: "node-a", Agent: "runner", Note: "taking leg", FencingToken: &goodTok, Now: now.Add(time.Minute)})
	if err != nil {
		t.Fatal(err)
	}
	if !replay.IdempotentHit {
		t.Fatal("expected second ack to report IdempotentHit=true")
	}
	raw2, _ := os.ReadFile(filepath.Join(hdir, legFile))
	doc2, _ := decodeJSONPreservingNumbers(raw2)
	if evs, ok := doc2["relay"].([]any); !ok || len(evs) != 1 {
		t.Fatalf("idempotent ack appended duplicate relay event: %v", doc2["relay"])
	}

	// Terminal complete leg cannot be downgraded back to acked.
	if _, err := AckLeg(AckOptions{Root: root, LegID: "complete.json", Machine: "node-a", Agent: "runner", Now: now}); err == nil {
		t.Fatal("expected error acking terminal complete leg")
	}
}

func TestClaimCheckTakeReleaseFencingAndLegacyFixtures(t *testing.T) {
	v := loadVectors(t)
	now, _ := parseRFC3339OrISO(v.ReferenceNowUTC)
	root := t.TempDir()
	claimsDir := ClaimsDir(root)
	for _, f := range []string{"active_string_scope.json", "active_list_scope.json", "released_claim.json", "expired_claim.json"} {
		copyFixture(t, filepath.Join("claims", f), filepath.Join(claimsDir, f))
	}

	// Active string-scope overlap.
	conflicts, err := CheckClaims(root, `src\pkg\a.py`, "node-a", now)
	if err != nil || len(conflicts) != 1 || conflicts[0].Overlap[0] != "src/pkg/a.py" {
		t.Fatalf("expected conflict on string scope, got %+v err=%v", conflicts, err)
	}
	// Legacy list-scope overlap.
	conflictsLegacy, err := CheckClaims(root, "src/pkg/legacy.py", "node-a", now)
	if err != nil || len(conflictsLegacy) != 1 {
		t.Fatalf("expected conflict on legacy list scope, got %+v err=%v", conflictsLegacy, err)
	}
	// Released and expired fixtures must not block claims.
	for _, clearScope := range []string{"src/pkg/released.py", "src/pkg/expired.py"} {
		c, err := CheckClaims(root, clearScope, "node-a", now)
		if err != nil || len(c) != 0 {
			t.Fatalf("expected %s clear, got %+v err=%v", clearScope, c, err)
		}
	}

	// Take claim with fenced leg, check idempotent reuse, heartbeat, reclaim + stale fence reject.
	rec, _, hit, err := TakeClaim(ClaimOptions{
		Root:    root,
		Scope:   "gorelay/claim.go",
		Goal:    "Implement fenced claims",
		Machine: "node-a",
		Agent:   "runner",
		Session: "sess-a",
		LegID:   "L-FENCE-1",
		Now:     now,
	})
	if err != nil || hit || rec.FencingToken != 1 || len(rec.LeaseID) != 12 {
		t.Fatalf("unexpected take result: rec=%+v hit=%v err=%v", rec, hit, err)
	}

	// Same holder retry is idempotent (no duplicate claim file).
	rec2, _, hit2, err := TakeClaim(ClaimOptions{
		Root:    root,
		Scope:   "gorelay/claim.go",
		Goal:    "Implement fenced claims",
		Machine: "node-a",
		Agent:   "runner",
		Session: "sess-a",
		LegID:   "L-FENCE-1",
		Now:     now,
	})
	if err != nil || !hit2 || rec2.File != rec.File {
		t.Fatalf("expected idempotent claim reuse, got rec=%+v hit=%v err=%v", rec2, hit2, err)
	}

	// Simulate lease expiry (15m > 10m TTL); second worker reclaims token=2, stale token=1 fails release.
	later := now.Add(15 * time.Minute)
	lease2, err := AcquireLease(root, "L-FENCE-1", "node-c", "runner", "sess-c", "Implement fenced claims", 10, false, later)
	if err != nil || lease2.FencingToken != 2 || lease2.AttemptCount != 1 || !strings.HasPrefix(lease2.History[len(lease2.History)-1].Evidence, "reclaim:") {
		t.Fatalf("expected monotonic reclaim token=2, got %+v err=%v", lease2, err)
	}
	staleTok := 1
	if _, _, err := ReleaseClaims(ReleaseOptions{Root: root, Scope: "gorelay/claim.go", Machine: "node-a", Session: "sess-a", LegID: "L-FENCE-1", FencingToken: &staleTok, Now: later}); err == nil {
		t.Fatal("expected stale token release to fail")
	}

	validTok := 2
	if err := ReleaseLease(root, "L-FENCE-1", "complete", &validTok, "verified", later); err != nil {
		t.Fatalf("expected token 2 release to succeed: %v", err)
	}
	// Sibling session isolation during ReleaseClaims.
	relCount, skippedCount, err := ReleaseClaims(ReleaseOptions{Root: root, Scope: "gorelay/claim.go", Machine: "node-a", Session: "sess-other", Now: later})
	if err != nil || relCount != 0 || skippedCount != 1 {
		t.Fatalf("expected sibling claim preserved, got rel=%d skip=%d err=%v", relCount, skippedCount, err)
	}
	relCount2, _, err := ReleaseClaims(ReleaseOptions{Root: root, Scope: "gorelay/claim.go", Machine: "node-a", Session: "sess-a", Now: later})
	if err != nil || relCount2 != 1 {
		t.Fatalf("expected owning session claim released, got rel=%d err=%v", relCount2, err)
	}
	_ = strings.TrimSpace("")
}
