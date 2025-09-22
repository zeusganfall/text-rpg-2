import json
import os
import random
import time

class Player:
    def __init__(self, name, hp, current_location, inventory=None):
        self.name = name
        self.hp = hp
        self.current_location = current_location
        self.inventory = inventory if inventory is not None else []

class Location:
    def __init__(self, name, description, exits, items=None, monsters=None):
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items if items is not None else []
        self.monsters = monsters if monsters is not None else []

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Monster:
    def __init__(self, name, hp, attack_power, loot=None):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.loot = loot if loot is not None else []

# --- Data Loading ---
def load_game_data(filepath="game_data.json"):
    with open(filepath, 'r') as f:
        data = json.load(f)

    items = {name: Item(name=name, **details) for name, details in data['items'].items()}
    monsters = {name: Monster(name=name, **details) for name, details in data['monsters'].items()}
    locations = {name: Location(name=name, **details) for name, details in data['locations'].items()}

    return data, items, monsters, locations

# --- Helper Functions ---
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
    print("  - help: Show this help screen")
    print("  - quit: Exit the game")

def handle_look(location):
    clear_screen()
    print(f"📍 {location.name}")
    print(location.description)

    print("Exits:")
    if not location.exits:
        print("  None")
    else:
        for i, (direction, dest) in enumerate(location.exits.items(), 1):
            print(f"  {i}. {direction.capitalize()} → {dest}")

    print(f"Items: {', '.join(location.items) if location.items else 'none'}")
    print(f"Monsters: {', '.join(location.monsters) if location.monsters else 'none'}")

# --- Game Loop ---
def main():
    game_data, items, monsters, locations = load_game_data()
    player = Player("Player", 20, game_data['player_start']) # Increased HP for better survival

    handle_look(locations[player.current_location])

    while True:
        current_loc = locations[player.current_location]
        user_input = input("\n> ").lower().strip()
        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0]
        target_name = " ".join(parts[1:]) if len(parts) > 1 else None

        if command.isdigit():
            exit_index = int(command) - 1
            if 0 <= exit_index < len(current_loc.exits):
                exit_dest = list(current_loc.exits.values())[exit_index]
                player.current_location = exit_dest
                handle_look(locations[player.current_location])
            else:
                print("Invalid exit number.")

        elif command == "quit":
            print("Thanks for playing!")
            break

        elif command == "look":
            handle_look(current_loc)

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

        elif command == "attack":
            if not target_name:
                print("Attack what?")
                continue

            monster_to_attack = None
            for monster_name in current_loc.monsters:
                if target_name.lower() == monster_name.lower():
                    monster_to_attack = monsters[monster_name]
                    break

            if monster_to_attack:
                # Simple combat
                player_attack = random.randint(1, 5) # Player has no weapon yet
                monster_attack = monster_to_attack.attack_power

                monster_to_attack.hp -= player_attack
                print(f"You attack the {monster_to_attack.name} for {player_attack} damage.")

                if monster_to_attack.hp <= 0:
                    print(f"You defeated the {monster_to_attack.name}!")
                    current_loc.monsters.remove(monster_to_attack.name)
                    if monster_to_attack.loot:
                        for loot_item in monster_to_attack.loot:
                            current_loc.items.append(loot_item)
                            print(f"The {monster_to_attack.name} dropped a {loot_item}.")
                    # Restore monster HP for next encounter from the original data
                    monster_to_attack.hp = game_data['monsters'][monster_to_attack.name]['hp']
                else:
                    print(f"{monster_to_attack.name} has {monster_to_attack.hp} HP left.")
                    player.hp -= monster_attack
                    print(f"{monster_to_attack.name} attacks you for {monster_attack} damage.")
                    print(f"You have {player.hp} HP left.")
                    if player.hp <= 0:
                        print("You have been defeated. Game over.")
                        break # End game
            else:
                print(f"You don't see a {target_name} here.")

        elif command == "help":
            print_help()

        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
