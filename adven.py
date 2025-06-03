# game_engine.py
# Member 1: Game Engine & Core Logic

import world # Member 2's module
import items # Member 3's module
import puzzles # Member 4's module
import ui # Member 5's module

class Player:
    def __init__(self, start_room_id):
        self.current_room_id = start_room_id
        self.inventory = [] # List of item IDs or item objects
        self.game_flags = {} # For tracking game state, e.g., {"met_wizard": True}
        # Add more player attributes: health, score, etc. (adds ~5-10 lines)

    def has_item(self, item_id):
        return item_id in [item.id for item in self.inventory] # Assuming inventory stores item objects

    def add_item(self, item_object):
        self.inventory.append(item_object)
        ui.display_text(f"You picked up {item_object.name}.")

i
    def remove_item(self, item_object):
        if item_object in self.inventory:
            self.inventory.remove(item_object)
            # Potentially add a message here
        
    # Add more player methods: check_flag, set_flag, etc. (adds ~10 lines)
    def parse_command(command_str, player, current_room_data):
    """
    Parses the player's command and calls appropriate handler functions.
    Expected to grow significantly with more commands. (adds ~50-70 lines for full parsing)
    """
    command = command_str.lower().split()
    if not command:
        ui.display_text("Please enter a command.")
        return

    action = command[0]
    target = " ".join(command[1:]) if len(command) > 1 else None

    if action in ["go", "move"]:
        handle_movement(player, target, current_room_data)
    elif action in ["look", "examine"]:
        if target:
            # Look at a specific item or feature
            item_in_room = current_room_data.get_item_by_name(target)
            item_in_inventory = next((item for item in player.inventory if item.name.lower() == target.lower()), None)
            if item_in_room:
                 ui.display_text(item_in_room.description)
            elif item_in_inventory:
                 ui.display_text(item_in_inventory.description)
            elif target.lower() == "around" or target.lower() == current_room_data.name.lower():
                ui.display_room_description(current_room_data, player)
            else:
                ui.display_text(f"You don't see '{target}' here.")
        else:
            # Generic "look around"
            ui.display_room_description(current_room_data, player)
    elif action in ["take", "get", "pickup"]:
        handle_take_item(player, target, current_room_data)
    elif action in ["drop"]:
        handle_drop_item(player, target, current_room_data)
    elif action in ["inventory", "i"]:
        ui.display_inventory(player)
    elif action in ["use"]:
        handle_use_item(player, target, current_room_data)
    elif action == "talk" and target: # Example for puzzle/NPC interaction
        puzzles.handle_talk_npc(player, target, current_room_data)
    elif action == "help":
        ui.display_help()
    elif action == "quit":
        return "quit"
    else:
        ui.display_text("I don't understand that command.")
    # Add more command handling: 'use item on target', 'open door', 'talk to character' etc.
    return None # Continue game
def handle_movement(player, direction, current_room_data):
    """Handles player movement."""
    if direction in current_room_data.exits:
        next_room_id = current_room_data.exits[direction]
        # Check for locked doors/puzzle conditions before moving
        if puzzles.can_player_enter(player, current_room_data.id, next_room_id):
            player.current_room_id = next_room_id
            ui.display_text(f"You go {direction}.")
            # Potentially trigger room entry events here
        else:
            ui.display_text(puzzles.get_block_message(player, current_room_data.id, next_room_id) or "Something blocks your way.")
    else:
        ui.display_text("You can't go that way.")
    # Add more logic for locked exits, conditional movement (adds ~10-15 lines)

def handle_take_item(player, item_name, current_room_data):
    """Handles taking an item from the room."""
    if not item_name:
        ui.display_text("Take what?")
        return
    item_to_take = current_room_data.get_item_by_name(item_name)
    if item_to_take and item_to_take.takeable:
        player.add_item(item_to_take)
        current_room_data.remove_item(item_to_take)
    elif item_to_take and not item_to_take.takeable:
        ui.display_text(f"You can't take the {item_name}.")
    else:
        ui.display_text(f"You don't see '{item_name}' here.")
    # Add logic for item weight, inventory limits etc. (adds ~5-10 lines)

def handle_drop_item(player, item_name, current_room_data):
    """Handles dropping an item into the room."""
    if not item_name:
        ui.display_text("Drop what?")
        return
    item_to_drop = next((item for item in player.inventory if item.name.lower() == item_name.lower()), None)
    if item_to_drop:
        player.remove_item(item_to_drop)
        current_room_data.add_item(item_to_drop) # Add to room's item list
        ui.display_text(f"You dropped {item_to_drop.name}.")
    else:
        ui.display_text(f"You don't have '{item_name}' in your inventory.")
    # Add more logic here (adds ~5 lines)

def handle_use_item(player, item_name_with_target, current_room_data):
    """Handles using an item, possibly on something."""
    if not item_name_with_target:
        ui.display_text("Use what? And on what (optional)?")
        return

    parts = item_name_with_target.split(" on ", 1)
    item_name = parts[0]
    target_name = parts[1] if len(parts) > 1 else None

    item_to_use = next((item for item in player.inventory if item.name.lower() == item_name.lower()), None)

    if not item_to_use:
        ui.display_text(f"You don't have a {item_name}.")
        return

    # This is where interaction with puzzles module is crucial
    puzzles.try_use_item_puzzle(player, item_to_use, target_name, current_room_data)
    # The puzzles module will handle success/failure messages and state changes
    # Add more general item use logic if not puzzle-related (adds ~15-20 lines)
def game_loop():
    """Main game loop."""
    ui.display_welcome()
    player = Player(start_room_id='hall') # Starting room ID

    # Load all game data
    world.load_world_data() # Member 2
    items.load_item_data()   # Member 3
    puzzles.load_puzzle_data() # Member 4
    # (UI text is mostly loaded by Member 5's module itself or on demand)

    while True:
        current_room_data = world.get_room(player.current_room_id)
        if not current_room_data:
            ui.display_text("Error: You are in an unknown void. Quitting.")
            break
        
        # Display room description first time or if "look" is typed
        # For now, let's display it every time a room is entered by movement.
        # A more sophisticated approach would track if the room is "new" to the player.
        if not hasattr(player, 'last_room_id') or player.last_room_id != player.current_room_id:
            ui.display_room_description(current_room_data, player)
            player.last_room_id = player.current_room_id


        command_str = ui.get_player_input("> ")
        if not command_str: # Handle empty input after prompt
            continue

        result = parse_command(command_str, player, current_room_data)

        if result == "quit":
            ui.display_text("Thanks for playing!")
            break
        
        # Check for game win/lose conditions
        if puzzles.check_win_condition(player):
            ui.display_win_message() # Define in UI
            break
        if puzzles.check_lose_condition(player): # Define in Puzzles
            ui.display_lose_message() # Define in UI
            break
        
        # Add more complex game state updates after each command (adds ~10-20 lines)

if __name__ == "__main__":
    # This check ensures the game_loop runs only when game_engine.py is executed directly.
    # It's good practice for making modules reusable.
    game_loop()
    def _init_(self, id, name, description, exits=None, item_ids=None, puzzle_triggers=None, features=None):
        self.id = id
        self.name = name
        self.description_default = description # Base description
        self.exits = exits if exits else {} # e.g., {"north": "kitchen", "south": "garden"}
        self.item_ids_in_room = item_ids if item_ids else [] # List of item IDs
        self.items_in_room = [] # Will hold actual Item objects
        self.puzzle_triggers = puzzle_triggers if puzzle_triggers else {} # e.g., {"examine_statue": "statue_puzzle_id"}
        self.features = features if features else {} # e.g., {"statue": "A stone statue stands here."}
        # Add more room attributes: light level, special properties, visited flag etc. (adds ~5-10 lines)

    def get_dynamic_description(self, player):
        """Generates description based on room state, player actions, puzzles solved."""
        desc = self.description_default
        # Add logic for changing description based on game flags or solved puzzles (adds ~10-15 lines)
        # e.g., if player.game_flags.get("unlocked_secret_passage_in_hall"):
        #    desc += "\nA newly revealed passage gapes in the west wall."

        # List visible items
        if self.items_in_room:
            desc += "\nYou see here: " + ", ".join([item.name for item in self.items_in_room]) + "."

        # List features
        if self.features:
            desc += "\nNotable features: " + ", ".join(self.features.keys()) + "."
        return desc

    def add_item(self, item_obj):
        self.items_in_room.append(item_obj)

    def remove_item(self, item_obj):
        if item_obj in self.items_in_room:
            self.items_in_room.remove(item_obj)

    def get_item_by_name(self, item_name):
        for item_obj in self.items_in_room:
            if item_obj.name.lower() == item_name.lower():
                return item_obj
        return None

    # Add more room methods: on_enter, on_exit, check_feature (adds ~10-15 lines)


# Global dictionary to store all room objects, keyed by room_id
GAME_MAP = {}

def load_world_data():
    """
    Populates the GAME_MAP with Room objects.
    This is where the actual game world is defined.
    Expected to be one of the largest data definition areas. (adds ~50-80 lines for a decent map)
    """
    global GAME_MAP
    GAME_MAP = {
        'hall': Room(
            id='hall',
            name="Grand Hall",
            description="You are in a dusty Grand Hall. Cobwebs hang from the ceiling.",
            exits={"north": "kitchen", "east": "library_door"},
            item_ids=['key_rusty', 'note_crumpled'], # Item IDs to be resolved
            features={"chandelier": "A large, tarnished chandelier hangs precariously."}
        ),
        'kitchen': Room(
            id='kitchen',
            name="Messy Kitchen",
            description="The kitchen is a mess. Pots and pans are strewn everywhere.",
            exits={"south": "hall"},
            item_ids=['apple_red'],
            puzzle_triggers={"open_cupboard": "cupboard_puzzle"}
        ),
        'library_door': Room(
            id='library_door',
            name="Library Entrance",
            description="A large oak door blocks the way to the east. It seems locked.",
            exits={"west": "hall"}, # East exit to 'library' would be conditional (puzzle)
            # This room might have a puzzle associated with opening the door to 'library'
        ),
        'library': Room(
            id='library',
            name="Dusty Library",
            description="Rows of ancient books line the walls. A faint scent of old paper fills the air.",
            exits={"west": "library_door"}, # Assuming door opens back this way
            item_ids=['book_ancient', 'scroll_sealed']
        ),
        # Add many more rooms, connections, and details...
    }

    # After defining rooms with item_ids, resolve them to actual item objects
    # This requires the item_manager (Member 3's module) to be loaded or accessible
    for room_id, room_obj in GAME_MAP.items():
        for item_id in room_obj.item_ids_in_room:
            item_obj_actual = item_manager.get_item_by_id(item_id)
            if item_obj_actual:
                room_obj.items_in_room.append(item_obj_actual)
            else:
                print(f"Warning: Item ID '{item_id}' in room '{room_id}' not found in item definitions.")

    # You would also link puzzles to rooms/features here if not done directly in Room constructor
    # puzzles.link_puzzles_to_world(GAME_MAP) # A function in puzzles.py

def get_room(room_id):
    """Returns the Room object for a given room_id."""
    return GAME_MAP.get(room_id)

# Add functions for map display (text-based), checking connections, etc. (adds ~10-20 lines)

if _name_ == '_main_':
    # Example of how to test this module independently
    load_world_data()
    item_manager.load_item_data() # Need items for rooms to populate correctly for testing

    hall = get_room('hall')
    if hall:
        print(f"Welcome to the {hall.name}")
        print(hall.get_dynamic_description(None)) # Pass a dummy player or None for basic test
        print("Exits:", hall.exits)
        print("Items initially in hall:", [item.name for item in hall.items_in_room])

    kitchen = get_room('kitchen')
    if kitchen:
        print(f"\nMoving to {kitchen.name}")
        print(kitchen.get_dynamic_description(None))
# items.py
# Member 3: Items & Inventory System

class Item:
    def __init__(self, id, name, description, takeable=True, use_effect=None, use_message=None, properties=None):
        self.id = id
        self.name = name
        self.description = description # Detailed description when examined
        self.takeable = takeable # Can the player pick this up?
        self.use_effect = use_effect # A function or identifier for its effect when used
        self.use_message = use_message # Message displayed when used (if no complex effect)
        self.properties = properties if properties else {} # e.g., {"edible": True, "unlocks": "library_door_puzzle"}
        # Add more item attributes: weight, value, charges, etc. (adds ~5-10 lines)

    def on_use(self, player, target_obj_name=None, current_room=None):
        """
        Called when an item is used.
        This might interact with the puzzle system or change player/world state.
        """
        if self.use_message:
            # ui.display_text(self.use_message) # Would need ui module import
            print(self.use_message) # For standalone testing

        if self.use_effect:
            # The actual effect logic might be better handled in the puzzles.py
            # or game_engine.py to keep item definitions clean.
            # For now, just indicate it has an effect.
            # This function could return a status or data for the engine.
            print(f"The {self.name} has a special effect: {self.use_effect}")
            return {"effect_handled": True, "details": self.use_effect}
        return {"effect_handled": False}
    
    # Add more item methods: combine_with, inspect_details (adds ~5-10 lines)

# Global dictionary to store all item definitions, keyed by item_id
ALL_ITEMS = {}

def load_item_data():
    """
    Populates the ALL_ITEMS with Item objects.
    This is where all game items are defined.
    Expected to be a significant data definition area. (adds ~50-80 lines for many items)
    """
    global ALL_ITEMS
    ALL_ITEMS = {
        'key_rusty': Item(
            id='key_rusty',
            name="rusty key",
            description="A small, very rusty key. It looks like it might fit an old lock.",
            properties={"unlocks_puzzle": "library_door_puzzle"} # Custom property
        ),
        'note_crumpled': Item(
            id='note_crumpled',
            name="crumpled note",
            description="'The treasure is hidden where the sun doesn't shine indoors,' it reads.",
            use_message="You read the note again. It's cryptic."
        ),
        'apple_red': Item(
            id='apple_red',
            name="red apple",
            description="A shiny red apple. Looks delicious.",
            takeable=True,
            use_message="You eat the apple. It's crisp and refreshing!",
            properties={"edible": True}
            # use_effect could potentially restore health if player has health attribute
        ),
        'book_ancient': Item(
            id='book_ancient',
            name="ancient book",
            description="A heavy tome bound in cracked leather. The title is unreadable.",
            takeable=True,
            use_message="You try to read the book, but the language is unknown to you."
            # Could trigger a puzzle or reveal info if player has 'translation_skill' flag
        ),
        'scroll_sealed': Item(
            id='scroll_sealed',
            name="sealed scroll",
            description="A parchment scroll, tightly rolled and sealed with wax.",
            takeable=True,
            # use_effect could be 'unseal_scroll_puzzle'
        ),
        # Add many more items...
    }

def get_item_by_id(item_id):
    """Returns the Item object for a given item_id."""
    return ALL_ITEMS.get(item_id)

# Add functions for managing player inventory (these might be better in Player class in game_engine.py,
# but item-specific checks could reside here)
# e.g., check_if_item_is_usable(item_id), get_item_property(item_id, prop_name) (adds ~10-15 lines)

if __name__ == '__main__':
    # Example of how to test this module independently
    load_item_data()
    
    key = get_item_by_id('key_rusty')
    if key:
        print(f"Item: {key.name}, Desc: {key.description}, Takeable: {key.takeable}")
        key.on_use(None) # Pass dummy player

    apple = get_item_by_id('apple_red')
    if apple:
        print(f"Item: {apple.name}, Desc: {apple.description}, Takeable: {apple.takeable}")
        apple.on_use(None)
        # ui.py
# Member 5: Story, Dialogue & User Interface

import textwrap # For formatting long lines of text

# Store major text blocks here. Smaller ones might be in their respective objects (Item, Room).
WELCOME_MESSAGE = """
Welcome, brave adventurer, to the Mysteries of Eldoria!
Darkness has fallen upon the land, and only you can uncover the secrets hidden within.
Type 'help' for a list of commands. Good luck!
"""

HELP_TEXT = """
Available commands:
  go [direction]     - Move north, south, east, west, up, down.
  look / look around - Examine your current surroundings.
  look at [object/feature] - Examine something specific.
  take [item]        - Pick up an item from the room.
  drop [item]        - Drop an item from your inventory.
  inventory / i      - Check your inventory.
  use [item]         - Use an item from your inventory.
  use [item] on [target] - Use an item on something specific.
  talk to [character]- Interact with characters.
  help               - Show this help message.
  quit               - Exit the game.

More commands might be discovered as you explore...
(This help text can be expanded - adds ~10 lines)
"""

WIN_MESSAGE = "Congratulations! You have unraveled the Mysteries of Eldoria and saved the land!"
LOSE_MESSAGE = "Alas, your adventure ends here. The darkness prevails..."
# Add more specific messages for different endings, events etc. (adds ~20-30 lines)

def display_text(message, width=80):
    """Prints text to the console, wrapped to a certain width."""
    print("\n".join(textwrap.wrap(message, width=width)))
    print() # Add a little space after messages

def get_player_input(prompt="> "):
    """Gets input from the player."""
    return input(prompt).strip()

def display_welcome():
    display_text(WELCOME_MESSAGE)

def display_help():
    display_text(HELP_TEXT)

def display_win_message():
    display_text(WIN_MESSAGE)

def display_lose_message():
    display_text(LOSE_MESSAGE)

def display_room_description(room_obj, player_obj):
    """
    Displays the full description of the current room.
    This function might get more complex if descriptions change dynamically.
    """
    display_text(f"--- {room_obj.name} ---")
    display_text(room_obj.get_dynamic_description(player_obj)) # Uses Room's method

    # Display exits clearly
    if room_obj.exits:
        exit_list = ", ".join([f"{direction} to {name}" for direction, name in room_obj.exits.items()])
        display_text(f"Exits: {exit_list}.")
    else:
        display_text("There are no obvious exits.")
    # Add more UI elements: mini-map, status bars (graphical if using a library like Pygame/Curses)
    # For text, this is fairly complete for room desc. (adds ~5-10 lines for more flair)

def display_inventory(player_obj):
    """Displays the player's inventory."""
    if not player_obj.inventory:
        display_text("Your inventory is empty.")
        return

    display_text("You are carrying:")
    for item in player_obj.inventory:
        # Assuming item objects have a 'name' attribute
        display_text(f"- {item.name} ({item.description[:30]}...)") # Show short description
    # Add options for examining items directly from inventory display (adds ~5-10 lines)

# Add more UI functions:
# - clear_screen() (platform dependent, or just print newlines)
# - formatted_error_message(error_text)
# - formatted_event_message(event_text)
# - display_dialogue(character_name, dialogue_text, options)
# (adds ~30-40 lines for these utility functions)

if __name__ == '__main__':
    # Example of how to test this module independently
    display_welcome()
    display_help()

    class MockPlayer: # For testing inventory display
        def __init__(self):
            self.inventory = []
    class MockItem:
        def __init__(self, name, description):
            self.name = name
            self.description = description

    player = MockPlayer()
    player.inventory.append(MockItem("Shiny Gem", "A gem that glitters brightly."))
    player.inventory.append(MockItem("Old Map", "A tattered map with strange symbols."))
    display_inventory(player)

    class MockRoom:
        def __init__(self, name, description, exits, items, features):
            self.name = name
            self.description_default = description
            self.exits = exits
            self.items_in_room = items
            self.features = features
        def get_dynamic_description(self, player): # Simplified for test
            desc = self.description_default
            if self.items_in_room: desc += "\nItems: " + ", ".join([item.name for item in self.items_in_room])
            if self.features: desc += "\nFeatures: " + ", ".join(self.features.keys())
            return desc

    test_room = MockRoom(
        name="Test Chamber",
        description="A plain room for testing UI.",
        exits={"north": "The Void", "west": "Another Void"},
        items=[MockItem("Test Item", "An item for testing.")],
        features={"lever": "A rusty lever."}
    )
    display_room_description(test_room, player)

    user_cmd = get_player_input("Test input: ")
    display_text(f"You typed: {user_cmd}")
