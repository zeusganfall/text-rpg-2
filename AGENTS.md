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

# RPG AGENTS (Phase 2)

This section expands the AGENTS design for **Phase 2**, focusing on progression, items, and quests.

---

## Agents (Classes)

### 1. Player (Expanded)

* **New Attributes:**

  * `xp`: integer (experience points)
  * `level`: integer (player level)
  * `attack_power`: integer (base damage, increases with level or equipped weapon)
  * `equipped_weapon`: reference to `Weapon` item (optional)
  * `equipped_armor`: reference to `Armor` item (optional)
* **New Behavior:**

  * `gain_xp(amount)`: Increases XP; checks for level-up.
  * `level_up()`: Increases `hp` and `attack_power` when XP threshold is reached.
  * `equip(item)`: Equip a weapon or armor.
  * `unequip(item_type)`: Remove currently equipped weapon or armor.

### 2. Item (Expanded via Subclasses)

* Base `Item`: `name`, `description`.
* **Weapon (Subclass of Item):**

  * Attributes: `damage`
  * Behavior: Adds to player attack power when equipped.
* **Armor (Subclass of Item):**

  * Attributes: `defense`
  * Behavior: Reduces damage taken when equipped.
* **Potion (Subclass of Item):**

  * Attributes: `heal_amount`
  * Behavior: `use()` restores player HP.

### 3. NPC (New)

* **Purpose:** Characters that are not monsters or players.
* **Attributes:**

  * `name`: string
  * `dialogue`: list of strings
  * `quests`: list of `Quest` objects (optional)
* **Behavior:**

  * `talk()`: Print dialogue lines.
  * `give_quest()`: Offer a quest to the player.

### 4. Quest (New / Expanded)

* **Purpose:** Track goals, rewards, and starting effects.
* **Attributes:**

  * `name`: string
  * `description`: string
  * `goal`: condition (e.g., kill X monsters)
  * `progress`: current progress value
  * `is_complete`: boolean
  * `reward`: XP, item, or both
  * `on_accept`: optional effect (e.g., grant item, XP, or trigger dialogue)
* **Behavior:**

  * `update_progress(event)`: Increments progress.
  * `check_completion()`: Marks quest complete and grants reward.
  * `accept()`: Grants any `on_accept` effects (items, XP, dialogue) when the quest starts.

---

## Tools (Commands / Player Interactions)

### 1. Player Progression

* `xp` and `level` displayed with `status` command.
* Leveling up increases player stats automatically.

### 2. Inventory (Expanded)

* New commands:

  * `equip [item]`: Equip a weapon or armor.
  * `unequip [weapon/armor]`: Unequip current gear.
  * `use [potion]`: Consume a potion to heal.

### 3. NPC Interaction

* `talk [npc]`: Display dialogue and potential quest offer.

### 4. Quest Tracking

- `quests`: List active quests and their progress.

### 5. Combat (Turn-Based Update)
- **Command:** `attack [monster]`
- **Behavior:**
  - First attack message: `You engage the [monster] in combat!`
  - Each `attack` command executes one **turn**:
    - Player attack → print damage dealt and monster’s HP left.
    - Monster counterattacks (if alive) → print damage dealt and player’s HP left.
  - Player must type `attack [monster]` again for the next turn.
  - Combat ends when either the monster or player is defeated.
- **Additional Combat Actions:**
  - `use [potion]`: Restores HP instead of attacking.
  - `flee`: Attempt to escape combat, returning to the previous location. May have a chance of failure or allow the monster one free attack.

---

## System Tools (Behind-the-Scenes)

### 1. Quest Tracker

* Updates progress when monsters are defeated or conditions are met.
* Stores completed quests and prevents re-taking story quests.
* Supports `on_accept` effects for starting quests.

### 2. Leveling System

* Defines XP thresholds for each level.
* Triggers `level_up()` on Player when thresholds are crossed.

### 3. Combat Controller
- Manages turn flow (attack, potion use, flee).
- Ensures each input advances combat by only one turn.

---

## Input and Output Conventions (Summary)

- **Input:**
  - Numbers for navigation.
  - Text commands for actions (`look`, `inventory`, `equip sword`, `talk guard`, `quests`, `attack goblin`, `use healing potion`, `flee`, etc.).
- **Output:**
  - Clear feedback when leveling up, completing quests, equipping items, receiving `on_accept` effects, or during combat turns.

---

## Sample NPC + Quest Flow

**Scenario:** Player talks to a guard captain in Luminaris.

```
📍 Luminaris
You see: Guard Captain

> talk guard captain
Guard Captain: "Shadows are stirring in Shademire Woods. Can you help us?"
Quest offered: "Clear the Woods"
- Defeat 3 Goblins in Shademire Woods.
Reward: 50 XP, Healing Potion
You receive a Healing Potion to aid you.

> quests
Active quests:
- Clear the Woods (0/3 Goblins defeated)

📍 Shademire Woods
Monsters: Goblin

> attack goblin
You engage the Goblin in combat!
You attack the Goblin for 3 damage.
Goblin has 7 HP left.
Goblin attacks you for 2 damage.
You have 18 HP left.

> use healing potion
You use a Healing Potion and restore 5 HP.
You now have 23 HP.

> flee
You attempt to flee...
You escape back to Luminaris!

> quests
Active quests:
- Clear the Woods (0/3 Goblins defeated)
```

---
