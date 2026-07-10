# PR Response Doc — CineLog Watchlist Feature

## AI Usage

<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename

**What I did:**
I went to search, looked up any mention of "Save_to_watchlist()" and replaced with "Add_to_watchlist()"

**How I verified:**
Save_to_watchlist() is referenced by the add_film route call in watchlist.py, and is first defined in watchlist_service.py(), so I would just need to go to those two files to change. This particular PR is about maintaining a consistent function name so as long as I don't find any references to Save_to_watchlist(), I have fulfilled this PR comment.

## Comment 2 — Deduplication

**What I did:**
Ported the deduplication pattern from `add_to_collection()`. Added an
`AlreadyInWatchlistError` exception class and, in `add_to_watchlist()`, a
check that queries for an existing `(user_id, film_id)` WatchlistEntry after
the film-exists check and raises if one is found — preventing duplicate rows.

**How I verified:**
Wrote `tests/test_watchlist.py::test_add_to_watchlist_duplicate_raises`, which
adds the same film twice and asserts (a) the second call raises
`AlreadyInWatchlistError` via `pytest.raises`, and (b) only one entry exists
(`count == 1`), so no duplicate is silently created. `pytest tests/` → all pass.

## Comment 3 — Missing test

**What I did:**
Added `tests/test_watchlist.py::test_add_to_watchlist_nonexistent_film_raises`,
modeled after `test_add_to_collection_nonexistent_film_raises` in
`tests/test_collection.py`. The test calls `add_to_watchlist()` with a
`film_id` that isn't in the database (`999999`) and asserts, via
`pytest.raises`, that it raises `FilmNotFoundError` — confirming the service
validates the film exists before creating a `WatchlistEntry`, rather than
failing with a database integrity error. It was landed as its own `test:`
commit rather than bundled into the Fix 2 (deduplication) commit.

**How I verified:**
`pytest tests/test_watchlist.py` → all pass.

## Comment 4 — Default visibility

**My position:**
Watchlist entries should default to **private** (`public=False`). The previous
`default=True` was an unintentional inherited default rather than a deliberate
design decision — the reviewer is right to flag it, and I've corrected it in
[models.py](models.py) so new entries are private unless the user explicitly
opts in to sharing.

**Reasoning:**

"CineLog is a personal film-logging app — the watchlist is one person's private queue of what they mean to watch next, reflecting their taste, mood. However, CineLog should be designed to also accommodate for sensitive interests (guilty pleasures, difficult subject matter). Its users are individuals cataloging their own viewing, not curators publishing public recommendations. As such, I actually believe that the default that serves them is a private queue, with sharing as a deliberate act."

**Tradeoff acknowledged:**
Defaulting to private means watchlists aren't socially discoverable out of the
box and it may be difficult for users of cinelog to be able to connect with each other: A user who _wants_ to share their list has to explicitly set it public (in which case we'll need to rework our UI to give a hint to the user if they want to connect with others how they can share their watchlist).
I think that's the correct tradeoff: privacy-by-default with opt-in sharing is
safer than public-by-default with opt-out, and the discoverability cost can be
revisited if/when a deliberate sharing feature is prioritized.

**Follow-up work (out of scope for this PR):**
Now that a watchlist can be private or public, we'll need a way to toggle that
visibility. Since a watchlist is retrieved per user (`get_watchlist(user_id)`),
visibility is a per-user setting — one flag, not one per film — so it belongs
on the `User` model (e.g. `User.watchlist_public`) rather than on each
`WatchlistEntry`. The toggle would fetch the user by `user_id`, set the flag to
the requested value, and commit. Setting it to the value it's already at is a
harmless no-op, so — unlike the add-to-watchlist path, which guards against
duplicate _rows_ — it doesn't need to raise an error. I've kept the current
per-entry `public` field (defaulted to private) as the interim mechanism and
scoped the migration to a single per-user flag as follow-up work.

## Comment 5 — Sort order

**My position:**
I agree with the reviewer. The watchlist should default to sorting by most
recent date added (newest first), rather than the current alphabetical
`Film.title` order.

**Reasoning:**
A user might accidentally add the wrong film, so surfacing the most recently
added entries at the top lets them spot and fix mistakes quickly and
conveniently. More generally, recency is the more useful default signal for a
"want to watch" list — the thing you just added is usually the thing you care
about right now — whereas alphabetical order buries recent activity.

**Engagement with reviewer's point:**
The maintainer's read — that most users want to see what they added recently —
matches how I'd expect a "want to watch" list to be used: it's an active queue,
not an archive, so the newest entry is usually the reason you opened it. I'd
treat that as a safe assumption, though it's the kind of thing worth confirming
with usage data if we ever have it. The reviewer's suggestion also lines up with
an inconsistency worth noting: the
collection service already sorts newest-first
(`CollectionEntry.date_added.desc()` in `services/collection_service.py`),
while the watchlist currently sorts by title, so the two lists behave
differently for no strong reason. Admittedly, there is a trade off to weigh between either sorting by date added or alphabetical order. Alphabetical order does have one merit — it's
easier to scan for a specific known title in a long list (especially when many of the entries might be sequels, only distinguished by what comes after the name)— but that's better
served by a search/filter feature than by the default sort, and the recency
signal is more valuable day-to-day. Defaulting the watchlist to a newest-first design
would make it consistent with the collection.

## Comment 6 — Rebase

**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description

<!-- Written at the end — feature overview, design decisions, manual testing steps -->
