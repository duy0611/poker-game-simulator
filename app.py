import logging
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level='INFO')

from flask import Flask, jsonify, request, abort, render_template
from werkzeug.utils import secure_filename
app = Flask(__name__, static_url_path='/static', static_folder='static_files', template_folder='templates')
app.config["UPLOAD_FOLDER"] = './tmp'

import docker
docker_client = docker.from_env()

import os
import shutil
import zipfile

from src.poker_simulator import start_simulation


LOGGER = logging.getLogger(__name__)

# List of players in memory - the player name will be corresponding to poker-agent container name
PLAYERS = []


@app.route('/health', methods=['GET'])
def health():
    return "OK"

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

    LOGGER.info("DONE Register and Build container for player: {}!".format(player_name))
    return ""

@app.route('/players/start_agent/<player_name>', methods=['POST'])
def start_agent(player_name):
    if not player_name in PLAYERS:
        abort(400, "Player {} is not registered".format(player_name))

    image_name = 'poker-agent:{}-latest'.format(player_name)
    container_name = 'agent-{}'.format(player_name)

    try:
        container = docker_client.containers.get(container_name)
        container.stop()
    except docker.errors.NotFound:
        LOGGER.warn('Container not running yet: %s' % container_name)

    container = docker_client.containers.run(image_name, 
        name=container_name, auto_remove=True, remove=True,
        network="poker-game-simulator-shared", detach=True)

    LOGGER.info('Started new container: %s' % container.name)
    return ""

@app.route('/players/submit/<player_name>', methods=['GET'])
def render_submit_agent(player_name):
    if not player_name in PLAYERS:
        abort(400, "Player {} is not registered".format(player_name))
    
    return render_template('upload.html', player_name=player_name)

@app.route('/players/submit/<player_name>', methods=['POST'])
def submit_agent(player_name):
    if not player_name in PLAYERS:
        abort(400, "Player {} is not registered".format(player_name))
    
    player_submission = request.files['file']

    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], player_name, 'upload')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    final_file_path = os.path.join(upload_path, secure_filename(player_submission.filename))
    player_submission.save(final_file_path)
    LOGGER.info('New file is uploaded to %s' % final_file_path)

    unzip_path = os.path.join(app.config["UPLOAD_FOLDER"], player_name, 'src')
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)

    with zipfile.ZipFile(final_file_path, "r") as zip_ref:
        zip_ref.extractall(unzip_path)
        LOGGER.info('New file is extracted to %s' % unzip_path)

    shutil.copyfile('./agent-build/app.py', os.path.join(app.config["UPLOAD_FOLDER"], player_name, 'app.py'))
    shutil.copyfile('./agent-build/Dockerfile', os.path.join(app.config["UPLOAD_FOLDER"], player_name, 'Dockerfile'))
    shutil.copyfile('./agent-build/requirements.txt', os.path.join(app.config["UPLOAD_FOLDER"], player_name, 'requirements.txt'))
    
    build_image, build_logs = docker_client.images.build(
        path=os.path.join(app.config["UPLOAD_FOLDER"], player_name), 
        tag='poker-agent:{}-latest'.format(player_name))

    LOGGER.info(list(build_logs))
    
    return render_template('upload.html', player_name=player_name, success_message='New file has been uploaded sucessfully!')

@app.route('/simulations/start_new', methods=['POST'])
def start_new_simulation():
    players = request.args['players']
    players = players.split(',')

    if (not set(players).issubset(set(PLAYERS))):
        abort(400, "Some players have not registered: {}".format(players))

    init_pot = int(request.args['init_pot'])
    small_blind_stake = int(request.args['small_blind_stake'])
    max_iterations = int(request.args['max_iterations'] or 1)

    histogram = start_simulation(players=players, init_pot=init_pot, 
        small_blind_stake=small_blind_stake, max_iterations=max_iterations, use_local=False)

    LOGGER.info('DONE Start new simulation with players={} init_pot={} small_blind_stake={} for {} iterations'.format(
        players, init_pot, small_blind_stake, max_iterations
    ))

    return jsonify(histogram)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
