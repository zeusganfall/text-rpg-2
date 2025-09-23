import pytest
from rpg import (
    Player,
    Location,
    Item,
    Weapon,
    Armor,
    Potion,
    Readable,
    Monster,
    NPC,
    Quest,
    load_game_data,
    handle_quest_completion
)
import copy

@pytest.fixture
def game_state():
    """Fixture to initialize the game state for each test."""
    game_data, items, monsters, locations, npcs, quests, _ = load_game_data("game_data.json")
    player_data = game_data['player']
    player = Player(
        name="Player",
        hp=player_data['hp'],
        max_hp=player_data['max_hp'],
        attack_power=player_data['attack_power'],
        level=player_data['level'],
        xp=player_data['xp'],
        current_location=game_data['player_start']
    )
    return player, locations, items, monsters, npcs, quests

def test_quest_clear_the_woods(game_state):
    player, locations, items, monsters, npcs, quests = game_state

    # Accept quest
    quest = quests["Clear the Woods"]
    player.active_quests["Clear the Woods"] = copy.deepcopy(quest)

    # Defeat goblins
    for _ in range(3):
        player.gain_xp(monsters["Shadow-Touched Goblin"].xp)
        quest.progress += 1

    # Check completion
    assert quest.progress >= quest.goal['count']
    handle_quest_completion(player, quest, quests)
    assert "Clear the Woods" in player.completed_quests

def test_quest_clear_the_catacombs(game_state):
    player, locations, items, monsters, npcs, quests = game_state
    player.completed_quests.append("Clear the Woods")

    # Accept quest
    quest = quests["Clear the Catacombs"]
    player.active_quests["Clear the Catacombs"] = copy.deepcopy(quest)
    player.active_quests["Clear the Catacombs"].progress = {"Skeleton": 0, "Undead Wight": 0}

    # Defeat skeletons
    for _ in range(3):
        player.gain_xp(monsters["Skeleton"].xp)
        player.active_quests["Clear the Catacombs"].progress["Skeleton"] += 1

    # Defeat wight
    player.gain_xp(monsters["Undead Wight"].xp)
    player.active_quests["Clear the Catacombs"].progress["Undead Wight"] += 1

    # Check completion
    all_reqs_met = True
    for req in quest.goal['requirements']:
        if player.active_quests["Clear the Catacombs"].progress.get(req['target'], 0) < req['count']:
            all_reqs_met = False
            break
    assert all_reqs_met
    handle_quest_completion(player, quest, quests)
    assert "Clear the Catacombs" in player.completed_quests

def test_quest_investigate_the_hollow_clues(game_state):
    player, locations, items, monsters, npcs, quests = game_state
    player.completed_quests.extend(["Clear the Woods", "Clear the Catacombs"])

    # Accept quest
    quest = quests["Investigate the Hollow Clues"]
    player.active_quests["Investigate the Hollow Clues"] = copy.deepcopy(quest)

    # Collect items
    player.inventory.extend(["Old Scroll", "Cultist Note", "Lore Fragment"])

    # Check completion
    all_items_collected = True
    for item_name in quest.goal['targets']:
        if item_name not in player.inventory:
            all_items_collected = False
            break
    assert all_items_collected
    handle_quest_completion(player, quest, quests)
    assert "Investigate the Hollow Clues" in player.completed_quests
