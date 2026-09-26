"""A leg's identity must survive being renamed, and must never be guessed.

Before ids were embedded, identity lived only in the filename and `ack --id`
globbed for a substring. Two consequences, both silent: renaming a record
destroyed its identity, and a short or shared id could match several legs —
whereupon the tool picked the newest and edited a record the caller never
named. Acking the wrong leg looks exactly like acking the right one.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nougen_relay import core  # noqa: E402


class RecordId(unittest.TestCase):
    def test_embedded_id_is_preferred(self):
        self.assertEqual(core.record_id({"id": "embedded"}, Path("other.json")), "embedded")

    def test_falls_back_to_filename_for_legacy_records(self):
        # Records written before this field existed must keep resolving.
        self.assertEqual(core.record_id({}, Path("20260731T120000Z__box__lane.json")),
                         "20260731T120000Z__box__lane")

    def test_falls_back_to_underscore_file_key(self):
        self.assertEqual(core.record_id({"_file": "a__b__c.json"}), "a__b__c")

    def test_returns_none_when_nothing_identifies_it(self):
        self.assertIsNone(core.record_id({}))

    def test_blank_embedded_id_does_not_shadow_the_filename(self):
        self.assertEqual(core.record_id({"id": "   "}, Path("real-name.json")), "real-name")


class Resolution(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="relay-id-"))
        self.dir = self.tmp / ".handoffs"
        self.dir.mkdir(parents=True)
        self._prev = core.os.environ.get("NOUGEN_GIT_HANDOFF_DIR")
        core.os.environ["NOUGEN_GIT_HANDOFF_DIR"] = str(self.dir)

    def tearDown(self):
        if self._prev is None:
            core.os.environ.pop("NOUGEN_GIT_HANDOFF_DIR", None)
        else:
            core.os.environ["NOUGEN_GIT_HANDOFF_DIR"] = self._prev

    def _write(self, name: str, rec: dict):
        (self.dir / f"{name}.json").write_text(json.dumps(rec), encoding="utf-8")

    def test_exact_filename_resolves(self):
        self._write("20260731T120000Z__boxa__lane", {"goal": "one"})
        got = core._record_path(self.tmp, "20260731T120000Z__boxa__lane")
        self.assertIsNotNone(got)
        self.assertEqual(json.loads(got.read_text(encoding="utf-8"))["goal"], "one")

    def test_embedded_id_resolves_even_after_a_rename(self):
        # The file is renamed; the id inside it is not. Identity must follow
        # the record, which is the entire point of embedding it.
        self._write("something-else-entirely", {"id": "20260731T130000Z__boxa__lane", "goal": "renamed"})
        got = core._record_path(self.tmp, "20260731T130000Z__boxa__lane")
        self.assertIsNotNone(got, "a renamed record must still resolve by its embedded id")
        self.assertEqual(json.loads(got.read_text(encoding="utf-8"))["goal"], "renamed")

    def test_ambiguous_substring_refuses_rather_than_guessing(self):
        self._write("20260731T120000Z__boxa__lane", {"goal": "first"})
        self._write("20260731T990000Z__boxa__lane", {"goal": "second"})
        self.assertIsNone(core._record_path(self.tmp, "boxa"),
                          "a substring matching two legs must refuse, not pick the newest")

    def test_unique_substring_still_resolves(self):
        self._write("20260731T120000Z__boxa__lane", {"goal": "only"})
        got = core._record_path(self.tmp, "boxa")
        self.assertIsNotNone(got)
        self.assertEqual(json.loads(got.read_text(encoding="utf-8"))["goal"], "only")

    def test_exact_match_wins_over_a_substring_collision(self):
        # "lane" is both a full filename and a substring of the other.
        self._write("lane", {"goal": "exact"})
        self._write("20260731T120000Z__boxa__lane", {"goal": "substring"})
        got = core._record_path(self.tmp, "lane")
        self.assertEqual(json.loads(got.read_text(encoding="utf-8"))["goal"], "exact")

    def test_missing_id_returns_none(self):
        self.assertIsNone(core._record_path(self.tmp, "nothing-here"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
