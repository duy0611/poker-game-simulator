from typing import List, Tuple


def get_agent_action(valid_actions: List[Tuple[str, int, int]]) -> Tuple[str, int]:
    actions = [action for (action, min_stake, max_stake) in valid_actions]
    if ('check' in actions):
        return ('check', 0)
    elif ('call' in actions):
        return ('call', valid_actions[actions.index('call')][1])
    else:
        print('something wrong here!!!')
        return ('fold', 0)
