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
