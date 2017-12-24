"""Entrypoint for hlt bot, hanldes game loop."""
import logging
from datetime import datetime, timedelta

from . import constants, entity, networking

log = logging.getLogger(__name__)


def run() -> None:
    """Start and maintain a running halite game."""
    log.debug('Initializing Game')
    game = networking.Game('SimKev2')
    log.debug('Starting Game')

    # After 60 seconds pre processing
    game.begin_game()

    while True:
        turn_start = datetime.utcnow()
        game_map = game.update_map()
        me = game_map.get_me()
        command_queue = []

        for ship in game_map.get_me().all_ships():
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                continue

            if datetime.utcnow() - turn_start > timedelta(seconds=1.7):
                log.warning('Near timeout sending commands.')
                break

            command = None
            entities_by_distance = game_map.nearby_entities_by_distance(ship)

            for dist in sorted(entities_by_distance):
                for obj in sorted(
                        entities_by_distance[dist],
                        key=lambda o: o.radius,
                        reverse=True):

                    if isinstance(obj, entity.Planet):
                        if ship.can_dock(obj):
                            obj.curr_docking.append(ship)
                            command = ship.dock(obj)
                            break
                        elif obj.is_full() and obj.owner == me:
                            continue
                        elif obj.is_owned() and obj.owner != me:
                            continue
                        else:
                            open_spots = obj.num_docking_spots - (
                                len(obj.all_docked_ships()) +
                                obj.enroute +
                                len(obj.curr_docking))

                            if not open_spots:
                                continue

                            obj.enroute += 1

                    elif isinstance(obj, entity.Ship):
                        if me.get_ship(obj.id):
                            continue

                    command = ship.navigate(
                        ship.closest_point_to(obj),
                        game_map,
                        speed=int(constants.MAX_SPEED))

                    break

                if command:
                    break

            if command:
                command_queue.append(command)

        game.send_command_queue(command_queue)
