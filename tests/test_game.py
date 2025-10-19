import pytest

from playox.game import Game, GameError, GameOver, Move, random_move


def test_game_initialization():
    """Test that a new game initializes correctly."""
    game = Game()
    assert game.positions == ["", "", "", "", "", "", "", "", ""]
    assert game.winner is None
    assert game.finished is False
    assert game.next_player == "X"


def test_valid_move():
    """Test playing a valid move updates positions correctly."""
    game = Game()
    move = Move(x=0, y=0, player="X")
    game.play(move)
    assert game.positions[0] == "X"
    assert game.next_player == "O"


def test_turn_enforcement():
    """Test that playing out of turn raises an error."""
    game = Game()
    move1 = Move(x=0, y=0, player="O")  # O tries to play first
    with pytest.raises(GameError, match="It is not O's turn"):
        game.play(move1)

    move2 = Move(x=0, y=0, player="X")
    game.play(move2)
    move3 = Move(x=1, y=0, player="X")  # X tries to play twice
    with pytest.raises(GameError, match="It is not X's turn"):
        game.play(move3)  # noqa: B018


def test_move_on_occupied_position():
    """Test that playing on an already occupied cell raises an error."""
    game = Game()
    move1 = Move(x=0, y=0, player="X")
    move2 = Move(x=0, y=0, player="O")
    game.play(move1)
    with pytest.raises(GameError, match="has already been played"):
        game.play(move2)  # noqa: B018


def test_winner_row():
    """Test detecting a winner in a row."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=0, y=1, player="O"))
    game.play(Move(x=1, y=0, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=2, y=0, player="X"))
    assert game.winner == "X"
    assert game.finished is True


def test_winner_column():
    """Test detecting a winner in a column."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=1, y=0, player="O"))
    game.play(Move(x=0, y=1, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=0, y=2, player="X"))
    assert game.winner == "X"
    assert game.finished is True
    with pytest.raises(GameOver):
        game.next_player  # noqa: B018


def test_winner_diagonal():
    """Test detecting a winner in a diagonal."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=0, y=1, player="O"))
    game.play(Move(x=1, y=1, player="X"))
    game.play(Move(x=0, y=2, player="O"))
    game.play(Move(x=2, y=2, player="X"))
    assert game.winner == "X"
    assert game.finished is True
    with pytest.raises(GameOver):
        game.next_player  # noqa: B018


def test_draw_game():
    """Test a full board with no winner is a draw."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=0, y=1, player="O"))
    game.play(Move(x=0, y=2, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=1, y=0, player="X"))
    game.play(Move(x=1, y=2, player="O"))
    game.play(Move(x=2, y=2, player="X"))
    game.play(Move(x=2, y=0, player="O"))
    game.play(Move(x=2, y=1, player="X"))
    assert game.winner is None
    assert game.finished is True
    with pytest.raises(GameOver):
        game.next_player  # noqa: B018


def test_game_completed_error():
    """Test that playing after game completion raises an error."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=0, y=1, player="O"))
    game.play(Move(x=1, y=0, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=2, y=0, player="X"))
    move_after_win = Move(x=2, y=1, player="O")
    with pytest.raises(GameError, match="game is finished"):
        game.play(move_after_win)


def test_game_play_with_bad_player():
    """Test that playing after game completion raises an error."""
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=0, y=1, player="O"))
    with pytest.raises(GameError, match="not in game"):
        game.play(Move(x=1, y=0, player="Y"))


def test_random_move():
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=0, y=1, player="X"))

    move = random_move(game, "O")
    assert isinstance(move, Move)
    assert move.player == "O"
    assert 0 <= move.x <= 2
    assert 0 <= move.y <= 2
    assert move.get_position() in game.empty_positions


def test_random_move_finished_game():
    # Test raises GameOver on finished game
    game = Game()
    game.play(Move(x=0, y=0, player="X"))
    game.play(Move(x=1, y=0, player="O"))
    game.play(Move(x=0, y=1, player="X"))
    game.play(Move(x=1, y=1, player="O"))
    game.play(Move(x=0, y=2, player="X"))

    with pytest.raises(GameOver):
        random_move(game, "O")
