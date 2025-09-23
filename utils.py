import json

def validate_game_data(data):
    """
    Validates the game data for integrity.
    - Checks for broken exit links.
    - Checks for undefined items, monsters, npcs, and quests.
    """
    errors = []

    locations = data.get('locations', {})
    items = data.get('items', {})
    monsters = data.get('monsters', {})
    npcs = data.get('npcs', {})
    quests = data.get('quests', {})

    # Check exits
    for loc_name, loc_data in locations.items():
        for exit_dir, exit_dest in loc_data.get('exits', {}).items():
            if exit_dest not in locations:
                errors.append(f"Broken exit in '{loc_name}': '{exit_dest}' does not exist.")

    # Check items in locations
    for loc_name, loc_data in locations.items():
        for item_name in loc_data.get('items', []):
            if item_name not in items:
                errors.append(f"Undefined item in '{loc_name}': '{item_name}'.")

    # Check monsters in locations
    for loc_name, loc_data in locations.items():
        for monster_name in loc_data.get('monsters', []):
            if monster_name not in monsters:
                errors.append(f"Undefined monster in '{loc_name}': '{monster_name}'.")

    # Check npcs in locations
    for loc_name, loc_data in locations.items():
        for npc_name in loc_data.get('npcs', []):
            if npc_name not in npcs:
                errors.append(f"Undefined NPC in '{loc_name}': '{npc_name}'.")

    # Check monster loot
    for monster_name, monster_data in monsters.items():
        for item_name in monster_data.get('loot', []):
            if item_name not in items:
                errors.append(f"Undefined loot item for '{monster_name}': '{item_name}'.")
        for drop in monster_data.get('drop_table', []):
            if drop.get('item') not in items:
                errors.append(f"Undefined drop_table item for '{monster_name}': '{drop.get('item')}'.")

    # Check quest rewards and goals
    for quest_name, quest_data in quests.items():
        reward_item = quest_data.get('reward', {}).get('item')
        if reward_item and reward_item not in items:
            errors.append(f"Undefined reward item for quest '{quest_name}': '{reward_item}'.")

        on_accept_item = quest_data.get('on_accept', {}).get('item')
        if on_accept_item and on_accept_item not in items:
            errors.append(f"Undefined on_accept item for quest '{quest_name}': '{on_accept_item}'.")

        if quest_data.get('goal', {}).get('type') == 'kill':
            target = quest_data.get('goal', {}).get('target')
            if target and target not in monsters:
                errors.append(f"Undefined kill target for quest '{quest_name}': '{target}'.")

    # Check NPC quests
    for npc_name, npc_data in npcs.items():
        for quest_name in npc_data.get('quests', []):
            if quest_name not in quests:
                errors.append(f"Undefined quest for NPC '{npc_name}': '{quest_name}'.")

    return errors
