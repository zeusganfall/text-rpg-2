# RPG Agents and Tools (Phase 1)

This document explains the **core agents (classes)** and **tools (commands and systems)** used in the game for Phase 1.
It describes what they do, how to interact with them, and the expected input/output conventions.

---

💡 **Tip:** At any time, type `help` to see the list of available commands.

---

## Agents (Classes)

### 1. Player

* **Purpose:** Represents the player character.
* **Attributes:**

  * `name`: string
  * `hp`: integer (health points)
  * `current_location`: string (key matching a location in `game_data.json`)
  * `inventory`: list of item names
* **Behavior:** Moves between locations, picks up items, fights monsters.

### 2. Location

* **Purpose:** Represents a place in the world.
* **Attributes (loaded from JSON):**

  * `name`: string
  * `description`: string
  * `exits`: dictionary of direction → location
  * `items`: list of item names
  * `monsters`: list of monster names
* **Behavior:** Shows description, connects to other locations, stores items/monsters.

### 3. Item

* **Purpose:** Represents objects the player can collect.
* **Attributes:**

  * `name`: string
  * `description`: string
* **Behavior:** Can be added to or removed from locations and inventory.

### 4. Monster

* **Purpose:** Represents enemies that can be fought.
* **Attributes:**

  * `name`: string
  * `hp`: integer
  * `attack_power`: integer
  * `loot`: list of item names
* **Behavior:** Can attack the player and drop loot when defeated.

---

## Tools (Commands / Player Interactions)

The player interacts with the world using **number-based input for movement** and **text commands for actions**.

### 1. Movement (Numbered Navigation)

* **Command:** Enter the number shown in the exits list.
* **Example Input/Output:**

  ```
  📍 Luminaris
  The weakened capital of Eryndral. Merchants whisper of shadows stirring beyond the gates.
  Exits:
  1. North → Shademire Woods
  2. Down → Crumbling Catacombs

  Choose an exit:
  > 1
  You move north.
  You are now in Shademire Woods.
  ```

### 2. Observation

* **Command:** `look`
* **Output Example:**

  ```
  📍 Shademire Woods
  Twisted trees block out the sun. The air feels heavy, and faint eyes glimmer in the dark.
  Exits:
  1. South → Luminaris
  Items: none
  Monsters: Goblin
  ```

### 3. Inventory

* **Command:** `inventory`
* **Output Example:**

  ```
  You are carrying:
  - Rusted Sword
  ```

### 4. Item Interaction

* **Commands:**

  * `get [item]`
  * `drop [item]`
* **Example Input/Output:**

  ```
  > get Rusted Sword
  You pick up the Rusted Sword.
  ```

### 5. Combat

* **Command:** `attack [monster]`
* **Output Example:**

  ```
  You attack the Goblin for 3 damage.
  Goblin has 7 HP left.
  Goblin attacks you for 2 damage.
  You have 8 HP left.
  ```

### 6. Help

* **Command:** `help`
* **Output Example:**

  ```
  Available commands:
  - look: Show your current location and surroundings
  - [number]: Move to another location using the exit list
  - get [item]: Pick up an item
  - drop [item]: Drop an item
  - inventory: Show what you are carrying
  - attack [monster]: Fight a monster
  - help: Show this help screen
  - quit: Exit the game
  ```

---

## System Tools (Behind-the-Scenes)

These are not “agents” inside the world but **support tools** that make the game function.

### 1. Game Loop

* **Purpose:** Keeps the game running until the player quits.
* **Input:** Accepts number inputs for navigation and text commands for actions.
* **Output:** Prints results of each action (movement, combat, inventory, etc.).
* **Convention:** Runs as a `while True` loop, ends on a `quit` command.

### 2. Parser

* **Purpose:** Interprets input as either:

  * A **number** for navigation.
  * A **command** like `look`, `inventory`, `attack [monster]`.
* **Input Example:**

  ```
  2
  ```
* **Output Example:**

  ```python
  {"command": "go", "target": "Crumbling Catacombs"}
  ```

### 3. JSON Loader

* **Purpose:** Loads game data (locations, items, monsters) from `game_data.json`.
* **Input:** JSON file.
* **Output:** Python dictionaries and class objects (e.g., `Location`, `Item`, `Monster`).
* **Convention:** Always reference game entities by their `name` keys.

### 4. Output Formatter

* **Purpose:** Ensures consistent display of text (location headers, combat logs, inventory lists).
* **Input:** Game state data (player, location, combat events).
* **Output Example:**

  ```
  📍 Shademire Woods
  Twisted trees block out the sun. The air feels heavy, and faint eyes glimmer in the dark.
  Exits:
  1. South → Luminaris
  Items: none
  Monsters: Goblin
  ```

### 5. Screen Management

* **Purpose:** Keeps the console readable by clearing old text.
* **Implementation:**

  ```python
  import os

  def clear_screen():
      if os.name == "nt":  # Windows
          os.system("cls")
      else:  # macOS / Linux
          os.system("clear")
  ```
* **Best Practice:**

  * Clear the screen **before** showing a new state (e.g., when entering a location).
  * In combat, show results clearly before the next clear.

---

## Data Source (game\_data.json)

* All game content (locations, monsters, items) is stored in `game_data.json`.
* **Input convention:** Load the JSON file at game start.
* **Output convention:** The game reads attributes and creates objects dynamically.

---

## Input and Output Conventions (Summary)

* **Input:**

  * Numbers for navigation (e.g., `1`, `2`).
  * Text commands for actions (e.g., `look`, `attack goblin`).
  * Case-insensitive.
  * Whitespace trimmed.

* **Output:** Plain text responses, may include:

  * Location descriptions.
  * Combat feedback.
  * Inventory changes.
  * Status updates (HP, monster defeat, item pickups).

---
