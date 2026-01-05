from typing import Literal
from pydantic import BaseModel, Field

class ReasoningTreeNodeToGenerate(BaseModel):
    """⚠️ ONLY use this if you have taken LESS than 2-3 steps on the current path.
    
    If you have already taken 2-3 reasoning steps on the current path, you MUST use MoveToNode instead to explore a different branch!
    
    Each reasoning step should be concise (2-3 sentences) and focused on one clear point.
    """
    reasoning: str = Field(..., description="⚠️ ONLY use if you have taken LESS than 2-3 steps on current path. If you've taken 2-3+ steps, you MUST use MoveToNode instead! The reasoning should be concise (approximately 2-3 sentences) and focused on one clear point or insight.")
    brief: str = Field(..., description="A brief summary of the above reasoning. Must be no longer than one sentence.")

class ReasoningTreeNode(ReasoningTreeNodeToGenerate):
    id: int = Field(..., description="Integer representing the id of the node (in order of creation)")
    children: list["ReasoningTreeNode"] = Field([], description="The children of the node, it will be null if the node is a leaf")

class MoveToNode(BaseModel):
    """🚨 REQUIRED ACTION: You MUST use this after taking 2-3 reasoning steps on one path!
    
    After 2-3 reasoning steps on the current path, you are REQUIRED to use MoveToNode to explore a different branch.
    This is MANDATORY for proper exploration - do NOT continue reasoning on the same path!
    
    ⚠️ CRITICAL CONSTRAINT: The node_id you select MUST be one that exists in the latest rendered tree!
    - You CANNOT select a node_id that is not shown in the rendered tree
    - You CANNOT select a node_id that is greater than or equal to the current tree size
    - You MUST only select a node_id that appears in the <rendered_tree> section shown to you
    - Look at the rendered tree and choose an id that is actually present (typically 0, 1, 2, etc. up to the current active node)
    
    Navigate back to earlier nodes (like node 0, 1, 2, etc.) that are visible in the rendered tree to explore alternative approaches or different hypotheses.
    This will give you expanded visibility over all the nodes leading and including that point, allowing you to branch out in new directions.
    
    Example: If you're at node 5 and have taken 2-3 steps, navigate to node 0 or another node that exists in the rendered tree to explore a different angle.
    """
    node_id: int = Field(..., description="🚨 REQUIRED after 2-3 steps on current path! ⚠️ CRITICAL: The node_id MUST be one that exists in the latest rendered tree. You CANNOT select a node_id that is not shown in the rendered tree. You MUST only choose an id that appears in the <rendered_tree> section. Look at the rendered tree and select an id that is actually present (typically 0, 1, 2, etc. up to the current active node). This is MANDATORY after 2-3 steps on one path!")

class FinishedReasoning(BaseModel):
    """Select this option ONLY when you have thoroughly explored the problem from multiple angles, 
    considered alternative explanations/solutions, evaluated evidence, and reached a well-reasoned conclusion.
    Do NOT finish after just one or two reasoning steps - that is premature.
    This will cause the reasoning process to end and the final answer to be returned.
    """
    finished: Literal["yes"] = "yes"

class NextReasoningAction(BaseModel):
    """Select the action to take next in the reasoning process."""
    action: ReasoningTreeNodeToGenerate | MoveToNode | FinishedReasoning

    