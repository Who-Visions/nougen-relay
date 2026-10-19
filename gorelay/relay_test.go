package main

import (
	"os"
	"path/filepath"
	"testing"
)

func write(t *testing.T, dir, name, body string) {
	t.Helper()
	if err := os.WriteFile(filepath.Join(dir, name), []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestOpenLegs(t *testing.T) {
	d := t.TempDir()
	write(t, d, "b.json", `{"machine":"node-b","agent":"x","goal":"later","created_utc":"2026-10-02"}`)
	write(t, d, "a.json", `{"machine":"node-b","agent":"x","goal":"earlier","status":"open","created_utc":"2026-10-01"}`)
	write(t, d, "mine.json", `{"machine":"node-a","created_utc":"2026-10-01"}`)
	write(t, d, "done.json", `{"machine":"node-b","status":"acked","created_utc":"2026-10-01"}`)
	write(t, d, "bad.json", `{not json`)
	legs, err := OpenLegs(d, "node-a")
	if err != nil {
		t.Fatal(err)
	}
	if len(legs) != 2 || legs[0].Goal != "earlier" || legs[1].Goal != "later" {
		t.Fatalf("got %+v", legs)
	}
}

func TestOpenLegsEmpty(t *testing.T) {
	legs, err := OpenLegs(t.TempDir(), "node-a")
	if err != nil || len(legs) != 0 {
		t.Fatalf("got %v %v", legs, err)
	}
}
