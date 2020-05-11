import uuid
from typing import List


class Game:
    
    def __init__(self, players: List[str], init_pot: int, min_pot: int):
        self._uuid = uuid.SafeUUID
        self._players = players
        self._init_pot = init_pot
        self._min_pot = min_pot

    @property
    def players(self):
        return self._players

    @property
    def init_pot(self):
        return self._init_pot

    @property
    def min_pot(self):
        return self._min_pot

    def __str__(self):
        return """
        Game [
            uuid={uuid},
            players={players},
            init_pot={init_pot},
            min_pot={min_pot}
        ]
        """.format(uuid=self._uuid, players=self._players, init_pot=self._init_pot, min_pot=self._min_pot)
