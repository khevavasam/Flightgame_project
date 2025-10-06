# ✈️ Flightgame_project

## 📚 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [How to Play](#how-to-play)
- [Documentation](#documentation)
- [Authors](#authors)

## Overview

Simple flight game made with **Python** and **MariaDB**.
Players receive quests to fly to specific airports and must plan the most eco-friendly route (least fuel consumption).

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

5. **Database setup**

- Create database flight_game

```bash
# From sql/
mariadb -u <your-username> -p flight_game < flight_game.sql
```

## How to Play

From project root:

```bash
python -m game.cli
```

## Documentation

Full API and module documentation generated with Sphinx.

[📜 Link to API Docs](https://flightgame-api.netlify.app/)

### 📂 Structure of docs/

```text
docs/
├─ source/
│  ├─ _static/     # static assets
│  ├─ _templates/  # custom templates
│  ├─ conf.py      # Sphinx configuration
│  ├─ index.rst    # main documentation page
│  └─ modules/     # auto-generated module docs
└─ build/          # generated HTML (ignored in Git)
```

### 🔧 Build Documentation Locally

```bash

# From docs/
pip install -r doc-requirements.txt
make clean
make html
```

## Authors

- **Artur**
- **Miki**
- **Lauri**
