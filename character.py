"""
Character classes combining RPG roles with chess piece movements.
"""

import random
from chess_moves import ChessMove


class Character:
    """Base character class."""

    def __init__(self, name, char_class, piece_type, x, y):
        self.name = name
        self.char_class = char_class  # RPG class (wizard, thief, healer, etc.)
        self.piece_type = piece_type  # Chess piece type
        self.x = x
        self.y = y

        # Base stats
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # Combat stats (scaled by class)
        self.max_hp = 100
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.magic_attack = 10
        self.range = 1

        # Special properties
        self.is_alive = True
        self.is_invisible = False
        self.attack_type = 'melee'  # 'melee', 'ranged', 'magic'
        self.special_abilities = []

        # Movement
        self.has_moved = False
        self.is_first_move = True
        self.has_acted = False  # For turn-based system

        # Apply class-specific stats
        self._apply_class_stats()

    def _apply_class_stats(self):
        """Apply class-specific stat modifiers."""
        class_stats = {
            'wizard': {
                'hp': 80, 'attack': 5, 'magic_attack': 25, 'defense': 3,
                'attack_type': 'magic', 'range': 5,
                'abilities': ['fireball', 'teleport']
            },
            'warrior': {
                'hp': 150, 'attack': 20, 'magic_attack': 0, 'defense': 15,
                'attack_type': 'melee', 'range': 1,
                'abilities': ['shield_bash', 'war_cry']
            },
            'thief': {
                'hp': 90, 'attack': 15, 'magic_attack': 0, 'defense': 8,
                'attack_type': 'melee', 'range': 1,
                'abilities': ['backstab', 'dodge']
            },
            'healer': {
                'hp': 100, 'attack': 5, 'magic_attack': 15, 'defense': 5,
                'attack_type': 'magic', 'range': 4,
                'abilities': ['heal', 'shield']
            },
            'shadow_assassin': {
                'hp': 60, 'attack': 25, 'magic_attack': 0, 'defense': 3,
                'attack_type': 'melee', 'range': 1, 'invisible': True,
                'abilities': ['stealth', 'critical_strike']
            },
            'paladin': {
                'hp': 130, 'attack': 15, 'magic_attack': 10, 'defense': 12,
                'attack_type': 'melee', 'range': 2,
                'abilities': ['holy_smite', 'lay_on_hands']
            },
            'ranger': {
                'hp': 100, 'attack': 18, 'magic_attack': 5, 'defense': 8,
                'attack_type': 'ranged', 'range': 6,
                'abilities': ['multi_shot', 'trap']
            }
        }

        if self.char_class in class_stats:
            stats = class_stats[self.char_class]
            self.max_hp = stats['hp']
            self.hp = stats['hp']
            self.attack = stats['attack']
            self.magic_attack = stats['magic_attack']
            self.defense = stats['defense']
            self.attack_type = stats['attack_type']
            self.range = stats['range']
            self.special_abilities = stats['abilities']
            self.is_invisible = stats.get('invisible', False)

    def get_valid_moves(self, board_size, obstacles):
        """Get all valid moves for this character."""
        result = ChessMove.get_moves_for_piece(
            self.piece_type, self.x, self.y, board_size, obstacles,
            is_first_move=self.is_first_move
        )

        # Handle pawn returning tuple
        if self.piece_type == 'pawn':
            moves, attacks = result
            return moves, attacks
        return result, []

    def get_attack_range(self, board_size):
        """Get all positions this character can attack."""
        if self.attack_type == 'melee':
            # Melee uses movement range
            obstacles = set()  # No obstacles for attack range calculation
            moves = ChessMove.get_moves_for_piece(
                self.piece_type, self.x, self.y, board_size, obstacles
            )
            if isinstance(moves, tuple):
                return moves[1] if len(moves) > 1 else moves[0]
            return moves
        else:
            # Ranged/magic can attack within range in any direction
            attack_positions = []
            for dx in range(-self.range, self.range + 1):
                for dy in range(-self.range, self.range + 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < board_size and 0 <= ny < board_size:
                        distance = abs(dx) + abs(dy)
                        if distance <= self.range:
                            attack_positions.append((nx, ny))
            return attack_positions

    def move(self, new_x, new_y):
        """Move character to new position."""
        self.x = new_x
        self.y = new_y
        self.has_moved = True
        self.is_first_move = False

    def swap_piece_type(self, other_character):
        """Swap chess piece movement type with another character."""
        self.piece_type, other_character.piece_type = other_character.piece_type, self.piece_type

    def calculate_damage(self):
        """Calculate damage output based on attack type and level."""
        base_damage = self.attack if self.attack_type != 'magic' else self.magic_attack
        # Add some randomness
        damage = base_damage * (0.8 + random.random() * 0.4)
        # Scale with level
        damage *= (1 + (self.level - 1) * 0.2)
        return int(damage)

    def take_damage(self, damage):
        """Take damage reduced by defense."""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage

    def heal(self, amount):
        """Heal this character."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def gain_xp(self, amount):
        """Gain XP and level up if threshold reached."""
        self.xp += amount
        leveled_up = False

        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            self._level_up()
            leveled_up = True

        return leveled_up

    def _level_up(self):
        """Increase stats on level up."""
        # Increase stats based on class
        hp_gain = 10 + random.randint(-2, 5)
        self.max_hp += hp_gain
        self.hp = self.max_hp

        if self.attack_type in ['melee', 'ranged']:
            self.attack += random.randint(2, 4)
        else:
            self.magic_attack += random.randint(2, 4)

        self.defense += random.randint(1, 2)

    def reset_turn(self):
        """Reset turn-based flags."""
        self.has_moved = False
        self.has_acted = False

    def get_color(self):
        """Get character color based on class."""
        colors = {
            'wizard': (100, 100, 255),      # Blue
            'warrior': (200, 50, 50),       # Red
            'thief': (150, 150, 50),        # Yellow-ish
            'healer': (100, 255, 100),      # Green
            'shadow_assassin': (128, 0, 128),  # Purple
            'paladin': (255, 215, 0),       # Gold
            'ranger': (139, 69, 19),        # Brown
        }
        return colors.get(self.char_class, (150, 150, 150))

    def __repr__(self):
        return f"{self.name} ({self.char_class}/{self.piece_type}) Lv{self.level} HP:{self.hp}/{self.max_hp}"


def create_default_party():
    """Create a default party with varied characters."""
    party = [
        Character("Gandor", "wizard", "bishop", 0, 0),
        Character("Brutus", "warrior", "rook", 0, 0),
        Character("Swift", "thief", "knight", 0, 0),
        Character("Aria", "healer", "queen", 0, 0),
        Character("Shadow", "shadow_assassin", "pawn", 0, 0),
        Character("Valor", "paladin", "king", 0, 0),
    ]
    return party
