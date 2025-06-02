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
