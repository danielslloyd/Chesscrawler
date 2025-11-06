# Chess Dungeon Crawler - HTML5 Version

A fully-featured dungeon crawler game running in a single HTML file! Characters move using chess piece mechanics with RPG combat, fog of war, portals, and a built-in level editor.

## 🎮 How to Play

Simply open `chess_dungeon.html` in any modern web browser. No installation or server required!

## ✨ Features

### Core Gameplay

- **Chess Movement System**: Each character moves using authentic chess piece rules
  - **Knight** (Thief): L-shaped movement, can jump over walls
  - **Rook** (Warrior): Straight lines only
  - **Bishop** (Wizard): Diagonal movement only
  - **Queen** (Healer): All directions
  - **King** (Paladin): One square in any direction
  - **Pawn** (Assassin): Forward movement, diagonal attacks

- **Proper Wall Collision**: Only Knight pieces can pass through/over walls
- **Ability Swapping**: Click an ally to swap movement types while keeping characters in place

### New Features

#### 🌀 Portal Ability
- The Wizard has a special portal ability
- **First click** on wizard: Sets portal start point
- **Second click** on a valid tile: Creates portal endpoint
- **Right-click** on portal endpoint: Teleports selected character through the portal
- Portals persist until wizard creates a new one

#### 🌫️ Fog of War
- Unexplored areas are completely dark
- Each character has a visibility range (displayed in UI)
- Once explored, tiles remain visible but darker if no character nearby
- Characters with higher visibility ranges:
  - Assassin: 8 tiles (stealth detection)
  - Wizard: 7 tiles (magical sight)
  - Healer & Thief: 6 tiles
  - Paladin: 5 tiles
  - Warrior: 4 tiles (focused on combat)

#### 🔒 Locked Door System
- One locked door (🔒) blocks all non-knight movement
- Find the key (🔑) somewhere in the dungeon
- Approach the locked door with the key to unlock it
- Door becomes a regular door (🚪) once unlocked

### 🎨 Sprite Legend

The game uses emoji sprites for easy visibility:

| Sprite | Description |
|--------|-------------|
| 🧙 | Wizard (Bishop, Portal ability) |
| ⚔️ | Warrior (Rook) |
| 🗡️ | Thief (Knight, ignores walls) |
| ✨ | Healer (Queen) |
| 🥷 | Assassin (Pawn, high visibility) |
| 🛡️ | Paladin (King) |
| 👺 | Goblin Enemy |
| 🕷️ | Spider Enemy |
| 👹 | Boss Enemy |
| 🧱 | Wall (blocks non-knight) |
| 🔒 | Locked Door |
| 🔑 | Key |
| 💰 | Loot |
| 💎 | Power-up (+2 ATK) |
| 🌀 | Portal |

### 🛠️ Level Editor

Press **E** or click "Level Editor" to access the built-in level editor:

#### Editor Features:
- **Click** a tool, then click the canvas to place it
- **Right-click** on the canvas to remove tiles
- Place walls, doors, locked doors, keys, loot, and power-ups
- Position party members and enemies
- Save/Load custom levels as JSON files
- Clear level to start fresh

#### Editor Tools:
- ⬜ Floor
- 🧱 Wall
- 🚪 Door
- 🔒 Locked Door
- 🔑 Key
- 💰 Loot
- 💎 Power-up
- 👥 Party Spawn
- 👹 Enemy Spawn

#### Tips:
- Place exactly one key and one locked door for the mechanic to work
- Ensure there's a path for non-knight characters
- Test your level by exiting the editor and playing!

## 🎯 Controls

### In-Game
- **Left Click**: Select character, move, or attack
- **Right Click**: Use portal (if available)
- **Space**: End turn
- **Tab**: Cycle through party members
- **1-6**: Quick select party members
- **E**: Open level editor
- **R**: Restart game

### Level Editor
- **Left Click**: Place selected tool
- **Right Click**: Remove tile/character
- **💾 Save**: Export level as JSON
- **📂 Load**: Import level from JSON
- **🗑️ Clear**: Clear entire level
- **✅ Done**: Return to game

## 🎲 Gameplay Tips

1. **Use the Right Character**: Knights can access areas others can't
2. **Portal Strategy**: Use wizard's portal to teleport characters across the dungeon
3. **Key Hunt**: Find the key early to unlock more areas
4. **Fog Management**: Characters with high visibility reveal more tiles
5. **Swap Abilities**: Transfer knight movement to other characters to open up strategies
6. **Range Advantage**: Wizard and Healer can attack from safety
7. **Wall Tactics**: Use walls for cover, only knights can ignore them

## 🔧 Technical Details

- **Single File**: Everything bundled in one HTML file
- **No Dependencies**: Pure HTML5, CSS3, and JavaScript
- **Canvas Rendering**: Smooth 2D graphics
- **Save/Load**: Export custom levels as JSON
- **Responsive UI**: Clean interface with real-time updates

## 🎨 Customization

The game is fully customizable by editing the HTML file:

- **Sprites**: Change emoji in the `SPRITES` object (line ~115)
- **Colors**: Modify CSS variables in the `<style>` section
- **Board Size**: Adjust `BOARD_WIDTH` and `BOARD_HEIGHT` constants
- **Character Stats**: Edit stats in `Character.applyClassStats()` method
- **Visibility Ranges**: Modify in character stats
- **Portal Behavior**: Customize in `handleRightClick()` method

## 🐛 Known Limitations

- Portal currently only works with right-click (may not work on all devices)
- Level editor doesn't validate level completability
- No undo/redo in level editor
- Save files are local only (no cloud sync)

## 🚀 Future Enhancements

Potential additions:
- Multiple portal sets
- Teleportation pads
- One-way doors
- Pressure plates and triggers
- Character inventory system
- Multiple dungeon levels
- Boss special abilities
- Multiplayer mode

## 📝 File Information

- **File**: `chess_dungeon.html`
- **Size**: ~60KB
- **Lines**: ~1400
- **Compatibility**: Chrome, Firefox, Safari, Edge (modern versions)

## 🎉 Credits

Created as a unique twist on traditional dungeon crawlers by combining:
- Chess movement mechanics
- RPG character progression
- Tactical strategy gameplay
- Procedural dungeon exploration
- Level design tools

Enjoy your chess-based adventure! 🏰♟️
