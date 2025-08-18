import logging
from collections import defaultdict

class NodeScriptTracker:
    """
    Manages the state of spoken scripts for each node, including segments
    and re-ask variants to handle interruptions and avoid repetition.
    """
    def __init__(self):
        # node_id -> list of script segments
        self.node_scripts = {}
        # node_id -> index of the last successfully spoken segment
        self.spoken_segment_index = defaultdict(lambda: -1)
        # node_id -> number of times a re-ask variant has been used
        self.reask_counters = defaultdict(int)
        # node_id -> if the primary script has been fully spoken
        self.completed_scripts = set()

    def register_script(self, node_id: str, segments: list[str]):
        """Registers the script for a node if it hasn't been completed already."""
        if node_id not in self.completed_scripts:
            self.node_scripts[node_id] = segments
            self.spoken_segment_index[node_id] = -1
            self.reask_counters[node_id] = 0
            logging.info(f"Registered script for node '{node_id}' with {len(segments)} segments.")

    def get_next_segment(self, node_id: str) -> tuple[int, str | None]:
        """Gets the next script segment to be spoken."""
        if node_id not in self.node_scripts:
            return -1, None
        
        next_index = self.spoken_segment_index[node_id] + 1
        script = self.node_scripts[node_id]

        if 0 <= next_index < len(script):
            return next_index, script[next_index]
        
        return -1, None

    def mark_segment_spoken(self, node_id: str, segment_index: int):
        """Marks a script segment as successfully spoken."""
        self.spoken_segment_index[node_id] = segment_index
        logging.info(f"Marked segment {segment_index} for node '{node_id}' as spoken.")

        # If it was the last segment, mark the script as completed
        if node_id in self.node_scripts and segment_index == len(self.node_scripts[node_id]) - 1:
            self.completed_scripts.add(node_id)
            logging.info(f"Completed primary script for node '{node_id}'.")


    def get_reask_variant(self, node_id: str, reask_variants: list[str]) -> str | None:
        """Gets the next available re-ask variant."""
        if not reask_variants:
            return None
        
        reask_index = self.reask_counters[node_id]
        self.reask_counters[node_id] += 1

        if reask_index < len(reask_variants):
            logging.info(f"Using re-ask variant #{reask_index} for node '{node_id}'.")
            return reask_variants[reask_index]
        
        logging.warning(f"Exhausted re-ask variants for node '{node_id}'.")
        return None # Exhausted

    def should_speak_script(self, node_id: str) -> bool:
        """Determines if there's more of the primary script to speak."""
        return node_id not in self.completed_scripts

    def reset_node(self, node_id: str):
        """Resets the tracking for a specific node."""
        if node_id in self.node_scripts:
            del self.node_scripts[node_id]
        if node_id in self.spoken_segment_index:
            del self.spoken_segment_index[node_id]
        if node_id in self.reask_counters:
            del self.reask_counters[node_id]
        if node_id in self.completed_scripts:
            self.completed_scripts.remove(node_id)
        logging.info(f"Reset script tracking for node '{node_id}'.")

    def reset(self):
        """Reset the tracker for a new conversation."""
        self.node_scripts.clear()
        self.spoken_segment_index.clear()
        self.reask_counters.clear()
        self.completed_scripts.clear()
        logging.info("Node script tracker reset for new conversation.")
