# Project Outline: Text-Based Fantasy RPG (Lore-Aligned & Revised)

A roadmap for building a text-based fantasy RPG in Python, designed for a solo developer learning OOP and data-driven programming.  
Lore is based on the Kingdom of **Eryndral**, Princess **Elenya**, and the antagonist **Malveth the Hollow**.

---

## Phase 1: Core Foundation (MVP)
**Goal:** Build a tiny, playable prototype that proves the game loop works.

### 1. Core Classes (The "Nouns")
- `Player`: `name`, `hp`, `current_location`, `inventory`, `xp`, `level`.
- `Location`: `name`, `description`, `exits`, `items`, `monsters`.
- `Item`: base class with `name`, `description`.
- `Monster`: basic class with `name`, `hp`, `attack_power`.
- `Character`: base class for `Player`, `Monster`, and `NPC`.

### 2. Core Mechanics (The "Verbs")
- **Game Loop:** main `while` loop to accept player input.
- **Parser:** split input into command + target (e.g., `go north`).
- **Movement:** `go [direction]` or numbered exits.
- **Observation:** `look` shows current location, items, monsters.
- **Inventory:** `get [item]`, `drop [item]`, `inventory`.
- **Combat:** `attack [monster]` — turn-based until one is defeated.

### 3. World Scope (MVP)
- Locations: **Luminaris (Capital City)**, **Shademire Woods**, **Crumbling Catacombs**.
- Monster: Goblin (placeholder for “shadow-touched creature”).
- Item: Rusted Sword.

---

## Phase 2: RPG Systems
**Goal:** Add player progression, advanced items, and basic quests.

### 1. Player Progression
- Add XP rewards for defeating monsters.
- `level_up()` increases `max_hp` and `attack_power`.

### 2. Items (Inheritance & Polymorphism)
- Subclasses of `Item`:
  - `Weapon` (adds `damage`).
  - `Armor` (adds `defense`).
  - `Potion` (consumable, `use()` heals).
- Commands: `equip`, `unequip`, `use [potion]`.

### 3. NPCs & Quests
- Add an `NPC` subclass of `Character`.
- Introduce simple quest-giving NPC in Luminaris.
- Create a `Quest` class (track progress, rewards).
- First quest: Guard captain asks player to **defeat 3 shadow beasts in Shademire Woods**.

---

## Phase 3: Lore & World Expansion
**Goal:** Connect lore into gameplay and expand the world.

### 1. Locations
- **Sunken Swamp** (corrupted area of the kingdom).
- **Additional Catacombs rooms** with undead enemies.
- Unique monster types per location.

### 2. Lore Integration
- Command: `examine [target]` for lore details.
- `Readable` subclass of `Item` for books, scrolls, notes.
- NPC dialogue expanded: allow `ask [topic]`.

### 3. Story Quests
- Player learns about **Elenya’s capture** through scrolls and rumors.
- Quests escalate:
  - Clear undead in Catacombs.
  - Defeat a cultist lieutenant in Shademire Woods.
  - Investigate corruption in Sunken Swamp.
- Each quest gives XP and occasional lore fragments.

---

## Phase 4: Persistence & Final Quest
**Goal:** Ensure progress can be saved and conclude the story.

### 1. Save/Load
- Use `json` to save/load player state and key world events.

### 2. Final Questline
- Triggered after completing earlier quests.
- **Hollow Spire** unlocked (Malveth’s stronghold).
- Final quest: Rescue Elenya and defeat **Malveth the Hollow**.
- Boss fight: Malveth (higher stats, unique loot).
- Ending: narrative sequence describing restoration of the Veil.

---

## Phase 5: End-Game Content (Replayable)
**Goal:** Add small, achievable activities for replayability.

### 1. Bounty Quests (Repeatable)
- Guard captain or bounty board in Luminaris.
- Examples:
  - “Slay 5 cultists in Shademire Woods.”
  - “Clear skeletons from the Catacombs.”
- Rewards: XP, gold, consumables.

### 2. Arena / Trials of Light
- NPC in Luminaris offers wave-based combat challenges.
- Progressively harder fights, scaling rewards.

### 3. Elite/World Boss Respawns
- After defeating Malveth, elite shadow creatures spawn randomly.
- Drop rare loot and lore items.

---

## Data-Driven Design Notes
- Store locations, items, monsters, and quests in JSON.
- Example Monster JSON:
  ```json
  {
    "Goblin": {"hp": 10, "attack_power": 2, "loot": ["Goblin Ear"]},
    "Malveth the Hollow": {"hp": 50, "attack_power": 8, "loot": ["Shadow Relic"]}
  }
  ```
- Example Location JSON:
  ```json
  {
    "Luminaris": {
      "description": "The weakened capital of Eryndral, shadow encroaches at its gates.",
      "exits": {"north": "Shademire Woods", "down": "Crumbling Catacombs"},
      "items": [],
      "monsters": []
    }
  }
  ```

---

