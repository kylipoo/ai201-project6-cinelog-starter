# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used an AI coding assistant (Claude Code) during this project. Specific uses:

- **Git rebase onto `main` (Comment 6).** When `main`'s integer→UUID `Film.id`
  migration conflicted with my watchlist code, I used the assistant to walk
  through the rebase, resolve the `.gitignore` and `models.py` conflicts, and
  find the remaining integer-ID references (the `999999` test value and a
  docstring) that git couldn't flag on its own.
- **Test scaffolding (Comment 3).** I had it draft the
  `test_add_to_watchlist_nonexistent_film_raises` test modeled on the existing
  collection test, then reviewed it and put it in its own `test:` commit.
- **Drafting/refining the reasoning write-ups (Comments 4 & 5).** I described
  the positions I wanted to take (private-by-default, newest-first sort) and
  used the assistant to help draft and tighten the wording; the design
  decisions and final wording are my own.
- **History cleanup.** I used it to help reword and squash commits (e.g.
  folding the Comment 4 reasoning into the visibility-default commit).

All design decisions, final wording, and verification were reviewed and
approved by me.

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
`film_id` that isn't in the database (a well-formed but nonexistent UUID) and asserts, via
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
signal is more valuable day-to-day. Defaulting the watchlist to newest-first
would make it consistent with the collection.

## Comment 6 — Rebase

I ran `git fetch origin` and `git rebase origin/main` to replay my 10
watchlist commits on top of main's history (which includes the
`refactor: migrate film IDs from integer to UUID` commit).

**What conflicted:**
1. **`.gitignore`** — an add/add conflict: both main and my first commit
   independently added a `.gitignore`. The only real difference was that
   main's version listed `.pytest_cache/`.
2. **`models.py`** — the substantive one. My new `WatchlistEntry` class landed
   in a file main had rewritten so that `Film.id` is now a UUID
   (`db.String(36)`) instead of an integer. My `WatchlistEntry.film_id` was
   still `db.Integer`, so it would have been an integer foreign key pointing at
   a UUID primary key — broken.

**How I resolved it:**
- `.gitignore`: took the **union** of both sides (kept `.pytest_cache/`,
  `.venv/`, and `venv/`) — no information lost.
- `models.py`: kept the `WatchlistEntry` class but changed
  `film_id = db.Column(db.Integer, ...)` → `db.Column(db.String(36), ...)` so
  the foreign key matches main's UUID `Film.id`.
- Git can't catch value-level assumptions, so I also swept the watchlist code
  for lingering integer IDs: the nonexistent-film test now uses a UUID string
  (`"00000000-0000-0000-0000-000000000000"`) instead of `999999`, and the
  `add_to_watchlist()` docstring documents `film_id` as a UUID `str` rather
  than `int`.

**How I verified no conflict remains:**
- `pytest tests/` → all 7 pass.
- `grep` for `db.Integer` on `film_id` / `999999` / `film_id (int)` across
  `models.py`, `services/`, and `tests/` returns nothing.
- `git log --merges origin/main..HEAD` is **empty** — the history is linear,
  with no merge commits (a rebase, not a merge).
- The branch's merge-base with `origin/main` is main's current tip, confirming
  the branch is rebased directly on top of main.

## PR Description

### What this adds

This PR adds a **watchlist** to CineLog — a per-user list of films a user wants
to watch later. It's separate from the existing collection (films already
watched); the watchlist is the "save for later" queue. In plain terms: you POST
a film under a user, and you can GET that user's saved films back.

It introduces:

- **`WatchlistEntry` model** (`models.py`) — links a user to a film, with a
  `date_added` timestamp and a `public` visibility flag. `film_id` is a UUID
  string (matching main's UUID `Film.id`).
- **Two endpoints** (blueprint mounted at `/watchlist`):
  - `GET /watchlist/<user_id>` — returns the user's watchlist as a JSON array.
  - `POST /watchlist/<user_id>/add` with body `{"film_id": "<uuid>"}` — adds a
    film and returns the created entry with `201`.
- **Service logic** (`services/watchlist_service.py`) — validates the film
  exists (raises `FilmNotFoundError`) and blocks duplicates (raises
  `AlreadyInWatchlistError`), mirroring the collection service's patterns.

### Design decisions

- **Default visibility → private (`public=False`).** A watchlist reflects a
  user's personal taste, so entries are private by default and sharing is an
  explicit opt-in. (See Comment 4.)
- **Sort order → currently alphabetical; decided to move to newest-first.**
  `get_watchlist()` currently orders by `Film.title` (alphabetical). We've
  decided newest-first (`date_added` descending) is the better default because
  a watchlist is an active queue where the most recent add is usually what the
  user cares about — but that change is **not implemented in this PR**. (See
  Comment 5.)

### Manual testing steps

There are no endpoints to create users or films, so seed one of each first.

1. **Install & run:**
   ```
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python app.py            # serves on http://127.0.0.1:5000
   ```
2. **Seed a user and a film**, noting the printed UUIDs (in a second shell):
   ```
   python -c "
   from app import create_app, db
   from models import User, Film
   with create_app().app_context():
       u = User(username='tester', email='t@example.com')
       f = Film(title='Paddington 2', year=2017, genre='Comedy')
       db.session.add_all([u, f]); db.session.commit()
       print('USER', u.id); print('FILM', f.id)
   "
   ```
3. **Add the film** (substitute the printed IDs):
   ```
   curl -X POST http://127.0.0.1:5000/watchlist/<USER_ID>/add \
        -H 'Content-Type: application/json' -d '{"film_id": "<FILM_ID>"}'
   ```
   → Expect `201` and a JSON entry with `"public": false`.
4. **View the watchlist:**
   ```
   curl http://127.0.0.1:5000/watchlist/<USER_ID>
   ```
   → Expect a JSON array containing the film.
5. **Confirm the guards:**
   - POST the same film again → the add is rejected (`AlreadyInWatchlistError`).
   - POST `{"film_id": "00000000-0000-0000-0000-000000000000"}` → rejected
     (`FilmNotFoundError`).
6. **Run the automated tests:** `pytest tests/` → **7 passing**.

### Known limitation / follow-up

The `add_film` route doesn't yet translate `FilmNotFoundError` /
`AlreadyInWatchlistError` into clean HTTP 4xx responses — they currently surface
as a `500`. The service raises the right exceptions (and the unit tests assert
them), so mapping them to `404`/`409` in the route is a small follow-up.
