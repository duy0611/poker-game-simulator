from flask import Flask, jsonify, request
app = Flask(__name__)

import docker
docker_client = docker.from_env()

from src.poker_simulator import start_simulation

# List of players in memory - the player name will be corresponding to poker-agent container name
PLAYERS = []

@app.route('/players')
def get_players():
    """Return list of players registered"""
    return jsonify(PLAYERS)

@app.route('/players/register/<player_name>', methods=['POST'])
def register_new_player(player_name):
    """Register new player"""
    if player_name in PLAYERS:
        return "Already registered: {}!".format(player_name)
    
    PLAYERS.append(player_name)
    return "DONE Register and Build container for player: {}!".format(player_name)

@app.route('/simulations/start_new', methods=['POST'])
def start_new_simulation():
    players = request.args['players']
    init_pot = int(request.args['init_pot'])
    small_blind_stake = int(request.args['small_blind_stake'])
    max_iterations = int(request.args['max_iterations'] or 1)

    start_simulation(players=players.split(','), init_pot=init_pot, small_blind_stake=small_blind_stake, max_iterations=max_iterations)

    return 'DONE Start new simulation with players={} init_pot={} small_blind_stake={} for {} iterations'.format(
        players, init_pot, small_blind_stake, max_iterations
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
