# PlayOX Tic Tac Toe/Noughts and Crosses

A FastAPI-based REST API for playing Tic-Tac-Toe (Noughts and Crosses) against a computer opponent with an included web interface.

## Running

With Docker:

```
docker build -t playox . && docker run --rm -p 8000:8000 playox
```

Locally with [uv](https://docs.astral.sh/uv/):

```
uv run uvicorn playox.app:app --port 8000
```

Visit:

- http://localhost:8000 to play the game in-browser.
- http://localhost:8000/api/docs to view the interactive docs and test the API in browser

## Testing

Unit tests, linting, and type checking can be run using [uv](https://docs.astral.sh/uv/):

```
uv run pytest
uv run ruff check
uv run ty check
```

## Commentary

I spent four hours over a weekend working on this project. In the first two hours I started shaping my answer then gave my brain time to churn overnight. The next day I spent another couple hours iterating, then cleaning it up, adding more edge test cases, creating its Dockerfile, and linting and type-checking.

I am not including the time writing this README.

### Assumptions

I made the following assumptions based on the challenge description and for simplicity in a proof-of-concept:

- The user always plays as X and goes first.
- The computer opponent uses random move selection (suggested in the assignment).
- It's okay if "list all games previously played" in the user story is limited the lifetime of the process in memory, for the purpose of this test, so there is no persistence.

### Choices and trade-offs

I've made a few of implementation choices and trade-offs:

- I've tried to do some separation of concerns: game logic is confined to `playox/game.py`, the REST API is implemented in `playox/app.py`.

  This results in some duplication (`Move`/`RequestMove` and `Game`/`ResponseGame`) that I'm not thrilled with, but they fit this conceptual framework. They're the difference between the representation of each as submitted by/presented to the API user, and what I believe is needed for the game logic. So I'm accepting some repetition as a result.

- Within the game logic I've chosen to represent the gameboard as a flat list of player strings indexed to their position on the board.

  This simplifies the logic (in my mind at least—winning positions are just three-tuples of indices, available positions are the idices of empty strings, etc) at the cost of slightly more complexity in converting x,y coordinates for input/output.

  One thing I'm not very happy with is the way I'm hiding the internal `positions` in my `ResponseGame`, a subclass of `Game`, but this is to avoid a lot of other model field duplication.

- I made `random_move()` its own isolated function with the idea that there could be multiple callables with different computer move behavior, and the user could chose the type of opponent. Clearly that's not functionality I've implemented though.

- On API design, I've made adding a move its own resource as a `POST` to `games/{game_id}/moves`.

  An argument could be made for moves to be a `PUT` to the `games/{game_id}` endpoint (and perhaps the `moves` endpoint generally doesn't need to exist separate from `games/{game_id}`).

  I find separating out `moves` to be a little cleaner, and if they are their own resource, `POST` is semantically correct.

### What's Missing

This is a proof-of-concept project where I prioritized simple, correct, well-structured code that is readable and meets my understanding of the described requirements, over extra features and completeness. As a result, there are a few glaring omissions that would be high priority if something like this were to be built upon (in roughly the order I'd see them as priorities):

- **There is no support for authentication** or multiple users (or throttling or similar best practices), this should **NEVER** be exposed to the open web.
- **There is no persistence**, the games are all stored in memory.
- **There's no locking/atomicity/etc during the move**, it's possible that multiple user requests to add a move at the same time could make the game state unrecoverable.
- **No customization of player**, the user always plays X and goes first.
- **There's no `DELETE` support** to remove games, they just accumulate as long as the process runs.
- The datetimes on games and moves are **not timezone-aware**.
- More interesting opponent logic, as described above.

### On Tools and LLMs

I am a casual user of FastAPI and Pydantic but they seemed the correct tools for this project. It's possible I could have used one or both in a more idiomatic way than I have here, and would typically rely on code review/pairing to check that.

With respect to LLMs:

- I used Claude (free) to generate the index.html file in its entirety (I can claim no authorship of that file) to add an in-browser UI in front of the API to play the game. For my prompt, I gave it the API specification and asked it to create an htmx-based single-page frontend.
- I used Claude to suggest alternative data models to the flat list I created, as a way to check some of my assumptions about the game logic (especially in lieu of code review), but I didn't find any of its suggestions particularly better or more readable to my eye.
- I used Claude to suggest move coordinates to use in my test cases for particular scenarios (like a winning sequence that finishes the game with empty spaces to test that subsequent attempts at moves return a 400 in `tests/test_app.py::test_post_move_game_finished`).

But everything else (for better and worse), including the game logic and API implementation, are mine.

I have used LLMs for boilerplate generation (i.e. `pyproject.toml`) in the past, however I did not do that here. I used `uv` for initialization and dependency management and the pytest and ruff configuration I pulled from other projects of mine.

### Feedback

This was a fun challenge that I took to reflect both rapid-turnaround data modeling skills and API design skills. I have no feedback other than to please continue doing hiring this way and resist the (understandable in the age of LLMs) trend back toward real-time rapid-fire leetcode-style interviews.

This kind of assignment mirrors the way I approach real-world software engineering problems. I was able to read through this, start thinking about it and forming a mental model before I wrote any code. And when I did, I was able to step away and let my brain continue working and come back the next day and complete it.

Therefore I believe my response is an accurate reflection of my abilities and flaws (it's not flashy, and I don't know that there's any gee-whiz), and what I prize in my code (readability is very important to me). Whether I've succeeded at these things is up to you, of course, and that is how I would prefer to be tested.
