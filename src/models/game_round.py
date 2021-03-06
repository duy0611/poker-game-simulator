from typing import List
from poker import Combo


class GameRound:

    def __init__(self, pos: int, small_blind: str, big_blind: str,
                 players: List[str], player_pots: List[int], player_hands: List[Combo], small_blind_stake: int):

        self._pos = pos
        self._small_blind = small_blind
        self._big_blind = big_blind
        self._players = players
        self._player_pots = player_pots
        self._player_hands = player_hands
        self._small_blind_stake = small_blind_stake

    @property
    def small_blind(self):
        return self._small_blind

    @property
    def big_blind(self):
        return self._big_blind

    @property
    def players(self):
        return self._players

    @property
    def player_pots(self):
        return self._player_pots

    @property
    def player_hands(self):
        return self._player_hands

    @property
    def small_blind_stake(self):
        return self._small_blind_stake

    def get_first_moving_player_index(self):
        return self._players.index(self._small_blind)

    def get_orderd_players(self, filtered_players: List[str]):
        return [player for player in self._players if player in filtered_players]

    def get_ordered_player_hands(self, filtered_players: List[str]):
        return [self._player_hands[i] for i, player in enumerate(self._players) if player in filtered_players]

    def __str__(self):
        return """
        GameRound [
            pos={pos},
            small_blind={small_blind},
            big_blind={big_blind},
            players={players},
            player_pots={player_pots},
            player_hands={player_hands},
            small_blind_stake={small_blind_stake}
        ]
        """.format(
            pos=self._pos, small_blind=self._small_blind, big_blind=self._big_blind,
            players=self._players, player_pots=self._player_pots, player_hands=self._player_hands,
            small_blind_stake=self._small_blind_stake)
        