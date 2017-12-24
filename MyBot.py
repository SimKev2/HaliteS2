"""Entrypoint for Halite bot to run a game."""
import logging

import hlt

logging.basicConfig(
    filename='Simkev2Bot.log',
    format='%(asctime)s %(filename)s:%(lineno)d %(message)s',
    level=logging.DEBUG)

log = logging.getLogger('Simkev2Bot')
log.debug('Entering game.')
hlt.main.run()
