import logging
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level='INFO')

from flask import Flask, request, jsonify
app = Flask(__name__)

import json

from src.poker_agent import get_agent_action


LOGGER = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    return "OK"

@app.route('/agent_action', methods=['POST'])
def agent_action():
    jsondata = request.get_json()
    data = json.loads(jsondata)
    
    LOGGER.info(data)
    
    valid_actions = [tuple(x) for x in data['valid_actions']]
    return jsonify(agent_action=get_agent_action(valid_actions=valid_actions))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
