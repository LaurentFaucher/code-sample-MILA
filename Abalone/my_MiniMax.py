from player_abalone import PlayerAbalone
from seahorse.player.player import Player
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from itertools import groupby

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob2", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)
        self.move_counter = 0
        self.normal_config = False
        #self.border_keys1 = [(4,0), (3,1), (2,2), (1,3), (0,4), (1,5), (2,6), (3,7), (4,8), (6,8), (8,8), (10,8), (12,8), (13,7), (14,6), (15,5), (16,4), (15,3), (14,2), (13,1), (12,0), (10,0), (8,0), (6,0)]
        self.border_keys1 = [tuple(map(int, line.strip().split(','))) for line in open('border_keys.txt')]

    def cutoff_depth(d):
        """A cutoff function that searches to depth d."""
        return lambda state, depth: depth > d
    
    def is_normal_config(self, state: GameStateAbalone):
        """
        Check if the current configuration of the game board is a normal (initial) configuration.

        Args:
            state (GameStateAbalone): The current state of the game, which includes the board and the next player.

        Returns:
            bool: True if the current configuration matches either the black or white initial configuration, False otherwise.
        """
        player = state.next_player
        board = state.get_rep().get_env()
        black_init_keys = [(10, 6), (10, 8), (11, 5), (11, 7), (12, 4), (12, 6), (12, 8), (13, 5), (13, 7), (14, 4), (14, 6), (15, 3), (15, 5), (16, 4)]
        white_init_keys = [(0, 4), (1, 3), (1, 5), (2, 2), (2, 4), (3, 1), (3, 3), (4, 0), (4, 2), (4, 4), (5, 1), (5, 3), (6, 0), (6, 2)]
        player_keys = [key for key in board.keys() if board[key].get_owner_id() == player.get_id()]
        return player_keys == black_init_keys or player_keys == white_init_keys


    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        if self.move_counter == 0 and self.is_normal_config(current_state):
            self.normal_config = True

        self.move_counter += 1
        depth = 4

        if self.normal_config and self.move_counter <= 6:
            depth = 1
        
        _, move = self.h_alphabeta_search(current_state, depth=depth, h=self.combined_heuristic)
        return move


    def h_alphabeta_search(self, state: GameState, depth=2, h=lambda s, p: 0):
        """
        Perform an alpha-beta search with heuristic pruning to find the best move.

        Args:
            state (GameState): The current state of the game.
            depth (int): The maximum depth to search. Default is 2.
            h (function): A heuristic function that takes a state and a player and returns a heuristic value. Default is a function that returns 0.

        Returns:
            tuple: The best value and the corresponding move.
        """
        player = state.next_player
        memo_max = {}
        memo_min = {}

        def max_value(state, alpha, beta, current_depth):
            """
            Compute the maximum value for the given state using alpha-beta pruning.

            Args:
                state (GameState): The current state of the game.
                alpha (float): The alpha value for alpha-beta pruning.
                beta (float): The beta value for alpha-beta pruning.
                current_depth (int): The current depth in the search tree.

            Returns:
                tuple: The best value and the corresponding move.
            """
            if hash(state) in memo_max: # Memoization
                return memo_max[hash(state)]

            if state.is_done() or current_depth > depth: # Terminal condition
                return h(state, player), None
            
            value = float('-inf')
            move = None

            # Sort actions based on heuristic value
            sorted_actions = sorted(state.get_possible_actions(), key=lambda a: h(a.next_game_state, player), reverse=True)
            # Select top half of actions
            sorted_actions = sorted_actions[:max(1, len(sorted_actions) // 2)]

            for a in sorted_actions:
                v2, _ = min_value(a.next_game_state, alpha, beta, current_depth + 1)
                if v2 > value:
                    value = v2
                    move = a
                    alpha = max(alpha, value)
                if value >= beta:
                    return value, move
            memo_max[hash(state)] = value, move
            return value, move
        
        def min_value(state, alpha, beta, current_depth):
            """
            Compute the minimum value for the given state using alpha-beta pruning.

            Args:
                state (GameState): The current state of the game.
                alpha (float): The alpha value for alpha-beta pruning.
                beta (float): The beta value for alpha-beta pruning.
                current_depth (int): The current depth in the search tree.

            Returns:
                tuple: The best value and the corresponding move.
            """
            if hash(state) in memo_min: # Memoization
                return memo_min[hash(state)]

            if state.is_done() or current_depth > depth: # Terminal condition
                return h(state, player), None
            
            value = float('inf')
            move = None

            # Sort actions based on heuristic value
            sorted_actions = sorted(state.get_possible_actions(), key=lambda a: h(a.next_game_state, player), reverse=False)
            # Select top half of actions
            sorted_actions = sorted_actions[:max(1, len(sorted_actions) // 2)]

            for a in sorted_actions:
                v2, _ = max_value(a.next_game_state, alpha, beta, current_depth + 1)
                if v2 < value:
                    value = v2
                    move = a
                    beta = min(beta, value)
                if value <= alpha:
                    return value, move
            memo_min[hash(state)] = value, move
            return value, move

        return max_value(state, float('-inf'), float('inf'), 0)
    
 
    def score_heuristic(self, state: GameState, player: Player, multiplier=20): #H2
        """
        Calculate the heuristic score for the given player in the current game state.

        Args:
            state (GameState): The current state of the game.
            player (Player): The player for whom the heuristic score is being calculated.
            multiplier (int): A multiplier to scale the heuristic score. Default is 20.

        Returns:
            int: The heuristic score for the given player.
        """
        scores = state.get_scores()
        actual_player_score = scores[player.get_id()]
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]
        other_player_score = scores[other_player_id]
        return (actual_player_score - other_player_score) * multiplier
    
    def gravity_center_heuristic(self, state: GameState, player: Player, multiplier=1): #H1
        """
        Calculate the heuristic score based on the gravity center for the given player in the current game state.

        Args:
            state (GameState): The current state of the game.
            player (Player): The player for whom the heuristic score is being calculated.
            multiplier (int): A multiplier to scale the heuristic score. Default is 1.

        Returns:
            int: The heuristic score for the given player.
        """
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
        
        return (other_score - actual_score) * multiplier
    
    def board_heuristic(self, state: GameState, player: Player, g_multiplier=1, b_multiplier=1): #H2 & H3
        """
        Calculate the heuristic score based on the board configuration for the given player in the current game state.

        This heuristic combines two factors:
        1. The distance of the player's pieces from the center of the board.
        2. The presence of the player's pieces on the border of the board.

        Args:
            state (GameState): The current state of the game.
            player (Player): The player for whom the heuristic score is being calculated.
            g_multiplier (int): A multiplier to scale the gravity center heuristic score. Default is 1.
            b_multiplier (int): A multiplier to scale the border heuristic score. Default is 1.

        Returns:
            int: The combined heuristic score for the given player.
        """
        board = state.get_rep().get_env()
        actual_player_id = player.get_id()
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]

        actual_score = 0
        other_score = 0

        border_score = 0

        for key in board.keys():
            if board[key].get_owner_id() == actual_player_id:
                actual_score += abs(key[0] - 8) + abs(key[1] - 4)
                if key in self.border_keys1:
                    border_score -= 1
            elif board[key].get_owner_id() == other_player_id:
                other_score += abs(key[0] - 8) + abs(key[1] - 4)
                if key in self.border_keys1:
                    border_score += 2

        return ((other_score - actual_score) * g_multiplier) + (border_score * b_multiplier)
    
    def combined_heuristic(self, state: GameState, player: Player): #H
        """
        Calculate the combined heuristic score for the given player in the current game state.

        This heuristic combines:
        1. The score heuristic, which evaluates the player's score relative to the opponent's score.
        2. The board heuristic, which evaluates the player's position on the board based on distance from the center and border presence.

        Args:
            state (GameState): The current state of the game.
            player (Player): The player for whom the heuristic score is being calculated.

        Returns:
            int: The combined heuristic score for the given player.
        """
        score_heuristic = self.score_heuristic(state, player, 100)
        score = score_heuristic + self.board_heuristic(state, player, 2, 5)
        return score