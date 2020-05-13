import logging
import random
from poker import Card, Hand, Combo
from typing import List, Tuple

from src.models.game import Game
from src.models.game_result import GameResult
from src.models.game_round import GameRound
from src.models.game_state import GameState
from src.models.betting_state import BettingState
from src.poker_agent import agent_call_action


LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level='INFO')


LOGGER = logging.getLogger(__name__)


def start_simulation(players: List[str], init_pot: int = 100, small_blind_stake: int = 5, max_iterations: int = 100):
    histogram = { player: 0 for player in players }
    for i in range(max_iterations):
        winner = start_new_game(players=players, init_pot=init_pot, small_blind_stake=small_blind_stake)
        histogram[winner] += 1
    
    histogram_percentage = { player: str(win_count*100/max_iterations)+'%' for (player, win_count) in histogram.items() }

    LOGGER.info('End simulation. Winners are: %s' % histogram_percentage)


def start_new_game(players: List[str], init_pot: int = 100, small_blind_stake: int = 5, max_rounds: int = 100):
    new_game = Game(players=players, init_pot=init_pot, small_blind_stake=small_blind_stake)

    LOGGER.info('New game: %s' % new_game)

    game_result = GameResult(None)

    game_state = GameState(
        players=players,
        player_pots=[init_pot for _ in range(len(players))]
    )

    LOGGER.debug('New game state: %s' % game_state)

    # test with only max_rounds
    for pos in range(max_rounds):

        if len(game_state.remaining_players) == 1:
            game_result.set_winner(game_state.remaining_players[0])
            break

        deck = list(Card)
        random.shuffle(deck)

        game_round = GameRound(pos=pos, 
            small_blind=game_state.get_small_blind_player(pos), 
            big_blind=game_state.get_big_blind_player(pos), 
            players=game_state.remaining_players, 
            player_pots=game_state.remaining_player_pots, 
            player_hands=game_state.generate_player_hands(deck),
            small_blind_stake=small_blind_stake)

        LOGGER.debug('New game round: %s' % game_round)

        state_index = -1
        board_cards: List[Card] = []

        # pre-flop state
        state_index = state_index + 1
        next_move, pre_flop_state = game_state_move(state_index, "pre-flop", board_cards, game_round, game_state, None)

        if (not next_move):
            round_complete(game_round, game_state, pre_flop_state)
            continue

        # post-flop state
        board_cards.extend([deck.pop() for __ in range(3)])
        LOGGER.debug('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, post_flop_state = game_state_move(state_index, "post-flop", board_cards, game_round, game_state, pre_flop_state)

        if (not next_move):
            round_complete(game_round, game_state, pre_flop_state, post_flop_state)
            continue
        
        # turn state
        board_cards.extend([deck.pop() for __ in range(1)])
        LOGGER.debug('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, turn_state = game_state_move(state_index, "turn", board_cards, game_round, game_state, post_flop_state)

        if (not next_move):
            round_complete(game_round, game_state, pre_flop_state, post_flop_state, turn_state)
            continue

        # river state
        board_cards.extend([deck.pop() for __ in range(1)])
        LOGGER.debug('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, river_state = game_state_move(state_index, "river", board_cards, game_round, game_state, turn_state)

        round_complete(game_round, game_state, pre_flop_state, post_flop_state, turn_state, river_state)

    if (not game_result.winner):
        # determine winner in the remaining players by number of chips
        game_result.set_winner(game_state.get_player_with_most_chips())

    LOGGER.debug('End game. Winner is ' + game_result.winner)
    return game_result.winner


def game_state_move(state_index: int, board_state: str, board_cards: List[Card], 
    game_round: GameRound, game_state: GameState, previous_betting_state: BettingState):

    has_next_move = True
    remaining_players = previous_betting_state.remaining_players if previous_betting_state else game_round.players

    betting_state = BettingState(pos=state_index, board_state=board_state, board_cards=board_cards, 
        game_round=game_round, players=remaining_players, previous_state=previous_betting_state)

    if (betting_state.is_pre_flop_state()):
        betting_state.add_player_action(game_round.small_blind, ('small_blind', game_round.small_blind_stake))
        betting_state.add_player_action(game_round.big_blind, ('big_blind', game_round.small_blind_stake*2))

        game_state.update_player_pot(game_round.small_blind, -game_round.small_blind_stake)
        game_state.update_player_pot(game_round.big_blind, -game_round.small_blind_stake*2)

    player_index = game_round.get_first_moving_player_index()
    while(not betting_state.is_betting_state_complete()):

        player_move(player_index, game_round, betting_state, game_state)

        player_index = player_index - 1
        if (player_index < 0):
            player_index = len(game_round.players) - 1

    if (betting_state.is_round_complete()):        
        has_next_move = False

    return has_next_move, betting_state


def round_complete(game_round: GameRound, game_state: GameState, *betting_states: List[BettingState]):
    final_betting_state = betting_states[-1]
    LOGGER.debug('Round complete at betting state: %s' % final_betting_state.board_state)

    round_winner = final_betting_state.get_round_winner()
    round_total_pot = final_betting_state.get_round_total_pot()

    LOGGER.debug('Round winner: %s' % round_winner)
    LOGGER.debug('Round total pot: %d' % round_total_pot)

    game_state.update_player_pot(round_winner, round_total_pot)

    LOGGER.debug('Updated game state: %s' % game_state)


def player_move(player_index: int, game_round: GameRound, betting_state: BettingState, game_state: GameState):
    player = game_round.players[player_index]
    player_pot = game_state.get_player_pot(player)

    valid_actions = betting_state.get_valid_actions(player=player, player_pot=player_pot, small_blind_stake=game_round.small_blind_stake)
    if (valid_actions):
        player_action = agent_call_action(valid_actions=valid_actions)
        betting_state.add_player_action(player, player_action)

        execute_player_action(player, player_action, game_state)


def execute_player_action(player: str, player_action: Tuple[str, int], game_state: GameState):
    action, chip = player_action
    if (action == 'call' or action == 'raise'):
        game_state.update_player_pot(player, -chip)
