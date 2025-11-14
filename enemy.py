"""
Enemy classes for the dungeon crawler.
"""

import random
from character import Character


class Enemy(Character):
    """Base enemy class."""

    def __init__(self, name, enemy_type, piece_type, x, y, level=1):
        # Initialize as a character
        super().__init__(name, enemy_type, piece_type, x, y)

        self.enemy_type = enemy_type
        self.xp_value = 50  # XP given when defeated
        self.level = level

        # Apply enemy-specific stats
        self._apply_enemy_stats()
        self._scale_to_level()

    def _apply_enemy_stats(self):
        """Apply enemy type-specific stats."""
        enemy_stats = {
            'goblin': {
                'hp': 60, 'attack': 12, 'defense': 4,
                'attack_type': 'melee', 'range': 1,
                'xp_value': 30
            },
            'goblin_archer': {
                'hp': 50, 'attack': 10, 'defense': 3,
                'attack_type': 'ranged', 'range': 4,
                'xp_value': 35
            },
            'goblin_shaman': {
                'hp': 45, 'attack': 5, 'magic_attack': 15, 'defense': 3,
                'attack_type': 'magic', 'range': 3,
                'xp_value': 40
            },
            'spider': {
                'hp': 40, 'attack': 8, 'defense': 2,
                'attack_type': 'melee', 'range': 1,
                'xp_value': 25
            },
            'giant_spider': {
                'hp': 80, 'attack': 15, 'defense': 5,
                'attack_type': 'melee', 'range': 2,
                'xp_value': 50,
                'abilities': ['web', 'poison']
            },
            'spider_queen': {
                'hp': 120, 'attack': 20, 'defense': 8,
                'attack_type': 'ranged', 'range': 3,
                'xp_value': 75,
                'abilities': ['web', 'poison', 'spawn']
            }
        }

        if self.enemy_type in enemy_stats:
            stats = enemy_stats[self.enemy_type]
            self.max_hp = stats['hp']
            self.hp = stats['hp']
            self.attack = stats['attack']
            self.magic_attack = stats.get('magic_attack', 0)
            self.defense = stats['defense']
            self.attack_type = stats['attack_type']
            self.range = stats['range']
            self.xp_value = stats['xp_value']
            self.special_abilities = stats.get('abilities', [])

    def _scale_to_level(self):
        """Scale enemy stats based on level."""
        if self.level > 1:
            scale = 1 + (self.level - 1) * 0.3
            self.max_hp = int(self.max_hp * scale)
            self.hp = self.max_hp
            self.attack = int(self.attack * scale)
            self.magic_attack = int(self.magic_attack * scale)
            self.defense = int(self.defense * scale)
            self.xp_value = int(self.xp_value * scale)

    def get_color(self):
        """Get enemy color based on type."""
        colors = {
            'goblin': (100, 150, 50),
            'goblin_archer': (120, 170, 60),
            'goblin_shaman': (80, 130, 100),
            'spider': (80, 40, 80),
            'giant_spider': (100, 50, 100),
            'spider_queen': (150, 50, 150),
            'boss': (200, 0, 0)
        }
        return colors.get(self.enemy_type, (150, 100, 100))

    def choose_action(self, party_positions, board_size, obstacles):
        """
        Simple AI to choose enemy action.
        Returns: ('move', (x, y)) or ('attack', target_index)
        """
        # Find closest party member
        closest_target = None
        min_distance = float('inf')

        for i, (px, py) in enumerate(party_positions):
            if px is None or py is None:  # Dead character
                continue
            distance = abs(self.x - px) + abs(self.y - py)
            if distance < min_distance:
                min_distance = distance
                closest_target = i

        if closest_target is None:
            return None

        target_x, target_y = party_positions[closest_target]

        # Check if target is in attack range
        attack_range = self.get_attack_range(board_size)
        if (target_x, target_y) in attack_range:
            return ('attack', closest_target)

        # Otherwise, try to move closer
        valid_moves, _ = self.get_valid_moves(board_size, obstacles)

        if not valid_moves:
            return None

        # Find move that gets closest to target
        best_move = None
        best_distance = min_distance

        for move_x, move_y in valid_moves:
            # Check if move is occupied
            if (move_x, move_y) in party_positions:
                continue

            distance = abs(move_x - target_x) + abs(move_y - target_y)
            if distance < best_distance:
                best_distance = distance
                best_move = (move_x, move_y)

        if best_move:
            return ('move', best_move)

        return None


class Boss(Enemy):
    """Boss enemy with enhanced stats and abilities."""

    def __init__(self, name, boss_type, x, y, dungeon_level=1):
        # Bosses are powerful enemies
        piece_type = 'queen'  # Bosses move like queens for maximum mobility

        super().__init__(name, boss_type, piece_type, x, y, level=dungeon_level + 2)

        self.is_boss = True
        self._apply_boss_stats()

    def _apply_boss_stats(self):
        """Apply boss-specific enhanced stats."""
        boss_stats = {
            'goblin_king': {
                'hp': 300, 'attack': 30, 'defense': 15,
                'attack_type': 'melee', 'range': 2,
                'xp_value': 500,
                'abilities': ['summon_minions', 'war_cry', 'enrage']
            },
            'arachne': {
                'hp': 250, 'attack': 25, 'defense': 12,
                'attack_type': 'ranged', 'range': 4,
                'xp_value': 500,
                'abilities': ['web_prison', 'poison_rain', 'spawn_spiders']
            },
            'lich': {
                'hp': 200, 'attack': 10, 'magic_attack': 40, 'defense': 10,
                'attack_type': 'magic', 'range': 5,
                'xp_value': 600,
                'abilities': ['life_drain', 'summon_undead', 'death_ray']
            },
            'dragon': {
                'hp': 400, 'attack': 40, 'defense': 20,
                'attack_type': 'ranged', 'range': 6,
                'xp_value': 800,
                'abilities': ['fire_breath', 'tail_sweep', 'fly']
            }
        }

        if self.enemy_type in boss_stats:
            stats = boss_stats[self.enemy_type]
            self.max_hp = stats['hp']
            self.hp = stats['hp']
            self.attack = stats['attack']
            self.magic_attack = stats.get('magic_attack', self.attack)
            self.defense = stats['defense']
            self.attack_type = stats['attack_type']
            self.range = stats['range']
            self.xp_value = stats['xp_value']
            self.special_abilities = stats['abilities']

        # Scale with dungeon level
        scale = 1 + (self.level - 1) * 0.25
        self.max_hp = int(self.max_hp * scale)
        self.hp = self.max_hp
        self.attack = int(self.attack * scale)
        self.magic_attack = int(self.magic_attack * scale)
        self.defense = int(self.defense * scale)
        self.xp_value = int(self.xp_value * scale)


def spawn_enemies(dungeon_level, num_enemies):
    """Spawn random enemies appropriate for dungeon level."""
    enemies = []

    # Most enemies are now spiders with king-style movement for puzzle gameplay
    enemy_pool = [
        ('spider', 'king', 0.6),  # Most common - basic spider
        ('giant_spider', 'king', 0.25),  # Tougher spider
        ('goblin', 'knight', 0.1),  # Occasional goblin for variety
        ('goblin_archer', 'rook', 0.05),
    ]

    # Add tougher enemies at higher levels
    if dungeon_level >= 3:
        enemy_pool.append(('spider_queen', 'king', 0.15))

    for i in range(num_enemies):
        # Weighted random selection
        rand = random.random()
        cumulative = 0
        selected_enemy = enemy_pool[0]

        for enemy_type, piece, weight in enemy_pool:
            cumulative += weight
            if rand <= cumulative:
                selected_enemy = (enemy_type, piece)
                break

        enemy_type, piece = selected_enemy
        name = f"{enemy_type.capitalize()}_{i+1}"
        level = dungeon_level + random.randint(-1, 1)
        level = max(1, level)

        enemy = Enemy(name, enemy_type, piece, 0, 0, level)
        enemies.append(enemy)

    return enemies


def spawn_boss(dungeon_level):
    """Spawn a boss for the dungeon."""
    boss_types = ['goblin_king', 'arachne', 'lich', 'dragon']
    boss_type = random.choice(boss_types[:min(len(boss_types), dungeon_level)])

    name = boss_type.replace('_', ' ').title()
    boss = Boss(name, boss_type, 0, 0, dungeon_level)

    return boss
