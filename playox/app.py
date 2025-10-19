from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, computed_field

from playox.game import Game, GameError, GameOver, Move, random_move

api = FastAPI(title="PlayOX API")


# Store games by id in memory in the running process.
GAMES: dict[str, Game] = {}


# Move model for requests, which just takes X, Y coordinates
class RequestMove(BaseModel):
    x: int = Field(..., ge=0, le=2, description="X coordinate (0-2)")
    y: int = Field(..., ge=0, le=2, description="Y coordinate (0-2)")


# Response class for Game that hides the positions list and adds a computed
# 3x3 game board representation
class ResponseGame(Game):
    positions: list[str] | None = Field(default=None, exclude=True)

    @computed_field(return_type=list[list[str]])
    def board(self) -> list[list[str]]:
        return [self.positions[i : i + 3] for i in range(0, 9, 3)]


@api.get("/games", response_model=list[ResponseGame])
def list_games():
    """List all available games in the order they were created"""
    # I'm relying on Python 3.7+'s preservation of insert order for dictionaries
    # to return these in chronological order
    return list(GAMES.values())


@api.post("/games")
def post_game() -> str:
    """Create a new game, returning the game id"""
    game = Game()
    GAMES[str(game.id)] = game
    return str(game.id)


@api.get("/games/{game_id}", response_model=ResponseGame)
def get_game(game_id: str) -> Game:
    """Get game state by id"""
    game = GAMES.get(game_id)

    if not game:
        raise HTTPException(404, "Game not found")

    return game


@api.get("/games/{game_id}/moves", response_model=list[Move])
def list_moves(game_id: str):
    """List all moves in a game chronologically."""
    game = GAMES.get(game_id)

    if not game:
        raise HTTPException(404, "Game not found")

    return game.moves


@api.post("/games/{game_id}/moves", response_model=ResponseGame)
def post_move(game_id: str, move: RequestMove):
    """Add a move to a game by id

    This will trigger a responding random move from the computer player.

    This will raise a 400 if the game does not exist, and for any GameErrors
    that are raised making the move (such as if the game is finished, or it's
    not the player's turn).
    """
    game = GAMES.get(game_id)

    if not game:
        raise HTTPException(404, "Game not found")

    if game.finished:
        raise HTTPException(400, "Game already finished")

    game_move = Move(x=move.x, y=move.y, player=game.next_player)

    try:
        game.play(game_move)
    except GameError as err:
        raise HTTPException(400, str(err)) from err

    # Check for winner or draw
    if game.winner or game.finished:
        return game

    # Play a random move for the alternative player, unless the game is over
    try:
        rand_move = random_move(game, game.next_player)
        game.play(rand_move)
    except GameOver:
        pass

    return game


app = FastAPI(title="PlayOX")
app.mount("/api", api)
app.mount("/", StaticFiles(directory="html", html=True), name="html")
