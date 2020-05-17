import uuid
from typing import List


class Game:

    def __init__(self, players: List[str], init_pot: int, small_blind_stake: int):
        self._uuid = uuid.SafeUUID
        self._players = players
        self._init_pot = init_pot
        self._small_blind_stake = small_blind_stake

    @property
    def players(self):
        return self._players

    @property
    def init_pot(self):
        return self._init_pot

    @property
    def small_blind_stake(self):
        return self._small_blind_stake

    def __str__(self):
        return """
        Game [
            uuid={uuid},
            players={players},
            init_pot={init_pot},
            small_blind_stake={small_blind_stake}
        ]
        """.format(
            uuid=self._uuid, players=self._players,
            init_pot=self._init_pot, small_blind_stake=self._small_blind_stake
        )
