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
