# puzzles.py
# Member 4: Puzzles & Interactions

# Needs access to player state, items, and world information.
# These would typically be passed as arguments to functions.
# import game_engine (for Player object, typically not directly to avoid circular deps)
# import items
# import world
import ui # For displaying puzzle-specific messages

class Puzzle:
    def _init_(self, id, description, solution_conditions, reward_item_id=None,
                 unlocks_exit_from_to=None, message_on_solve="", message_on_fail="",
                 required_item_id=None, consumes_item=False, solved_flag_name=None,
                 npc_dialogue_tree=None):
        self.id = id
        self.description = description # Clue or initial state of the puzzle
        self.solution_conditions = solution_conditions # Could be complex: e.g., {'item_used': 'key_rusty', 'on_target': 'library_door'}
                                                      # or a function to call for custom logic
        self.reward_item_id = reward_item_id
        self.unlocks_exit_from_to = unlocks_exit_from_to # e.g., {'from_room': 'library_door', 'to_room': 'library', 'direction': 'east'}
        self.message_on_solve = message_on_solve
        self.message_on_fail = message_on_fail or "That didn't seem to work."
        self.required_item_id = required_item_id # Simplified: specific item needed
        self.consumes_item = consumes_item
        self.solved = False # Runtime state
        self.solved_flag_name = solved_flag_name or f"{id}_solved" # Game flag to set in player
        self.npc_dialogue_tree = npc_dialogue_tree # For NPC interactions leading to puzzle solve
        # Add more puzzle attributes: attempts, hints, multi-stage logic (adds ~5-10 lines)

    def check_solution(self, player, used_item_obj=None, target_name=None, current_room=None):
        """
        Checks if the player's action solves the puzzle.
        This will contain the core logic for each puzzle.
        Can become very complex. (adds ~20-30 lines per complex puzzle's logic within this or helper functions)
        """
        # Example: Simple item-based puzzle
        if self.required_item_id and used_item_obj:
            if used_item_obj.id == self.required_item_id:
                # Further check if target is correct, if applicable
                # Example: if self.id == "library_door_puzzle" and current_room.id == "library_door":
                self.solve(player, used_item_obj)
                return True
        
        # Example: Keyword based puzzle from dialogue or examining something
        # if 'keyword' in self.solution_conditions and player_input == self.solution_conditions['keyword']:
        #    self.solve(player)
        #    return True
            
        ui.display_text(self.message_on_fail)
        return False

    def solve(self, player, item_used=None):
        """Actions to take when a puzzle is solved."""
        if self.solved: # Prevent re-solving if not intended
            # ui.display_text("You've already dealt with that.")
            return

        self.solved = True
        player.game_flags[self.solved_flag_name] = True
        ui.display_text(self.message_on_solve or f"You solved the {self.id} puzzle!")

        if self.reward_item_id:
            # This part needs access to item definitions and player's inventory add method
            # reward_item = items_module.get_item_by_id(self.reward_item_id) # Assuming items_module is available
            # if reward_item:
            #    player.add_item(reward_item) # Player object needs add_item method
            #    ui.display_text(f"You receive {reward_item.name}.")
            print(f"DEBUG: Player would receive item {self.reward_item_id}") # Placeholder

        if self.unlocks_exit_from_to:
            # This would modify the GAME_MAP in world.py or set a flag the engine checks
            # world_module.unlock_exit(...)
            from_room = self.unlocks_exit_from_to['from_room']
            to_room = self.unlocks_exit_from_to['to_room']
            direction = self.unlocks_exit_from_to['direction']
            print(f"DEBUG: Exit {direction} from {from_room} to {to_room} would be unlocked.")
            # world.GAME_MAP[from_room].exits[direction] = to_room # Direct modification (careful with coupling)


        if self.consumes_item and item_used:
            player.remove_item(item_used) # Player object needs remove_item method
            ui.display_text(f"The {item_used.name} was consumed.")
        
        # Trigger other game events, update NPC states, etc. (adds ~5-10 lines)

    # Add more puzzle methods: give_hint, reset_puzzle (adds ~5-10 lines)

# Global dictionary for puzzles
GAME_PUZZLES = {}
# Global dictionary for NPCs (if any)
NPCS = {} # {"npc_id": {"name": "Old Man", "dialogue_tree": {...}, "current_state": "initial"}}


def load_puzzle_data():
    """
    Populates GAME_PUZZLES and NPCS.
    Expected to be a significant data and logic definition area. (adds ~50-80 lines)
    """
    global GAME_PUZZLES, NPCS
    GAME_PUZZLES = {
        'library_door_puzzle': Puzzle(
            id='library_door_puzzle',
            description="The large oak door to the library is firmly shut. It has a rusty keyhole.",
            required_item_id='key_rusty', # Solution: use 'key_rusty'
            unlocks_exit_from_to={'from_room': 'library_door', 'to_room': 'library', 'direction': 'east'},
            message_on_solve="With a click, the rusty key turns the lock. The library door creaks open!",
            message_on_fail="This item doesn't seem to work on the door.",
            consumes_item=False # Or True if the key breaks or stays in lock
        ),
        'cupboard_puzzle': Puzzle(
            id='cupboard_puzzle',
            description="A stuck cupboard in the kitchen. It might contain something useful.",
            # solution_conditions could be {'action': 'force_open', 'strength_check': 10} (custom logic)
            # Or maybe it requires a 'crowbar' item.
            required_item_id='crowbar', # Assuming a crowbar item exists
            reward_item_id='hidden_message_part1',
            message_on_solve="You pry open the cupboard and find a piece of a message!",
        ),
        # Add more puzzles...
    }
    
    NPCS = {
        "old_man_in_garden": {
            "name": "Old Gardener",
            "dialogue_tree": {
                "initial": "The old gardener looks up. 'Lost, are ye?' (ask about [garden]/[house]/[himself])",
                "garden_query": "He sighs. 'This garden ain't what it used to be... especially since the Whispering Bloom vanished.' (ask about [bloom])",
                "bloom_query": "The Whispering Bloom... legend says it only reveals itself to those who understand the silence of the stones. (triggers 'stone_riddle_puzzle')"
            },
            "current_node": "initial", # Tracks dialogue state
            # Add more NPC properties: items they carry, quests they give
        }
    }
    # Link puzzles to world elements if needed (e.g., a puzzle associated with a room feature)


def try_use_item_puzzle(player, item_obj, target_name, current_room_data):
    """
    Attempts to use an item in the context of solving a puzzle.
    This function iterates through relevant puzzles.
    """
    # Check puzzles associated with the current room or features in it
    # Also check puzzles associated with the item itself (e.g. item.properties['unlocks_puzzle'])
    
    puzzle_id_from_item = item_obj.properties.get("unlocks_puzzle")
    if puzzle_id_from_item and puzzle_id_from_item in GAME_PUZZLES:
        puzzle = GAME_PUZZLES[puzzle_id_from_item]
        # Check if the puzzle is relevant to the current context (e.g., current room)
        # For a door puzzle, the target_name might be the door, or implied by the room.
        # This is a simplification; more context might be needed.
        if puzzle.id == "library_door_puzzle" and current_room_data.id == "library_door": # Example specific check
            if not puzzle.solved:
                puzzle.check_solution(player, used_item_obj=item_obj, current_room=current_room_data)
                return # Puzzle attempted
            else:
                ui.display_text("You've already used that here successfully.")
                return


    # If no item-specific puzzle matched, check room-based puzzles if target_name implies one
    if target_name and target_name in current_room_data.puzzle_triggers:
        puzzle_id = current_room_data.puzzle_triggers[target_name]
        if puzzle_id in GAME_PUZZLES:
            puzzle = GAME_PUZZLES[puzzle_id]
            if not puzzle.solved:
                 # This puzzle might not directly use an item, or 'item_obj' could be 'None' if it's an action puzzle
                puzzle.check_solution(player, used_item_obj=item_obj, target_name=target_name, current_room=current_room_data)
                return

    # Default item use message if no puzzle interaction occurred
    if item_obj.use_message:
        ui.display_text(item_obj.use_message)
    elif item_obj.use_effect: # Generic effect if not puzzle
        ui.display_text(f"You use the {item_obj.name}, but nothing specific happens here with '{target_name if target_name else 'it'}'.")
    else:
        ui.display_text(f"You can't seem to use the {item_obj.name} {'on ' + target_name if target_name else 'like that'}.")


def can_player_enter(player, from_room_id, to_room_id):
    """Checks if an exit is blocked by an unsolved puzzle."""
    for puzzle_id, puzzle_obj in GAME_PUZZLES.items():
        if not puzzle_obj.solved and puzzle_obj.unlocks_exit_from_to:
            unlock_info = puzzle_obj.unlocks_exit_from_to
            if unlock_info['from_room'] == from_room_id and unlock_info['to_room'] == to_room_id:
                return False # Blocked by this unsolved puzzle
    return True # No puzzle blocks this specific transition

def get_block_message(player, from_room_id, to_room_id):
    """Gets the message for a blocked exit."""
    for puzzle_id, puzzle_obj in GAME_PUZZLES.items():
        if not puzzle_obj.solved and puzzle_obj.unlocks_exit_from_to:
            unlock_info = puzzle_obj.unlocks_exit_from_to
            if unlock_info['from_room'] == from_room_id and unlock_info['to_room'] == to_room_id:
                # Return a generic message or a puzzle-specific one
                return puzzle_obj.description or "The way is blocked." 
    return None


def handle_talk_npc(player, npc_name_input, current_room_data):
    """Handles talking to an NPC."""
    # Find NPC in current room (this implies NPCs are part of room data or a global list with locations)
    # For simplicity, let's assume NPCS dict has location or we check against a known NPC.
    # This needs more robust NPC location management.
    found_npc = None
    for npc_id, npc_data in NPCS.items():
        if npc_data["name"].lower() == npc_name_input.lower(): # Basic check
            # Add a check if npc_data["location"] == current_room_data.id
            found_npc = npc_data
            break
    
    if found_npc:
        current_node_id = found_npc.get("current_node", "initial")
        dialogue_options = found_npc["dialogue_tree"].get(current_node_id)
        if dialogue_options:
            ui.display_text(f"{found_npc['name']}: {dialogue_options}")
            # Here you'd parse player's response to navigate dialogue tree
            # e.g., player.last_spoken_to = npc_id
            # This can get very complex with choices (adds ~20-30 lines)
        else:
            ui.display_text(f"{found_npc['name']} has nothing more to say right now.")
    else:
        ui.display_text(f"You don't see anyone named '{npc_name_input}' here to talk to.")

def check_win_condition(player):
    """Checks if the player has met the win conditions."""
    # Example: if player.game_flags.get("found_treasure_and_escaped"): return True
    # This will depend heavily on the game's story and goals (adds ~5-15 lines)
    if player.current_room_id == 'treasury' and player.has_item('crown_jewels'): # Example
        if player.game_flags.get('main_quest_completed'):
            return True
    return False

def check_lose_condition(player):
    """Checks if the player has met any lose conditions."""
    # Example: if player.health <= 0: return True
    # Or if player.game_flags.get("cursed_forever"): return True
    # (adds ~5-15 lines)
    if player.game_flags.get('time_ran_out_doom_clock'):
        return True
    return False


if _name_ == '_main_':
    # Example of how to test this module independently
    # You'd need mock Player, Item, Room objects or simplified versions.
    class MockPlayer:
        def _init_(self):
            self.inventory = []
            self.game_flags = {}
        def has_item(self, item_id): return item_id in self.inventory
        def add_item(self, item_obj): self.inventory.append(item_obj.id if hasattr(item_obj, 'id') else item_obj) # simplified
        def remove_item(self, item_obj): self.inventory.remove(item_obj.id if hasattr(item_obj, 'id') else item_obj)

    class MockItem:
        def _init_(self, id, name, properties=None):
            self.id = id
            self.name = name
            self.properties = properties if properties else {}
            self.use_message = "Mock item used."

    class MockRoom:
        def _init_(self, id, name):
            self.id = id
            self.name = name
            self.puzzle_triggers = {}


    load_puzzle_data() # Load puzzle definitions
    
    player = MockPlayer()
    key = MockItem('key_rusty', 'rusty key', {"unlocks_puzzle": "library_door_puzzle"})
    library_entrance = MockRoom('library_door', 'Library Entrance')
    
    if 'library_door_puzzle' in GAME_PUZZLES:
        puzzle = GAME_PUZZLES['library_door_puzzle']
        print(f"Puzzle: {puzzle.id}, Desc: {puzzle.description}")
        if not puzzle.solved:
            # Simulate the game engine calling try_use_item_puzzle
            # This simplified call bypasses some of try_use_item_puzzle's context checks
            puzzle.check_solution(player, used_item_obj=key, current_room=library_entrance) 
        if puzzle.solved:
            print("Library door puzzle was solved by mock test.")
        else:
            print("Library door puzzle was NOT solved by mock test.")
