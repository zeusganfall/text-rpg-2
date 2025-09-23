# Walkthrough Test Plan (Phase 3)

These tests verify the game works as described in the Walkthrough (Phase 3 Player Guide).

## Tests to Implement

1. **Step 0 — Guard Captain**
   - Talk to Guard Captain, accept *Clear the Woods*.
   - Assert Healing Potion given (`on_accept`).

2. **Step 1 — Catacomb Gear & Rest**
   - Enter Crumbling Catacombs, auto-start *Clear the Catacombs*.
   - Pick up and equip Rusted Sword + Leather Armor.
   - Simulate damage → `rest` restores HP (station `uses` decremented).

3. **Step 2 — Clear Catacombs**
   - Complete via 3 Skeletons OR 1 Wight.
   - Assert quest completion and reward applied.

4. **Step 3 — Woods Clues**
   - Collect Old Scroll.
   - Kill Cultist (seed RNG) to drop Cultist Note.

5. **Step 4 — Scholar & Hollow Clues**
   - Hand in Old Scroll or Cultist Note to Scholar.
   - Assert *Investigate Hollow Clues* completes.
   - Scholar offers *Defeat the Cultist Lieutenant*.

6. **Step 5 — Lieutenant Fight**
   - Fight Cultist Lieutenant with gear equipped.
   - Assert survival possible with potion or level-up heal.
   - Assert quest completes and reward applied.

7. **Step 6 — Sunken Swamp**
   - Enter Swamp Edge → quest auto-starts.
   - Collect Captured Letter OR defeat swamp monster for Lore Fragment.
   - Assert quest completes.

8. **Validation**
   - Run `validate_game_data()`.
   - Assert no errors on game_data.json.

## Notes
- Seed RNG for deterministic drops.
- Reset state between tests.
- Fixes should be minimal (e.g., quest start triggers, `hand_in`, heal/rest clamping, drop_table logic).
