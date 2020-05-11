import random
from poker import Card, Hand, Combo
from typing import List, Tuple

from src.models.game import Game
from src.models.game_result import GameResult
from src.models.game_round import GameRound
from src.models.game_state import GameState
from src.models.betting_state import BettingState
from src.poker_agent import agent_call_action


def start_new_game(players: List[str], init_pot: int = 100, min_pot: int = 5, max_round: int = 100):
    new_game = Game(players=players, init_pot=init_pot, min_pot=min_pot)

    print('New game: %s' % new_game)

    game_state = GameState(
        players=players,
        player_pots=[init_pot for _ in range(len(players))]
    )

    print('New game state: %s' % game_state)

    # test with only 5 rounds
    for pos in range(max_round):

        if len(game_state.remaining_players) == 1:
            print('End game. Winner is ' + game_state.remaining_players[0])
            break

        deck = list(Card)
        random.shuffle(deck)

        game_round = GameRound(pos=pos, 
            small_blind=game_state.get_small_blind_player(pos), 
            big_blind=game_state.get_big_blind_player(pos), 
            players=game_state.remaining_players, 
            player_pots=game_state.remaining_player_pots, 
            player_hands=game_state.generate_player_hands(deck),
            min_pot=min_pot)

        print('New game round: %s' % game_round)

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
        print('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, post_flop_state = game_state_move(state_index, "post-flop", board_cards, game_round, game_state, pre_flop_state)

        if (not next_move):
            round_complete(game_round, game_state, pre_flop_state, post_flop_state)
            continue
        
        # turn state
        board_cards.extend([deck.pop() for __ in range(1)])
        print('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, turn_state = game_state_move(state_index, "turn", board_cards, game_round, game_state, post_flop_state)

        if (not next_move):
            round_complete(game_round, game_state, pre_flop_state, post_flop_state, turn_state)
            continue

        # river state
        board_cards.extend([deck.pop() for __ in range(1)])
        print('Board cards: %s' % board_cards)

        state_index = state_index + 1
        next_move, river_state = game_state_move(state_index, "river", board_cards, game_round, game_state, turn_state)

        round_complete(game_round, game_state, pre_flop_state, post_flop_state, turn_state, river_state)


def game_state_move(state_index: int, board_state: str, board_cards: List[Card], 
    game_round: GameRound, game_state: GameState, previous_betting_state: BettingState):

    has_next_move = True
    remaining_players = previous_betting_state.remaining_players if previous_betting_state else game_round.players

    betting_state = BettingState(pos=state_index, board_state=board_state, board_cards=board_cards, 
        game_round=game_round, players=remaining_players, previous_state=previous_betting_state)

    if (betting_state.is_pre_flop_state()):
        betting_state.add_player_action(game_round.small_blind, ('small_blind', game_round.min_pot))
        betting_state.add_player_action(game_round.big_blind, ('big_blind', game_round.min_pot*2))

        game_state.update_player_pot(game_round.small_blind, -game_round.min_pot)
        game_state.update_player_pot(game_round.big_blind, -game_round.min_pot*2)

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
    print('Round complete at betting state: %s' % final_betting_state.board_state)

    round_winner = final_betting_state.get_round_winner()
    round_total_pot = final_betting_state.get_round_total_pot()

    print('Round winner: %s' % round_winner)
    print('Round total pot: %d' % round_total_pot)

    game_state.update_player_pot(round_winner, round_total_pot)

    print('Updated game state: %s' % game_state)


def player_move(player_index: int, game_round: GameRound, betting_state: BettingState, game_state: GameState):
    player = game_round.players[player_index]
    player_pot = game_state.get_player_pot(player)

    valid_actions = betting_state.get_valid_actions(player=player, player_pot=player_pot, min_pot=game_round.min_pot)
    if (valid_actions):
        player_action = agent_call_action(valid_actions=valid_actions)
        betting_state.add_player_action(player, player_action)

        execute_player_action(player, player_action, game_state)


def execute_player_action(player: str, player_action: Tuple[str, int], game_state: GameState):
    action, chip = player_action
    if (action == 'call' or action == 'raise'):
        game_state.update_player_pot(player, -chip)
