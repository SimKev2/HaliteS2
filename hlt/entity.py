import abc
import math
from enum import Enum
from typing import Dict, List, Tuple, Union

from . import constants


class Entity:
    """
    Then entity abstract base-class represents all game entities possible.

    As a base all entities possess a position, radius, health, an owner and an
    id. Note that ease of interoperability, Position inherits from Entity.

    :ivar health: The entity's health.
    :ivar id: The entity ID
    :ivar owner: The player ID of the owner, if any.
        If None, Entity is not owned.
    :ivar radius: The radius of the entity (may be 0)
    :ivar x: The entity x-coordinate.
    :ivar y: The entity y-coordinate.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(
            self,
            x: float,
            y: float,
            radius: float,
            health: Union[int, None],
            player: Union[int, None],
            entity_id: Union[int, None]):
        self.health = health
        self.id = entity_id
        self.owner = player
        self.radius = radius
        self.x = x
        self.y = y

    def calculate_distance_between(self, target: 'Entity') -> float:
        """
        Calculates the distance between this object and the target.

        :param target: The target to get distance to.
        :return: Distance to the target.
        """
        return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)

    def calculate_angle_between(self, target: 'Entity') -> float:
        """
        Calculates the angle between this object and the target in degrees.

        :param target: The target to get the angle between.
        :return: Angle between entities in degrees
        """
        return math.degrees(math.atan2(
            target.y - self.y, target.x - self.x)) % 360

    def closest_point_to(
            self, target: 'Entity', min_distance: int = 3) -> 'Position':
        """
        Find the closest point to the given ship near the given target.

        This point will be outside its given radius, with an added fudge
        of min_distance.

        :param target: The target to compare against
        :param min_distance: Minimum distance specified from the object's
            outer radius
        :return: The closest point's coordinates
        """
        angle = target.calculate_angle_between(self)
        radius = target.radius + min_distance
        x = target.x + radius * math.cos(math.radians(angle))
        y = target.y + radius * math.sin(math.radians(angle))

        return Position(x, y)

    @abc.abstractmethod
    def _link(self, players, planets):
        pass

    def __str__(self):
        return (
            'Entity {} (id: {}) at position: (x = {}, y = {}), with '
            'radius = {}'.format(
                self.__class__.__name__, self.id, self.x, self.y, self.radius))

    def __repr__(self):
        return self.__str__()


class Planet(Entity):
    """
    A planet on the game map.

    :ivar current_production: How much production the planet has generated at
        the moment. Once it reaches the threshold, a ship will spawn and this
        will be reset.
    :ivar num_docking_spots: The max number of ships that can be docked.
    :ivar remaining_resources: The remaining production capacity of the planet.
    """

    def __init__(
            self,
            planet_id: int,
            x: float,
            y: float,
            hp: int,
            radius: float,
            docking_spots: int,
            current: int,
            remaining: int,
            owned: Union[int, None],
            owner: int,
            docked_ships: [int]):
        super().__init__(
            x, y, radius, hp, owner if bool(int(owned)) else None, planet_id)
        self.radius = radius
        self.current_production = current
        self.num_docking_spots = docking_spots
        self.remaining_resources = remaining

        self.someone_docking = False

        self._docked_ship_ids = docked_ships
        self._docked_ships = {}

    def get_docked_ship(self, ship_id: int) -> 'Ship':
        """
        Return the docked ship designated by its id.

        :param ship_id: The id of the ship to be returned.
        :return: The Ship object representing that id or None if not docked.
        """
        return self._docked_ships.get(ship_id)

    def all_docked_ships(self) -> ['Ship']:
        """
        The list of all ships docked into the planet

        :return: The list of all ships docked
        """
        return list(self._docked_ships.values())

    def is_owned(self) -> bool:
        """
        Determines if the planet has an owner.

        :return: True if owned, False otherwise
        """
        return self.owner is not None

    def is_full(self) -> bool:
        """
        Determines if the planet has been fully occupied.

        :return: True if full, False otherwise.
        """
        return len(self._docked_ship_ids) >= self.num_docking_spots

    def _link(self, players: Dict[int, 'Player'], planets: ['Planet']) -> None:
        """
        Link Planet entities to the correct Player and docked Ship entities.

        :param players: A dictionary of player objects keyed by id.
        """
        self.someone_docking = False
        if self.owner is not None:
            self.owner = players.get(self.owner)
            for ship in self._docked_ship_ids:
                self._docked_ships[ship] = self.owner.get_ship(ship)

    @staticmethod
    def _parse_single(tokens: List[str]) -> Tuple[int, 'Planet', List[str]]:
        """
        Parse a single planet given tokenized input from the game environment.

        :return: The planet ID, planet object, and unused tokens.
        """
        (plid, x, y, hp, r, docking, current, remaining,
         owned, owner, num_docked_ships, *remainder) = tokens

        plid = int(plid)
        docked_ships = []

        for _ in range(int(num_docked_ships)):
            ship_id, *remainder = remainder
            docked_ships.append(int(ship_id))

        planet = Planet(
            int(plid),
            float(x),
            float(y),
            int(hp),
            float(r),
            int(docking),
            int(current),
            int(remaining),
            bool(int(owned)),
            int(owner),
            docked_ships)

        return plid, planet, remainder

    @staticmethod
    def _parse(tokens: List[str]) -> Tuple[dict, List[str]]:
        """
        Parse planet data given a tokenized input.

        :param tokens: The tokenized input.
        :return: The populated planet dict and the unused tokens.
        """
        num_planets, *remainder = tokens
        num_planets = int(num_planets)
        planets = {}

        for _ in range(num_planets):
            plid, planet, remainder = Planet._parse_single(remainder)
            planets[plid] = planet

        return planets, remainder


class Ship(Entity):
    """
    A ship in the game.

    :ivar docking_status: The docking status
        (UNDOCKED, DOCKED, DOCKING, UNDOCKING)
    :ivar planet: The ID of the planet the ship is docked to, if applicable.
    :ivar vel_x: The x velocity of the ship.
    :ivar vel_y: The y velocity of the ship.
    """

    class DockingStatus(Enum):
        UNDOCKED = 0
        DOCKING = 1
        DOCKED = 2
        UNDOCKING = 3

    def __init__(
            self,
            player_id: int,
            ship_id: int,
            x: float,
            y: float,
            hp: int,
            vel_x: float,
            vel_y: float,
            docking_status: 'DockingStatus',
            planet: Union[int, None],
            progress: float,
            cooldown: float):
        super().__init__(x, y, constants.SHIP_RADIUS, hp, player_id, ship_id)
        self.docking_status = docking_status
        self.planet = planet if (
            docking_status is not Ship.DockingStatus.UNDOCKED) else None
        self.vel_x = vel_x
        self.vel_y = vel_y

        self._docking_progress = progress
        self._weapon_cooldown = cooldown

    def thrust(self, magnitude: int, angle: float) -> str:
        """
        Generate a command to accelerate this ship.

        :param magnitude: The speed through which to move the ship
        :param angle: The angle to move the ship in
        :return: The command string to be passed to the Halite engine.
        """
        # we want to round angle to nearest integer, but we want to round
        # magnitude down to prevent overshooting and unintended collisions
        return 't {} {} {}'.format(self.id, int(magnitude), round(angle))

    def dock(self, planet: 'Planet') -> str:
        """
        Generate a command to dock to a planet.

        :param planet: The planet object to dock to
        :return: The command string to be passed to the Halite engine.
        """
        return 'd {} {}'.format(self.id, planet.id)

    def undock(self) -> str:
        """
        Generate a command to undock from the current planet.

        :return: The command trying to be passed to the Halite engine.
        """
        return 'u {}'.format(self.id)

    def navigate(
            self,
            target: 'Entity',
            game_map: 'game_map.Map',
            speed: int,
            avoid_obstacles: bool = True,
            max_corrections: int = 18,
            angular_step: int = 5,
            ignore_ships: bool = False,
            ignore_planets: bool = False
            ) -> Union[str, None]:
        """
        Move a ship to a specific target position (Entity).

        It is recommended to place the position itself here, else navigate
        will crash into the target. If avoid_obstacles is set to True (default)
        will avoid obstacles on the way, with up to max_corrections
        corrections. Note that each correction accounts for angular_step
        degrees difference, meaning that the algorithm will naively try
        max_correction degrees before giving up (and returning None).
        The navigation will only consist of up to one command; call this
        method again in the next turn to continue navigating to the position.

        :param target: The entity to which you will navigate
        :param game_map: The map of the game, from which obstacles
            will be extracted
        :param speed: The (max) speed to navigate. If the obstacle is
            nearer, will adjust accordingly.
        :param avoid_obstacles: Whether to avoid the obstacles in
            the way (simple pathfinding).
        :param max_corrections: The maximum number of degrees to deviate
            per turn while trying to pathfind. If exceeded returns None.
        :param angular_step: The degree difference to deviate if the
            original destination has obstacles
        :param ignore_ships: Whether to ignore ships in calculations
            (this will make your movement faster, but more precarious)
        :param ignore_planets: Whether to ignore planets in calculations
            (useful if you want to crash onto planets)
        :return: The command trying to be passed to the Halite engine
            or None if movement is not possible within max_corrections degrees.
        """
        # Assumes a position, not planet
        # (as it would go to the center of the planet otherwise)
        if max_corrections <= 0:
            return None

        if angular_step > 0 and self.id % 2 != 0:
            angular_step *= -1

        distance = self.calculate_distance_between(target)
        angle = self.calculate_angle_between(target)

        if avoid_obstacles:
            obstacles = game_map.obstacles_between(
                self,
                target,
                ignore_ships=ignore_ships,
                ignore_planets=ignore_planets)

            if obstacles:
                new_target_dx = math.cos(math.radians(
                    angle + angular_step)) * distance
                new_target_dy = math.sin(math.radians(
                    angle + angular_step)) * distance

                new_target = Position(
                    self.x + new_target_dx, self.y + new_target_dy)

                return self.navigate(
                    new_target,
                    game_map,
                    speed,
                    True,
                    max_corrections - 1,
                    angular_step)

        speed = speed if (distance >= speed) else distance
        return self.thrust(speed, angle)

    def can_dock(self, planet: 'Planet') -> bool:
        """
        Determine whether a ship can dock to a planet

        :param planet: The planet wherein you wish to dock
        :return: True if can dock, False otherwise
        """
        if planet.is_full() or planet.someone_docking:
            return False

        if planet.is_owned() and planet.owner.id != self.owner.id:
            return False

        return (
            self.calculate_distance_between(planet)
            <= planet.radius + constants.DOCK_RADIUS + constants.SHIP_RADIUS)

    def _link(
            self,
            players: Dict[int, 'game_map.Player'],
            planets: Dict[int, 'Planet']
            ) -> None:
        """
        Link the owner and planet ivars to the Entities instead of ids.

        :param players: A dictionary of player objects keyed by id
        :param planets: A dictionary of planet objects keyed by id
        """
        self.owner = players.get(self.owner)
        self.planet = planets.get(self.planet)

    @staticmethod
    def _parse_single(
            player_id: int,
            tokens: List[str]
    ) -> Tuple[int, 'Ship', List[str]]:
        """
        Parse a single ship given tokenized input from the game environment.

        :param player_id: The id of the player who controls the ships
        :param tokens: The remaining tokens
        :return: The ship ID, ship object, and unused tokens.
        """
        (sid, x, y, hp, vel_x, vel_y,
         docked, docked_planet, progress, cooldown, *remainder) = tokens

        sid = int(sid)
        docked = Ship.DockingStatus(int(docked))

        ship = Ship(player_id,
                    sid,
                    float(x), float(y),
                    int(hp),
                    float(vel_x), float(vel_y),
                    docked, int(docked_planet),
                    int(progress), int(cooldown))

        return sid, ship, remainder

    @staticmethod
    def _parse(player_id: int, tokens: List[str]) -> Tuple[dict, List[str]]:
        """
        Parse ship data given a tokenized input.

        :param player_id: The id of the player who owns the ships
        :param tokens: The tokenized input
        :return: The dict of Players and unused tokens.
        """
        ships = {}
        num_ships, *remainder = tokens
        for _ in range(int(num_ships)):
            ship_id, ships[ship_id], remainder = Ship._parse_single(
                player_id, remainder)

        return ships, remainder


class Position(Entity):
    """
    A simple wrapper for a coordinate.

    Intended to be passed to some functions in place of a ship or planet.
    """

    def __init__(self, x, y):
        super().__init__(x, y, 0, None, None, None)

    def _link(self, players, planets):
        raise NotImplementedError("Position should not have link attributes.")
