"""Scope overlap decides whether a second machine is allowed to start work.

Too loose and every claim collides, so agents learn to pass --force and the
system is decoration. Too tight and two machines edit the same file believing
they are clear — the duplicate-work failure the claim primitive exists to stop.
"""

from nougen_relay import core


def overlap(a, b):
    return core._scopes_overlap(a, b)


# --- must collide -----------------------------------------------------------

def test_identical_scope_collides():
    assert overlap("src/app/page.tsx", "src/app/page.tsx") == ["src/app/page.tsx"]


def test_directory_claim_covers_a_file_inside_it():
    """Claiming a directory has to protect its contents, in both directions —
    otherwise one machine claims `src/lib` and another edits `src/lib/twitch.ts`
    with no warning."""
    assert overlap("src/lib", "src/lib/twitch.ts")
    assert overlap("src/lib/twitch.ts", "src/lib")


def test_one_shared_path_in_a_multi_path_claim_collides():
    hits = overlap("docs/RELAY.md tools/relay.py", "tools/relay.py")
    assert hits == ["tools/relay.py"]


def test_separators_and_case_do_not_hide_a_collision():
    assert overlap("Src/App/Page.tsx", "src/app/page.tsx")
    assert overlap("src/lib/,tools/relay.py", "tools/relay.py")
    assert overlap("/src/lib/", "src/lib")


# --- must NOT collide -------------------------------------------------------

def test_sibling_files_are_independent():
    assert overlap("src/app/page.tsx", "src/app/layout.tsx") == []


def test_prefix_of_a_name_is_not_a_path_prefix():
    """`src/lib` must not swallow `src/library` — string-prefix matching without
    a separator check would block unrelated work."""
    assert overlap("src/lib", "src/library") == []


def test_unrelated_topics_are_independent():
    assert overlap("oauth flow", "analytics view") == []


def test_empty_scope_collides_with_nothing():
    assert overlap("", "src/lib") == []
    assert overlap("   ", "") == []


# --- topics, not just paths -------------------------------------------------

def test_topic_words_match_exactly_not_fuzzily():
    """A matcher that guessed synonyms would produce confident false overlaps.
    'oauth' claims 'oauth', and nothing else."""
    assert overlap("oauth", "oauth") == ["oauth"]
    assert overlap("oauth", "auth") == []
