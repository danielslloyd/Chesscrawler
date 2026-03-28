# Chess Dungeon Crawler — CLAUDE.md

## Project Overview

A single-file HTML5 dungeon crawler where party members and enemies move using chess-piece rules. The main game file is `chess_dungeon.html` — open it directly in any modern browser, no build step or server needed.

The Python files (`game.py`, `character.py`, etc.) are an older prototype and are **not** the active game. All active development is in `chess_dungeon.html`.

## Running the Game

```
open chess_dungeon.html     # macOS
xdg-open chess_dungeon.html # Linux
```

Or just double-click the file in a file manager.

## Architecture (`chess_dungeon.html`)

All code lives in a single `<script>` block (~2800 lines). Key classes:

| Class | Purpose |
|-------|---------|
| `ChessMove` | Static methods returning valid squares for each piece type |
| `Character` | Player party member — stats, movement, portal ability |
| `Enemy extends Character` | Enemy AI, scaling, `chooseAction()` |
| `Game` | Main controller: board generation, rendering, input, turn loop |

### Key constants

- `BOARD_WIDTH = 80`, `BOARD_HEIGHT = 60` — full dungeon size
- `VIEWPORT_WIDTH = 30`, `VIEWPORT_HEIGHT = 25` — tiles visible at once
- `TILE_SIZE = 32` px

### Board coordinates

`board[y][x]` — row-major. Camera offsets `cameraX`/`cameraY` translate between world and viewport. **Always use `getTileCoords(e, canvas)`** to convert mouse events to world tiles; it applies the CSS→canvas scale factor. Do NOT inline the coordinate math.

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
4. Portals persist until the wizard creates a new one.

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
- Level editor "Party Spawn" tool only repositions the first party member.
- No undo/redo in level editor.
- Save files are local JSON only; no cloud sync.
- Pawn direction is always "up" (decreasing y). Enemies spawned with pawn movement always attack upward.
