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
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order

**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase

**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description

<!-- Written at the end — feature overview, design decisions, manual testing steps -->
