"""
Procedural dungeon generation system.
"""

import random


class Tile:
    """Represents a single dungeon tile."""
    FLOOR = 0
    WALL = 1
    DOOR = 2
    LOCKED_DOOR = 3
    LOOT = 4
    POWERUP = 5
    STAIRS_DOWN = 6
    BOSS_MARKER = 7

    def __init__(self, tile_type=FLOOR):
        self.type = tile_type
        self.occupied_by = None  # Character or enemy
        self.required_movement = None  # For restricted areas


class Room:
    """Represents a room in the dungeon."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.connections = []
        self.is_boss_room = False
        self.required_movement = None  # Restrict access to certain piece types

    def intersects(self, other):
        """Check if this room intersects with another room."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def get_tiles(self):
        """Get all tile positions in this room."""
        tiles = []
        for x in range(self.x, self.x + self.width):
            for y in range(self.y, self.y + self.height):
                tiles.append((x, y))
        return tiles


class Dungeon:
    """Procedurally generated dungeon."""

    def __init__(self, width=40, height=30, dungeon_level=1):
        self.width = width
        self.height = height
        self.dungeon_level = dungeon_level

        # Initialize dungeon with walls
        self.tiles = [[Tile(Tile.WALL) for _ in range(width)] for _ in range(height)]

        self.rooms = []
        self.corridors = []
        self.start_room = None
        self.boss_room = None

        # Generate dungeon
        self._generate()

    def _generate(self):
        """Generate the dungeon layout."""
        # Generate rooms
        num_rooms = 8 + self.dungeon_level * 2
        self._generate_rooms(num_rooms)

        # Connect rooms with corridors
        self._connect_rooms()

        # Add doors
        self._add_doors()

        # Designate boss room (furthest from start)
        self._designate_boss_room()

        # Add restricted areas
        self._add_restricted_areas()

        # Add loot and powerups
        self._add_loot()

    def _generate_rooms(self, num_rooms):
        """Generate random rooms that don't overlap."""
        attempts = 0
        max_attempts = num_rooms * 10

        while len(self.rooms) < num_rooms and attempts < max_attempts:
            # Random room size
            width = random.randint(4, 10)
            height = random.randint(4, 8)

            # Random position (leave border for walls)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)

            new_room = Room(x, y, width, height)

            # Check for overlaps
            overlap = False
            for room in self.rooms:
                if new_room.intersects(room):
                    overlap = True
                    break

            if not overlap:
                self._carve_room(new_room)
                self.rooms.append(new_room)

                if self.start_room is None:
                    self.start_room = new_room

            attempts += 1

    def _carve_room(self, room):
        """Carve out a room in the dungeon."""
        for x in range(room.x, room.x + room.width):
            for y in range(room.y, room.y + room.height):
                self.tiles[y][x] = Tile(Tile.FLOOR)

    def _connect_rooms(self):
        """Connect rooms with corridors."""
        # Connect each room to the nearest unconnected room
        for i, room in enumerate(self.rooms):
            if i == 0:
                continue

            # Find nearest room
            nearest = self.rooms[i - 1]
            min_dist = self._room_distance(room, nearest)

            for other in self.rooms[:i]:
                dist = self._room_distance(room, other)
                if dist < min_dist:
                    min_dist = dist
                    nearest = other

            # Create corridor
            self._create_corridor(room, nearest)

        # Add some extra connections for more interesting layout
        num_extra = len(self.rooms) // 3
        for _ in range(num_extra):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            if room1 != room2:
                self._create_corridor(room1, room2)

    def _room_distance(self, room1, room2):
        """Calculate distance between two rooms."""
        dx = room1.center_x - room2.center_x
        dy = room1.center_y - room2.center_y
        return abs(dx) + abs(dy)

    def _create_corridor(self, room1, room2):
        """Create a corridor between two rooms."""
        x1, y1 = room1.center_x, room1.center_y
        x2, y2 = room2.center_x, room2.center_y

        # L-shaped corridor
        if random.random() < 0.5:
            # Horizontal then vertical
            self._carve_h_corridor(x1, x2, y1)
            self._carve_v_corridor(y1, y2, x2)
        else:
            # Vertical then horizontal
            self._carve_v_corridor(y1, y2, x1)
            self._carve_h_corridor(x1, x2, y2)

        room1.connections.append(room2)
        room2.connections.append(room1)

    def _carve_h_corridor(self, x1, x2, y):
        """Carve horizontal corridor."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = Tile(Tile.FLOOR)

    def _carve_v_corridor(self, y1, y2, x):
        """Carve vertical corridor."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = Tile(Tile.FLOOR)

    def _add_doors(self):
        """Add doors at room entrances."""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.tiles[y][x].type == Tile.FLOOR:
                    # Check if this is a doorway (floor with walls on opposite sides)
                    # Horizontal door
                    if (self.tiles[y][x-1].type == Tile.WALL and
                        self.tiles[y][x+1].type == Tile.WALL and
                        self.tiles[y-1][x].type == Tile.FLOOR and
                        self.tiles[y+1][x].type == Tile.FLOOR):
                        if random.random() < 0.3:  # 30% chance of door
                            self.tiles[y][x] = Tile(Tile.DOOR)
                    # Vertical door
                    elif (self.tiles[y-1][x].type == Tile.WALL and
                          self.tiles[y+1][x].type == Tile.WALL and
                          self.tiles[y][x-1].type == Tile.FLOOR and
                          self.tiles[y][x+1].type == Tile.FLOOR):
                        if random.random() < 0.3:
                            self.tiles[y][x] = Tile(Tile.DOOR)

    def _designate_boss_room(self):
        """Designate the furthest room from start as boss room."""
        if not self.rooms or not self.start_room:
            return

        max_dist = 0
        boss_room = self.rooms[-1]

        for room in self.rooms:
            dist = self._room_distance(self.start_room, room)
            if dist > max_dist:
                max_dist = dist
                boss_room = room

        boss_room.is_boss_room = True
        self.boss_room = boss_room

        # Mark boss room
        self.tiles[boss_room.center_y][boss_room.center_x].type = Tile.BOSS_MARKER

    def _add_restricted_areas(self):
        """Add areas that require specific movement types to access."""
        # Select some side rooms to restrict
        num_restricted = min(3, len(self.rooms) // 3)
        movement_types = ['knight', 'bishop', 'rook']

        candidates = [r for r in self.rooms
                     if r != self.start_room and r != self.boss_room]

        for i in range(min(num_restricted, len(candidates))):
            room = random.choice(candidates)
            candidates.remove(room)

            movement_type = movement_types[i % len(movement_types)]
            room.required_movement = movement_type

            # Mark tiles in room
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    self.tiles[y][x].required_movement = movement_type

    def _add_loot(self):
        """Add loot and powerups to rooms."""
        for room in self.rooms:
            if room == self.start_room:
                continue

            # Add loot
            if random.random() < 0.5:
                loot_x = room.x + random.randint(1, room.width - 2)
                loot_y = room.y + random.randint(1, room.height - 2)
                if self.tiles[loot_y][loot_x].type == Tile.FLOOR:
                    self.tiles[loot_y][loot_x].type = Tile.LOOT

            # Add powerup
            if random.random() < 0.3:
                powerup_x = room.x + random.randint(1, room.width - 2)
                powerup_y = room.y + random.randint(1, room.height - 2)
                if self.tiles[powerup_y][powerup_x].type == Tile.FLOOR:
                    self.tiles[powerup_y][powerup_x].type = Tile.POWERUP

    def get_start_positions(self, num_positions):
        """Get starting positions in the start room."""
        if not self.start_room:
            return [(0, 0)] * num_positions

        positions = []
        room = self.start_room

        for i in range(num_positions):
            attempts = 0
            while attempts < 100:
                x = room.x + random.randint(1, room.width - 2)
                y = room.y + random.randint(1, room.height - 2)

                if (x, y) not in positions and self.tiles[y][x].type == Tile.FLOOR:
                    positions.append((x, y))
                    break
                attempts += 1

        # Fill remaining with center positions if needed
        while len(positions) < num_positions:
            positions.append((room.center_x, room.center_y))

        return positions

    def get_enemy_spawn_positions(self, num_enemies):
        """Get spawn positions for enemies (not in start room)."""
        positions = []
        valid_rooms = [r for r in self.rooms if r != self.start_room and r != self.boss_room]

        for _ in range(num_enemies):
            if not valid_rooms:
                break

            room = random.choice(valid_rooms)
            attempts = 0

            while attempts < 50:
                x = room.x + random.randint(1, room.width - 2)
                y = room.y + random.randint(1, room.height - 2)

                if (x, y) not in positions and self.tiles[y][x].type == Tile.FLOOR:
                    positions.append((x, y))
                    break
                attempts += 1

        return positions

    def get_boss_position(self):
        """Get position for boss spawn."""
        if self.boss_room:
            return (self.boss_room.center_x, self.boss_room.center_y)
        return (self.width // 2, self.height // 2)

    def is_walkable(self, x, y):
        """Check if a position is walkable."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[y][x].type not in [Tile.WALL]

    def get_tile(self, x, y):
        """Get tile at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
