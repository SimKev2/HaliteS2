"""Communication with the halite engine."""
import sys
import logging
import copy
from typing import List

from . import game_map

log = logging.getLogger(__name__)


class Game:
    """
    :ivar map: Current map representation
    :ivar initial_map: The initial version of the map before game starts
    """

    @staticmethod
    def _send_string(s: str) -> None:
        """Send data to the game."""
        sys.stdout.write(s)

    @staticmethod
    def _done_sending() -> None:
        """Finish sending commands to the game."""
        sys.stdout.write('\n')
        sys.stdout.flush()

    @staticmethod
    def _get_string() -> str:
        """
        Read input from the game.

        :return: The input read from the Halite engine
        """
        result = sys.stdin.readline().rstrip('\n')
        return result

    @staticmethod
    def send_command_queue(command_queue: List[str]) -> None:
        """
        Issue the given list of commands.

        :param command_queue: List of commands to send the Halite engine
        """
        for command in command_queue:
            Game._send_string(command)

        Game._done_sending()

    def __init__(self, name: str):
        """
        Initialize the bot with the given name.

        :param name: The name of the bot.
        """
        self.turn_num = 0
        self._name = name

        _id = int(self._get_string())
        width, height = [int(x) for x in self._get_string().strip().split()]

        self.map = game_map.Map(_id, width, height)

        self.update_map()
        self.initial_map = copy.deepcopy(self.map)

    def update_map(self) -> game_map.Map:
        """
        Parse the map given by the engine.

        :return: Newly parsed map
        """
        log.debug(f'---TURN {self.turn_num}---')
        self.map.parse(self._get_string())
        self.turn_num += 1
        return self.map

    def begin_game(self) -> None:
        """Begin the game by sending the bot name to the engine."""
        self._send_string(self._name)
        self._done_sending()
        self.turn_num = 0
