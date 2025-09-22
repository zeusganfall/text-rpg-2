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
  - `flee`: Instantly ends combat and returns the player to the previous location. Monsters remain in the current location. No free hit is taken when fleeing in Phase 2.

---

## System Tools (Behind-the-Scenes)

### 1. Quest Tracker
- Updates progress when monsters are defeated or conditions are met.
- Stores completed quests and prevents re-taking story quests.
- Supports `on_accept` effects for starting quests.

### 2. Leveling System
- Defines XP thresholds for each level.
- Triggers `level_up()` on Player when thresholds are crossed.

### 3. Combat Controller
- Manages turn flow (attack, potion use, flee).
- Ensures each input advances combat by only one turn.
- **Combat Banner UX Fix:** Always display a combat banner when in battle to remind the player:
  ```
  --- Combat: Goblin (8 HP) ---
  Your HP: 16 / 20
  Available actions: attack, use [item], flee
  ```
- **Flee UX Fix:** After fleeing, print a summary message before showing the location:
  ```
  You attempt to flee...
  You barely escape the Goblin!
  You return to Luminaris.
  ```

---

## Input and Output Conventions (Summary)

- **Input:**
  - Numbers for navigation.
  - Text commands for actions (`look`, `inventory`, `equip sword`, `talk guard`, `quests`, `attack goblin`, `use healing potion`, `flee`, etc.).
- **Output:**
  - Clear feedback when leveling up, completing quests, equipping items, receiving `on_accept` effects, or during combat turns.
  - Combat banner shown each turn to provide context.
  - Flee results explained before returning to the location view.

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
--- Combat Started ---
You engage the Goblin in combat!
Goblin HP: 10 | Your HP: 20
Available actions: attack, use [item], flee

> attack goblin
You attack the Goblin for 3 damage.
Goblin has 7 HP left.
Goblin attacks you for 2 damage.
You have 18 HP left.

> flee
You attempt to flee...
You barely escape the Goblin!
You return to Luminaris.

📍 Luminaris
The weakened capital of Eryndral...
```

---
