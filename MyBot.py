"""Entrypoint for Halite bot to run a game."""
import logging

import hlt

logging.basicConfig()
log = logging.getLogger('Simkev2Bot')
log.debug('Entering game.')
hlt.main.run()
