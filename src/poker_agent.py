import random
from poker import Card, Hand, Combo
from typing import List, Tuple


def agent_call_action(valid_actions: List[Tuple[str, int, int]]) -> Tuple[str, int]:
    actions = [action for (action, min_chip, max_chip) in valid_actions]
    if ('check' in actions):
        return ('check', 0)
    elif ('call' in actions):
        return ('call', valid_actions[actions.index('call')][1])
    else:
        print('something wrong here!!!')
        return ('fold', 0)
