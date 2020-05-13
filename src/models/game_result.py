

class GameResult:

    def __init__(self, winner: str):
        self._winner = winner

    @property
    def winner(self):
        return self._winner

    def set_winner(self, winner: str):
        self._winner = winner
