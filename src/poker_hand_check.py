from collections import defaultdict
from itertools import combinations
from typing import List, Tuple
from poker import Card, Hand, Combo, Rank


card_order_dict = {
    Rank.DEUCE:2, Rank.THREE:3, Rank.FOUR:4, Rank.FIVE:5, 
    Rank.SIX:6, Rank.SEVEN:7, Rank.EIGHT:8, Rank.NINE:9, 
    Rank.TEN:10,Rank.JACK:11, Rank.QUEEN:12, Rank.KING:13, 
    Rank.ACE:14
}


# Return best possible hand with its score
def detect_hand(player_hand: Combo, board_cards: List[Card]) -> Tuple[int, List[Card]]:
    all_cards = [player_hand.first, player_hand.second] + board_cards
    hand_combinations = list(combinations(all_cards, 5))

    hand_combinations_with_rank = {}
    for hand in hand_combinations:
        hand_value = check_hand(hand)
        hand_combinations_with_rank.setdefault(hand_value, []).append(hand)

    best_hand_score = max(hand_combinations_with_rank.keys())
    best_hands = hand_combinations_with_rank[best_hand_score]

    best_hand = []

    if len(best_hands) == 1 or best_hand_score == 10:
        best_hand = best_hands[0]
    else:
        best_hand = compare_tied_hands(best_hands, best_hand_score)

    return best_hand_score, best_hand


# Return winner hand if they are tied (same hand score)
def compare_tied_hands(hands, hand_score):
    best_hand = []

    if (hand_score in [9, 6, 5, 1]):
        best_hand = compare_card_not_same_kind(hands)
    elif(hand_score in [8, 7, 4, 3, 2]):
        best_hand = compare_card_same_kind(hands)
    
    return best_hand


# Return Values:
# Royal Flush: (10,)
# Straight Flush: (9, high card)
# Four of a Kind: (8, quad card, kicker)
# Full House: (7, trips card, pair card)
# Flush: (6, [flush high card, flush second high card, ..., flush low card])
# Straight: (5, high card)
# Three of a Kind: (4, trips card, (kicker high card, kicker low card))
# Two Pair: (3, high pair card, low pair card, kicker)
# Pair: (2, pair card, (kicker high card, kicker med card, kicker low card))
# High Card: (1, [high card, second high card, third high card, etc.])
def check_hand(hand):
    if check_royal_flush(hand):
        return 10
    elif check_straight_flush(hand):
        return 9
    elif check_four_of_a_kind(hand):
        return 8
    elif check_full_house(hand):
        return 7
    elif check_flush(hand):
        return 6
    elif check_straight(hand):
        return 5
    elif check_three_of_a_kind(hand):
        return 4
    elif check_two_pairs(hand):
        return 3
    elif check_one_pairs(hand):
        return 2
    else:
        return 1

def check_royal_flush(hand):
    if check_flush(hand) and check_straight(hand):
        values = [c.rank for c in hand]
        if set(values).issuperset(set(["T", "J", "Q", "K", "A"])):
            return True
        return False
    else:
        return False

def check_straight_flush(hand):
    if check_flush(hand) and check_straight(hand):
        return True
    else:
        return False

def check_four_of_a_kind(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values: 
        value_counts[v]+=1
    if 4 in value_counts.values():
        return True
    return False

def check_full_house(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values: 
        value_counts[v]+=1
    if 2 in value_counts.values() and 3 in value_counts.values():
        return True
    return False

def check_flush(hand):
    suits = [c.suit for c in hand]
    suit_counts = defaultdict(lambda:0)
    for s in suits: 
        suit_counts[s]+=1
    if 5 in suit_counts.values():
        return True
    return False

def check_straight(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v] += 1
    rank_values = [card_order_dict[i] for i in values]
    value_range = max(rank_values) - min(rank_values)
    if len(set(value_counts.values())) == 1 and (value_range==4):
        return True
    else: 
        #check straight with low Ace
        if set(values).issuperset(set(["A", "2", "3", "4", "5"])):
            return True
        return False

def check_three_of_a_kind(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if 3 in value_counts.values():
        return True
    else:
        return False

def check_two_pairs(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if list(value_counts.values()).count(2) == 2:
        return True
    else:
        return False

def check_one_pairs(hand):
    values = [c.rank for c in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if list(value_counts.values()).count(2) == 1:
        return True
    else:
        return False

def check_high_card(hand):
    values = [c.rank for c in hand]
    rank_values = [card_order_dict[i] for i in values]
    return max(rank_values)

# straight_flush, flush, straight, high card
def compare_card_not_same_kind(hands):
    hand_scores = [(i, check_high_card(hand)) for i, hand in enumerate(hands)]
    winner = sorted(hand_scores , key=lambda x:x[1])[-1][0]
    return hands[winner]

# four_of_a_kind, full_house, three_of_a_kind, two_pairs, one_pair
def compare_card_same_kind(hands):
    hand_scores = [(i, _eval_card_same_kind(hand)) for i, hand in enumerate(hands)]
    winner = sorted(hand_scores , key=lambda x:x[1])[-1][0]
    return hands[winner]

def _eval_card_not_same_kind(hand):
    ranks = [c.rank for c in hand]
    rcounts = {card_order_dict[r]: ranks.count(r) for r in ranks}.items()
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts)[::-1])
    return score, ranks

def _eval_card_same_kind(hand):
    ranks = [c.rank for c in hand]
    rcounts = {card_order_dict[r]: ranks.count(r) for r in ranks}.items()
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts)[::-1])
    return score, ranks
    