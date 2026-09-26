"""Machine and agent identity — the "who did this, on which box" half of every
record. A wrong answer here is worse than no answer: it is a confident lie in a
registry other machines act on."""

import pytest

from nougen_relay import core


@pytest.fixture(autouse=True)
def no_ambient_identity(monkeypatch):
    """Identity now resolves env -> git config -> probe, so these tests must
    control BOTH sources. Without this they pass or fail depending on whether
    the developer ran `relay init` in their own clone — a test whose result
    depends on the machine it runs on is worse than no test."""
    monkeypatch.setattr(core, "_AGENT_CACHE", None)
    monkeypatch.setattr(core, "_MACHINE_CACHE", None)
    real_git = core._git

    def _git_without_identity(*args, **kw):
        if args[:3] in (("config", "--get", "nougen.agent"),
                        ("config", "--get", "nougen.machine")):
            return None
        return real_git(*args, **kw)

    monkeypatch.setattr(core, "_git", _git_without_identity)


def test_env_machine_wins_over_hostname(monkeypatch):
    monkeypatch.setenv("NOUGEN_MACHINE", "phoebus")
    assert core.resolve_machine() == "phoebus"


def test_hostname_is_the_fallback(monkeypatch):
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core.socket, "gethostname", lambda: "WhoArt")
    assert core.resolve_machine() == "whoart"


def test_hostname_failure_does_not_raise(monkeypatch):
    """Identity resolution must never be the thing that takes the CLI down."""
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)

    def boom():
        raise OSError("no hostname")

    monkeypatch.setattr(core.socket, "gethostname", boom)
    assert core.resolve_machine() == "unknown-machine"


def test_blank_env_is_not_an_identity(monkeypatch):
    """An exported-but-empty NOUGEN_MACHINE is a shell accident, not a name."""
    monkeypatch.setenv("NOUGEN_MACHINE", "   ")
    monkeypatch.setattr(core.socket, "gethostname", lambda: "blade1tb")
    assert core.resolve_machine() == "blade1tb"


def test_names_are_slugged_into_filename_safe_tokens(monkeypatch):
    """Record filenames embed these values; a raw hostname with dots or spaces
    would produce paths that differ per platform."""
    monkeypatch.setenv("NOUGEN_MACHINE", "Who-Mac-Mini.local")
    assert core.resolve_machine() == "who-mac-mini-local"


def test_git_config_names_the_machine_when_env_is_unset(monkeypatch):
    """Observed 2026-08-05 on phoebus: `relay init --machine phoebus` stored
    the name, then an env-less shell acked a leg as the raw hostname anyway,
    because nothing ever read nougen.machine back."""
    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.setattr(core, "_MACHINE_CACHE", None)
    monkeypatch.setattr(core, "_git",
                        lambda *a, **k: "stored-box" if a[:3] == ("config", "--get", "nougen.machine") else None)
    assert core.resolve_machine() == "stored-box"
    assert core.machine_source() == "git config nougen.machine"


def test_env_still_beats_stored_machine_config(monkeypatch):
    """A one-off override must not require unsetting anything."""
    monkeypatch.setenv("NOUGEN_MACHINE", "one-off-box")
    monkeypatch.setattr(core, "_MACHINE_CACHE", None)
    monkeypatch.setattr(core, "_git",
                        lambda *a, **k: "stored-box" if a[:3] == ("config", "--get", "nougen.machine") else None)
    assert core.resolve_machine() == "one-off-box"
    assert core.machine_source() == "NOUGEN_MACHINE"


def test_missing_agent_is_named_not_guessed(monkeypatch):
    """No env, no git config: say unknown rather than invent a lane."""
    monkeypatch.delenv("NOUGEN_AGENT", raising=False)
    assert core.resolve_agent() == core.UNKNOWN_AGENT


def test_git_config_names_the_lane_when_env_is_unset(monkeypatch):
    """The friction fix: set once per clone, no exports, survives new shells."""
    monkeypatch.delenv("NOUGEN_AGENT", raising=False)
    monkeypatch.setattr(core, "_AGENT_CACHE", None)
    monkeypatch.setattr(core, "_git",
                        lambda *a, **k: "stored-lane" if a[:3] == ("config", "--get", "nougen.agent") else None)
    assert core.resolve_agent() == "stored-lane"
    assert core.agent_source() == "git config nougen.agent"


def test_env_still_beats_stored_config(monkeypatch):
    """A one-off override must not require unsetting anything."""
    monkeypatch.setenv("NOUGEN_AGENT", "one-off")
    monkeypatch.setattr(core, "_AGENT_CACHE", None)
    monkeypatch.setattr(core, "_git",
                        lambda *a, **k: "stored-lane" if a[:3] == ("config", "--get", "nougen.agent") else None)
    assert core.resolve_agent() == "one-off"
    assert core.agent_source() == "NOUGEN_AGENT"


def test_identity_reports_where_each_answer_came_from(monkeypatch):
    """A reader must be able to tell an env-var name from an OS-probed one."""
    monkeypatch.setenv("NOUGEN_MACHINE", "whoart")
    monkeypatch.setenv("NOUGEN_AGENT", "claude-cli")
    ident = core.identity()
    assert ident["machine_source"] == "NOUGEN_MACHINE"
    assert ident["agent_source"] == "NOUGEN_AGENT"

    monkeypatch.delenv("NOUGEN_MACHINE", raising=False)
    monkeypatch.delenv("NOUGEN_AGENT", raising=False)
    ident = core.identity()
    assert ident["machine_source"] == "socket.gethostname()"
    assert ident["agent_source"] == "fallback"


def test_anonymous_write_warns_loudly(monkeypatch, capsys):
    """Observed 2026-07-31: an ack landed stamped 'unknown-agent' with no sign
    anything was wrong, because NOUGEN_AGENT never reached the process."""
    monkeypatch.delenv("NOUGEN_AGENT", raising=False)
    core.warn_if_anonymous()
    assert core.UNKNOWN_AGENT in capsys.readouterr().out

    monkeypatch.setenv("NOUGEN_AGENT", "claude-cli")
    core.warn_if_anonymous()
    assert capsys.readouterr().out == ""
