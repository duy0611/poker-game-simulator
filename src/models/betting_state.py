import logging
from typing import List, Tuple, Dict
from poker import Card

from src.models.game_round import GameRound
from src.poker_engine.poker_hand_check import detect_hand, compare_hands


LOGGER = logging.getLogger(__name__)


class BettingState:

    def __init__(self, pos: int, board_state: str, board_cards: List[Card], game_round: GameRound,
                 players: List[str], player_actions: Dict[str, List[Tuple[str, int]]] = None,
                 previous_state: 'BettingState' = None):

        self._pos = pos
        self._board_state = board_state
        self._board_cards = board_cards
        self._game_round = game_round
        self._players = players
        self._player_actions = player_actions or {}
        self._previous_state = previous_state

    @property
    def board_state(self):
        return self._board_state

    @property
    def board_cards(self):
        return self._board_cards

    @property
    def players(self):
        return self._players

    @property
    def player_actions(self):
        return self._player_actions

    @property
    def remaining_players(self):
        filtered_players = [player for (player, actions) in self._player_actions.items() if actions[-1][0] != 'fold']
        return self._game_round.get_orderd_players(filtered_players)

    def is_pre_flop_state(self):
        return bool(self._board_state == 'pre-flop')

    def is_post_flop_state(self):
        return bool(self._board_state == 'post-flop')

    def is_turn_state(self):
        return bool(self._board_state == 'turn')

    def is_river_state(self):
        return bool(self._board_state == 'river')

    def is_betting_state_complete(self):
        all_players_called_action = len(self._players) == len(self._player_actions)
        if all_players_called_action:

            player_betting_chips = [sum([x[1] for x in actions])
                                    for actions in self._player_actions.values() if actions[-1][0] != 'fold']

            is_chips_the_same = len(set(player_betting_chips)) == 1

            return is_chips_the_same

        return False

    def is_round_complete(self):
        all_players_called_action = len(self._players) == len(self._player_actions)
        if all_players_called_action:

            number_of_players_folded = len([player for (player, actions) in
                                            self._player_actions.items() if actions[-1][0] == 'fold'])

            is_other_players_folded = number_of_players_folded == (len(self._players) - 1)

            return is_other_players_folded or (self.is_betting_state_complete() and self.is_river_state())

        return False

    def add_player_action(self, player: str, player_action: Tuple[str, int]):
        self._player_actions.setdefault(player, []).append(player_action)

    def get_valid_actions(self, player: str, player_pot: int, small_blind_stake: int) -> List[Tuple[str, int, int]]:
        # valid actions: check, call, raise, fold
        # no_action (if player has already folded) -> for this we return an empty list
        valid_actions = []

        # do nothing if player has already folded
        previous_player_action = self._player_actions[player][-1] if player in self._player_actions else None
        if (previous_player_action and previous_player_action[0] == 'fold'):
            return valid_actions

        valid_actions.append(('fold', 0, 0))

        biggest_betting_chip = max([sum([x[1] for x in actions]) for (pl, actions) in self._player_actions.items()
                                    if actions[-1][0] != 'fold' and pl != player]) \
                               if len(self._player_actions) > 0 else 0

        if biggest_betting_chip == 0:
            valid_actions.append(('check', 0, 0))
            valid_actions.append(('raise', small_blind_stake, player_pot))
        else:
            current_betting_chip = sum([action[1] for action in self._player_actions[player]]) \
                                   if player in self._player_actions else 0
            if current_betting_chip < biggest_betting_chip:
                valid_actions.append(
                    ('call', biggest_betting_chip - current_betting_chip, biggest_betting_chip - current_betting_chip))
                valid_actions.append(
                    ('raise', biggest_betting_chip - current_betting_chip + small_blind_stake, player_pot))
            else:
                valid_actions.append(('check', 0, 0))
                valid_actions.append(('raise', small_blind_stake, player_pot))

        return valid_actions

    def get_round_winner(self):
        if not self.is_river_state():
            return [player for (player, actions) in self._player_actions.items() if actions[-1][0] != 'fold'][0]

        player_hand_checks = [detect_hand(player_hand, self._board_cards)
                              for player_hand in self._game_round.get_ordered_player_hands(self.remaining_players)]

        LOGGER.debug('Player hand checks: %s', player_hand_checks)

        best_hand = compare_hands(player_hand_checks)

        # detect if it is a tied round
        # TODO: do something here

        winner = self.remaining_players[player_hand_checks.index((best_hand))]

        return winner

    def get_round_total_pot(self):
        previous_state_total_pot = self._previous_state.get_round_total_pot() if self._previous_state else 0
        return previous_state_total_pot + sum([betting_chip for actions in
                                               self._player_actions.values() for (action, betting_chip) in actions])

    def __str__(self):
        return """
        BettingState[
            pos={pos},
            board_state={board_state},
            board_cards={board_cards},
            players={players},
            player_actions={player_actions}
        ]
        """.format(pos=self._pos, board_state=self._board_state, board_cards=self._board_cards,
                   players=self._players, player_actions=self._player_actions)
