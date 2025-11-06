"""
Main game logic and rendering.
"""

import pygame
import sys
from character import Character, create_default_party
from enemy import Enemy, spawn_enemies, spawn_boss
from dungeon import Dungeon, Tile
from chess_moves import ChessMove


class Game:
    """Main game class."""

    # Colors
    COLOR_BG = (20, 20, 30)
    COLOR_FLOOR_LIGHT = (80, 80, 85)
    COLOR_FLOOR_DARK = (60, 60, 65)
    COLOR_WALL = (40, 40, 45)
    COLOR_DOOR = (139, 69, 19)
    COLOR_LOOT = (255, 215, 0)
    COLOR_POWERUP = (255, 0, 255)
    COLOR_BOSS_MARKER = (200, 0, 0)
    COLOR_HIGHLIGHT = (100, 150, 255)
    COLOR_ATTACK_RANGE = (255, 100, 100)
    COLOR_SWAP_RANGE = (100, 255, 100)
    COLOR_TEXT = (255, 255, 255)
    COLOR_UI_BG = (30, 30, 40)

    def __init__(self, screen_width=1400, screen_height=900):
        pygame.init()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Chess Dungeon Crawler")

        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)

        # Game state
        self.dungeon_level = 1
        self.dungeon = None
        self.party = []
        self.enemies = []
        self.boss = None

        # Rendering
        self.tile_size = 20
        self.camera_x = 0
        self.camera_y = 0

        # UI Areas
        self.ui_panel_width = 350
        self.game_area_width = screen_width - self.ui_panel_width

        # Selection and interaction
        self.selected_character = None
        self.valid_moves = []
        self.valid_attacks = []
        self.hover_tile = None

        # Turn management
        self.player_turn = True
        self.turn_number = 1

        # Messages
        self.messages = []
        self.max_messages = 8

        # Game state
        self.game_state = 'playing'  # 'playing', 'victory', 'defeat', 'boss_fight'

        # Initialize game
        self._start_new_dungeon()

    def _start_new_dungeon(self):
        """Start a new dungeon level."""
        self.add_message(f"=== Entering Dungeon Level {self.dungeon_level} ===")

        # Generate dungeon
        self.dungeon = Dungeon(width=50, height=40, dungeon_level=self.dungeon_level)

        # Create or reset party
        if not self.party:
            self.party = create_default_party()

        # Position party
        start_positions = self.dungeon.get_start_positions(len(self.party))
        for char, (x, y) in zip(self.party, start_positions):
            char.x = x
            char.y = y
            char.reset_turn()

        # Spawn enemies
        num_enemies = 5 + self.dungeon_level * 2
        self.enemies = spawn_enemies(self.dungeon_level, num_enemies)

        enemy_positions = self.dungeon.get_enemy_spawn_positions(len(self.enemies))
        for enemy, (x, y) in zip(self.enemies, enemy_positions):
            enemy.x = x
            enemy.y = y

        # Spawn boss
        self.boss = spawn_boss(self.dungeon_level)
        boss_x, boss_y = self.dungeon.get_boss_position()
        self.boss.x = boss_x
        self.boss.y = boss_y

        # Reset game state
        self.selected_character = None
        self.valid_moves = []
        self.valid_attacks = []
        self.player_turn = True
        self.game_state = 'playing'

        # Center camera on party
        self._center_camera_on_party()

    def _center_camera_on_party(self):
        """Center camera on party position."""
        if self.party:
            avg_x = sum(c.x for c in self.party if c.is_alive) / max(1, sum(1 for c in self.party if c.is_alive))
            avg_y = sum(c.y for c in self.party if c.is_alive) / max(1, sum(1 for c in self.party if c.is_alive))

            self.camera_x = int(avg_x * self.tile_size - self.game_area_width // 2)
            self.camera_y = int(avg_y * self.tile_size - self.screen_height // 2)

    def add_message(self, message):
        """Add a message to the message log."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        print(message)  # Also print to console

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.player_turn:
                        self._end_player_turn()
                elif event.key == pygame.K_TAB:
                    self._cycle_selection()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                    idx = event.key - pygame.K_1
                    if idx < len(self.party) and self.party[idx].is_alive:
                        self._select_character(self.party[idx])

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

    def _handle_click(self, pos):
        """Handle mouse click."""
        if not self.player_turn:
            return

        mouse_x, mouse_y = pos

        # Check if click is in game area
        if mouse_x >= self.game_area_width:
            return

        # Convert to tile coordinates
        tile_x = (mouse_x + self.camera_x) // self.tile_size
        tile_y = (mouse_y + self.camera_y) // self.tile_size

        # Check if clicking on a character
        clicked_char = self._get_character_at(tile_x, tile_y)
        if clicked_char and clicked_char.is_alive:
            if clicked_char in self.party:
                self._select_character(clicked_char)
                return

        # Check if clicking on valid move
        if self.selected_character and (tile_x, tile_y) in self.valid_moves:
            self._move_character(self.selected_character, tile_x, tile_y)
            return

        # Check if clicking on valid attack
        if self.selected_character and (tile_x, tile_y) in self.valid_attacks:
            target = self._get_enemy_at(tile_x, tile_y)
            if target:
                self._attack_enemy(self.selected_character, target)
                return

        # Check if clicking on ally for swap
        if self.selected_character:
            ally = self._get_character_at(tile_x, tile_y)
            if ally and ally in self.party and ally != self.selected_character and ally.is_alive:
                self._swap_abilities(self.selected_character, ally)
                return

    def _handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effects."""
        mouse_x, mouse_y = pos

        if mouse_x >= self.game_area_width:
            self.hover_tile = None
            return

        tile_x = (mouse_x + self.camera_x) // self.tile_size
        tile_y = (mouse_y + self.camera_y) // self.tile_size

        self.hover_tile = (tile_x, tile_y)

    def _select_character(self, character):
        """Select a character and show valid moves."""
        self.selected_character = character

        # Get valid moves
        obstacles = self._get_obstacles()
        result = character.get_valid_moves(self.dungeon.width, obstacles)

        if isinstance(result, tuple):
            moves, attacks = result
            self.valid_moves = [m for m in moves if self.dungeon.is_walkable(m[0], m[1])]
            # For pawn, attacks are separate
            pawn_attacks = [a for a in attacks if self.dungeon.is_walkable(a[0], a[1])]
        else:
            self.valid_moves = [m for m in result if self.dungeon.is_walkable(m[0], m[1])]
            pawn_attacks = []

        # Get valid attacks
        attack_range = character.get_attack_range(self.dungeon.width)
        self.valid_attacks = []

        for pos in attack_range:
            if self._get_enemy_at(pos[0], pos[1]):
                self.valid_attacks.append(pos)

        # Add pawn attacks if enemy present
        for pos in pawn_attacks:
            if self._get_enemy_at(pos[0], pos[1]):
                self.valid_attacks.append(pos)

        self.add_message(f"Selected {character.name} ({character.piece_type})")

    def _cycle_selection(self):
        """Cycle through party members."""
        if not self.party:
            return

        living_party = [c for c in self.party if c.is_alive]
        if not living_party:
            return

        if self.selected_character is None or self.selected_character not in living_party:
            self._select_character(living_party[0])
        else:
            idx = living_party.index(self.selected_character)
            next_idx = (idx + 1) % len(living_party)
            self._select_character(living_party[next_idx])

    def _move_character(self, character, x, y):
        """Move character to new position."""
        old_x, old_y = character.x, character.y
        character.move(x, y)

        # Check for loot/powerups
        tile = self.dungeon.get_tile(x, y)
        if tile:
            if tile.type == Tile.LOOT:
                self._collect_loot(character)
                tile.type = Tile.FLOOR
            elif tile.type == Tile.POWERUP:
                self._collect_powerup(character)
                tile.type = Tile.FLOOR

        self.add_message(f"{character.name} moved to ({x}, {y})")

        # Deselect after move
        self.selected_character = None
        self.valid_moves = []
        self.valid_attacks = []

    def _attack_enemy(self, attacker, target):
        """Attack an enemy."""
        damage = attacker.calculate_damage()
        actual_damage = target.take_damage(damage)

        self.add_message(f"{attacker.name} attacks {target.name} for {actual_damage} damage!")

        if not target.is_alive:
            self.add_message(f"{target.name} defeated!")
            xp_gained = target.xp_value
            attacker.gain_xp(xp_gained)
            self.add_message(f"{attacker.name} gained {xp_gained} XP")

            # Remove from enemies list
            if target in self.enemies:
                self.enemies.remove(target)
            elif target == self.boss:
                self._boss_defeated()

        # Deselect after attack
        self.selected_character = None
        self.valid_moves = []
        self.valid_attacks = []

    def _swap_abilities(self, char1, char2):
        """Swap chess piece abilities between two characters."""
        old_type1 = char1.piece_type
        old_type2 = char2.piece_type

        char1.swap_piece_type(char2)

        self.add_message(f"{char1.name} and {char2.name} swapped movement types!")
        self.add_message(f"{char1.name}: {old_type1} -> {char1.piece_type}")
        self.add_message(f"{char2.name}: {old_type2} -> {char2.piece_type}")

        # Refresh selection
        self._select_character(char1)

    def _collect_loot(self, character):
        """Collect loot."""
        gold = (10 + self.dungeon_level * 5) * (1 + character.level * 0.1)
        self.add_message(f"{character.name} found {int(gold)} gold!")

    def _collect_powerup(self, character):
        """Collect powerup."""
        import random
        powerup_type = random.choice(['hp', 'attack', 'defense'])

        if powerup_type == 'hp':
            heal_amount = character.max_hp // 2
            actual_heal = character.heal(heal_amount)
            self.add_message(f"{character.name} found a health potion! +{actual_heal} HP")
        elif powerup_type == 'attack':
            character.attack += 2
            character.magic_attack += 2
            self.add_message(f"{character.name} found a power gem! +2 ATK")
        elif powerup_type == 'defense':
            character.defense += 2
            self.add_message(f"{character.name} found armor! +2 DEF")

    def _end_player_turn(self):
        """End player turn and start enemy turn."""
        self.player_turn = False
        self.selected_character = None
        self.valid_moves = []
        self.valid_attacks = []

        self.add_message("--- Enemy Turn ---")

        # Reset character turn flags
        for char in self.party:
            char.reset_turn()

    def _get_obstacles(self):
        """Get all obstacle positions (walls, characters, enemies)."""
        obstacles = set()

        # Add walls
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if not self.dungeon.is_walkable(x, y):
                    obstacles.add((x, y))

        # Add characters
        for char in self.party:
            if char.is_alive:
                obstacles.add((char.x, char.y))

        # Add enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                obstacles.add((enemy.x, enemy.y))

        if self.boss and self.boss.is_alive:
            obstacles.add((self.boss.x, self.boss.y))

        return obstacles

    def _get_character_at(self, x, y):
        """Get character at position."""
        for char in self.party:
            if char.is_alive and char.x == x and char.y == y:
                return char
        return None

    def _get_enemy_at(self, x, y):
        """Get enemy at position."""
        for enemy in self.enemies:
            if enemy.is_alive and enemy.x == x and enemy.y == y:
                return enemy
        if self.boss and self.boss.is_alive and self.boss.x == x and self.boss.y == y:
            return self.boss
        return None

    def _boss_defeated(self):
        """Handle boss defeat."""
        self.add_message("=== BOSS DEFEATED! ===")
        self.game_state = 'victory'

        # Distribute XP to all living party members
        xp = self.boss.xp_value
        for char in self.party:
            if char.is_alive:
                char.gain_xp(xp)
                self.add_message(f"{char.name} gained {xp} XP")

    def _update(self):
        """Update game state."""
        if not self.player_turn and self.game_state == 'playing':
            self._enemy_turn()

        # Check for victory
        if not any(e.is_alive for e in self.enemies) and (not self.boss or not self.boss.is_alive):
            if self.game_state == 'playing':
                self.game_state = 'victory'

        # Check for defeat
        if not any(c.is_alive for c in self.party):
            if self.game_state == 'playing':
                self.game_state = 'defeat'
                self.add_message("=== PARTY DEFEATED ===")

    def _enemy_turn(self):
        """Execute enemy turn."""
        import time

        all_enemies = self.enemies + ([self.boss] if self.boss and self.boss.is_alive else [])

        for enemy in all_enemies:
            if not enemy.is_alive:
                continue

            # Get party positions
            party_positions = [(c.x, c.y) if c.is_alive else (None, None) for c in self.party]

            # Get obstacles
            obstacles = self._get_obstacles()

            # Choose action
            action = enemy.choose_action(party_positions, self.dungeon.width, obstacles)

            if action:
                action_type, data = action

                if action_type == 'move':
                    new_x, new_y = data
                    enemy.move(new_x, new_y)

                elif action_type == 'attack':
                    target_idx = data
                    if 0 <= target_idx < len(self.party):
                        target = self.party[target_idx]
                        if target.is_alive:
                            damage = enemy.calculate_damage()
                            actual_damage = target.take_damage(damage)
                            self.add_message(f"{enemy.name} attacks {target.name} for {actual_damage} damage!")

                            if not target.is_alive:
                                self.add_message(f"{target.name} has fallen!")

            # Small delay for visibility
            pygame.time.wait(100)
            self._render()

        # End enemy turn
        self.player_turn = True
        self.turn_number += 1
        self.add_message(f"--- Turn {self.turn_number} ---")

    def _render(self):
        """Render the game."""
        self.screen.fill(self.COLOR_BG)

        # Render dungeon
        self._render_dungeon()

        # Render UI panel
        self._render_ui()

        pygame.display.flip()

    def _render_dungeon(self):
        """Render the dungeon view."""
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                screen_x = x * self.tile_size - self.camera_x
                screen_y = y * self.tile_size - self.camera_y

                # Skip if off screen
                if screen_x < -self.tile_size or screen_x > self.game_area_width:
                    continue
                if screen_y < -self.tile_size or screen_y > self.screen_height:
                    continue

                tile = self.dungeon.tiles[y][x]

                # Determine tile color
                if tile.type == Tile.WALL:
                    color = self.COLOR_WALL
                elif tile.type == Tile.DOOR:
                    color = self.COLOR_DOOR
                elif tile.type == Tile.LOOT:
                    color = self.COLOR_LOOT
                elif tile.type == Tile.POWERUP:
                    color = self.COLOR_POWERUP
                elif tile.type == Tile.BOSS_MARKER:
                    color = self.COLOR_BOSS_MARKER
                else:
                    # Checkerboard pattern for floor
                    if (x + y) % 2 == 0:
                        color = self.COLOR_FLOOR_LIGHT
                    else:
                        color = self.COLOR_FLOOR_DARK

                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, self.tile_size, self.tile_size))

                # Highlight valid moves
                if (x, y) in self.valid_moves:
                    pygame.draw.rect(self.screen, self.COLOR_HIGHLIGHT,
                                   (screen_x, screen_y, self.tile_size, self.tile_size), 2)

                # Highlight valid attacks
                if (x, y) in self.valid_attacks:
                    pygame.draw.rect(self.screen, self.COLOR_ATTACK_RANGE,
                                   (screen_x, screen_y, self.tile_size, self.tile_size), 2)

        # Render characters
        for char in self.party:
            if char.is_alive:
                self._render_character(char)

        # Render enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                self._render_enemy(enemy)

        if self.boss and self.boss.is_alive:
            self._render_enemy(self.boss, is_boss=True)

    def _render_character(self, character):
        """Render a character."""
        screen_x = character.x * self.tile_size - self.camera_x
        screen_y = character.y * self.tile_size - self.camera_y

        # Draw circle for character
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        radius = self.tile_size // 3

        color = character.get_color()

        # Draw character
        if character.is_invisible:
            # Make invisible characters semi-transparent (draw outline only)
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius, 2)
        else:
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

        # Draw selection indicator
        if character == self.selected_character:
            pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), radius + 3, 2)

        # Draw HP bar
        bar_width = self.tile_size
        bar_height = 3
        hp_percentage = character.hp / character.max_hp

        pygame.draw.rect(self.screen, (255, 0, 0),
                        (screen_x, screen_y - 5, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (screen_x, screen_y - 5, int(bar_width * hp_percentage), bar_height))

    def _render_enemy(self, enemy, is_boss=False):
        """Render an enemy."""
        screen_x = enemy.x * self.tile_size - self.camera_x
        screen_y = enemy.y * self.tile_size - self.camera_y

        # Draw square for enemy
        size = self.tile_size // 2 if not is_boss else self.tile_size * 2 // 3
        offset = (self.tile_size - size) // 2

        color = enemy.get_color()
        pygame.draw.rect(self.screen, color,
                        (screen_x + offset, screen_y + offset, size, size))

        # Draw HP bar
        bar_width = self.tile_size
        bar_height = 3
        hp_percentage = enemy.hp / enemy.max_hp

        pygame.draw.rect(self.screen, (255, 0, 0),
                        (screen_x, screen_y - 5, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (screen_x, screen_y - 5, int(bar_width * hp_percentage), bar_height))

    def _render_ui(self):
        """Render UI panel."""
        panel_x = self.game_area_width
        panel_rect = pygame.Rect(panel_x, 0, self.ui_panel_width, self.screen_height)
        pygame.draw.rect(self.screen, self.COLOR_UI_BG, panel_rect)

        y_offset = 10

        # Title
        title = self.font_large.render("Chess Dungeon", True, self.COLOR_TEXT)
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += 50

        # Dungeon info
        level_text = self.font_medium.render(f"Level: {self.dungeon_level}", True, self.COLOR_TEXT)
        self.screen.blit(level_text, (panel_x + 10, y_offset))
        y_offset += 30

        turn_text = self.font_small.render(f"Turn: {self.turn_number}", True, self.COLOR_TEXT)
        self.screen.blit(turn_text, (panel_x + 10, y_offset))
        y_offset += 25

        phase_text = "Player Turn" if self.player_turn else "Enemy Turn"
        phase_color = (100, 255, 100) if self.player_turn else (255, 100, 100)
        phase = self.font_small.render(phase_text, True, phase_color)
        self.screen.blit(phase, (panel_x + 10, y_offset))
        y_offset += 40

        # Party status
        party_title = self.font_medium.render("Party:", True, self.COLOR_TEXT)
        self.screen.blit(party_title, (panel_x + 10, y_offset))
        y_offset += 30

        for i, char in enumerate(self.party):
            if not char.is_alive:
                continue

            # Character name and class
            name_text = f"{i+1}. {char.name} ({char.piece_type[:3].upper()})"
            name = self.font_small.render(name_text, True, char.get_color())
            self.screen.blit(name, (panel_x + 15, y_offset))
            y_offset += 20

            # HP bar
            hp_text = f"HP: {char.hp}/{char.max_hp}"
            hp = self.font_small.render(hp_text, True, self.COLOR_TEXT)
            self.screen.blit(hp, (panel_x + 20, y_offset))
            y_offset += 18

            # Level and XP
            level_text = f"Lv{char.level} ({char.xp}/{char.xp_to_next_level} XP)"
            level = self.font_small.render(level_text, True, (200, 200, 200))
            self.screen.blit(level, (panel_x + 20, y_offset))
            y_offset += 25

        y_offset += 10

        # Enemies remaining
        enemies_alive = len([e for e in self.enemies if e.is_alive])
        boss_alive = self.boss.is_alive if self.boss else False

        enemies_text = f"Enemies: {enemies_alive}"
        enemies = self.font_small.render(enemies_text, True, self.COLOR_TEXT)
        self.screen.blit(enemies, (panel_x + 10, y_offset))
        y_offset += 25

        if boss_alive:
            boss_text = f"Boss: {self.boss.name}"
            boss = self.font_small.render(boss_text, True, (255, 0, 0))
            self.screen.blit(boss, (panel_x + 10, y_offset))
            y_offset += 20

            boss_hp_text = f"HP: {self.boss.hp}/{self.boss.max_hp}"
            boss_hp = self.font_small.render(boss_hp_text, True, (255, 0, 0))
            self.screen.blit(boss_hp, (panel_x + 10, y_offset))
            y_offset += 30

        # Messages
        y_offset += 20
        msg_title = self.font_medium.render("Messages:", True, self.COLOR_TEXT)
        self.screen.blit(msg_title, (panel_x + 10, y_offset))
        y_offset += 30

        for msg in self.messages[-8:]:
            msg_surface = self.font_small.render(msg[:40], True, (200, 200, 200))
            self.screen.blit(msg_surface, (panel_x + 10, y_offset))
            y_offset += 18

        # Controls
        y_offset = self.screen_height - 120
        controls_title = self.font_small.render("Controls:", True, self.COLOR_TEXT)
        self.screen.blit(controls_title, (panel_x + 10, y_offset))
        y_offset += 20

        controls = [
            "Click: Select/Move/Attack",
            "Tab: Cycle characters",
            "Space: End turn",
            "ESC: Quit"
        ]

        for control in controls:
            text = self.font_small.render(control, True, (150, 150, 150))
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 18

        # Victory/Defeat message
        if self.game_state == 'victory':
            victory_text = self.font_large.render("VICTORY!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(self.game_area_width // 2, self.screen_height // 2))
            self.screen.blit(victory_text, text_rect)
        elif self.game_state == 'defeat':
            defeat_text = self.font_large.render("DEFEATED", True, (255, 0, 0))
            text_rect = defeat_text.get_rect(center=(self.game_area_width // 2, self.screen_height // 2))
            self.screen.blit(defeat_text, text_rect)
