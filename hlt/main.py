"""Entrypoint for hlt bot, hanldes game loop."""
import logging

from . import constants, networking

log = logging.getLogger(__name__)


def run() -> None:
    """Start and maintain a running halite game."""
    log.debug('Initializing Game')
    game = networking.Game('SimKev2')
    log.debug('Starting Game')

    while True:
        game_map = game.update_map()
        command_queue = []

        for ship in game_map.get_me().all_ships():
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                continue

            for planet in game_map.all_planets():
                if planet.is_owned():
                    continue

                if ship.can_dock(planet):
                    command_queue.append(ship.dock(planet))
                else:
                    navigate_command = ship.navigate(
                        ship.closest_point_to(planet),
                        game_map,
                        speed=int(constants.MAX_SPEED / 2),
                        ignore_ships=True)

                    if navigate_command:
                        command_queue.append(navigate_command)
                break

        game.send_command_queue(command_queue)
