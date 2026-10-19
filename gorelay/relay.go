// Package main is a static, dependency-free port of `nougen relay open`:
// list handoff legs from other machines that nobody has acked.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
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

func main() {
	dir := os.Getenv("NOUGEN_GIT_HANDOFF_DIR")
	if dir == "" {
		dir = ".handoffs"
	}
	if len(os.Args) > 1 {
		dir = os.Args[1]
	}
	self := os.Getenv("NOUGEN_MACHINE")
	legs, err := OpenLegs(dir, self)
	if err != nil {
		fmt.Fprintln(os.Stderr, "relay open:", err)
		os.Exit(1)
	}
	if len(legs) == 0 {
		fmt.Println("✅ no unacked legs — every baton has been picked up")
		return
	}
	fmt.Printf("⚠️ %d leg(s) waiting for an ack:\n", len(legs))
	for _, l := range legs {
		goal := l.Goal
		if goal == "" {
			goal = "(no goal)"
		}
		fmt.Printf("  • %s/%s — %s\n", l.Machine, l.Agent, goal)
	}
}
