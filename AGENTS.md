# RPG Agents and Tools (Phase 1–3)

This document explains the **core agents (classes)** and **tools (commands and systems)** used in the game. It reflects the current implementation in `game_data.json`.

---

💡 **Tip:** At any time, type `help` to see the list of available commands.

---

## Agents (Classes)

### 1. Player
* **Purpose:** Represents the player character.
* **Attributes:**
  * `name`: string
  * `hp`: integer (health points)
  * `max_hp`: integer (maximum health points)
  * `attack_power`: integer
  * `level`: integer
  * `xp`: integer (experience points)
  * `current_location`: string (key matching a location in `game_data.json`)
  * `inventory`: list of item names
* **Behavior:** Moves between locations, picks up items, fights monsters, completes quests, levels up.

### 2. Location
* **Purpose:** Represents a place in the world.
* **Attributes (loaded from JSON):**
  * `name`: string
  * `description`: string
  * `exits`: dictionary of direction → location
  * `items`: list of item names
  * `monsters`: list of monster names
  * `npcs`: list of NPC names
  * `healing_station` (optional): restores some HP, with limited uses
* **Behavior:** Shows description, connects to other locations, stores items/monsters, can contain healing stations.

### 3. Item
* **Purpose:** Represents objects the player can collect.
* **Attributes:**
  * `type`: string (Weapon, Armor, Potion, Item, or Readable)
  * `name`: string
  * `description`: string
  * Extra fields by type:
    * Weapon → `damage`
    * Armor → `defense`
    * Potion → `heal_amount`
    * Readable → `lore_text`
* **Behavior:** Can be collected, equipped, used, or examined for lore.

### 4. Monster
* **Purpose:** Represents enemies that can be fought.
* **Attributes:**
  * `name`: string
  * `hp`: integer
  * `attack_power`: integer
  * `loot`: list of item names
  * `xp`: integer (reward for defeating)
  * `drop_table` (optional): list of probabilistic drops (item + chance)
* **Behavior:** Attacks the player, can be defeated to drop loot and XP.

### 5. NPC
* **Purpose:** Represents characters the player can talk to.
* **Attributes:**
  * `dialogue`: list of strings
  * `quests`: list of quest IDs
  * `services` (optional): e.g., healing services
* **Behavior:** Provides quests, delivers lore, offers services.

---

## Tools (Commands / Player Interactions)

### 1. Movement (Numbered Navigation)
* **Command:** Enter the number shown in the exits list.
* **Example Input/Output:**
  ```
  📍 Luminaris
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
* **Output:** Shows description, exits, items, monsters, and NPCs at the location.

### 3. Inventory
* **Command:** `inventory`
* **Output:** Lists items the player is carrying.

### 4. Item Interaction
* **Commands:**
  * `get [item]`
  * `drop [item]`
  * `use [item]` (for potions)
  * `examine [item]` (for readable items)

### 5. Combat (Turn-Based)
* **Command:** `attack [monster]`
* **Behavior:**
  * First attack → starts combat.
  * Each attack executes one turn: player attacks, then monster counterattacks (if alive).
  * Combat ends when one side is defeated.
* **Additional Actions:**
  * `use [potion]` → restores HP instead of attacking.
  * `flee` → ends combat and returns to the previous location.

### 6. Quests
* **Commands:**
  * `talk [npc]` → starts dialogue, may offer a quest.
  * `accept [quest]` → accepts a quest from an NPC.
  * `quests` → lists active quests and progress.

### 7. Healing
* **Commands:**
  * `heal` → if near a healing NPC (e.g., Temple Cleric).
  * `rest` → if at a healing station.
* **Behavior:** Restores HP according to the service or station.

---

## System Tools

### 1. Quest Tracker
* Tracks quest progress.
* Handles prerequisites, goals, and rewards.
* Supports automatic completion (`completion: auto`) or NPC confirmation (`completion: talk_to_giver`).

### 2. Leveling System
* Tracks XP thresholds.
* Triggers level-ups and restores HP to max on level-up.

### 3. Combat Controller
* Manages attack turns, potion use, and fleeing.
* Always displays a combat banner during battle.

---

## Quest System Conventions
* **Quest Fields:**
  * `description`: what the quest requires.
  * `lead_in`: NPC line that introduces the quest.
  * `start`: how the quest becomes available (currently only `npc` type is implemented).
  * `prerequisite`: required quest to be completed first (if any).
  * `goal`: kill, collect, or composite requirements.
  * `completion`: how the quest completes (`auto`, `talk_to_giver`).
  * `reward`: XP and/or items.
  * `on_accept`: items given when the quest starts (optional).

* **Quest Progression:**
  * Quests are sequential: Guard Captain → Wandering Scholar → Swamp Hermit.
  * Lore items (`Old Scroll`, `Cultist Note`, `Captured Letter`) tie directly into quests.

---

## Healing Sources

1. **Healing NPCs**
   * Example: Temple Cleric in Luminaris offers full healing for free.
2. **Healing Stations**
   * Example: Crumbling Catacombs has a one-use partial heal.
3. **Monster Drops**
   * Some monsters can drop Healing Potions based on chance.
4. **Level-Up Healing**
   * Player HP fully restored on level-up.

---

## Removed / Redundant Info
* Quest start types `location_enter`, `item_pickup`, `item_or_npc`, `auto` → described in earlier drafts, but **not implemented in JSON**.
* Quest goal types `collect_or_talk`, `collect_or_kill`, `alternate_goal` → not present in JSON.
* Safe zone passive regeneration → not present in JSON.

(These features may be added in later phases.)

