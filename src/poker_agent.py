import logging
import json
import requests
from typing import List, Tuple


LOGGER = logging.getLogger(__name__)


def agent_call_action(player: str, valid_actions: List[Tuple[str, int, int]], use_local=True) -> Tuple[str, int]:
    if (use_local):
        actions = [action for (action, min_chip, max_chip) in valid_actions]
        if ('check' in actions):
            return ('check', 0)
        elif ('call' in actions):
            return ('call', valid_actions[actions.index('call')][1])
        else:
            LOGGER.warn('Cannot proceed agent_call_action: player={} valid_actions={}'.format(player, valid_actions))
            return ('fold', 0)
    else:
        # Remote call to agent container
        req = {
            'valid_actions': valid_actions
        }
        res = requests.post('http://agent-{}:5000/agent_action'.format(player), json=json.dumps(req))

        if (res.status_code == 200):
            return tuple(res.json()['agent_action'])

        LOGGER.warn('Cannot proceed agent_call_action: player={} valid_actions={} response={}'.format(player, valid_actions, res))
        return ('fold', 0)
