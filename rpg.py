import json
import os
import random
import time
import copy

class Player:
    def __init__(self, name, hp, current_location, inventory=None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.current_location = current_location
        self.previous_location = current_location
        self.inventory = inventory if inventory is not None else []
        self.xp = 0
        self.level = 1
        self.attack_power = 1
        self.equipped_weapon = None
        self.equipped_armor = None
        self.active_quests = {}
        self.completed_quests = []
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
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Weapon(Item):
    def __init__(self, name, description, damage):
        super().__init__(name, description)
        self.damage = damage

class Armor(Item):
    def __init__(self, name, description, defense):
        super().__init__(name, description)
        self.defense = defense

class Potion(Item):
    def __init__(self, name, description, heal_amount):
        super().__init__(name, description)
        self.heal_amount = heal_amount

class Monster:
    def __init__(self, name, hp, attack_power, loot=None, xp=0):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.loot = loot if loot is not None else []
        self.xp = xp

class NPC:
    def __init__(self, name, dialogue=None, quests=None):
        self.name = name
        self.dialogue = dialogue if dialogue is not None else []
        self.quests = quests if quests is not None else []

class Quest:
    def __init__(self, name, description, goal, reward, on_accept=None):
        self.name = name
        self.description = description
        self.goal = goal
        self.reward = reward
        self.on_accept = on_accept if on_accept is not None else {}
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
        else:
            items[name] = Item(name=name, **details)
    monsters = {name: Monster(name=name, **details) for name, details in data['monsters'].items()}
    npcs = {name: NPC(name=name, **details) for name, details in data.get('npcs', {}).items()}
    quests = {name: Quest(name=name, **details) for name, details in data.get('quests', {}).items()}
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
    print("  - talk [npc]: Talk to an NPC")
    print("  - quests: View your active quests")
    print("  - help: Show this help screen")
    print("  - quit: Exit the game")

def show_location(location, npcs):
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
    location_npcs = [npc.name for npc in npcs.values() if npc.name in location.npcs]
    print(f"You see: {', '.join(location_npcs) if location_npcs else 'no one special'}")

def handle_look(location, npcs):
    clear_screen()
    show_location(location, npcs)

def print_combat_banner(player):
    monster = player.current_combat_target
    print(f"\n--- Combat: {monster.name} ({monster.hp} HP) ---")
    print(f"Your HP: {player.hp} / {player.max_hp}")
    print("Available actions: attack, use [item], flee")

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
    player = Player("Player", 20, game_data['player_start'])
    handle_look(locations[player.current_location], npcs)
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
                handle_look(new_loc, npcs)
            else:
                print("Invalid exit number.")
        elif command == "quit":
            print("Thanks for playing!")
            break
        elif command == "look":
            handle_look(current_loc, npcs)
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
            else:
                print(f"You don't see a {target_name} here.")
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
                    print(f"- {quest.name}: {quest.description} ({quest.progress}/{quest.goal['count']})")
                print("---------------------")
        elif command == "talk":
            if not target_name:
                print("Talk to whom?")
                continue
            npc_to_talk = None
            for npc_name in current_loc.npcs:
                if target_name.lower() == npc_name.lower():
                    npc_to_talk = npcs[npc_name]
                    break
            if npc_to_talk:
                for line in npc_to_talk.dialogue:
                    print(f'{npc_to_talk.name}: "{line}"')
                for quest_name in npc_to_talk.quests:
                    if quest_name not in player.active_quests and quest_name not in player.completed_quests:
                        quest_to_offer = quests[quest_name]
                        print(f"Quest offered: \"{quest_to_offer.name}\"")
                        print(f"- {quest_to_offer.description}")
                        print(f"Reward: {quest_to_offer.reward.get('xp', 0)} XP, {quest_to_offer.reward.get('item', 'nothing')}")
                        accept = input("Accept? (yes/no) > ").lower()
                        if accept == 'yes':
                            player.active_quests[quest_name] = quest_to_offer
                            print(f"Quest accepted: \"{quest_name}\"")
                            if 'item' in quest_to_offer.on_accept:
                                item_name = quest_to_offer.on_accept['item']
                                player.inventory.append(item_name)
                                print(f"You receive a {item_name}.")
            else:
                print(f"You don't see {target_name} here.")
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
                    if quest.goal['type'] == 'kill' and quest.goal['target'] == defeated_monster.name:
                        quest.progress += 1
                        print(f"Quest progress: {quest.name} ({quest.progress}/{quest.goal['count']})")
                        if quest.progress >= quest.goal['count']:
                            quest.is_complete = True
                            print(f"Quest Complete: {quest.name}")
                            if 'xp' in quest.reward:
                                player.gain_xp(quest.reward['xp'])
                            if 'item' in quest.reward:
                                item_name = quest.reward['item']
                                player.inventory.append(item_name)
                                print(f"You received a {item_name} as a reward.")
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
