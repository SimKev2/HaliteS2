import sys
import logging
import copy

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
    def send_command_queue(command_queue: [str]) -> None:
        """
        Issue the given list of commands.

        :param command_queue: List of commands to send the Halite engine
        """
        for command in command_queue:
            Game._send_string(command)

        Game._done_sending()

    @staticmethod
    def _set_up_logging(tag: int, name: str) -> None:
        """
        Set up and truncate the log.

        :param tag: The user tag (used for naming the log)
        :param name: The bot name (used for naming the log)
        """
        log_file = '{}_{}.log'.format(tag, name)
        log.addHandler(logging.FileHandler(filename=log_file, mode='w'))
        log.info('Initialized bot {}'.format(name))

    def __init__(self, name: str):
        """
        Initialize the bot with the given name.

        :param name: The name of the bot.
        """
        self._name = name
        self._send_name = False
        tag = int(self._get_string())
        Game._set_up_logging(tag, name)
        width, height = [int(x) for x in self._get_string().strip().split()]
        self.map = game_map.Map(tag, width, height)
        self.update_map()
        self.initial_map = copy.deepcopy(self.map)
        self._send_name = True

    def update_map(self) -> game_map.Map:
        """
        Parse the map given by the engine.

        :return: Newly parsed map
        """
        if self._send_name:
            self._send_string(self._name)
            self._done_sending()
            self._send_name = False

        log.info('---NEW TURN---')
        self.map._parse(self._get_string())
        return self.map
