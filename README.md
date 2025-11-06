# Chess Dungeon Crawler

A unique dungeon crawler where characters move using chess piece mechanics!

## Features

- **Chess Movement**: Each party member moves like a chess piece (Knight, Rook, Bishop, Queen, King, Pawn)
- **RPG Classes**: Characters have traditional RPG roles (Wizard, Thief, Healer, Warrior, etc.)
- **Ability Swapping**: Characters can "capture" allies to swap movement abilities
- **Procedural Dungeons**: Randomly generated dungeons with rooms, corridors, and locked areas
- **Strategic Combat**: Enemies also move using chess rules
- **Character Progression**: XP system with scaling abilities
- **Varied Abilities**: Ranged attackers, bashers, invisible characters, and more
- **Boss Fights**: Each dungeon culminates in a challenging boss encounter

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

```bash
python main.py
```

## Controls

- **Mouse Click**: Select character and move/attack
- **Space**: End turn
- **Tab**: Cycle through party members
- **ESC**: Pause menu
- **1-6**: Quick select party members

## Gameplay

- Click on your character to see available moves (highlighted in blue)
- Click on an ally to swap chess movement abilities
- Click on an enemy to attack (if in range)
- Different rooms require different movement types to access
- Gain XP by defeating enemies to level up your characters
- Collect loot and power-ups throughout the dungeon
- Defeat the boss to complete the dungeon!

## Character Classes

- **Wizard (Bishop)**: Ranged magical attacks, diagonal movement
- **Rook Warrior (Rook)**: High damage basher, straight line movement
- **Knight Thief (Knight)**: Can jump over obstacles, L-shaped movement
- **Queen Healer (Queen)**: Ranged healing, moves in any direction
- **Shadow Assassin (Pawn)**: Weak but invisible, forward movement
- **Paladin (King)**: Balanced fighter, moves one square in any direction

## Enemy Types

- **Goblins**: Fast attackers with varied movement
- **Spiders**: Web attacks and unpredictable movement
- **Boss**: Powerful enemy with special abilities
