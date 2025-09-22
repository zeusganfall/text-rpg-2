import json
import os
import random
import time
import copy

class Player:
    def __init__(self, name, hp, max_hp, attack_power, level, xp, current_location, inventory=None):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.current_location = current_location
        self.previous_location = current_location
        self.inventory = inventory if inventory is not None else []
        self.xp = xp
        self.level = level
        self.attack_power = attack_power
        self.equipped_weapon = None
        self.equipped_armor = None
        self.active_quests = {}
        self.completed_quests = []
        self.dialogue_history = set()
        self.current_combat_target = None

    def get_attack_power(self):
        total_power = self.attack_power
        if self.equipped_weapon:
            total_power += self.equipped_weapon.damage
        return total_power

    def gain_xp(self, amount):
        self.xp += amount
        print(f"You gained {amount} XP.")
        self.check_level_up()

    def check_level_up(self):
        xp_to_level_up = 100 * self.level
        if self.xp >= xp_to_level_up:
            self.xp -= xp_to_level_up
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.attack_power += 1
            print(f"You leveled up! You are now Level {self.level}.")

    def show_status(self):
        print("\n--- Player Status ---")
        print(f"Level: {self.level}")
        print(f"XP: {self.xp} / {100 * self.level}")
        print(f"HP: {self.hp} / {self.max_hp}")
        print(f"Attack Power: {self.get_attack_power()}")
        if self.equipped_weapon:
            print(f"Weapon: {self.equipped_weapon.name} (+{self.equipped_weapon.damage} dmg)")
        if self.equipped_armor:
            print(f"Armor: {self.equipped_armor.name} (+{self.equipped_armor.defense} def)")
        print("---------------------")

class Location:
    def __init__(self, name, description, exits, items=None, monsters=None, npcs=None):
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items if items is not None else []
        self.monsters = monsters if monsters is not None else []
        self.npcs = npcs if npcs is not None else []
        self.active_monsters = list(self.monsters)

class Item:
    def __init__(self, name, description, **kwargs):
        self.name = name
        self.description = description

class Weapon(Item):
    def __init__(self, name, description, damage, **kwargs):
        super().__init__(name, description, **kwargs)
        self.damage = damage

class Armor(Item):
    def __init__(self, name, description, defense, **kwargs):
        super().__init__(name, description, **kwargs)
        self.defense = defense

class Potion(Item):
    def __init__(self, name, description, heal_amount, **kwargs):
        super().__init__(name, description, **kwargs)
        self.heal_amount = heal_amount

class Readable(Item):
    def __init__(self, name, description, lore_text="", **kwargs):
        super().__init__(name, description, **kwargs)
        self.lore_text = lore_text

class Monster:
    def __init__(self, name, hp, attack_power, loot=None, xp=0, **kwargs):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.loot = loot if loot is not None else []
        self.xp = xp

class NPC:
    def __init__(self, name, dialogue=None, quests=None, topics=None):
        self.name = name
        self.dialogue = dialogue if dialogue is not None else []
        self.quests = quests if quests is not None else []
        self.topics = topics if topics is not None else {}

class Quest:
    def __init__(self, name, description, goal, reward, start=None, alternate_goal=None, on_accept=None, unlocks=None):
        self.name = name
        self.description = description
        self.goal = goal
        self.reward = reward
        self.start = start
        self.alternate_goal = alternate_goal
        self.on_accept = on_accept if on_accept is not None else {}
        self.unlocks = unlocks if unlocks is not None else []
        self.requires = None # New attribute for prerequisites
        self.progress = 0
        self.is_complete = False

def load_game_data(filepath="game_data.json"):
    with open(filepath, 'r') as f:
        data = json.load(f)
    items = {}
    for name, details in data['items'].items():
        item_type = details.pop('type', 'Item')
        if item_type == 'Weapon':
            items[name] = Weapon(name=name, **details)
        elif item_type == 'Armor':
            items[name] = Armor(name=name, **details)
        elif item_type == 'Potion':
            items[name] = Potion(name=name, **details)
        elif item_type == 'Readable':
            items[name] = Readable(name=name, **details)
        else:
            items[name] = Item(name=name, **details)
    monsters = {name: Monster(name=name, **details) for name, details in data['monsters'].items()}
    npcs = {name: NPC(name=name, **details) for name, details in data.get('npcs', {}).items()}
    if "Wandering Scholar" in npcs:
        npcs["Wandering Scholar"].topics = {
            "elenya": "Elenya is the keystone of the Veil. Without her, the kingdom will fall.",
            "hollow spire": "The Hollow Spire is a place of dark rituals. I've only read about it in old texts.",
            "veil": "The Celestial Veil protects us from the horrors of the void. But it is weakening."
        }
    quests = {name: Quest(name=name, **details) for name, details in data.get('quests', {}).items()}
    if "Investigate the Hollow Clues" in quests:
        quests["Investigate the Hollow Clues"].unlocks = ["Defeat the Cultist Lieutenant"]

    # Post-process to add 'requires' to unlocked quests
    for quest in quests.values():
        if quest.unlocks:
            for unlocked_quest_name in quest.unlocks:
                if unlocked_quest_name in quests:
                    quests[unlocked_quest_name].requires = quest.name

    locations = {name: Location(name=name, **details) for name, details in data['locations'].items()}
    return data, items, monsters, locations, npcs, quests

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def print_help():
    print("\nAvailable commands:")
    print("  - look: Show your current location and surroundings")
    print("  - [number]: Move to another location using the exit list")
    print("  - get [item]: Pick up an item")
    print("  - drop [item]: Drop an item")
    print("  - inventory: Show what you are carrying")
    print("  - attack [monster]: Fight a monster")
    print("  - status: Show your current level, XP, and HP")
    print("  - equip [item]: Equip a weapon or armor")
    print("  - unequip [weapon/armor]: Unequip your weapon or armor")
    print("  - use [potion]: Use a potion to heal")
    print("  - examine [item]: Examine an item in your inventory")
    print("  - ask [npc] [topic]: Ask an NPC about a specific topic.")
    print("  - talk [npc]: Talk to an NPC")
    print("  - quests: View your active quests")
    print("  - help: Show this help screen")
    print("  - quit: Exit the game")

def show_location(location, npcs, player, quests):
    print(f"📍 {location.name}")
    print(location.description)
    print("Exits:")
    if not location.exits:
        print("  None")
    else:
        for i, (direction, dest) in enumerate(location.exits.items(), 1):
            print(f"  {i}. {direction.capitalize()} → {dest}")
    print(f"Items: {', '.join(location.items) if location.items else 'none'}")
    print(f"Monsters: {', '.join(location.active_monsters) if location.active_monsters else 'none'}")

    location_npcs = []
    for npc_name in location.npcs:
        npc = npcs[npc_name]
        has_quest = False
        # Check if the NPC has any quests in their list that the player can take
        for quest_name in npc.quests:
            quest = quests.get(quest_name)
            if not quest: continue
            # Check for prerequisites
            if quest.requires and quest.requires not in player.completed_quests:
                continue
            if quest_name not in player.active_quests and quest_name not in player.completed_quests:
                has_quest = True
                break
        if has_quest:
            location_npcs.append(f"{npc.name} (!)")
        else:
            location_npcs.append(npc.name)
    print(f"You see: {', '.join(location_npcs) if location_npcs else 'no one special'}")

def handle_look(location, npcs, player, quests):
    clear_screen()
    show_location(location, npcs, player, quests)

def check_quest_availability(player, quests, trigger_type, trigger_ref):
    for quest_name, quest in quests.items():
        if quest_name in player.active_quests or quest_name in player.completed_quests:
            continue
        if quest.requires and quest.requires not in player.completed_quests:
            continue
        if not quest.start:
            continue

        start_type = quest.start.get('type')
        start_ref = quest.start.get('ref')

        unlocked = False
        if start_type == trigger_type:
            # NPC quests are handled via talk, so we ignore them here.
            if quest.start.get('type') == 'npc':
                continue
            if isinstance(start_ref, list) and trigger_ref in start_ref:
                unlocked = True
            elif trigger_ref == start_ref:
                unlocked = True

        if unlocked:
            # Auto-offer the quest
            print(f"\nA new quest has become available: \"{quest.name}\"")
            print(f"- {quest.description}")
            reward_item = quest.reward.get('item', 'nothing')
            if not reward_item: reward_item = 'nothing'
            print(f"Reward: {quest.reward.get('xp', 0)} XP, {reward_item}")

            accept = input("Accept? (yes/no) > ").lower()
            if accept == 'yes':
                player.active_quests[quest_name] = copy.deepcopy(quest)
                print(f"Quest accepted: \"{quest_name}\"")
                if 'item' in quest.on_accept and quest.on_accept['item']:
                    item_name = quest.on_accept['item']
                    player.inventory.append(item_name)
                    print(f"You receive a {item_name}.")

                # Immediately check if the quest is already complete
                check_collect_quests(player, quests)
            else:
                print("You have declined the quest.")

def print_combat_banner(player):
    monster = player.current_combat_target
    print(f"\n--- Combat: {monster.name} ({monster.hp} HP) ---")
    print(f"Your HP: {player.hp} / {player.max_hp}")
    print("Available actions: attack, use [item], flee")

def handle_quest_completion(player, quest, quests):
    quest.is_complete = True
    print(f"Quest Complete: {quest.name}")
    if 'xp' in quest.reward:
        player.gain_xp(quest.reward['xp'])
    if 'item' in quest.reward and quest.reward['item']:
        item_name = quest.reward['item']
        player.inventory.append(item_name)
        print(f"You received a {item_name} as a reward.")

    # Notify player if any quests were unlocked by this completion
    if quest.unlocks:
        for unlocked_quest_name in quest.unlocks:
            if unlocked_quest_name in quests:
                unlocked_quest = quests[unlocked_quest_name]
                if unlocked_quest.requires == quest.name:
                     print(f"You feel you can now pursue a new goal: \"{unlocked_quest_name}\"")

def check_collect_quests(player, quests):
    for quest_name, quest in player.active_quests.items():
        if quest.is_complete:
            continue

        goal = quest.goal
        goal_type = goal.get('type')

        if goal_type in ['collect_or_talk', 'collect_or_kill']:
            targets = goal.get('targets', [])

            # Check inventory
            for target in targets:
                if target in player.inventory:
                    quest.progress = goal.get('count', 1)
                    break

            # Check dialogue history for collect_or_talk
            if goal_type == 'collect_or_talk' and not quest.progress:
                 for target in targets:
                    if target in player.dialogue_history:
                        quest.progress = goal.get('count', 1)
                        break

        if quest.progress >= quest.goal.get('count', 1) and not quest.is_complete:
            handle_quest_completion(player, quest, quests)

def handle_monster_turn(player, monster):
    monster_attack = monster.attack_power
    if player.equipped_armor:
        monster_attack = max(0, monster_attack - player.equipped_armor.defense)
    player.hp -= monster_attack
    print(f"{monster.name} attacks you for {monster_attack} damage.")
    print(f"You have {player.hp} HP left.")
    if player.hp <= 0:
        return False
    return True

def main():
    game_data, items, monsters, locations, npcs, quests = load_game_data()
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
    check_quest_availability(player, quests, "location_enter", player.current_location)
    handle_look(locations[player.current_location], npcs, player, quests)
    while True:
        current_loc = locations[player.current_location]
        if player.current_combat_target:
            print_combat_banner(player)
        user_input = input("\n> ").lower().strip()
        if not user_input:
            continue
        parts = user_input.split()
        command = parts[0]
        target_name = " ".join(parts[1:]) if len(parts) > 1 else None
        if player.current_combat_target and command not in ["attack", "use", "flee", "inventory", "status", "quests", "quit", "help"]:
            print("You can't do that while in combat!")
            continue
        if command.isdigit():
            exit_index = int(command) - 1
            if 0 <= exit_index < len(current_loc.exits):
                exit_dest = list(current_loc.exits.values())[exit_index]
                player.previous_location = player.current_location
                player.current_location = exit_dest
                new_loc = locations[player.current_location]
                new_loc.active_monsters = list(new_loc.monsters)
                check_quest_availability(player, quests, "location_enter", new_loc.name)
                handle_look(new_loc, npcs, player, quests)
            else:
                print("Invalid exit number.")
        elif command == "quit":
            print("Thanks for playing!")
            break
        elif command == "look":
            handle_look(current_loc, npcs, player, quests)
        elif command == "get":
            if not target_name:
                print("Get what?")
                continue
            item_to_get = None
            for item_name in current_loc.items:
                if target_name.lower() == item_name.lower():
                    item_to_get = item_name
                    break
            if item_to_get:
                player.inventory.append(item_to_get)
                current_loc.items.remove(item_to_get)
                print(f"You pick up the {item_to_get}.")
                check_quest_availability(player, quests, "item_pickup", item_to_get)
                check_collect_quests(player, quests)
            else:
                print(f"You don't see a {target_name} here.")
        elif command == "examine":
            if not target_name:
                print("Examine what?")
                continue
            item_to_examine = None
            for item_name in player.inventory:
                if target_name.lower() == item_name.lower():
                    item_to_examine = items[item_name]
                    break
            if item_to_examine:
                print(f"You examine the {item_to_examine.name}.")
                print(item_to_examine.description)
                if isinstance(item_to_examine, Readable):
                    print(f"It reads: \"{item_to_examine.lore_text}\"")
                check_quest_availability(player, quests, "item_pickup", item_to_examine.name)
                check_quest_availability(player, quests, "item_or_npc", item_to_examine.name)
            else:
                print(f"You don't have a {target_name}.")
        elif command == "drop":
            if not target_name:
                print("Drop what?")
                continue
            item_to_drop = None
            for item_name in player.inventory:
                if target_name.lower() == item_name.lower():
                    item_to_drop = item_name
                    break
            if item_to_drop:
                player.inventory.remove(item_to_drop)
                current_loc.items.append(item_to_drop)
                print(f"You drop the {item_to_drop}.")
            else:
                print(f"You don't have a {target_name}.")
        elif command == "inventory":
            if not player.inventory:
                print("You are not carrying anything.")
            else:
                print("You are carrying:")
                for item in player.inventory:
                    print(f"  - {item}")
        elif command == "status":
            player.show_status()
        elif command == "quests":
            if not player.active_quests:
                print("You have no active quests.")
            else:
                print("\n--- Active Quests ---")
                for quest_name, quest in player.active_quests.items():
                    print(f"- {quest.name}: {quest.description} ({quest.progress}/{quest.goal.get('count', 1)})")
                print("---------------------")
        elif command == "ask":
            if not target_name:
                print("Ask whom about what?")
                continue

            npc_to_ask = None
            topic = None
            for npc_name in current_loc.npcs:
                if target_name.lower().startswith(npc_name.lower()):
                    npc_to_ask = npcs[npc_name]
                    topic = target_name[len(npc_name):].strip().lower()
                    break

            if npc_to_ask and topic:
                if topic in npc_to_ask.topics:
                    dialogue_key = f"{npc_to_ask.name}:{topic}"
                    player.dialogue_history.add(dialogue_key)
                    print(f'{npc_to_ask.name} says: "{npc_to_ask.topics[topic]}"')
                    check_quest_availability(player, quests, "ask_topic", dialogue_key)
                    check_collect_quests(player, quests)
                else:
                    print(f"{npc_to_ask.name} has nothing to say about {topic}.")
            else:
                print("Ask whom about what? (e.g., ask Wandering Scholar about Elenya)")
        elif command == "talk":
            if not target_name:
                print("Talk to whom?")
                continue
            npc_to_talk = None
            for npc_name in current_loc.npcs:
                if target_name.lower() == npc_name.lower():
                    npc_to_talk = npcs[npc_name]
                    break

            if not npc_to_talk:
                print(f"You don't see {target_name} here.")
                continue

            player.dialogue_history.add(npc_to_talk.name)
            check_collect_quests(player, quests)

            quest_offered = False
            # Iterate through the NPC's quest list in order
            for quest_name in npc_to_talk.quests:
                if quest_name in player.active_quests or quest_name in player.completed_quests:
                    continue

                quest = quests.get(quest_name)
                if not quest: continue
                if quest.requires and quest.requires not in player.completed_quests:
                    continue

                # Found an available quest to offer
                if npc_to_talk.dialogue:
                    print(f'{npc_to_talk.name}: "{npc_to_talk.dialogue[0]}"')

                quest_to_offer = quests[quest_name]
                print(f"Quest offered: \"{quest_to_offer.name}\"")
                print(f"- {quest_to_offer.description}")
                reward_item = quest_to_offer.reward.get('item', 'nothing')
                if not reward_item: reward_item = 'nothing'
                print(f"Reward: {quest_to_offer.reward.get('xp', 0)} XP, {reward_item}")

                accept = input("Accept? (yes/no) > ").lower()
                if accept == 'yes':
                    player.active_quests[quest_name] = copy.deepcopy(quest_to_offer)
                    print(f"Quest accepted: \"{quest_name}\"")
                    if 'item' in quest_to_offer.on_accept and quest_to_offer.on_accept['item']:
                        item_name = quest_to_offer.on_accept['item']
                        player.inventory.append(item_name)
                        print(f"You receive a {item_name}.")

                quest_offered = True
                break # Offer only one quest per interaction

            if not quest_offered:
                # If no quests were offered, give a generic response
                if len(npc_to_talk.dialogue) > 1:
                    # Use a different line for generic talk if available
                    print(f'{npc_to_talk.name}: "{npc_to_talk.dialogue[1]}"')
                elif npc_to_talk.dialogue:
                    # Fallback to the first line if it's the only one
                    print(f'{npc_to_talk.name}: "{npc_to_talk.dialogue[0]}"')
                else:
                    print(f"{npc_to_talk.name} has nothing more to say.")
        elif command == "equip":
            if not target_name:
                print("Equip what?")
                continue
            item_to_equip = None
            for item_name in player.inventory:
                if target_name.lower() == item_name.lower():
                    item_to_equip = items[item_name]
                    break
            if item_to_equip:
                if isinstance(item_to_equip, Weapon):
                    if player.equipped_weapon:
                        player.inventory.append(player.equipped_weapon.name)
                    player.equipped_weapon = item_to_equip
                    player.inventory.remove(item_to_equip.name)
                    print(f"You equipped the {item_to_equip.name}.")
                elif isinstance(item_to_equip, Armor):
                    if player.equipped_armor:
                        player.inventory.append(player.equipped_armor.name)
                    player.equipped_armor = item_to_equip
                    player.inventory.remove(item_to_equip.name)
                    print(f"You equipped the {item_to_equip.name}.")
                else:
                    print("You can't equip that.")
            else:
                print(f"You don't have a {target_name}.")
        elif command == "unequip":
            if not target_name:
                print("Unequip what? (weapon/armor)")
                continue
            if target_name == "weapon":
                if player.equipped_weapon:
                    item_name = player.equipped_weapon.name
                    player.inventory.append(item_name)
                    player.equipped_weapon = None
                    print(f"You unequipped the {item_name}.")
                else:
                    print("You have no weapon equipped.")
            elif target_name == "armor":
                if player.equipped_armor:
                    item_name = player.equipped_armor.name
                    player.inventory.append(item_name)
                    player.equipped_armor = None
                    print(f"You unequipped the {item_name}.")
                else:
                    print("You have no armor equipped.")
            else:
                print("You can only unequip 'weapon' or 'armor'.")
        elif command == "use":
            if not target_name:
                print("Use what?")
                continue
            item_to_use = None
            for item_name in player.inventory:
                if target_name.lower() == item_name.lower():
                    item_to_use = items[item_name]
                    break
            if item_to_use and isinstance(item_to_use, Potion):
                player.hp += item_to_use.heal_amount
                if player.hp > player.max_hp:
                    player.hp = player.max_hp
                player.inventory.remove(item_to_use.name)
                print(f"You used the {item_to_use.name} and healed for {item_to_use.heal_amount} HP.")
                print(f"You now have {player.hp}/{player.max_hp} HP.")
                if player.current_combat_target:
                    if not handle_monster_turn(player, player.current_combat_target):
                        print("You have been defeated. Game over.")
                        break
            else:
                print("You can't use that.")
        elif command == "flee":
            if not player.current_combat_target:
                print("You are not in combat.")
                continue
            monster = player.current_combat_target
            player.current_location = player.previous_location
            player.current_combat_target = None
            print("You attempt to flee...")
            print(f"You barely escape the {monster.name}!")
            input("\n[Press Enter to continue]")
            handle_look(locations[player.current_location], npcs)
        elif command == "attack":
            if not target_name:
                print("Attack what?")
                continue
            monster_to_attack = None
            if player.current_combat_target:
                if target_name.lower() != player.current_combat_target.name.lower():
                    print(f"You are already in combat with {player.current_combat_target.name}!")
                    continue
                monster_to_attack = player.current_combat_target
            else:
                monster_name_to_attack = None
                for monster_name in current_loc.active_monsters:
                    if target_name.lower() == monster_name.lower():
                        monster_name_to_attack = monster_name
                        break
                if not monster_name_to_attack:
                    print(f"You don't see a {target_name} here.")
                    continue
                monster_prototype = monsters[monster_name_to_attack]
                monster_to_attack = copy.deepcopy(monster_prototype)
                player.current_combat_target = monster_to_attack
                print("--- Combat Started ---")
                print(f"You engage the {monster_to_attack.name} in combat!")
            player_attack = player.get_attack_power()
            monster_to_attack.hp -= player_attack
            print(f"You attack the {monster_to_attack.name} for {player_attack} damage.")
            if monster_to_attack.hp <= 0:
                defeated_monster = monster_to_attack
                print(f"You defeated the {defeated_monster.name}!")
                current_loc.active_monsters.remove(defeated_monster.name)
                player.gain_xp(defeated_monster.xp)
                for quest in player.active_quests.values():
                    # Handle main goal
                    if quest.goal.get('type') == 'kill' and quest.goal.get('target') == defeated_monster.name:
                        quest.progress += 1
                    # Handle alternate goal
                    if quest.alternate_goal and quest.alternate_goal.get('type') == 'kill' and quest.alternate_goal.get('target') == defeated_monster.name:
                        # For alternate goals, we can just mark the quest as complete directly if the count is met.
                        # This is a simplification for the "Clear the Catacombs" quest.
                        quest.progress += quest.alternate_goal.get('count', 1)

                    # Check for completion
                    goal_count = quest.goal.get('count', 1)
                    if quest.alternate_goal and quest.alternate_goal.get('type') == 'kill':
                        # Special handling for "Clear the Catacombs"
                        if quest.goal.get('target') == 'Skeleton' and defeated_monster.name == 'Undead Wight':
                             # Killing one Undead Wight completes the quest
                             quest.progress = goal_count

                    if quest.progress >= goal_count and not quest.is_complete:
                        handle_quest_completion(player, quest, quests)
                    elif not quest.is_complete:
                        print(f"Quest progress: {quest.name} ({quest.progress}/{goal_count})")
                completed = [name for name, quest in player.active_quests.items() if quest.is_complete]
                for name in completed:
                    player.completed_quests.append(name)
                    del player.active_quests[name]
                if defeated_monster.loot:
                    for loot_item in defeated_monster.loot:
                        current_loc.items.append(loot_item)
                        print(f"The {defeated_monster.name} dropped a {loot_item}.")
                player.current_combat_target = None
            else:
                print(f"{monster_to_attack.name} has {monster_to_attack.hp} HP left.")
                if not handle_monster_turn(player, monster_to_attack):
                    player.current_combat_target = None
                    break
        elif command == "help":
            print_help()
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
