import random
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator

# Tic tac toe has specific winning positions, so if any one player occupies
# all positions within any of these possibilities, they are the winner.
# Because these are the only winning combination of positions, they're
# hardcoded, rather than calculated on the fly.
WINNING_POSITIONS = [
    # Rows
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    # Columns
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    # Diagonals
    (0, 4, 8),
    (2, 4, 6),
]


class GameError(ValueError):
    """To be raised for errors during a game"""

    pass


class GameOver(GameError):
    """To be raised when trying to perform some action after a game is over"""

    pass


class Move(BaseModel):
    """The x,y coordinates and player of a move on the game board"""

    x: int
    y: int
    player: str
    # Not timezone aware
    timestamp: datetime = Field(default_factory=datetime.now)

    def get_position(self) -> int:
        return self.y * 3 + self.x

    @classmethod
    def from_position(cls, position: int, player: str):
        x, y = position % 3, position // 3
        return cls(x=x, y=y, player=player)


class Game(BaseModel):
    """Game logic and state of a game of tic tac toe/noughts and crosses

    This class will track and validate moves, record their position on the game
    board, and determine a winner (if there is one).
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    # Not timezone-aware
    created_at: datetime = Field(default_factory=datetime.now)
    moves: list[Move] = []
    positions: list[str] = [""] * 9  # defaults to 9 empty strings

    @field_validator("positions")
    @classmethod
    def check_length(cls, positions: list[str]) -> list[str]:
        if len(positions) != 9:
            raise GameError(
                f"Cannot play game with {len(positions)} positions, 9 required."
            )
        return positions

    @computed_field(return_type=str)
    @property
    def winner(self) -> str | None:
        """Winning player string if there is a winner"""
        for line in WINNING_POSITIONS:
            if (
                self.positions[line[0]]
                == self.positions[line[1]]
                == self.positions[line[2]]
                != ""
            ):
                return self.positions[line[0]]  # Return 'X' or 'O'
        return None

    @computed_field(return_type=bool)
    @property
    def finished(self) -> bool:
        """The game is finished (no more moves can be made or there's a winner)"""
        return self.winner is not None or "" not in self.positions

    @property
    def next_player(self) -> str:
        """Determine whose turn it is based on board state"""
        if self.winner or self.finished:
            raise GameOver("No player is next, the game is over")

        x_count = self.positions.count("X")
        o_count = self.positions.count("O")

        return "X" if x_count == o_count else "O"

    @property
    def empty_positions(self):
        return [i for i, s in enumerate(self.positions) if s == ""]

    def play(self, move: Move):
        """Place the player at the move.position on the board"""

        # If there are no positions to play, the game is finished, and there's
        # nothing to do here.
        if self.finished:
            raise GameOver("Unable to play move, game is finished")

        # Get current players and ensure that, if there are two players who
        # have played the given player is in that set.
        players = set(self.positions) - {""}
        if len(players) == 2 and move.player not in players:
            raise GameError(
                f"Player {move.player} not in game between {' and '.join(players)}"
            )

        # Make sure it's the player who is trying to move's turn.
        if move.player != self.next_player:
            raise GameError(f"It is not {move.player}'s turn")

        position = move.get_position()

        # Make sure the given position index is empty and can be played.
        if position not in self.empty_positions:
            raise GameError(
                f"{move} has already been played by player {self.positions[position]}."
            )

        # Play the position
        self.moves.append(move)
        self.positions[position] = move.player


def random_move(game: Game, player: str) -> Move:
    if game.finished:
        raise GameOver("Cannot play a finished game")

    # game.finished checks that there are empty positions, so we aren't
    # checking that before trying to choose.
    position = random.choice(game.empty_positions)
    move = Move.from_position(position=position, player=player)
    return move
