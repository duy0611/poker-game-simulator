import logging

from src.poker_engine.poker_simulator import start_simulation


LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level='INFO')


start_simulation(players=['dnguyen', 'erik', 'mathias', 'dtran'],
                 init_pot=50, small_blind_stake=5, max_iterations=1, use_local=True)
