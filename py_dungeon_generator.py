import enum
import random
import math

class DivideDirection(enum.Enum):
    DIVIDE_X = 1
    DIVIDE_Y = 2

class TileTypes(enum.Enum):
    EMPTY = "empty"
    FLOOR = "floor"
    PATH = "path"
    WALL = "wall"
    DOOR = "door"

class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Path:
    def __init__(self):
        self.path = []

    def connect_points(self, x1: int, y1: int, x2: int, y2: int) -> list:
        """Connect points using L or Z shaped paths"""
        self.path = [(x1, y1)] # clear any existing path

        delta_x = x2 - x1
        delta_y = y2 - y1

        distance_x = abs(delta_x)
        distance_y = abs(delta_y)

        x_incr = 0 if distance_x == 0 else delta_x / distance_x
        y_incr = 0 if distance_y == 0 else delta_y / distance_y

        x = x1
        y = y1

        force_decision = 0
        if distance_x == distance_y:
            force_decision = random.randint(1, 2) # if the x any y distances are equal, randomly pick a direction

        if force_decision == 1 or distance_x > distance_y:
            bend_point = x1 + (random.randint(0, distance_x) * x_incr)

            while True:
                if x == bend_point:
                    while True:
                        y += y_incr
                        self.path.append((x, y))

                        if y == y2:
                            break

                x += x_incr
                self.path.append((x, y))

                if x == x2:
                    break

        elif force_decision == 2 or distance_x < distance_y:
            bend_point = y1 + (random.randint(0, distance_y) * y_incr)

            while True:
                if y == bend_point:
                    while True:
                        x += x_incr
                        self.path.append((x, y))

                        if x == x2:
                            break

                y += y_incr
                self.path.append((x, y))

                if y == y2:
                    break

        return self.path

class MapPartition:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = (None, None)
        self.room = None
        self.path = None
        self.parent = None

    def create_children(self, divide_direction: DivideDirection, divide_range: float = 0.7) -> tuple:
        """Generate children partitions by splitting the parent along a random axis"""

        modification_factor = ((2 * random.random()) - 1) * divide_range

        if divide_direction is DivideDirection.DIVIDE_X:
            divide_x = math.trunc((self.width / 2) + ((self.width / 2) * modification_factor))

            new_partition_1 = None
            new_partition_2 = None

            if divide_x > 0 and divide_x < self.width:
                new_partition_1 = MapPartition(self.x, self.y, divide_x, self.height)
                new_partition_1.parent = self

                new_partition_2 = MapPartition(self.x + divide_x, self.y, self.width - divide_x, self.height)
                new_partition_2.parent = self

            self.children = (new_partition_1, new_partition_2)

        elif divide_direction is DivideDirection.DIVIDE_Y:
            divide_y = math.trunc((self.height / 2) + ((self.height / 2) * modification_factor))

            new_partition_1 = None
            new_partition_2 = None

            if divide_y > 0 and divide_y < self.height:
                new_partition_1 = MapPartition(self.x, self.y, self.width, divide_y)
                new_partition_1.parent = self

                new_partition_2 = MapPartition(self.x, self.y + divide_y, self.width, self.height - divide_y)
                new_partition_2.parent = self

            self.children = (new_partition_1, new_partition_2)

        return self.children

    def create_room(self, min_room_size: int = 2, min_cells_from_side: int = 1) -> Room:
        """Generates a room that fits within the partition"""
        max_room_width = self.width - (2 * min_cells_from_side)
        max_room_height = self.height - (2 * min_cells_from_side)

        if max_room_width < min_room_size or max_room_height < min_room_size:
            return # if the partition is too small to have a room, don't create one

        room_width = random.randint(min_room_size, max_room_width)
        room_height = random.randint(min_room_size, max_room_height)

        room_x = self.x + random.randint(min_cells_from_side, self.width - room_width - 1)
        room_y = self.y + random.randint(min_cells_from_side, self.height - room_height - 1)

        self.room = Room(room_x, room_y, room_width, room_height)

        return self.room

    def create_key_point(self) -> tuple:
        """Generates a point that can be used to create a path between self and sibling"""
        if self.room is not None:
            key_point_x = self.room.x + random.randint(0, self.room.width - 1)
            key_point_y = self.room.y + random.randint(0, self.room.height - 1)

        elif self.path is not None:
            path_length = len(self.path.path)

            path_point = random.randint(0, path_length - 1)
            key_point_x, key_point_y = self.path.path[path_point]

        else:
            key_point_x = self.x + random.randint(0, self.width - 1)
            key_point_y = self.y + random.randint(0, self.height - 1)

        self.key_point = (key_point_x, key_point_y)

        return self.key_point

    def create_path_between_children(self) -> Path:
        """Generates a pathway between the key points of this partition's children"""
        child_0 = self.children[0]
        child_1 = self.children[1]

        if child_0 is not None and child_1 is not None:
            if child_0.key_point is None:
                child_0.create_key_point()

            if child_1.key_point is None:
                child_1.create_key_point()

            self.path = Path()
            x1, y1 = child_0.key_point
            x2, y2 = child_1.key_point

            self.path.connect_points(x1, y1, x2, y2)

            return self.path




class DungeonGenerator:
    def __init__(self):
        self.tile_dict = None

    def __write_room_to_map(self, map: list, map_width: int, room: Room) -> list:
        """Takes a Room and puts it into the dungeon map"""
        if room is None:
            return map

        map_height = math.trunc(len(map) / map_width)

        for y in range(room.height):
            for x in range(room.width):
                map_x = x + room.x
                map_y = y + room.y

                if (map_x < 0 or map_x >= map_width):
                    continue

                if (map_y < 0 or map_y >= map_height):
                    continue

                map_i = self.index_from_coordinates(map_x, map_y, map_width)
                map[map_i] = self.tile_dict.get(TileTypes.FLOOR)

    def __write_path_to_map(self, map: list, map_width: int, path: Path) -> list:
        """Takes a Path and puts it into the dungeon map"""
        if path is None:
            return map

        map_height = math.trunc(len(map) / map_width)

        for x, y in path.path:
            if x < 0 or x >= map_width:
                continue

            if y < 0 or y >= map_height:
                continue

            map_i = self.index_from_coordinates(x, y, map_width)

            map[map_i] = self.tile_dict.get(TileTypes.PATH)

    def __write_partitions_to_map(self, map: list, map_width: int, partition: MapPartition) -> list:
        """Traverses all partitions and puts partition features into the dungeon map"""
        self.__recurse_partition_to_map(map, map_width, partition)

    def __recurse_partition_to_map(self, map: list, map_width: int, partition: MapPartition) -> MapPartition:
        """Recursively writes partition features to dungeon map"""
        if partition.room is not None:
            self.__write_room_to_map(map, map_width, partition.room)

        if partition.path is not None:
            self.__write_path_to_map(map, map_width, partition.path)

        if partition.children[0] is not None:
            self.__recurse_partition_to_map(map, map_width, partition.children[0])

        if partition.children[1] is not None:
            self.__recurse_partition_to_map(map, map_width, partition.children[1])


    def __create_partitions(self, x: int, y: int, width: int, height: int, divisions: int) -> MapPartition:
        """Generates an initial MapPartition and recursively creates children to the depth specified"""
        partition = MapPartition(x, y, width, height)

        self.__recurse_partitions(partition, divisions)

        return partition

    def __recurse_partitions(self, partition: MapPartition, divisions: int) -> None:
        """Recursively generates children MapPartitions to the depth specified"""
        if divisions == 0:
            partition.create_room() # create a room in each of the final level partitions
            partition.create_key_point() # create a key point in each room to ensure accessibility
            return

        aspect_ratio = partition.width / partition.height

        divide_direction = DivideDirection(1) if aspect_ratio > 1 else DivideDirection(2)

        if aspect_ratio == 1:
            divide_direction = DivideDirection(random.randint(1, 2))

        partition_1, partition_2 = partition.create_children(divide_direction)

        if partition_1 is not None:
            self.__recurse_partitions(partition_1, divisions - 1)

        if partition_2 is not None:
            self.__recurse_partitions(partition_2, divisions - 1)

        partition.create_path_between_children()
        partition.create_key_point()

    def generate_default_tile_dict(self) -> dict:
        """Creates a dictionary for translating between tile types and map data"""
        self.tile_dict = {
            TileTypes.EMPTY: 0,
            TileTypes.FLOOR: 1,
            TileTypes.PATH: 2,
            TileTypes.WALL: 3,
            TileTypes.DOOR: 4
        }

        return self.tile_dict

    def generate_map(self, width: int, height: int, divisions: int = 4) -> list:
        """Procedurally genearates a map"""
        if (self.tile_dict is None):
            self.generate_default_tile_dict()

        generated_map = [self.tile_dict.get(TileTypes.EMPTY)]*(width * height)
        map_partitions = self.__create_partitions(0, 0, width, height, divisions)

        self.__write_partitions_to_map(generated_map, width, map_partitions)

        return (generated_map, map_partitions)

    def index_from_coordinates(self, x: int, y: int, width: int) -> int:
        return int(x + math.trunc(y * width))

    def coordinates_from_index(self, i: int, width: int) -> tuple:
        return (i % width, math.trunc(i / width))

