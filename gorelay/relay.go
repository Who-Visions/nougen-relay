// Package main is a static, dependency-free Go implementation of the
// NouGenRelay hot-path protocol (`open`, `ack`, `claim`, `lease`).
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const (
	exitOK       = 0
	exitFailure  = 1
	exitUsage    = 2
	exitDiverged = 3
)

// Leg is the subset of a handoff record that `relay open` reads.
type Leg struct {
	Machine    string `json:"machine"`
	Agent      string `json:"agent"`
	Goal       string `json:"goal"`
	Status     string `json:"status"`
	CreatedUTC string `json:"created_utc"`
	File       string `json:"-"`
}

// status mirrors relay_status: a missing status means open.
func (l Leg) status() string {
	if l.Status == "" {
		return "open"
	}
	return l.Status
}

// OpenLegs returns unacked legs from machines other than self, oldest first,
// de-duplicated by file name. Unreadable or malformed records are skipped.
func OpenLegs(dir, self string) ([]Leg, error) {
	paths, err := filepath.Glob(filepath.Join(dir, "*.json"))
	if err != nil {
		return nil, err
	}
	seen := map[string]bool{}
	var out []Leg
	for _, p := range paths {
		raw, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		var l Leg
		if json.Unmarshal(raw, &l) != nil {
			continue
		}
		l.File = filepath.Base(p)
		if l.Machine == self || l.status() != "open" || seen[l.File] {
			continue
		}
		seen[l.File] = true
		out = append(out, l)
	}
	sort.SliceStable(out, func(i, j int) bool { return out[i].CreatedUTC < out[j].CreatedUTC })
	return out, nil
}

func runOpen(args []string) int {
	fs := flag.NewFlagSet("open", flag.ContinueOnError)
	dirFlag := fs.String("dir", "", "handoffs directory")
	machineFlag := fs.String("machine", "", "self machine name")
	strictFlag := fs.Bool("strict", false, "exit 3 when open legs exist")
	if err := fs.Parse(args); err != nil {
		return exitUsage
	}
	dir := strings.TrimSpace(*dirFlag)
	if dir == "" && fs.NArg() > 0 {
		dir = fs.Arg(0)
	}
	if dir == "" {
		dir = os.Getenv("NOUGEN_GIT_HANDOFF_DIR")
	}
	if dir == "" {
		dir = ".handoffs"
	}
	self := ResolveMachine(*machineFlag)
	if *machineFlag == "" && strings.TrimSpace(os.Getenv("NOUGEN_MACHINE")) == "" {
		// Preserve historical empty self when NOUGEN_MACHINE unset on bare `gorelay open`.
		self = ""
	}
	legs, err := OpenLegs(dir, self)
	if err != nil {
		fmt.Fprintln(os.Stderr, "relay open:", err)
		return exitFailure
	}
	if len(legs) == 0 {
		fmt.Println("✅ no unacked legs — every baton has been picked up")
		return exitOK
	}
	fmt.Printf("⚠️ %d leg(s) waiting for an ack:\n", len(legs))
	for _, l := range legs {
		goal := l.Goal
		if goal == "" {
			goal = "(no goal)"
		}
		fmt.Printf("  • %s/%s — %s\n", l.Machine, l.Agent, goal)
	}
	if *strictFlag {
		return exitDiverged
	}
	return exitOK
}

func runAck(args []string) int {
	fs := flag.NewFlagSet("ack", flag.ContinueOnError)
	root := fs.String("root", "", "relay root directory")
	dir := fs.String("dir", "", "handoffs directory")
	id := fs.String("id", "", "handoff record id")
	machine := fs.String("machine", "", "machine identity")
	agent := fs.String("agent", "", "agent identity")
	note := fs.String("m", "", "ack note")
	noteLong := fs.String("message", "", "ack note")
	idem := fs.String("idempotency-key", "", "explicit SHA-256 idempotency key")
	fencing := fs.Int("fencing-token", -1, "lease fencing token")
	if err := fs.Parse(args); err != nil {
		return exitUsage
	}
	msg := *note
	if *noteLong != "" {
		msg = *noteLong
	}
	var tokenPtr *int
	if *fencing >= 0 {
		t := *fencing
		tokenPtr = &t
	}
	res, err := AckLeg(AckOptions{
		Root:           *root,
		HandoffsDir:    *dir,
		LegID:          *id,
		Machine:        *machine,
		Agent:          *agent,
		Note:           msg,
		IdempotencyKey: *idem,
		FencingToken:   tokenPtr,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "❌ relay ack:", err)
		return exitFailure
	}
	tag := "baton taken"
	if res.IdempotentHit {
		tag = "idempotent ack replay"
	}
	fmt.Printf("✅ %s: %s (idempotency=%s)\n", tag, res.LegID, res.IdempotencyKey)
	return exitOK
}

func runClaim(args []string) int {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "usage: gorelay claim <check|take|release|list> [flags]")
		return exitUsage
	}
	sub := args[0]
	rest := args[1:]
	switch sub {
	case "check":
		fs := flag.NewFlagSet("claim check", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		scope := fs.String("scope", "", "scope paths or keywords")
		machine := fs.String("machine", "", "machine identity")
		if err := fs.Parse(rest); err != nil {
			return exitUsage
		}
		conflicts, err := CheckClaims(ResolveRoot(*root), *scope, ResolveMachine(*machine), time.Now().UTC())
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ claim check:", err)
			return exitUsage
		}
		if len(conflicts) > 0 {
			fmt.Printf("⚠️ %d active claim(s) overlap this scope\n", len(conflicts))
			return exitDiverged
		}
		fmt.Println("✅ no active claim overlaps this scope")
		return exitOK

	case "take":
		fs := flag.NewFlagSet("claim take", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		scope := fs.String("scope", "", "scope paths or keywords")
		goal := fs.String("goal", "", "claim goal")
		machine := fs.String("machine", "", "machine identity")
		agent := fs.String("agent", "", "agent identity")
		session := fs.String("session", "", "session identity")
		leg := fs.String("leg", "", "optional leg id to lease and fence")
		ttl := fs.Float64("ttl", 0, "claim TTL in hours")
		force := fs.Bool("force", false, "override overlapping claims/leases")
		fencing := fs.Int("fencing-token", -1, "expected lease fencing token")
		if err := fs.Parse(rest); err != nil {
			return exitUsage
		}
		var tokenPtr *int
		if *fencing >= 0 {
			t := *fencing
			tokenPtr = &t
		}
		rec, _, idemHit, err := TakeClaim(ClaimOptions{
			Root:         *root,
			Scope:        *scope,
			Goal:         *goal,
			Machine:      *machine,
			Agent:        *agent,
			Session:      *session,
			LegID:        *leg,
			TTLHours:     *ttl,
			Force:        *force,
			FencingToken: tokenPtr,
		})
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ claim take:", err)
			return exitFailure
		}
		if idemHit {
			fmt.Printf("✅ idempotent claim reuse: %s (fencing_token=%d)\n", rec.File, rec.FencingToken)
		} else {
			fmt.Printf("✅ claimed: %s (%s, fencing_token=%d)\n", rec.Scope, rec.File, rec.FencingToken)
		}
		return exitOK

	case "release":
		fs := flag.NewFlagSet("claim release", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		scope := fs.String("scope", "", "scope filter")
		machine := fs.String("machine", "", "machine identity")
		session := fs.String("session", "", "session identity")
		leg := fs.String("leg", "", "optional leg id lease to release")
		allSess := fs.Bool("all-sessions", false, "release claims from sibling sessions")
		fencing := fs.Int("fencing-token", -1, "lease fencing token")
		if err := fs.Parse(rest); err != nil {
			return exitUsage
		}
		var tokenPtr *int
		if *fencing >= 0 {
			t := *fencing
			tokenPtr = &t
		}
		rel, skipped, err := ReleaseClaims(ReleaseOptions{
			Root:         *root,
			Scope:        *scope,
			Machine:      *machine,
			Session:      *session,
			LegID:        *leg,
			AllSessions:  *allSess,
			FencingToken: tokenPtr,
		})
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ claim release:", err)
			return exitFailure
		}
		fmt.Printf("✅ released %d claim(s) (skipped_other_session=%d)\n", rel, skipped)
		return exitOK

	case "list":
		fs := flag.NewFlagSet("claim list", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		all := fs.Bool("all", false, "include expired/released claims")
		if err := fs.Parse(rest); err != nil {
			return exitUsage
		}
		claims, err := ReadClaims(ClaimsDir(ResolveRoot(*root)))
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ claim list:", err)
			return exitFailure
		}
		now := time.Now().UTC()
		count := 0
		for _, c := range claims {
			active := ClaimIsActive(c, now)
			if !*all && !active {
				continue
			}
			count++
			fmt.Printf("  [%s] %s/%s · scope=%s\n", c.Status, c.Machine, c.Agent, c.Scope)
		}
		if count == 0 {
			fmt.Println("ℹ️ no claims recorded")
		}
		return exitOK

	default:
		fmt.Fprintf(os.Stderr, "❌ unknown claim action: %s\n", sub)
		return exitUsage
	}
}

func runLease(args []string) int {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "usage: gorelay lease <acquire|heartbeat|release> [flags]")
		return exitUsage
	}
	sub := args[0]
	rest := args[1:]
	switch sub {
	case "acquire":
		fs := flag.NewFlagSet("lease acquire", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		leg := fs.String("leg", "", "leg id")
		machine := fs.String("machine", "", "machine identity")
		agent := fs.String("agent", "", "agent identity")
		session := fs.String("session", "", "session identity")
		goal := fs.String("goal", "", "leg goal")
		ttl := fs.Float64("ttl", 0, "lease TTL minutes")
		force := fs.Bool("force", false, "force reclaim")
		if err := fs.Parse(rest); err != nil || strings.TrimSpace(*leg) == "" {
			return exitUsage
		}
		resolvedRoot := ResolveRoot(*root)
		unlock, err := AcquireWriterLock(resolvedRoot)
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease acquire:", err)
			return exitFailure
		}
		defer unlock()
		rec, err := AcquireLease(resolvedRoot, *leg, ResolveMachine(*machine), ResolveAgent(*agent), ResolveSession(*session), *goal, *ttl, *force, time.Now().UTC())
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease acquire:", err)
			return exitFailure
		}
		fmt.Printf("✅ leased %s: lease_id=%s fencing_token=%d idempotency=%s\n", rec.LegID, rec.LeaseID, rec.FencingToken, rec.IdempotencyKey)
		return exitOK

	case "heartbeat":
		fs := flag.NewFlagSet("lease heartbeat", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		leg := fs.String("leg", "", "leg id")
		fencing := fs.Int("fencing-token", -1, "fencing token")
		state := fs.String("state", "RUNNING", "lease state")
		if err := fs.Parse(rest); err != nil || strings.TrimSpace(*leg) == "" {
			return exitUsage
		}
		var tokenPtr *int
		if *fencing >= 0 {
			t := *fencing
			tokenPtr = &t
		}
		resolvedRoot := ResolveRoot(*root)
		unlock, err := AcquireWriterLock(resolvedRoot)
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease heartbeat:", err)
			return exitFailure
		}
		defer unlock()
		if err := HeartbeatLease(resolvedRoot, *leg, tokenPtr, *state, time.Now().UTC()); err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease heartbeat:", err)
			return exitFailure
		}
		fmt.Printf("✅ heartbeat %s\n", *leg)
		return exitOK

	case "release":
		fs := flag.NewFlagSet("lease release", flag.ContinueOnError)
		root := fs.String("root", "", "relay root")
		leg := fs.String("leg", "", "leg id")
		status := fs.String("status", "released", "final status")
		fencing := fs.Int("fencing-token", -1, "fencing token")
		evidence := fs.String("evidence", "", "release evidence")
		if err := fs.Parse(rest); err != nil || strings.TrimSpace(*leg) == "" {
			return exitUsage
		}
		var tokenPtr *int
		if *fencing >= 0 {
			t := *fencing
			tokenPtr = &t
		}
		resolvedRoot := ResolveRoot(*root)
		unlock, err := AcquireWriterLock(resolvedRoot)
		if err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease release:", err)
			return exitFailure
		}
		defer unlock()
		if err := ReleaseLease(resolvedRoot, *leg, *status, tokenPtr, *evidence, time.Now().UTC()); err != nil {
			fmt.Fprintln(os.Stderr, "❌ lease release:", err)
			return exitFailure
		}
		fmt.Printf("✅ released lease %s (%s)\n", *leg, *status)
		return exitOK

	default:
		fmt.Fprintf(os.Stderr, "❌ unknown lease action: %s\n", sub)
		return exitUsage
	}
}

func main() {
	if len(os.Args) <= 1 {
		os.Exit(runOpen(nil))
	}
	switch os.Args[1] {
	case "open":
		os.Exit(runOpen(os.Args[2:]))
	case "ack":
		os.Exit(runAck(os.Args[2:]))
	case "claim":
		os.Exit(runClaim(os.Args[2:]))
	case "lease":
		os.Exit(runLease(os.Args[2:]))
	default:
		os.Exit(runOpen(os.Args[1:]))
	}
}
