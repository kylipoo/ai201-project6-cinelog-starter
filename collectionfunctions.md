# Collection Functions — Plain-English Guide

This explains what [`services/collection_service.py`](services/collection_service.py) does in simple terms.

## What this file is for

It handles a user's **collection** — the list of films they have **already watched and logged**. It contains the "business logic": the rules for adding, removing, and listing watched films, and saving those changes to the database.

## The three main functions

### 1. `add_to_collection(user_id, film_id, rating=None)`
Marks a film as watched for a user.

- Checks that the film actually exists.
- Checks that the user hasn't already added it.
- If both checks pass, it saves a new entry (with an optional 1–5 rating).
- Gives back the new entry that was created.

### 2. `remove_from_collection(user_id, film_id)`
Removes a film from a user's collection.

- Finds the user's entry for that film.
- If it exists, deletes it and returns `True`.
- If it isn't there, it stops and reports an error.

### 3. `get_collection(user_id)`
Gets the user's whole collection to show them.

- Fetches all films the user has logged.
- Sorts them **newest first** (by date added).
- Returns a list of films, with each film's `date_added` and `rating` included.

## The error types (what can go wrong)

The file defines three custom errors so the rest of the app knows exactly what happened:

| Error | When it happens |
|-------|-----------------|
| `FilmNotFoundError` | The film ID doesn't exist in the database. |
| `AlreadyInCollectionError` | The user tries to add a film they've already added. |
| `NotInCollectionError` | The user tries to remove a film that isn't in their collection. |

## How it fits with the rest of the app

- It uses the `Film` and `CollectionEntry` models from [`models.py`](models.py).
- It talks to the database through the shared `db` from [`app.py`](app.py).
- It's called by the collection route ([`routes/collection.py`](routes/collection.py)), which handles the web requests and returns JSON to the user.

## One thing to note

The docstrings describe `film_id` as a **UUID string**, but on this branch the `Film` model still uses **integer** IDs (see the note in [`models.py`](models.py)). Worth keeping in mind if IDs behave unexpectedly.
