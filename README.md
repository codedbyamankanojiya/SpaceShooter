# SpaceShooter


## Overview

**SpaceShooter (Space Shooter Deluxe)** is a lightweight 2D arcade shooter built with Python and Pygame. Pilot a spaceship, shoot incoming enemies, and survive as long as possible while your score increases.

The game includes a simple UI flow (main menu, difficulty selection, gameplay, and game over screen), with a starfield background for visual depth.

## Features

- **Main menu + difficulty selection** (Easy / Normal / Hard)
- **Arcade shooting mechanics** with a fire-rate limit (shoot delay)
- **Enemy spawning system** that scales by difficulty (spawn rate + speed)
- **Score tracking** (+10 points per enemy hit)
- **Game over state** when the player collides with an enemy
- **Starfield background** using sprite-based particles

## Tech Stack

- **Language**: Python 3
- **Game Framework**: Pygame
- **Modules**: `random`, `sys`

## Getting Started

### Prerequisites

- Python 3.x installed
- Pygame installed

Install Pygame:

```bash
pip install pygame
```

### Run the Game

From the project directory:

```bash
python spaceshooter.py
```

## Controls

- **Move left**: `Left Arrow`
- **Move right**: `Right Arrow`
- **Shoot**: `Space`
- **Return to menu (during gameplay)**: `Esc`
- **UI navigation**: Mouse hover + left click

## Difficulty Modes

Difficulty affects both enemy spawn frequency and enemy falling speed:

- **Easy**
  - Higher spawn interval (slower spawns)
  - Lower enemy speed range
- **Normal**
  - Balanced spawn rate and speed
- **Hard**
  - Fast spawning enemies
  - Higher enemy speed range

You can adjust these values inside `spaceshooter.py` in the `DIFFICULTY` dictionary.

## Project Structure

- **`spaceshooter.py`**
  - Main game entry point
  - Game states: `MENU`, `DIFFICULTY`, `PLAYING`, `GAME_OVER`
  - Core sprites: `Player`, `Enemy`, `Bullet`, `Star`
- **`LICENSE`**
  - MIT License
- **`venv/`**
  - Local virtual environment (optional; not required if you install dependencies globally)

## Notes

- The game uses simple procedural shapes for sprites (no external image assets required).
- Enemy collision with the player triggers **Game Over**; use **Main Menu** to restart.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Author

**Aman Kanojiya**
