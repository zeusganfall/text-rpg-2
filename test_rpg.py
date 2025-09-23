import pytest
import copy
from rpg import (
    Player,
    load_game_data,
    handle_look,
    handle_quest_completion,
    check_quest_availability,
    handle_equip,
    handle_rest,
    handle_talk,
    handle_attack,
    handle_use,
    handle_get
)

@pytest.fixture
def game_state():
    """Fixture to initialize game state for each test."""
    data, items, monsters, locations, npcs, quests, quest_dialogue_map = load_game_data()

    player = Player(
        name="pytest_player",
        hp=data['player']['hp'],
        max_hp=data['player']['max_hp'],
        attack_power=data['player']['attack_power'],
        level=data['player']['level'],
        xp=data['player']['xp'],
        current_location=data['player_start']
    )

    return {
        "player": player,
        "items": items,
        "monsters": monsters,
        "locations": copy.deepcopy(locations),
        "npcs": npcs,
        "quests": copy.deepcopy(quests),
        "quest_dialogue_map": quest_dialogue_map
    }

def test_step_0_guard_captain_quest_on_accept_reward(game_state, monkeypatch):
    player = game_state['player']
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    handle_talk(player, "Guard Captain", game_state['locations'], game_state['npcs'], game_state['quests'], game_state['quest_dialogue_map'])
    assert "Healing Potion" in player.inventory
    assert "Clear the Woods" in player.active_quests

def test_step_1_catacomb_gear_and_rest(game_state, monkeypatch):
    player = game_state['player']
    locations = game_state['locations']
    player.current_location = "Crumbling Catacombs"
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    check_quest_availability(player, game_state['quests'], "location_enter", player.current_location)
    assert "Clear the Catacombs" in player.active_quests

    catacombs = locations[player.current_location]
    player.inventory.append("Rusted Sword")
    catacombs.items.remove("Rusted Sword")
    player.inventory.append("Leather Armor")
    catacombs.items.remove("Leather Armor")

    handle_equip(player, "Rusted Sword", game_state['items'])
    handle_equip(player, "Leather Armor", game_state['items'])

    assert player.equipped_weapon.name == "Rusted Sword"
    assert player.equipped_armor.name == "Leather Armor"

    player.hp -= 15
    assert player.hp == player.max_hp - 15

    station = locations[player.current_location].healing_station
    assert station['uses'] == 1

    handle_rest(player, locations)

    assert player.hp == player.max_hp - 5
    assert station['uses'] == 0

    handle_rest(player, locations)
    assert player.hp == player.max_hp - 5

def test_step_2_clear_catacombs_by_skeletons(game_state, monkeypatch):
    player = game_state['player']
    player.test_mode["insta_kill"] = True
    player.current_location = "Crumbling Catacombs"
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    check_quest_availability(player, game_state['quests'], "location_enter", player.current_location)
    quest_name = "Clear the Catacombs"
    assert quest_name in player.active_quests

    for i in range(3):
        game_state['locations'][player.current_location].active_monsters.append("Skeleton")
        handle_attack(player, "Skeleton", game_state)

    assert quest_name in player.completed_quests
    assert "Leather Armor" in player.inventory

def test_step_2_clear_catacombs_by_wight(game_state, monkeypatch):
    player = game_state['player']
    player.test_mode["insta_kill"] = True
    player.current_location = "Crumbling Catacombs - Depths"
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    player.active_quests["Clear the Catacombs"] = copy.deepcopy(game_state['quests']["Clear the Catacombs"])
    quest_name = "Clear the Catacombs"

    game_state['locations'][player.current_location].active_monsters.append("Undead Wight")
    handle_attack(player, "Undead Wight", game_state)

    assert quest_name in player.completed_quests
    assert "Leather Armor" in player.inventory

def test_step_3_woods_clues_and_deterministic_drops(game_state, monkeypatch):
    player = game_state['player']
    player.test_mode["insta_kill"] = True
    locations = game_state['locations']
    player.current_location = "Shademire Woods"
    woods = locations[player.current_location]

    player.inventory.append("Old Scroll")
    woods.items.remove("Old Scroll")
    assert "Old Scroll" in player.inventory

    monkeypatch.setattr('random.random', lambda: 0.05)

    woods.active_monsters.append("Cultist")
    handle_attack(player, "Cultist", game_state)

    assert "Cultist Note" in woods.items
    assert "Healing Potion" in woods.items

def test_step_4_scholar_quest_completion(game_state, monkeypatch):
    player = game_state['player']
    quests = game_state['quests']
    player.current_location = "Luminaris"
    player.inventory.append("Cultist Note")
    quest_name = "Investigate the Hollow Clues"
    player.active_quests[quest_name] = copy.deepcopy(quests[quest_name])

    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    handle_talk(player, "Wandering Scholar", game_state['locations'], game_state['npcs'], game_state['quests'], game_state['quest_dialogue_map'])

    assert quest_name in player.completed_quests
    assert "Defeat the Cultist Lieutenant" in player.active_quests

def test_step_5_lieutenant_fight(game_state, monkeypatch):
    player = game_state['player']

    player.inventory.append("Rusted Sword")
    player.inventory.append("Leather Armor")
    handle_equip(player, "Rusted Sword", game_state['items'])
    handle_equip(player, "Leather Armor", game_state['items'])
    player.inventory.append("Healing Potion")

    quest_name = "Defeat the Cultist Lieutenant"
    player.active_quests[quest_name] = copy.deepcopy(game_state['quests'][quest_name])

    player.current_location = "Shademire Woods"
    woods = game_state['locations'][player.current_location]
    woods.active_monsters.append("Cultist Lieutenant")

    handle_attack(player, "Cultist Lieutenant", game_state)
    assert player.current_combat_target is not None

    assert "Healing Potion" in player.inventory
    handle_use(player, "Healing Potion", game_state)
    assert "Healing Potion" not in player.inventory

    while player.current_combat_target:
        handle_attack(player, "Cultist Lieutenant", game_state)

    assert player.current_combat_target is None
    assert quest_name in player.completed_quests
    assert "Lore Fragment" in player.inventory


def test_step_6_sunken_swamp_by_collecting(game_state, monkeypatch):
    """
    Tests completing 'Investigate the Sunken Swamp' by collecting the 'Captured Letter'.
    - Step 6: Enter Swamp Edge -> quest auto-starts.
    - Collect Captured Letter.
    - Assert quest completes.
    """
    player = game_state['player']

    # Auto-start quest
    player.current_location = "Sunken Swamp (Edge)"
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    check_quest_availability(player, game_state['quests'], "location_enter", player.current_location)
    quest_name = "Investigate the Sunken Swamp"
    assert quest_name in player.active_quests

    # Move to swamp and collect letter
    player.current_location = "Sunken Swamp"
    swamp = game_state['locations'][player.current_location]
    assert "Captured Letter" in swamp.items

    # We need a `handle_get` function
    from rpg import handle_get
    handle_get(player, "Captured Letter", game_state)

    assert "Captured Letter" in player.inventory
    assert quest_name in player.completed_quests


def test_step_6_sunken_swamp_by_killing(game_state, monkeypatch):
    """
    Tests completing 'Investigate the Sunken Swamp' by killing a monster for a 'Lore Fragment'.
    """
    player = game_state['player']
    player.test_mode["insta_kill"] = True

    # Auto-start quest
    player.current_location = "Sunken Swamp (Edge)"
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    check_quest_availability(player, game_state['quests'], "location_enter", player.current_location)
    quest_name = "Investigate the Sunken Swamp"
    assert quest_name in player.active_quests

    # Move to swamp and kill a monster that drops a lore fragment
    player.current_location = "Sunken Swamp"
    swamp = game_state['locations'][player.current_location]
    swamp.active_monsters.append("Bog Horror")

    handle_attack(player, "Bog Horror", game_state)

    # The 'Lore Fragment' is loot, so it will be on the ground.
    # The quest should complete when we pick it up.
    assert "Lore Fragment" in swamp.items
    handle_get(player, "Lore Fragment", game_state)

    assert "Lore Fragment" in player.inventory
    assert quest_name in player.completed_quests


def test_game_data_validation():
    """
    Tests the integrity of the game_data.json file.
    - Step 8: Run `validate_game_data()`.
    - Assert no errors on game_data.json.
    """
    from utils import validate_game_data
    import json

    with open("game_data.json", 'r') as f:
        data = json.load(f)

    errors = validate_game_data(data)

    assert not errors, "Validation errors found in game_data.json:\n" + "\n".join(errors)
