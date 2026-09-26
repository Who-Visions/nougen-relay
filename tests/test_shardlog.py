"""`relay shards` copies a private vault into a tracked file. Three things can
go wrong, and only one of them is loud.

The loud one is writing nothing. The quiet ones are worse: leaking a credential
into a repo, and silently relaying the same knowledge twice (or skipping a day)
because the cutoff was wrong. So the scan is tested by asserting it BLOCKS, and
the cutoff is tested against a log written before the marker existed.
"""

import argparse
import json
import sqlite3
from pathlib import Path

import pytest

from nougen_relay import shardlog


def make_vault(tmp_path, rows):
    """A shard vault shaped like the real one: numbered files, one row each."""
    vault = tmp_path / "shards"
    vault.mkdir()
    for i, row in enumerate(rows, start=1):
        db = vault / f"nougen_shards_{i}.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "CREATE TABLE shards (id INTEGER PRIMARY KEY, timestamp TEXT, "
            "event_type TEXT, title TEXT, content TEXT, tags TEXT, file_hash TEXT)"
        )
        conn.execute(
            "INSERT INTO shards (timestamp, event_type, title, content, tags, file_hash)"
            " VALUES (?,?,?,?,?,?)",
            (
                row["ts"],
                "KNOWLEDGE",
                row["title"],
                row.get("content", "body"),
                json.dumps(row.get("tags", [])),
                row.get("hash", row["title"]),
            ),
        )
        conn.commit()
        conn.close()
    return vault


def run(tmp_path, vault, **over):
    args = argparse.Namespace(
        since=None, vault=str(vault), out=str(tmp_path / "docs"), date=None,
        exclude=None, include_tagged=False, dry=False,
    )
    for k, v in over.items():
        setattr(args, k, v)
    return shardlog.cmd_shards(args)


# --- the cutoff: relay each shard exactly once ------------------------------

def test_marker_sets_the_next_relay_cutoff(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "# Fleet log\n<!-- relay-shards through=2026-07-31T23:45:10.527740Z -->\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs) == "2026-07-31T23:45:10.527740Z"


def test_a_log_written_before_the_marker_still_yields_a_cutoff(tmp_path):
    """The first relay was hand-run and left no marker. If that file read as
    'never relayed', the next run would republish the whole day."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "# Fleet log — 2026-07-31\n\n"
        "## 13:56Z — first thing\n\nbody\n\n"
        "## 23:45Z — last thing\n\nbody\n\n"
        "## VERIFIED LIVE\n\nnot an entry heading\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs) == "2026-07-31T23:45:00.000000Z"


def test_prose_quoting_the_marker_format_is_not_a_cutoff(tmp_path):
    """Observed 2026-08-08, poisoning the live registry since 08-05: the
    2026-08-01 log documents the marker format in prose — `through=<iso>` —
    ABOVE its real footer. search() took the first match, `"<iso>"` won every
    string max() against real timestamps ('<' sorts above '9'), and every box
    reported 'the fleet is already current' forever after."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-08-01.md").write_text(
        "# Fleet log\n"
        "Each log ends with `<!-- relay-shards through=<iso> machine=<m> -->`.\n"
        "<!-- relay-shards through=2026-08-01T02:20:07.635032Z machine=whoart -->\n",
        encoding="utf-8",
    )
    (docs / "FLEET-LOG-2026-08-05.md").write_text(
        "# Fleet log\n<!-- relay-shards through=2026-08-05T04:55:27.029878Z machine=whoart -->\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs) == "2026-08-05T04:55:27.029878Z"


def test_a_log_whose_only_marker_is_prose_falls_back_to_headings(tmp_path):
    """A file can quote the format without ever writing a real footer — it
    must then be read like any pre-marker log, not silently skipped."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-08-01.md").write_text(
        "# Fleet log — 2026-08-01\n"
        "Each log ends with `<!-- relay-shards through=<iso> -->`.\n\n"
        "## 02:20Z — the entry\n\nbody\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs) == "2026-08-01T02:20:00.000000Z"


def test_another_machines_marker_is_not_my_cutoff(tmp_path):
    """Vaults are per-box. Observed 2026-08-08: whoart's 08-05 relay had
    advanced the fleet-wide cutoff past shards blade1tb had NEVER published —
    not republished, never offered at all, silently and permanently."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-08-05.md").write_text(
        "# Fleet log\n"
        "<!-- relay-shards through=2026-08-05T04:55:27.029878Z machine=whoart -->\n",
        encoding="utf-8",
    )
    (docs / "FLEET-LOG-2026-07-19.md").write_text(
        "# Fleet log\n"
        "<!-- relay-shards through=2026-07-19T15:14:07.803861Z machine=blade1tb -->\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs, "blade1tb") == "2026-07-19T15:14:07.803861Z"
    assert shardlog.last_relayed(docs, "whoart") == "2026-08-05T04:55:27.029878Z"
    # No machine asked = the old global answer, unchanged.
    assert shardlog.last_relayed(docs) == "2026-08-05T04:55:27.029878Z"


def test_an_unattributed_marker_still_binds_every_box(tmp_path):
    """Markers older than attribution can't be assigned, so they keep the
    conservative old meaning — and title dedup already backstops re-offers."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "<!-- relay-shards through=2026-07-31T23:45:10.527740Z -->\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs, "blade1tb") == "2026-07-31T23:45:10.527740Z"


def test_another_machines_log_headings_are_not_a_fallback_cutoff(tmp_path):
    """A log whose only valid marker belongs to another box must be skipped
    entirely — falling through to its headings would sneak the foreign cutoff
    back in through the pre-marker path."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-08-05.md").write_text(
        "# Fleet log\n"
        "## 04:55Z — whoart's entry\n\nbody\n"
        "<!-- relay-shards through=2026-08-05T04:55:27.029878Z machine=whoart -->\n",
        encoding="utf-8",
    )
    assert shardlog.last_relayed(docs, "blade1tb") is None


def test_a_box_that_never_relayed_has_no_cutoff(tmp_path):
    """First relay from a box sees its whole vault as unpublished — the truth.
    Curation is --since/--exclude, not a silently borrowed cutoff."""
    docs = tmp_path / "docs"
    docs.mkdir()
    assert shardlog.last_relayed(docs, "phoebus") is None


def test_already_relayed_shards_are_not_repeated(tmp_path):
    vault = make_vault(tmp_path, [
        {"ts": "2026-07-31T23:45:10.527740Z", "title": "old"},
        {"ts": "2026-08-01T00:01:19.612261Z", "title": "new"},
    ])
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "<!-- relay-shards through=2026-07-31T23:45:10.527740Z -->\n", encoding="utf-8"
    )
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    body = (docs / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "new" in body
    assert "## 23:45Z — old" not in body


def test_a_shard_named_in_an_earlier_log_is_never_republished(tmp_path):
    """The cutoff recovered from a pre-marker log only has minute precision, so
    a shard captured at :45:10 sits after a :45:00 cutoff. Title is the backstop."""
    vault = make_vault(tmp_path, [
        {"ts": "2026-07-31T23:45:10.527740Z", "title": "already told them"},
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "genuinely new"},
    ])
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "## 23:45Z — already told them\n\nbody\n", encoding="utf-8"
    )
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    body = (docs / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "genuinely new" in body
    assert "already told them" not in body


def test_a_withheld_shard_counts_as_published(tmp_path):
    """Naming it was the disclosure. Copying the body in a later relay would
    quietly reverse that decision."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FLEET-LOG-2026-07-31.md").write_text(
        "## Not included here\n\n- `00:06Z` The call-and-response (brand)\n",
        encoding="utf-8",
    )
    assert "The call-and-response" in shardlog.relayed_titles(docs)


def test_nothing_new_is_success_not_failure(tmp_path, capsys):
    """A quiet relay is a healthy relay. Exiting non-zero here would make the
    command unusable from a hook."""
    vault = make_vault(tmp_path, [{"ts": "2026-08-01T00:01:00.000000Z", "title": "x"}])
    assert run(tmp_path, vault, since="2026-08-02T00:00:00.000000Z") == shardlog.EXIT_OK
    assert "nothing new" in capsys.readouterr().out


# --- the scan: must BLOCK ---------------------------------------------------

@pytest.mark.parametrize("value", [
    "export KEY=sk-abcdefghijklmnopqrstuvwxyz012345",
    "ghp_abcdefghijklmnopqrstuvwxyz0123456789",
    "AKIAIOSFODNN7EXAMPLE",
    "hf_abcdefghijklmnopqrstuvwxyzABCD",
    "client_secret: aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW",
    "-----BEGIN RSA PRIVATE KEY-----",
])
def test_credential_shaped_values_block_the_write(tmp_path, value):
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "leaky", "content": value}
    ])
    assert run(tmp_path, vault) == shardlog.EXIT_FAILURE
    assert not (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").exists()


def test_a_variable_name_is_not_a_secret(tmp_path):
    """The real vault is full of `wrangler secret put TWITCH_CLIENT_SECRET`. A
    scan that tripped on the word would be turned off within a day."""
    vault = make_vault(tmp_path, [{
        "ts": "2026-08-01T00:01:00.000000Z", "title": "deploy",
        "content": "Run `wrangler secret put TWITCH_CLIENT_SECRET` then deploy.",
    }])
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    assert (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").exists()


def test_insurance_shards_do_not_travel(tmp_path):
    """Observed 2026-08-08: blade1tb held 8 shards of an active insurance
    claim — strategy, photo evidence, receipts — tagged 'insurance', which was
    not in WITHHELD_TAGS, so relay would have copied the bodies verbatim into
    a tracked file. An active claim has an adversarial counterparty; its
    strategy is exactly the document that must not exist in a repo."""
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "claim strategy",
         "content": "rebalance away from the mold sublimit", "tags": ["insurance"]},
        {"ts": "2026-08-01T00:02:00.000000Z", "title": "the bug", "content": "engineering"},
    ])
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    body = (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "mold sublimit" not in body


def test_excluded_shard_is_dropped_so_one_bad_shard_cannot_block_the_relay(tmp_path):
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "leaky",
         "content": "ghp_abcdefghijklmnopqrstuvwxyz0123456789"},
        {"ts": "2026-08-01T00:02:00.000000Z", "title": "clean", "content": "fine"},
    ])
    assert run(tmp_path, vault, exclude=["leaky"]) == shardlog.EXIT_OK
    body = (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "clean" in body and "ghp_" not in body


# --- what does not travel ---------------------------------------------------

def test_tagged_shards_are_named_but_not_copied(tmp_path):
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "the chant",
         "content": "SECRET SAUCE POSITIONING", "tags": ["brand", "culture"]},
        {"ts": "2026-08-01T00:02:00.000000Z", "title": "the bug", "content": "engineering"},
    ])
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    body = (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "SECRET SAUCE POSITIONING" not in body   # body withheld
    assert "the chant" in body                       # existence disclosed
    assert "Not included here" in body


def test_include_tagged_is_an_explicit_override(tmp_path):
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "the chant",
         "content": "SECRET SAUCE POSITIONING", "tags": ["brand"]},
    ])
    assert run(tmp_path, vault, include_tagged=True) == shardlog.EXIT_OK
    body = (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert "SECRET SAUCE POSITIONING" in body


# --- verbatim, but not structurally contagious ------------------------------

def test_shard_headings_cannot_impersonate_log_entries():
    text = shardlog.demote_headings("## LESSON\nbody\n### detail")
    assert text.startswith("### LESSON")
    assert "#### detail" in text


def test_headings_inside_code_fences_are_left_alone():
    """`# comment` in a shell block is code, not structure."""
    text = shardlog.demote_headings("```bash\n# install\nnpm i\n```")
    assert "\n# install" in text


def test_a_shard_body_is_copied_byte_for_byte(tmp_path):
    """The point of generating this file is that it is the record. Any rewording
    here would make it a summary of a summary."""
    content = "Line one.\n\n    indented literal\n\nLine two — em dash, `code`."
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "verbatim", "content": content}
    ])
    assert run(tmp_path, vault) == shardlog.EXIT_OK
    body = (tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").read_text(encoding="utf-8")
    assert content in body


def test_dry_run_writes_nothing(tmp_path):
    vault = make_vault(tmp_path, [{"ts": "2026-08-01T00:01:00.000000Z", "title": "x"}])
    assert run(tmp_path, vault, dry=True) == shardlog.EXIT_OK
    assert not Path(tmp_path / "docs" / "FLEET-LOG-2026-08-01.md").exists()


def test_a_box_with_no_home_can_still_run_the_cli(monkeypatch):
    """An import-time expanduser() once broke `relay --help` on any box without
    HOME. The default must resolve when it is used, not when the module loads."""
    monkeypatch.delenv("NOUGEN_VAULT", raising=False)
    for var in ("HOME", "USERPROFILE", "HOMEPATH", "HOMEDRIVE"):
        monkeypatch.delenv(var, raising=False)
    assert shardlog.vault_paths() == []


def test_missing_vault_fails_loudly(tmp_path):
    """Silence here would look identical to 'nothing new' — and the fleet would
    quietly stop receiving knowledge."""
    assert run(tmp_path, tmp_path / "nope") == shardlog.EXIT_FAILURE


def test_shards_are_read_from_every_vault_file_oldest_first(tmp_path):
    """A day's knowledge lands across several numbered files; reading only the
    newest would drop entries without saying so."""
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:05:00.000000Z", "title": "second"},
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "first"},
    ])
    rows = shardlog.read_shards(shardlog.vault_paths(str(vault)), None)
    assert [r["title"] for r in rows] == ["first", "second"]


def test_duplicate_shards_across_files_are_relayed_once(tmp_path):
    vault = make_vault(tmp_path, [
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "dupe", "hash": "same"},
        {"ts": "2026-08-01T00:01:00.000000Z", "title": "dupe", "hash": "same"},
    ])
    rows = shardlog.read_shards(shardlog.vault_paths(str(vault)), None)
    assert len(rows) == 1
