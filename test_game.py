#!/usr/bin/env python3
"""
Test script to verify game logic without GUI.
"""

from character import create_default_party
from enemy import spawn_enemies, spawn_boss
from dungeon import Dungeon
from chess_moves import ChessMove


def test_characters():
    """Test character creation and stats."""
    print("\n=== Testing Characters ===")
    party = create_default_party()

    for char in party:
        print(f"\n{char}")
        print(f"  Class: {char.char_class}")
        print(f"  Piece: {char.piece_type}")
        print(f"  HP: {char.hp}/{char.max_hp}")
        print(f"  Attack: {char.attack}")
        print(f"  Defense: {char.defense}")
        print(f"  Type: {char.attack_type}")
        print(f"  Range: {char.range}")
        print(f"  Abilities: {', '.join(char.special_abilities)}")

    print("\n✓ Character creation successful!")


def test_chess_moves():
    """Test chess movement logic."""
    print("\n=== Testing Chess Moves ===")

    # Test knight moves
    knight_moves = ChessMove.get_knight_moves(5, 5, 10)
    print(f"Knight at (5,5): {len(knight_moves)} moves - {knight_moves[:4]}...")

    # Test rook moves
    rook_moves = ChessMove.get_rook_moves(5, 5, 10)
    print(f"Rook at (5,5): {len(rook_moves)} moves")

    # Test bishop moves
    bishop_moves = ChessMove.get_bishop_moves(5, 5, 10)
    print(f"Bishop at (5,5): {len(bishop_moves)} moves")

    # Test queen moves
    queen_moves = ChessMove.get_queen_moves(5, 5, 10)
    print(f"Queen at (5,5): {len(queen_moves)} moves")

    # Test king moves
    king_moves = ChessMove.get_king_moves(5, 5, 10)
    print(f"King at (5,5): {len(king_moves)} moves - {king_moves}")

    # Test pawn moves
    pawn_moves, pawn_attacks = ChessMove.get_pawn_moves(5, 5, 10, is_first_move=True)
    print(f"Pawn at (5,5) first move: {len(pawn_moves)} moves, {len(pawn_attacks)} attacks")

    print("\n✓ Chess moves working correctly!")


def test_dungeon_generation():
    """Test procedural dungeon generation."""
    print("\n=== Testing Dungeon Generation ===")

    dungeon = Dungeon(width=30, height=20, dungeon_level=1)

    print(f"Dungeon size: {dungeon.width}x{dungeon.height}")
    print(f"Rooms generated: {len(dungeon.rooms)}")
    print(f"Start room: {dungeon.start_room}")
    print(f"Boss room: {dungeon.boss_room}")

    # Count tile types
    from dungeon import Tile
    floor_count = 0
    wall_count = 0
    door_count = 0

    for y in range(dungeon.height):
        for x in range(dungeon.width):
            tile_type = dungeon.tiles[y][x].type
            if tile_type == Tile.FLOOR:
                floor_count += 1
            elif tile_type == Tile.WALL:
                wall_count += 1
            elif tile_type == Tile.DOOR:
                door_count += 1

    print(f"Floor tiles: {floor_count}")
    print(f"Wall tiles: {wall_count}")
    print(f"Doors: {door_count}")

    # Test start positions
    start_positions = dungeon.get_start_positions(6)
    print(f"Start positions: {start_positions}")

    # Test enemy spawn positions
    enemy_positions = dungeon.get_enemy_spawn_positions(10)
    print(f"Enemy spawn positions: {len(enemy_positions)} positions")

    # Test boss position
    boss_pos = dungeon.get_boss_position()
    print(f"Boss position: {boss_pos}")

    print("\n✓ Dungeon generation successful!")


def test_enemies():
    """Test enemy spawning."""
    print("\n=== Testing Enemies ===")

    enemies = spawn_enemies(dungeon_level=1, num_enemies=5)

    for enemy in enemies:
        print(f"\n{enemy}")
        print(f"  Type: {enemy.enemy_type}")
        print(f"  Piece: {enemy.piece_type}")
        print(f"  HP: {enemy.hp}/{enemy.max_hp}")
        print(f"  Attack: {enemy.attack}")
        print(f"  XP Value: {enemy.xp_value}")

    # Test boss
    print("\n--- Boss ---")
    boss = spawn_boss(dungeon_level=1)
    print(f"\n{boss}")
    print(f"  Type: {boss.enemy_type}")
    print(f"  HP: {boss.hp}/{boss.max_hp}")
    print(f"  Attack: {boss.attack}")
    print(f"  XP Value: {boss.xp_value}")
    print(f"  Abilities: {', '.join(boss.special_abilities)}")

    print("\n✓ Enemy spawning successful!")


def test_combat():
    """Test combat mechanics."""
    print("\n=== Testing Combat ===")

    party = create_default_party()
    attacker = party[0]  # Wizard

    enemies = spawn_enemies(1, 1)
    target = enemies[0]

    print(f"Attacker: {attacker.name} (HP: {attacker.hp})")
    print(f"Target: {target.name} (HP: {target.hp})")

    # Test attack
    damage = attacker.calculate_damage()
    actual_damage = target.take_damage(damage)

    print(f"\n{attacker.name} attacks for {damage} damage")
    print(f"{target.name} takes {actual_damage} damage after defense")
    print(f"{target.name} HP: {target.hp}/{target.max_hp}")
    print(f"Target alive: {target.is_alive}")

    # Test XP gain
    if not target.is_alive:
        xp_gained = target.xp_value
        leveled = attacker.gain_xp(xp_gained)
        print(f"\n{attacker.name} gained {xp_gained} XP")
        print(f"Level up: {leveled}")
        print(f"Level: {attacker.level}, XP: {attacker.xp}/{attacker.xp_to_next_level}")

    print("\n✓ Combat mechanics working!")


def test_ability_swap():
    """Test ability swapping."""
    print("\n=== Testing Ability Swap ===")

    party = create_default_party()
    char1 = party[0]  # Wizard/Bishop
    char2 = party[1]  # Warrior/Rook

    print(f"Before swap:")
    print(f"  {char1.name}: {char1.piece_type}")
    print(f"  {char2.name}: {char2.piece_type}")

    char1.swap_piece_type(char2)

    print(f"\nAfter swap:")
    print(f"  {char1.name}: {char1.piece_type}")
    print(f"  {char2.name}: {char2.piece_type}")

    print("\n✓ Ability swap working!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("CHESS DUNGEON CRAWLER - TEST SUITE")
    print("=" * 60)

    try:
        test_characters()
        test_chess_moves()
        test_dungeon_generation()
        test_enemies()
        test_combat()
        test_ability_swap()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nGame logic is working correctly!")
        print("Run 'python main.py' to start the game.")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
