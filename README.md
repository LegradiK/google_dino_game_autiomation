# Dino Bot 🦕

**Work in progress — this project is not finished yet.**

An automated bot that plays the Chrome Dinosaur game using real-time screen capture and pixel-based obstacle detection.

## How It Works

The bot takes a screenshot of your screen, locates the game region, and continuously monitors a detection box just ahead of the dinosaur. It compares each frame against a stored baseline image — when a cactus enters the detection zone, the pixel difference spikes and the bot triggers a jump.

## Features

- **Automatic game region detection** — finds the Chrome Dino game on screen without manual configuration
- **Pixel-based obstacle detection** — detects cacti by comparing grayscale frames against a clean baseline
- **Smart jump timing** — jumps early enough for the dino to clear the obstacle
- **Post-jump noise suppression** — uses a higher detection threshold immediately after jumping to avoid false positives from landing movement
- **Pending jump queue** — if an obstacle is detected while the dino is still in the air, the jump is queued and fired as soon as the dino lands
- **Pending jump expiry** — queued jumps are discarded if the obstacle has already passed, preventing wasted jumps
- **Automatic baseline refresh** — recaptures the baseline after each jump so the ground state stays accurate as the game speeds up
- **Game over detection** — automatically stops the loop when the game ends

## Project Structure

```
├── main.py               # Main loop — detection, jumping, cooldown logic
├── obstacle_detector.py  # Screen capture and pixel diff detection
├── game_controller.py    # Launches browser and finds game region on screen
├── dino.py               # Controls the dinosaur (keyboard input)
├── debug.py              # Optional debug image saving
├── config.py             # Configuration (debug directory path etc.)
├── .gitignore
└── README.md
```

## Configuration

Key constants in `main.py`:

| Constant | Default | Description |
|---|---|---|
| `MAX_DURATION` | `120` | Max seconds to run before stopping |
| `JUMP_COOLDOWN` | `0.3` | Minimum seconds between jumps |
| `BASELINE_DELAY` | `0.35` | Seconds after jump before recapturing baseline |
| `POST_JUMP_THRESHOLD` | `15` | Detection threshold during jump recovery |

Key constants in `obstacle_detector.py`:

| Constant | Default | Description |
|---|---|---|
| `THRESHOLD` | `5` | Minimum mean pixel diff to trigger detection |
| `PROXIMITY` | `[300, 500, 120, 8]` | Detection box position relative to game region |

### Tuning the Detection Box

`PROXIMITY = [left, right, top, bottom]` defines the detection window relative to the game region:

- Increase `left` to detect obstacles later (jump closer to cactus)
- Decrease `left` to detect obstacles earlier (jump further from cactus)

## Requirements

- Python 3
- `Pillow`
- `numpy`
- A running Chrome Dinosaur game (chrome://dino)
- An **X11 display environment** — this bot does not support Wayland

Install dependencies:

```bash
pip install pillow numpy
```

## Usage

**1. Allow local X11 connections** (required before running — the bot uses X11 for screen capture and input):

```bash
xhost +local:
```

You should see:
```
non-network local connections being added to access control list
```

**2. Run the bot:**

```bash
python main.py
```

The bot will locate the game on screen, capture a baseline, and start playing automatically. Press `Ctrl+C` to stop early.

> **Note:** If you are on a Wayland session, you will need to switch to an X11 session before running. The `xhost +local:` step must be repeated each time you start a new session.

## Limitations

- Relies on pixel comparison so lighting changes or screen resolution changes can affect accuracy
- Does not currently handle flying pterodactyls
- Game speed increases over time — detection may need retuning at very high scores