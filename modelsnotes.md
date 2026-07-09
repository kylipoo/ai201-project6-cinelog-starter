# Summary of models.py

### Overview

models.py defines the SQLAlchemy ORM data layer for CineLog, a film-logging app. Declares the four database tables as classes and their relationships, built on the shared db object created in app.py.

#### Structure:

- Helper function generate_uuid() will return a string uuid used as the default primaru key generator for UUID keyed tables.

- Classes:
  - User
    - Key is a UUID string.
    - Carries information of the user's username, email when they created their account, has many collection entries.
  - Film
    - Key is integer autoincrement
    - Contains film metadata (title, year, director, genre, poster, average_rating)
  - Collection entry
    - Key is UUID string
    - Related to user class.
    - Film user has watched/logged, with an (optional) 1-5 star rating, unique per user_id and film_id
  - Watchlist Entry
    - Key UUID string
    - Film user wants to watch later with a public flag.

What depends on it

- app.py — provides the db instance that models.py imports; db.create_all() builds tables from these model definitions.
- routes/films.py — imports Film.
- services/collection_service.py — imports Film, CollectionEntry.
- services/watchlist_service.py — imports Film, WatchlistEntry.
- tests/test_collection.py — imports User, Film, CollectionEntry.
