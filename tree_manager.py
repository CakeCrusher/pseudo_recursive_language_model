from models import ReasoningTreeNode, ReasoningTreeNodeToGenerate, MoveToNode
import uuid
import json
import os

class TreeManager:
    def __init__(self):
        self.tree_manager_id = str(uuid.uuid4())[:4]
        self.root_node = ReasoningTreeNode(
            id=0,
            reasoning="",
            brief="",
            children=[],
        )
        self.size = 0
        self.current_node_id = 0

    
    def get_log_directory(self) -> str:
        """Get the directory path for logging (same as tree snapshots directory)."""
        dir_path = f"tree_snapshots/{self.tree_manager_id}"
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
        
    def move_to_node(self, move_to_node: MoveToNode):
        self.current_node_id = move_to_node.node_id
        
    def _find_node_by_id(self, target_node_id: int, current_node: ReasoningTreeNode) -> ReasoningTreeNode | None:
        """Internal recursive helper that returns None if not found (doesn't raise)."""
        if current_node.id == target_node_id:
            return current_node
        for child in current_node.children:
            result = self._find_node_by_id(target_node_id, child)
            if result:
                return result
        return None  # Not found in this branch - return None so parent can try other branches
    
    def get_node_by_id(self, target_node_id: int, current_node: ReasoningTreeNode | None = None) -> ReasoningTreeNode:
        """Search for the node with the given id from root."""
        if current_node is None:
            current_node = self.root_node
        result = self._find_node_by_id(target_node_id, current_node)
        if result is None:
            raise ValueError(f"Node with id {target_node_id} not found")
        return result

    def continue_reasoning(self, input: ReasoningTreeNodeToGenerate):
        current_node = self.get_node_by_id(self.current_node_id)

        new_node_id = self.size + 1

        new_node = ReasoningTreeNode(
            id=new_node_id,
            reasoning=input.reasoning,
            brief=input.brief,
            children=[],
        )

        current_node.children.append(new_node)
        self.size += 1

        self.current_node_id = new_node_id
        
        return new_node

    def _find_path_to_node(self, target_id: int, current_node: ReasoningTreeNode | None = None, path: list[int] | None = None) -> list[int] | None:
        """Find the path from root to the target node. Returns list of node IDs or None if not found."""
        if path is None:
            path = []
        if current_node is None:
            current_node = self.root_node
        
        # Add current node to path
        path = path + [current_node.id]
        
        # If we found the target, return the path
        if current_node.id == target_id:
            return path
        
        # Recursively search children
        for child in current_node.children:
            result = self._find_path_to_node(target_id, child, path)
            if result:
                return result
        
        # Not found in this branch
        return None
    
    def _render_node(self, node: ReasoningTreeNode, active_path: set[int]) -> dict:
        """Recursively render a node. If node is on active path, include reasoning; otherwise only brief."""
        node_dict = {
            "id": node.id,
            "brief": node.brief,
        }
        
        # Only include reasoning if node is on the active path
        if node.id in active_path:
            node_dict["reasoning"] = node.reasoning
        
        # Recursively render children
        if node.children:
            node_dict["children"] = [self._render_node(child, active_path) for child in node.children]
        else:
            node_dict["children"] = []
        
        return node_dict
    
    def render_compressed_tree(self, save_to_file: bool = True) -> dict:
        """Compressed nested JSON representation of the tree.
        Only nodes on the path to current_node_id show reasoning; others show only brief.
        """
        # Find the path to the current node
        path = self._find_path_to_node(self.current_node_id)
        if path is None:
            # If path not found, treat as empty path (only root is active)
            active_path = {0}
        else:
            active_path = set(path)
        
        # Render the tree starting from root
        tree_rendered = self._render_node(self.root_node, active_path)

        if save_to_file:
            with open(f"{self.get_log_directory()}/{self.size}.json", "w") as f:
                json.dump(tree_rendered, f, indent=4)

        return tree_rendered
