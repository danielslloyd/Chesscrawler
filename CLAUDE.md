# Chess Dungeon Crawler — CLAUDE.md

## Project Overview

A browser HTML5 dungeon crawler where party members and enemies move using chess-piece rules. The main game file is `chess_dungeon.html` plus an `assets/` folder of 32×32 PNG sprites.

The Python files in the repo root (`game.py`, `character.py`, etc.) are an older prototype and are **not** the active game. All active development is in `chess_dungeon.html`. The `tools/` directory holds the placeholder-sprite generator.

## Running the Game

Because the game loads PNGs via `<img src="assets/...">`, browsers block `file://` image loads in some configurations. Either open the file directly (most browsers allow it for same-folder assets) or serve the directory:

```
python3 -m http.server 8000      # then open http://localhost:8000/chess_dungeon.html
```

Sprites missing from `assets/` fall back to emoji glyphs automatically — the game still works without any image files.

To regenerate placeholder sprites (requires `pip install Pillow`):

```
python3 tools/gen_placeholder_sprites.py
```

## Architecture (`chess_dungeon.html`)

All code lives in a single `<script>` block (~3000 lines). Key classes / objects:

| Class | Purpose |
|-------|---------|
| `ChessMove` | Static methods returning valid squares for each piece type |
| `SpriteLoader` | Loads PNGs from `assets/`, exposes `draw(ctx, name, x, y, fallbackGlyph)` |
| `Character` | Player party member — stats, movement, portal/revive abilities |
| `Enemy extends Character` | Enemy AI, scaling, `chooseAction()` |
| `Game` | Main controller: board generation, rendering, input, turn loop, persistence |

### Key constants

- `BOARD_WIDTH = 80`, `BOARD_HEIGHT = 60` — full dungeon size
- `VIEWPORT_WIDTH = 30`, `VIEWPORT_HEIGHT = 25` — tiles visible at once
- `TILE_SIZE = 32` px
- `ASSET_NAMES` — list of PNG names the loader fetches from `assets/`. Add a new entry here when you ship a new sprite.

### Board coordinates

`board[y][x]` — row-major. Camera offsets `cameraX`/`cameraY` translate between world and viewport. **Always use `getTileCoords(e, canvas)`** to convert mouse events to world tiles; it applies the CSS→canvas scale factor. Do NOT inline the coordinate math.

### Rendering pipeline

`render()` (game) and `renderEditor()` both delegate per-tile drawing to `drawTileSprite(ctx, tile, x, y, screenX, screenY)` and per-character drawing to `drawCharSprite(ctx, char, screenX, screenY)`. Both helpers consult `SpriteLoader.images[name]` first; if the PNG is missing they fall back to the emoji glyph defined in the `SPRITES` constant. **Don't draw sprites inline** — go through these helpers so the fallback path works uniformly.

### Procedural generation

`generateDungeon()` picks a style at random (`rooms`, `arena`, or `caves`) and stores it on `this.levelStyle`:

| Style | Generator | Look |
|-------|-----------|------|
| `rooms` | `generateRoomsAndCorridors()` (BSP + irregular corridors + light smoothing) | Classic dungeon |
| `arena` | `generateArena()` (open carve + scattered cover clumps) | Tactical open arena |
| `caves` | `generateCaves()` (cellular automata + largest-floor-region keep) | Organic cave |

Cave generation uses `largestFloorRegion()` to keep only the biggest connected floor blob; isolated chambers become walls. Don't skip that step — without it the level isn't traversable.

### Items, stairs, level transitions

After generation `placeKey`, `placeLockedDoor`, `placeStairs` and `placeLoot` insert tile-typed objects. `TILE_TYPES.STAIRS` is the level exit; stepping a party member onto it triggers `nextLevel()` (which regenerates the board, repositions the party, scales enemies to the new `dungeonLevel`, and autosaves).

### Persistence

Two complementary save paths share `serializeState()` / `applyState(data)`:

1. **localStorage autosave** — `autosaveToLocalStorage()` runs after each enemy turn and on level transition. The constructor calls `loadFromLocalStorage()` and prompts the user to resume if a save exists.
2. **JSON export/import** — `exportLevelJSON()` downloads the current state, `importLevelJSON()` reads a JSON file. Same shape as the autosave so you can swap between them.

`restart()` deletes the localStorage save before generating a new game. The legacy `saveLevel()` / `loadLevel()` names still exist as aliases for the export/import buttons in the editor.

## Gameplay Design Spec

### Movement

Each party member has a `pieceType` (`knight`, `rook`, `bishop`, `queen`, `king`, `pawn`). This controls which tiles they can move to each turn.

- Only **knights** can jump over walls (`TILE_TYPES.WALL`) and locked doors.
- All other pieces are blocked by walls and locked doors.
- Doors (`TILE_TYPES.DOOR`) are passable by all.

### Chess Piece → Class Mapping

| Piece | Class | Notes |
|-------|-------|-------|
| Bishop | Wizard | Portal ability, magic ranged attack (range 5) |
| Rook | Warrior | Melee, high HP |
| Knight | Thief | Jumps over walls |
| Queen | Healer | Magic ranged attack (range 4) |
| Pawn | Assassin | High visibility, attacks **diagonally** (NOT forward) |
| King | Paladin | One square any direction, melee |

### Pawn (Assassin) Attack Rule

In chess a pawn **moves** forward but **attacks** diagonally. The assassin follows this:
- **Move mode**: one square forward (decreasing y)
- **Melee attack mode**: diagonal squares only `(x±1, y-1)`

### Ability Swapping (Capture Mode)

Press **C** (or click "Swap [C]") to enter capture mode. The highlighted squares show reachable allies. Click an ally to **swap chess movement types** between the two characters — their positions stay the same, only `pieceType` changes. This is the intended "capture" mechanic.

### Portal Ability (Wizard only)

1. Select Wizard → press **S** (Special mode).
2. **Left-click** a reachable tile to set the **portal endpoint** (the wizard's current position becomes the start).
3. To **teleport**: select any character, then **right-click on a portal tile** (start or end). The selected character instantly moves to the other portal end.
4. Portals persist until the wizard creates a new one. They are cleared on level transition.

### Healer Revive Ability

The Healer (queen) can revive fallen allies in-level:

1. Select Healer → press **S** (Special mode). Fallen allies within `range` (default 4 Manhattan tiles) are highlighted.
2. **Left-click** a fallen ally to revive them at 50% max HP.
3. Revive sets `reviveCooldown = 5` on the Healer; cooldown ticks down once per turn.

The cooldown counter is shown on the Revive button. The flow lives inside `handleClick()` under `actionMode === 'special'`.

### Level Editor

Press **E** to open. The toolbar covers terrain, items, stairs, party, and enemy. Selecting **Party** or **Enemy** reveals a sub-picker (`renderEditorSubPicker()`) for class/piece type. Place by left-click; right-click clears a tile. Editor state mutates `game.board`, `game.party`, `game.enemies` directly — there is no separate "level data" object. Use `📤 Export JSON` / `📥 Import JSON` to share levels.

### Right-click Behaviour

- If a **portal endpoint** is right-clicked and a character is selected → teleport that character to the other portal end.
- Otherwise → deselect current character.

Right-click does **not** swap abilities. Ability swapping is exclusively done via left-click in Capture mode (C).

## Controls Reference

| Key | Action |
|-----|--------|
| Left-click | Select character / move / attack / capture |
| Right-click | Teleport via portal (if on portal tile) / deselect |
| Space | End player turn |
| Tab | Cycle to next living party member |
| 1–6 | Quick-select party member |
| M | Move mode |
| A | Melee attack mode |
| G | Ranged attack mode |
| C | Capture/swap-abilities mode |
| S | Special ability mode |
| Arrow keys | Scroll camera |
| W | Camera up |
| D | Camera right |
| H / Home | Re-centre camera on party |
| E | Open level editor |
| R | Restart game |

## Fog of War

`fogOfWar[y][x]` — `true` = hidden. Revealed in a circle of radius `visibilityRange` around each living party member each time `updateFogOfWar()` is called. `exploredTiles` (Set of `"x,y"` strings) tracks permanently-seen tiles (shown dimmed when not in current vision).

## Known Limitations

- Portal right-click may not work reliably on touch devices (no touch event handler).
- No undo/redo in level editor.
- Save files are local JSON or browser localStorage only; no cloud sync.
- Pawn direction is always "up" (decreasing y). Enemies spawned with pawn movement always attack upward.
- Cave generation is rejection-based on connectivity — very rarely the largest region is too small for comfortable play. Hit **R** to regenerate if a level is unfair.
- The autosave-resume prompt is a `confirm()` dialog at page load; click Cancel to start fresh.
