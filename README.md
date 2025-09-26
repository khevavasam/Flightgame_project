# Flightgame_project

## 📚 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [How to Play](#how-to-play)
- [Authors](#authors)

## Overview

Simple flight game made with **Python** and **MariaDB**.
Players receive quests to fly to specific airports and must plan the most environmentally friendly route (least fuel consumption).

## Project Structure

```text
game/
├─ cli/       # for player interaction
├─ core/      # contains all game logic
├─ db/        # database queries and repositories
├─ utils/     # common helpers
└─ config.py  # project-level configuration (loads .env)
```

## Prerequisites

- **Python** 3.9.13
- **MariaDB** server (or MySQL compatible)
- **pip** (comes with Python) for installing dependencies
- **Optional**: a virtual environment tool such as
  - `venv` (built into Python)

## Setup

1. **Clone the repository**

```bash
git clone git@github.com:khevavasam/Flightgame_project.git
cd Flightgame_project
```

2. **Create a virtual environment (optional)**

```bash
python -m venv venv
# To activate virtual environment
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Copy .env.template and rename it to .env in the project root**

```bash
# Fill your personal database info into .env
# Example below:
DB_USER=username
DB_PASSWORD=secret_password
DB_NAME=flight_game
DB_HOST="127.0.0.1"
DB_PORT=3306
```

## How to Play

From project root:

```bash
python -m game.cli
```

## Authors

- **Artur**
- **Miki**
- **Lauri**
