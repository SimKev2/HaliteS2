"""Game map interactions and information."""
from typing import List, Tuple, Union

from . import collision, entity


class Map:
    """
    Map which houses the current game information/metadata.

    :ivar my_id: Current player id associated with the map
    :ivar width: Map width
    :ivar height: Map height
    """

    def __init__(self, my_id: int, width: int, height: int):
        """
        :param my_id: User's id (tag)
        :param width: Map width
        :param height: Map height
        """
        self.my_id = my_id
        self.width = width
        self.height = height
        self._players = {}
        self._planets = {}

    def get_me(self) -> 'Player':
        """
        Retrieve the bot's Player from all players in game.

        :return: The player associated with the current user.
        """
        return self._players.get(self.my_id)

    def get_player(self, player_id: int) -> 'Player':
        """
        Retrieve the Player with the given player_id.

        :param player_id: The id of the desired player
        :return: The player associated with player_id
        """
        return self._players.get(player_id)

    def all_players(self) -> List['Player']:
        """
        Retrieve all the players in the game.

        :return: List of all players
        """
        return list(self._players.values())

    def get_planet(self, planet_id: int) -> entity.Planet:
        """
        Retrieve the Planet with the given planet_id.

        :return: The planet associated with planet_id
        """
        return self._planets.get(planet_id)

    def all_planets(self) -> List[entity.Planet]:
        """
        Retrieve all Planet entities in the game.

        :return: List of all planets
        """
        return list(self._planets.values())

    def nearby_entities_by_distance(
            self, source_entity: entity.Entity) -> dict:
        """
        Retrieve the distances of entities nearby the given entity.

        :param source_entity: The source entity to find distances from
        :return: Dict containing all entities with their designated distances
        """
        result = {}
        for foreign_entity in self._all_ships() + self.all_planets():
            if source_entity == foreign_entity:
                continue

            result.setdefault(source_entity.calculate_distance_between(
                foreign_entity), []).append(foreign_entity)

        return result

    def _link(self) -> None:
        """Update all the entities with the correct ship and planet objects."""
        for celestial_object in self.all_planets() + self._all_ships():
            celestial_object._link(self._players, self._planets)

    def parse(self, map_string: str) -> None:
        """
        Parse the map description from the game.

        :param map_string: The string which the Halite engine outputs
        """
        tokens = map_string.split()

        self._players, tokens = Player.parse(tokens)
        self._planets, tokens = entity.Planet.parse(tokens)

        assert len(tokens) == 0, 'Extra tokens were present after parsing.'
        self._link()

    def _all_ships(self) -> List[entity.Ship]:
        """
        Helper function to extract all ships from all players.

        :return: List of ships
        """
        all_ships = []
        for player in self.all_players():
            all_ships.extend(player.all_ships())

        return all_ships

    def _intersects_entity(
            self, target: Union[entity.Ship, entity.Position]
            ) -> Union[entity.Entity, None]:
        """
        Check if the specified entity (x, y, r) intersects any planets.

        Entity is assumed to not be a planet.

        :param target: The entity to check intersections with.
        :return: The colliding entity if so, else None.
        """
        for celestial_object in self._all_ships() + self.all_planets():
            if celestial_object is target:
                continue

            d = celestial_object.calculate_distance_between(target)
            if d <= celestial_object.radius + target.radius + 0.1:
                return celestial_object

        return None

    def obstacles_between(
            self,
            ship: entity.Ship,
            target: entity.Entity,
            ignore_ships: bool = False,
            ignore_planets: bool = False,
            ) -> List[entity.Entity]:
        """
        Determine the obstacles between the ship and the target.

        :param ship: Source entity
        :param target: Target entity
        :param ignore_ships: Flag representing if ships should be ignored.
        :param ignore_planets: Flag representing if planets should be ignored.
        :return: The list of obstacles between the ship and target
        """
        obstacles = []

        entities = []
        entities += self.all_planets() if not ignore_planets else []
        entities += self._all_ships() if not ignore_ships else []

        for foreign_entity in entities:
            if foreign_entity == ship or foreign_entity == target:
                continue

            fudge = (2 * ship.radius if isinstance(
                foreign_entity, entity.Ship) else ship.radius + 0.2)

            if collision.intersect_segment_circle(
                    ship, target, foreign_entity, fudge=fudge):
                obstacles.append(foreign_entity)

        return obstacles


class Player:
    """
    :ivar id: The player's unique id
    """

    def __init__(self, player_id: int, ships: dict = None):
        """
        :param player_id: User's id
        :param ships: Ships user controls (optional)
        """
        self.id = player_id
        self._ships = ships or {}

    def all_ships(self) -> List[entity.Ship]:
        """
        Retrieve all ships belonging to this Player.

        :return: A list of all controlled ships
        """
        return list(self._ships.values())

    def get_ship(self, ship_id: int) -> entity.Ship:
        """
        Retrieve a Ship with the given ship_id under Player control.

        :param ship_id: The ship id of the desired ship.
        :return: The ship designated by ship_id belonging to this user.
        """
        return self._ships.get(ship_id)

    @staticmethod
    def _parse_single(tokens: List[str]) -> Tuple[int, 'Player', List[str]]:
        """
        Parse one user given an input string from the Halite engine.

        :param tokens: Halite engine split input.
        :return: The parsed player id, player object, and remaining tokens
        """
        player_id, *remainder = tokens
        player_id = int(player_id)
        ships, remainder = entity.Ship.parse(player_id, remainder)
        player = Player(player_id, ships)
        return player_id, player, remainder

    @staticmethod
    def parse(tokens: List[str]) -> Tuple[dict, List[str]]:
        """
        Parse an entire user input string from the Halite engine for all users.

        :param tokens: Halite engine split input.
        :return: The parsed players in the form of player dict,
            and remaining tokens
        """
        num_players, *remainder = tokens
        num_players = int(num_players)
        players = {}

        for _ in range(num_players):
            player, players[player], remainder = Player._parse_single(
                remainder)

        return players, remainder

    def __str__(self):
        return 'Player {} with ships {}'.format(self.id, self.all_ships())

    def __repr__(self):
        return self.__str__()
