import pytest
from rpg import Player, NPC, Quest, resolve_npc_dialogue

@pytest.fixture
def player():
    return Player("Test Player", 20, 20, 3, 1, 0, "Luminaris")

@pytest.fixture
def quests():
    return {
        "quest1": Quest("quest1", "desc1", {}, {}, prerequisite=None),
        "quest2": Quest("quest2", "desc2", {}, {}, prerequisite="quest1"),
    }

@pytest.fixture
def npc(quests):
    return NPC(
        name="Test NPC",
        dialogue={
            "default": "Hello there.",
            "quest_offer": {"quest1": "Please do quest 1.", "quest2": "Please do quest 2."},
            "quest_active": {"quest1": "Quest 1 is active.", "quest2": "Quest 2 is active."},
            "after_all_quests": "Thanks for everything!",
        },
        quests=["quest1", "quest2"]
    )

def test_npc_offers_first_quest(npc, player, quests):
    dialogue, offer = resolve_npc_dialogue(npc, player, quests)
    assert dialogue == "Please do quest 1."
    assert offer == "quest1"

def test_npc_with_active_quest(npc, player, quests):
    player.active_quests["quest1"] = quests["quest1"]
    dialogue, offer = resolve_npc_dialogue(npc, player, quests)
    assert dialogue == "Quest 1 is active."
    assert offer is None

def test_npc_offers_second_quest_after_first_is_complete(npc, player, quests):
    player.completed_quests.append("quest1")
    dialogue, offer = resolve_npc_dialogue(npc, player, quests)
    assert dialogue == "Please do quest 2."
    assert offer == "quest2"

def test_npc_after_all_quests_complete(npc, player, quests):
    player.completed_quests.extend(["quest1", "quest2"])
    dialogue, offer = resolve_npc_dialogue(npc, player, quests)
    assert dialogue == "Thanks for everything!"
    assert offer is None

def test_npc_with_no_quests():
    player = Player("Test Player", 20, 20, 3, 1, 0, "Luminaris")
    npc = NPC(name="Bystander", dialogue={"default": "Nice weather."})
    dialogue, offer = resolve_npc_dialogue(npc, player, {})
    assert dialogue == "Nice weather."
    assert offer is None

def test_npc_quest_prerequisite_not_met(npc, player, quests):
    # This NPC only has quest2, which requires quest1
    npc.quests = ["quest2"]
    dialogue, offer = resolve_npc_dialogue(npc, player, quests)
    # Should fall back to default dialogue because prereq for quest2 is not met
    assert dialogue == "Hello there."
    assert offer is None
