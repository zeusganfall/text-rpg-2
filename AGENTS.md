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

## Phase 3 Additions

### Location Updates
- Locations can now have **sub-areas** (e.g., `Crumbling Catacombs - Depths`).
- Each location may feature **unique monsters tied to lore themes** (e.g., Bog Horror in Sunken Swamp).

### Item Updates
- **Readable (Subclass of Item):**
  - Attribute: `lore_text` (string, full lore passage shown when examined).
  - Behavior: Using `examine [item]` reveals lore. May unlock new quests or NPC dialogue topics.

### NPC Updates
- NPCs now support **topic-based dialogue**:
  - Command: `ask [npc] [topic]`.
  - Topics can expand lore or unlock quests.
- NPCs can act as **quest gates**, requiring the player to present items (e.g., Cultist Note) before unlocking new quests.

### Quest Updates
- New goal types supported:
  - `collect_or_talk` → hand in an item or speak to NPC.
  - `collect_or_kill` → either collect item(s) or defeat specific monsters.
  - `alternate_goal` → complete one of multiple possible objectives.
- Quests can now **escalate the story**, unlocking further quests upon completion.
- **Quest Start Indicator:** Each quest now has a `start` field in `game_data.json` specifying how the quest becomes available:
  - `npc` → talk to an NPC to receive quest.
  - `location_enter` → entering a location triggers availability.
  - `item_pickup` → picking up/examining an item makes quest available.
  - `item_or_npc` → presenting an item or talking to a specific NPC starts quest.
  - `auto` → automatically available under certain conditions.
- When available, NPCs are marked with `(!)` in the location view, and the game notifies the player of new quests.

### System Tools Updates
- **Lore Integration System**
  - Links `Readable` items and NPC dialogue to quest progression.
  - Examining an item or asking about a topic may update quest tracker.
- **Quest Chaining**
  - Completing one story quest may trigger the availability of the next in sequence.

---

### Sample Phase 3 Flow
```
📍 Crumbling Catacombs - Depths
The deeper tunnels reek of decay. Shadows cling to the walls.
Monsters: Undead Wight

> attack wight
--- Combat: Undead Wight (18 HP) ---
Your HP: 20/20
Available actions: attack, use [item], flee

> examine captured letter
The bloodied letter reads: "Elenya has been taken... they dragged her to the Hollow Spire." A chill grips you.

> talk wandering scholar
Scholar: "That letter confirms it. Malveth holds the princess in the Hollow Spire. Ask me about 'Elenya' if you wish to know more."

> ask scholar elenya
Scholar: "Elenya is the keystone of the Veil. Without her, the kingdom will fall."

> quests
Active quests:
- Investigate the Sunken Swamp (0/1 evidence found)
- Clear the Catacombs (1/3 Skeletons defeated)
```

---

## Quest Start Conventions (Phase 3)
To avoid player confusion about where quests start, use a small `start` block inside each quest in `game_data.json`. The engine will use `start.type` to show indicators and offer quests. The supported values and behavior:

- `npc` — quest is offered by an NPC via `talk [npc]`. The NPC will display `(!)` in the `look` view when the quest is available.
  - `start`: `{ "type": "npc", "ref": "Guard Captain" }`
- `location_enter` — entering the location notifies the player a quest is available and places it in *available quests*.
  - `start`: `{ "type": "location_enter", "ref": "Crumbling Catacombs" }`
- `item_pickup` — picking up a specific item notifies player of a nearby quest (optionally auto-offer).
  - `start`: `{ "type": "item_pickup", "ref": "Old Scroll" }`
- `item_or_npc` — handing in or presenting an item to an NPC (or talking about it) triggers the quest start.
  - `start`: `{ "type": "item_or_npc", "ref": ["Cultist Note", "Old Scroll", "Wandering Scholar"] }`
- `auto` — quest auto-accepts when certain conditions are met (use sparingly).

### Engine Behavior Rules
- On location load: notify and add `location_enter` quests to available list.
- On `look`: show `NPC (!) `marker when `npc` start exists for that NPC and the player hasn't started/completed the quest.
- On `examine` of a Readable with matching `item_pickup` or `item_or_npc` start: notify player and add to available quests.
- On `talk [npc]`: if NPC offers `npc`-type quests, allow `accept [quest]`.
- On `hand_in [item] to [npc]`: satisfy `item_or_npc`/`collect_or_talk` starts/goal logic.

### Example `start` usage
```
"Clear the Woods": {
  "description": "Defeat 3 Shadow-Touched Goblins in Shademire Woods.",
  "start": { "type": "npc", "ref": "Guard Captain" },
  "goal": { "type": "kill", "target": "Shadow-Touched Goblin", "count": 3 },
  "reward": { "xp": 50 }
}
```

---

(End of Phase 3 additions.)

---

## Contextual & Sequential NPC Dialogue (`talk` behavior)

- `talk [npc]` will now offer quests **contextually** and **one at a time**:
  1. The game iterates the NPC's `quests` array (order defined in `game_data.json`) and finds the first quest that is **available** (not started/completed and whose `start` condition matches the current context).
  2. If the quest object has a `lead_in` string, that line prints before offering the quest. Otherwise, fall back to a generic dialogue line from `npc.dialogue`.
  3. After offering that one quest (with its lead-in), the `talk` interaction ends — the NPC will not offer additional quests in the same interaction.

- If the NPC has no available quests, print a generic `npc.dialogue` line (rotate or pick randomly).
- NPCs can vary the lead-in based on the player's inventory or quest progress by setting conditional `lead_in` variations in future iterations (out of scope for Phase 3).

### JSON convention (recommended)
Add an optional `lead_in` field to quest objects. Example:

```json
"Clear the Woods": {
  "description": "Defeat 3 Shadow-Touched Goblins in Shademire Woods.",
  "start": { "type": "npc", "ref": "Guard Captain" },
  "lead_in": "Shadows are stirring near the woods — we need help!",
  "goal": { "type": "kill", "target": "Shadow-Touched Goblin", "count": 3 }
}
```

### Implementation notes for the `talk` refactor
- Iterate `npc.quests` in order. For each quest `q`:
  - Skip if `player.has_started(q)` or `player.has_completed(q)`.
  - Check if `q.start` conditions match current context (e.g., `npc` type quests only offered when talking to that NPC).
  - If available: print `q.lead_in` if present, otherwise print NPC generic line. Offer quest (`accept [quest]`) and **end** the `talk` interaction.
- Keep backward compatibility: if no `lead_in`, use existing `npc.dialogue`.

---

(End of Contextual Dialogue additions.)

---

## Healing Sources & Mechanics (Phase 3 Balance)

To make Phase 3 survivable without forcing a single "correct" path, add multiple, small, renewable healing sources. These are intentionally simple to implement and data-driven so your coding agent can pick them up from `game_data.json`.

### 1. Healing NPC (Temple Cleric)
- **Location:** Luminaris
- **Role:** Offers a `heal` service. Example JSON fields:
  ```json
  "Temple Cleric": {
    "dialogue": ["May the light mend you, traveler."],
    "services": {"heal": {"cost": 0, "type": "full"}},
    "quests": []
  }
  ```
- **Behavior:** `talk Temple Cleric` reveals the service; `heal` or choosing heal restores HP (full if `type==full`, or numeric amount). If `cost > 0`, require gold or an item.

### 2. Healing Station / Checkpoint
- **Location flag example:**
  ```json
  "Crumbling Catacombs": {
    "healing_station": {"type": "partial", "amount": 10, "uses": 1}
  }
  ```
- **Behavior:** At locations with `healing_station`, `rest` or `use station` will restore HP by `amount` or to full depending on `type`. `uses` can limit re-use.

### 3. Monster Healing Drops (small chance)
- Add optional `drop_table` entries to monsters to allow non-deterministic potion drops. Example:
  ```json
  "Cultist": {
    "loot": ["Cultist Note"],
    "drop_table": [{"item":"Healing Potion","chance":0.10}]
  }
  ```
- **Behavior:** On kill, roll against `drop_table`. If success, add healing potion to loot. This adds forgiving randomness without guaranteed excess supplies.

### 4. Level-Up Full Heal (already present)
- Your current `check_level_up` sets `self.hp = self.max_hp`. Keep this — it's a core pacing mechanic.

### 5. Optional: Passive Regeneration in Safe Zones
- Locations flagged `safe_zone: true` slowly regenerate HP (e.g., +1 HP per minute / per rest action). This is optional but smooths small chip damage.

---

## AGENTS.md: Commands for Healing (append these to the Player Interaction section)

### Healing Commands
- `heal` — Use when at a Healing NPC or Healing Station. If at an NPC with a `heal` service, prompt cost/confirmation.
- `rest` — Use at a healing station/`safe_zone` to recover the configured amount. May consume `uses`.
- `hand_in [item] to [npc]` — can also be used to pay or barter for healing if NPC requires an item.

### NPC Services
- NPCs can declare a `services` map in JSON, e.g. `{"heal": {"cost": 5, "type": "full"}}`.
- The parser should show available services when `talk [npc]` is used and allow `use service_name` or `heal` shorthand.

### Monster Drops
- Parser and loot resolution should support `drop_table` with probabilistic drops. Document that `drop_table` is optional.

---

## Suggested JSON Patches (copy into `game_data.json`)

Below are small, ready-to-paste patches. Merge them into the corresponding `npcs`, `locations`, and `monsters` sections.

1) Add Temple Cleric NPC (Luminaris):
```json
"Temple Cleric": {
  "dialogue": ["May the light mend you, traveler.", "I can restore your wounds, for free or coin depending on your need."],
  "services": {"heal": {"cost": 0, "type": "full"}},
  "quests": []
}
```

2) Mark Crumbling Catacombs as a single-use partial healing station (checkpoint):
```json
"Crumbling Catacombs": {
  "healing_station": {"type": "partial", "amount": 10, "uses": 1}
}
```

3) Add drop_table to a few monsters (small chance):
```json
"Cultist": { "drop_table": [{"item": "Healing Potion", "chance": 0.10}] },
"Shadow-Touched Goblin": { "drop_table": [{"item": "Healing Potion", "chance": 0.03}] },
"Bog Horror": { "drop_table": [{"item": "Healing Potion", "chance": 0.12}] }
```

---

## Implementation Notes for the Coding Agent
- `heal` and `rest` should be simple commands that check location/NPC `services` or `healing_station` flags and modify `player.hp` accordingly.
- `drop_table` handling should be optional fallback logic: if `drop_table` exists, roll a random float in `[0,1)` for each entry and add item on success.
- Document the new JSON fields in `AGENTS.md` (as above) for future reference.

---