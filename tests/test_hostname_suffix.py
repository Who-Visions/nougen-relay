"""A probed hostname has to produce a name its operator recognises.

mDNS appends `.local`, so the Mac mini probed as `KushBoyGroups-Mac-mini.local`
and every record it wrote said `kushboygroups-mac-mini-local` — correct by the
tool's own rules, and recognisable to nobody. Observed 2026-07-31 in this repo's
own history.
"""

import pytest

from nougen_relay import core


@pytest.fixture(autouse=True)
def no_stored_machine(monkeypatch):
    """These tests probe the hostname path, which is now the LAST resort:
    env -> git config nougen.machine -> gethostname(). Run from a clone whose
    operator has done `relay init --machine`, the stored name would shadow
    every mocked hostname below."""
    monkeypatch.setattr(core, "_MACHINE_CACHE", None)
    real_git = core._git

    def _git_without_machine(*args, **kw):
        if args[:3] == ("config", "--get", "nougen.machine"):
            return None
        return real_git(*args, **kw)

    monkeypatch.setattr(core, "_git", _git_without_machine)


@pytest.mark.parametrize("hostname,expected", [
    ("KushBoyGroups-Mac-mini.local", "kushboygroups-mac-mini"),  # the real one
    ("blade1tb.lan", "blade1tb"),
    ("box.home", "box"),
    ("runner.internal", "runner"),
    ("host.localdomain", "host"),
    ("MacBook.LOCAL", "macbook"),                                # case-insensitive
    ("WhoArt", "whoart"),                                        # nothing to strip
])
def test_network_suffixes_are_not_part_of_the_name(hostname, expected, monkeypatch):
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core.socket, "gethostname", lambda: hostname)
    assert core.resolve_machine() == expected


def test_a_general_fqdn_is_left_alone(monkeypatch):
    """`build.corp.example.com` -> `build` would collide with a `build` in some
    other domain. A wrong-but-unique name beats a pretty ambiguous one."""
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core.socket, "gethostname", lambda: "build.corp.example.com")
    assert core.resolve_machine() == "build-corp-example-com"


def test_only_a_trailing_suffix_counts(monkeypatch):
    """`.local` inside the name is part of the name."""
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core.socket, "gethostname", lambda: "local-build-01")
    assert core.resolve_machine() == "local-build-01"


def test_a_hostname_that_is_only_a_suffix_survives(monkeypatch):
    """Stripping must never leave an empty name."""
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core.socket, "gethostname", lambda: ".local")
    assert core.resolve_machine() == "local"


def test_an_explicit_name_is_passed_through_untouched(monkeypatch):
    """If an operator types a dotted name, that is their word on what this box
    is called — the tool does not second-guess an explicit answer."""
    monkeypatch.setenv("NOUGEN_MACHINE", "phoebus.local")
    assert core.resolve_machine() == "phoebus-local"
