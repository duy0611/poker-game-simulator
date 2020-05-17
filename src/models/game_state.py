from typing import List, Tuple
from poker import Combo


class GameState:

    def __init__(self, players: List[str], player_pots: List[int]):
        self.players = players
        self.player_pots = player_pots

    def get_small_blind_player(self, round_pos: int):
        return self.remaining_players[round_pos % len(self.remaining_players)]

    def get_big_blind_player(self, round_pos: int):
        small_blind_player_index = round_pos % len(self.remaining_players)
        big_blind_player_index = small_blind_player_index + 1

        return self.remaining_players[big_blind_player_index
                                      if big_blind_player_index < len(self.remaining_players) else 0]

    @property
    def remaining_players(self):
        return [x for (x, y) in self.current_player_states if y > 0]

    @property
    def remaining_player_pots(self):
        return [y for (x, y) in self.current_player_states if y > 0]

    @property
    def current_player_states(self) -> List[Tuple[str, int]]:
        return list(zip(self.players, self.player_pots))

    def generate_player_hands(self, deck: List[Combo]):
        return [Combo.from_cards(deck.pop(), deck.pop()) for _ in range(len(self.remaining_players))]

    def update_player_pot(self, player: str, chip_amount: int):
        self.player_pots[self.players.index(player)] = self.player_pots[self.players.index(player)] + chip_amount

    def get_player_pot(self, player: str):
        return self.player_pots[self.players.index(player)]

    def get_player_with_most_chips(self):
        return sorted([(x, y) for (x, y) in self.current_player_states if y > 0], key=lambda x: x[1])[-1][0]

    def __str__(self):
        return """
        GameState[
            players={players}
        ]
        """.format(players=list(zip(self.players, self.player_pots)))
