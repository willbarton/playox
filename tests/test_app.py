import uuid
from unittest import mock

from fastapi.testclient import TestClient

from playox.app import GAMES, app
from playox.game import Move

client = TestClient(app)


def test_post_game():
    response = client.post("/api/games")
    assert response.status_code == 200

    game_id = response.json()
    assert game_id in GAMES


def test_get_game():
    game_id = client.post("/api/games").json()

    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == game_id


def test_get_game_not_found():
    response = client.get("/api/games/FOOO")
    assert response.status_code == 404


def test_list_games():
    game_id_1 = client.post("/api/games").json()
    game_id_2 = client.post("/api/games").json()

    response = client.get("/api/games")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2

    ids = [game["id"] for game in data]
    assert game_id_1 in ids
    assert game_id_2 in ids


def test_post_move_valid_move():
    game_id = client.post("/api/games").json()

    move_resp = client.post(
        f"/api/games/{game_id}/moves",
        json={
            "x": 0,
            "y": 0,
        },
    )
    assert move_resp.status_code == 200

    data = move_resp.json()

    # Board should have the move by X
    assert data["board"][0][0] == "X" or data["board"][0][0] == "O"

    # Move by the computer player O should be in moves
    assert len(data["moves"]) == 2
    assert data["moves"][1]["player"] == "O"


@mock.patch("playox.app.random_move")
def test_post_move_game_finished(mock_random_move):
    mock_random_move.side_effect = [
        Move(x=0, y=0, player="O"),
        Move(x=1, y=1, player="O"),
        Move(x=2, y=2, player="O"),
    ]

    game_id = client.post("/api/games").json()

    client.post(f"/api/games/{game_id}/moves", json={"x": 1, "y": 0})
    client.post(f"/api/games/{game_id}/moves", json={"x": 2, "y": 0})
    client.post(f"/api/games/{game_id}/moves", json={"x": 2, "y": 1})
    last_move_resp = client.post(f"/api/games/{game_id}/moves", json={"x": 2, "y": 2})

    assert last_move_resp.status_code == 400
    assert last_move_resp.json()["detail"] == "Game already finished"


@mock.patch("playox.app.random_move")
def test_post_move_taken(mock_random_move):
    mock_random_move.side_effect = [
        Move(x=2, y=2, player="O"),
        Move(x=2, y=1, player="O"),
    ]

    game_id = client.post("/api/games").json()

    client.post(f"/api/games/{game_id}/moves", json={"x": 0, "y": 0})
    client.post(f"/api/games/{game_id}/moves", json={"x": 1, "y": 0})
    last_move_resp = client.post(f"/api/games/{game_id}/moves", json={"x": 2, "y": 2})

    assert last_move_resp.status_code == 400
    assert "has already been played" in last_move_resp.json()["detail"]


def test_post_move_invalid_game():
    response = client.post(f"/api/games/{uuid.uuid4()}/moves", json={"x": 0, "y": 0})
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"


@mock.patch("playox.app.random_move")
def test_list_moves_ordered(mock_random_move):
    mock_random_move.side_effect = [
        Move(x=2, y=2, player="O"),
        Move(x=2, y=1, player="O"),
    ]

    game_id = client.post("/api/games").json()

    client.post(f"/api/games/{game_id}/moves", json={"x": 0, "y": 0})
    client.post(f"/api/games/{game_id}/moves", json={"x": 1, "y": 0})

    response = client.get(f"/api/games/{game_id}/moves")
    assert response.status_code == 200

    moves = response.json()
    assert len(moves) == 4

    # Ensure first and third moves are the coordinates provided above
    assert moves[0]["x"] == 0 and moves[0]["y"] == 0 and moves[0]["player"] == "X"
    assert moves[1]["x"] == 2 and moves[1]["y"] == 2 and moves[1]["player"] == "O"
    assert moves[2]["x"] == 1 and moves[2]["y"] == 0 and moves[2]["player"] == "X"


def test_list_moves_game_not_found():
    response = client.get("/api/games/FOOO/moves")
    assert response.status_code == 404
