"""Entrypoint for Halite bot to run a game."""
import logging

from .hlt.main import run

logging.basicConfig()
log = logging.getLogger('Simkev2Bot')
log.debug('Entering game.')
run()
