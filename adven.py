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
