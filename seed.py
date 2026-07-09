"""
seed.py — CineLog local testing helper

Creates a user and a sample film in the local database (cinelog.db) and
prints their IDs, so you can manually exercise the API — e.g.:

    python seed.py
    # user_id = <uuid>
    # film_id = 1

    curl -X POST http://127.0.0.1:5000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" -d '{"film_id": 1}'
"""

from app import create_app, db
from models import User, Film

app = create_app()

with app.app_context():
    # Reuse the user if it already exists (username/email are unique).
    user = User.query.filter_by(email="kyleyli2005@gmail.com").first()
    if user is None:
        user = User(username="KyleLi", email="kyleyli2005@gmail.com")
        db.session.add(user)

    film = Film(title="Paddington 2", year=2017, genre="Comedy")
    db.session.add(film)

    db.session.commit()

    print(f"user_id = {user.id}")
    print(f"film_id = {film.id}")
