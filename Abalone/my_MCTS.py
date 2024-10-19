import math

from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import MethodNotImplementedError

class Node:
    def __init__(self, state: GameState, parent=None, action=None):
        self.state = state  # Represents the game state associated with this node
        self.parent = parent  # Points to the parent node (None for the root node)
        self.action = action  # Represents the action taken to reach this state from the parent
        self.children = []  # List of child nodes (possible future states)
        self.visits = 0  # Number of times this node has been visited during simulations
        self.total_score = 0.0  # Accumulated score (or reward) for this node during simulations

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)
        self.num_simulations = 3


    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        #TODO
        root_node = Node(state=current_state)
        player = current_state.next_player
        for _ in range(self.num_simulations):  # Perform MCTS for a certain number of simulations
            selected_node = self.select(root_node)
            self.expand(selected_node)
            for child in selected_node.children:
                simulation_result = self.simulate(child, player)
                self.backpropagate(child, simulation_result)
        best_child = max(root_node.children, key=lambda child: child.visits)
        return best_child.action

    def select(self, node: Node) -> Node:
        selected_node = node
        while selected_node.children:
            best_UCT_Score = 0
            next_node = selected_node.children[0]
            for child in selected_node.children:
                UCT_Score = child.total_score / child.visits + math.sqrt(2 * math.log(node.visits)/node.visits)
                if UCT_Score > best_UCT_Score:
                    best_UCT_Score = UCT_Score
                    next_node = child
            selected_node = next_node
        return selected_node

    def expand(self, node: Node) -> None:
        possible_action = node.state.get_possible_actions()
        for action in possible_action:
            node.children.append(Node(state= action.next_game_state, parent=node, action=action))
    def simulate(self, node: Node, player: Player) -> float:
        current_state = node.state
        depth = 0
        while not current_state.is_done() and depth < 10:
            possible_actions = current_state.get_possible_actions()
            if not possible_actions:
                break  # No possible actions, exit the loop
            best_heuristic = float('-inf')
            best_action = None
            for action in possible_actions:
                action_heuristic = self.combined_heuristic(action.next_game_state, action.current_game_state.next_player)
                if action_heuristic > best_heuristic:
                    best_heuristic = action_heuristic
                    best_action = action

            current_state = best_action.next_game_state
            depth += 1

        return self.combined_heuristic(current_state, player)

    def backpropagate(self, node: Node, result: float) -> None:
        current_node = node
        node.visits += 1
        node.total_score += result
        while current_node.parent:
            current_node = current_node.parent
            current_node.visits += 1
            current_node.total_score += result
        return
    def score_heuristic(self, state: GameState, player: Player):
        scores = state.get_scores()
        actual_player_score = scores[player.get_id()]
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]
        other_player_score = scores[other_player_id]
        return (actual_player_score - other_player_score) * 20
    def gravity_center_heuristic(self, state: GameState, player: Player):
        board = state.get_rep().get_env()
        actual_player_id = player.get_id()
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]

        actual_score = 0
        other_score = 0

        for key in board.keys():
            if board[key].get_owner_id() == actual_player_id:
                actual_score += abs(key[0] - 8) + abs(key[1] - 4)
            elif board[key].get_owner_id() == other_player_id:
                other_score += abs(key[0] - 8) + abs(key[1] - 4)

        return other_score - actual_score

    def combined_heuristic(self, state: GameState, player: Player):
        return self.score_heuristic(state, player) + self.gravity_center_heuristic(state, player)
