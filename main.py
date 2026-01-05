from dotenv import load_dotenv
load_dotenv()

import json
from openai import OpenAI
from models import NextReasoningAction, ReasoningTreeNodeToGenerate, MoveToNode, FinishedReasoning
from tree_manager import TreeManager
from logger import ActionLogger

MAX_ITERATIONS = 20

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <task>")
        exit(1)
    task = sys.argv[1]
    client = OpenAI()
    tree_manager = TreeManager()
    
    # Initialize logger in the same directory as tree manager instance
    logger = ActionLogger(tree_manager.get_log_directory())
    logger.log_action("session_start", {
        "task": task,
        "tree_manager_id": tree_manager.tree_manager_id
    })
    
    for i in range(MAX_ITERATIONS):
        tree_rendered =  tree_manager.render_compressed_tree()
        tree_render_str = json.dumps(tree_rendered, indent=2)
        
        # Log the rendered tree (also prints to terminal)
        logger.log_tree(i, MAX_ITERATIONS, tree_render_str)

        SystemPrompt = "\n".join([
            "You are an agent that reasons about the user's request through a tree of nodes.",
            "",
            "🚨🚨🚨 MANDATORY EXPLORATION RULE 🚨🚨🚨",
            "",
            "AFTER TAKING 2-3 REASONING STEPS ON ONE PATH, YOU MUST USE MoveToNode!",
            "DO NOT continue reasoning on the same path after 2-3 steps!",
            "You MUST navigate back to an earlier node to explore a different branch!",
            "",
            "CRITICAL INSTRUCTIONS:",
            "- Each reasoning step should be SHORT and FOCUSED: approximately 2-3 sentences maximum. Make one clear point per step.",
            "- COUNT YOUR STEPS: After your 2nd or 3rd reasoning step on a path, you MUST use MoveToNode to explore a different branch.",
            "- EXPLORE MULTIPLE PATHS: This is REQUIRED, not optional. You must explore at least 2-3 different paths before finishing.",
            "- Use the tree structure to explore breadth: don't just go deep on one path. Navigate back to earlier nodes (like node 0, 1, 2) and branch out.",
            "- Before finishing, ensure you've explored at least 2-3 different approaches or paths through the problem space.",
            "- Only finish when you have: (1) explored multiple distinct paths/approaches, (2) compared different hypotheses or solutions, and (3) synthesized your findings into a conclusion.",
            "",
            "EXPLORATION STRATEGY:",
            "- Step 1-2: Reason on current path (ReasoningTreeNodeToGenerate)",
            "- Step 3: YOU MUST use MoveToNode to navigate to an earlier node (like node 0 or 1)",
            "- Then explore a new branch from that earlier node",
            "- Repeat this pattern: 2-3 steps on a path, then MoveToNode to explore another path",
            "- This is how you build breadth in your reasoning tree - it's REQUIRED!",
            "",
            "TREE NAVIGATION:",
            "- You only have full visibility (includes reasoning) over nodes leading to the active node (deepest leaf node with reasoning).",
            "- ReasoningTreeNodeToGenerate: ONLY if you've taken LESS than 2-3 steps on current path",
            "- MoveToNode: REQUIRED after 2-3 steps on current path. Navigate to earlier nodes to explore different branches.",
            "  ⚠️ CRITICAL: When using MoveToNode, the node_id MUST be one that exists in the rendered tree shown below!",
            "  - You CANNOT select a node_id that is not present in the <rendered_tree> section",
            "  - You MUST look at the rendered tree and choose an id that actually exists (check the 'id' fields in the tree)",
            "  - Only select node_ids that are visible in the rendered tree structure",
            "- Navigating back gives you expanded visibility over all nodes leading to that point, allowing you to branch out in new directions.",
            "",
            "The rendered tree below shows only the reasoning of nodes on the active branch:",
            "",
            "<rendered_tree>",
            tree_render_str,
            "</rendered_tree>"
        ])

        completion = client.chat.completions.parse(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": SystemPrompt},
                {"role": "user", "content": task},
            ],
            response_format=NextReasoningAction,
        )

        if completion.choices[0].message.parsed:
            action = completion.choices[0].message.parsed.action
            
            # Log the action with details
            if isinstance(action, ReasoningTreeNodeToGenerate):
                previous_node_id = tree_manager.current_node_id
                new_node = tree_manager.continue_reasoning(action)
                logger.log_action("continue_reasoning", {
                    "node_id": new_node.id,
                    "reasoning": action.reasoning,
                    "brief": action.brief,
                    "previous_node_id": previous_node_id,
                    "current_node_id": tree_manager.current_node_id
                })
            elif isinstance(action, MoveToNode):
                previous_node_id = tree_manager.current_node_id
                tree_manager.move_to_node(action)
                logger.log_action("move_to_node", {
                    "target_node_id": action.node_id,
                    "previous_node_id": previous_node_id,
                    "current_node_id": tree_manager.current_node_id
                })
            elif isinstance(action, FinishedReasoning):
                logger.log_action("finished_reasoning", {
                    "current_node_id": tree_manager.current_node_id,
                    "tree_size": tree_manager.size
                })
                logger.log_action("session_end", {
                    "tree_manager_id": tree_manager.tree_manager_id
                })
                return
            else:
                raise ValueError(f"Invalid action: {action}")
        else:
            logger.log_action("error", {
                "message": "No parsed response available",
                "current_node_id": tree_manager.current_node_id
            })
            return
    logger.log_action("error", {
        "message": "Max iterations reached",
        "current_node_id": tree_manager.current_node_id
    })
    return

if __name__ == "__main__":
    main()
