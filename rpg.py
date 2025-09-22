import json
import os
import time

# --- Utility Functions ---

def clear_screen():
    """Clears the console screen."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def pause():
    """Pauses the game and waits for user input."""
    input("\nPress Enter to continue...")

# --- Core Classes ---

class Player:
    """Represents the player character."""
    def __init__(self, name, hp, current_location):
        self.name = name
        self.hp = hp
        self.current_location = current_location
        self.inventory = []

class Location:
    """Represents a location in the game world."""
    def __init__(self, name, description, exits, items, monsters):
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items
        self.monsters = monsters

class Item:
    """Represents an item that can be found or used."""
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Monster:
    """Represents a monster that can be fought."""
    def __init__(self, name, hp, attack_power, loot):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.loot = loot

# --- Game Class ---

class Game:
    """Manages the overall game state, data, and main loop."""
    def __init__(self, data_file='game_data.json'):
        self.locations = {}
        self.items = {}
        self.monster_blueprints = {}
        self.player = None
        self.player_start_location_name = None
        self.load_game_data(data_file)
        self.setup_player()

    def load_game_data(self, data_file):
        """Loads all game data from the JSON file."""
        with open(data_file, 'r') as f:
            data = json.load(f)

        # Load items
        for item_name, item_data in data['items'].items():
            self.items[item_name] = Item(
                name=item_name,
                description=item_data['description']
            )

        # Load monster blueprints
        for monster_name, monster_data in data['monsters'].items():
            self.monster_blueprints[monster_name] = monster_data

        # Load locations
        for loc_name, loc_data in data['locations'].items():
            self.locations[loc_name] = Location(
                name=loc_name,
                description=loc_data['description'],
                exits=loc_data['exits'],
                items=loc_data['items'][:],
                monsters=loc_data['monsters'][:]
            )

        self.player_start_location_name = data['player_start']

    def setup_player(self):
        """Initializes the player character at the start location."""
        start_loc_name = self.player_start_location_name
        start_location = self.locations[start_loc_name]
        self.player = Player(name="Hero", hp=20, current_location=start_location)

    def run(self):
        """Starts and runs the main game loop."""
        clear_screen()
        print("Welcome to the world of Eryndral!")
        print("Your quest begins...")
        pause()

        self.game_is_running = True
        while self.game_is_running:
            self.show_current_location()
            self.prompt_for_action()

        print("\nGame has ended. Thanks for playing!")

    def show_current_location(self):
        """Displays the details of the player's current location."""
        clear_screen()
        location = self.player.current_location
        print(f"📍 {location.name}")
        print(f"  {location.description}")

        # Display items
        if location.items:
            print("\nItems here: " + ", ".join(item.capitalize() for item in location.items))

        # Display monsters
        if location.monsters:
            print("\nMonsters: " + ", ".join(monster.capitalize() for monster in location.monsters))

        # Display exits
        print("\nExits:")
        self.exit_map = {str(i+1): direction for i, direction in enumerate(location.exits.keys())}
        for num, direction in self.exit_map.items():
            destination = location.exits[direction]
            print(f"  {num}. {direction.capitalize()} → {destination}")

    def prompt_for_action(self):
        """Gets and processes the player's next action."""
        try:
            command = input("\n> ").lower().strip()
            if not command:
                return

            self.parse_command(command)
        except (EOFError, KeyboardInterrupt):
            self.game_is_running = False
            print("\n\nIt seems you have vanished from this world. Farewell.")

    def parse_command(self, command):
        """Parses and acts on the player's command."""
        if command in ["quit", "exit"]:
            self.game_is_running = False
            print("\nYou feel a strange pull, as if leaving this reality behind...")
            return

        if command in self.exit_map:
            direction = self.exit_map[command]
            self.move_player(direction)
            return

        parts = command.split()
        verb = parts[0]
        target = " ".join(parts[1:]) if len(parts) > 1 else None

        action_requires_pause = True
        if verb == "look":
            # The loop already shows the location, so we just let it refresh.
            action_requires_pause = False
        elif verb == "inventory":
            self.show_inventory()
        elif verb == "get":
            if target:
                self.get_item(target)
            else:
                print("What do you want to get?")
        elif verb == "drop":
            if target:
                self.drop_item(target)
            else:
                print("What do you want to drop?")
        elif verb == "attack":
            if target:
                self.start_combat(target)
                action_requires_pause = False # Combat handles its own pausing
            else:
                print("Who do you want to attack?")
        else:
            print("I don't understand that command.")

        if action_requires_pause:
            pause()

    def move_player(self, direction):
        """Moves the player to a new location."""
        current_location = self.player.current_location
        destination_name = current_location.exits[direction]
        if destination_name in self.locations:
            self.player.current_location = self.locations[destination_name]
            print(f"\nYou move {direction}.")
        else:
            print(f"Error: The path to {destination_name} seems to be blocked.")

    def show_inventory(self):
        """Displays the player's inventory."""
        if not self.player.inventory:
            print("You are not carrying anything.")
        else:
            print("You are carrying:")
            for item_name in self.player.inventory:
                print(f"- {item_name.capitalize()}")

    def get_item(self, item_name):
        """Allows the player to pick up an item."""
        location = self.player.current_location
        item_to_get = next((name for name in location.items if name.lower() == item_name.lower()), None)

        if item_to_get:
            location.items.remove(item_to_get)
            self.player.inventory.append(item_to_get)
            print(f"You pick up the {item_to_get}.")
        else:
            print(f"You don't see a {item_name} here.")

    def drop_item(self, item_name):
        """Allows the player to drop an item."""
        item_to_drop = next((name for name in self.player.inventory if name.lower() == item_name.lower()), None)

        if item_to_drop:
            self.player.inventory.remove(item_to_drop)
            self.player.current_location.items.append(item_to_drop)
            print(f"You drop the {item_to_drop}.")
        else:
            print(f"You don't have a {item_name}.")

    def start_combat(self, monster_name):
        """Initiates and manages combat with a monster."""
        location = self.player.current_location
        monster_to_fight_name = next((name for name in location.monsters if name.lower() == monster_name.lower()), None)

        if not monster_to_fight_name:
            print(f"There is no {monster_name} here to fight.")
            pause()
            return

        blueprint = self.monster_blueprints[monster_to_fight_name]
        monster = Monster(
            name=monster_to_fight_name, hp=blueprint['hp'],
            attack_power=blueprint['attack_power'], loot=blueprint['loot']
        )

        print(f"\nA wild {monster.name} appears and attacks!")
        pause()

        player_attack_power = 3

        while self.player.hp > 0 and monster.hp > 0:
            clear_screen()
            print(f"--- Combat: You vs. {monster.name} ---")
            print(f"Your HP: {self.player.hp} | {monster.name}'s HP: {monster.hp}\n")

            # Player's turn
            print(f"You attack the {monster.name} for {player_attack_power} damage.")
            monster.hp -= player_attack_power
            if monster.hp <= 0:
                print(f"\nYou have defeated the {monster.name}!")
                location.monsters.remove(monster.name)
                if monster.loot:
                    location.items.extend(monster.loot)
                    print(f"The {monster.name} dropped: {', '.join(monster.loot)}")
                pause()
                break

            print(f"{monster.name} has {monster.hp} HP left.")
            pause()

            # Monster's turn
            print(f"\n{monster.name} attacks you for {monster.attack_power} damage.")
            self.player.hp -= monster.attack_power
            if self.player.hp <= 0:
                print("\nYou have been defeated...")
                print("--- GAME OVER ---")
                self.game_is_running = False
                pause()
                break

            print(f"You have {self.player.hp} HP left.")
            pause()


# --- Main Game Logic ---

def main():
    """The main function to run the game."""
    try:
        game = Game()
        game.run()
    except FileNotFoundError:
        print("Error: game_data.json not found. Make sure it's in the same directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
