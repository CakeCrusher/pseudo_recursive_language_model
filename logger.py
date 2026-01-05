import os
from datetime import datetime
from typing import Any

class ActionLogger:
    """Logger for actions taken in the reasoning process."""
    
    def __init__(self, log_dir: str):
        """Initialize logger with directory path.
        
        Args:
            log_dir: Directory path where log file will be created (same as tree manager instance directory)
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file_path = os.path.join(log_dir, "actions.log")
        
    def _write_and_print(self, text: str):
        """Write text to log file and print to terminal."""
        with open(self.log_file_path, "a") as f:
            f.write(text)
        print(text, end="")
    
    def log_action(self, action_type: str, details: dict[str, Any]):
        """Log an action with its details as plain text. Also prints to terminal.
        
        Args:
            action_type: Type of action (e.g., "continue_reasoning", "move_to_node", "finished_reasoning")
            details: Dictionary containing action details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        output = f"\n{'='*80}\n"
        output += f"Timestamp: {timestamp}\n"
        output += f"Action Type: {action_type}\n"
        output += f"{'-'*80}\n"
        
        # Format details in a readable way
        for key, value in details.items():
            if isinstance(value, str) and len(value) > 100:
                # For long strings (like reasoning), format with line breaks
                output += f"{key}:\n{value}\n"
            else:
                output += f"{key}: {value}\n"
        
        output += f"{'='*80}\n"
        
        self._write_and_print(output)
    
    def log_tree(self, iteration: int, max_iterations: int, tree_json: str):
        """Log the rendered tree. Also prints to terminal.
        
        Args:
            iteration: Current iteration number (0-indexed)
            max_iterations: Maximum number of iterations
            tree_json: JSON string representation of the rendered tree
        """
        output = f"\n{'='*80}\n"
        output += f"Iteration {iteration + 1}/{max_iterations}\n"
        output += f"{'='*80}\n"
        output += "Rendered Tree:\n"
        output += tree_json + "\n"
        output += f"{'='*80}\n"
        
        self._write_and_print(output)

# Global logger instance (will be initialized in main)
logger: ActionLogger | None = None

