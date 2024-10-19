from player_abalone import PlayerAbalone
from seahorse.player.player import Player
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from itertools import groupby
from operator import itemgetter


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
        self.move_counter = 0
        self.normal_config = False
    
    def cutoff_depth(d):
        """A cutoff function that searches to depth d."""
        return lambda state, depth: depth > d
    
    def is_normal_config(self, state: GameStateAbalone):
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
        
        if self.move_counter == 22:
            depth = 4
        elif self.move_counter == 23:
            depth = 3
        elif self.move_counter == 24:
            depth = 2
        elif self.move_counter == 25:
            depth = 1
        
        if self.normal_config and self.move_counter <= 6:
            depth = 1
        
        print(f"Move counter: {self.move_counter}")
        _, move = self.h_alphabeta_search(current_state, depth=depth, h=self.combined_heuristic)
        return move


    def h_alphabeta_search(self, state: GameState, depth=2, h=lambda s, p: 0):
        
        player = state.next_player
        memo_max = {}
        memo_min = {}

        def max_value(state, alpha, beta, current_depth):

            if hash(state) in memo_max:
                return memo_max[hash(state)]

            if current_depth > depth:
                return h(state, player), None
            
            value = float('-inf')
            move = None

            # trier les possible actions du plus grand au plus petit et réitérer dessus
            sorted_actions = sorted(state.get_possible_actions(), key=lambda a: h(a.next_game_state, player), reverse=True)
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

            if hash(state) in memo_min:
                return memo_min[hash(state)]

            if current_depth > depth:
                return h(state, player), None
            
            value = float('inf')
            move = None

            # trier les actions du plus petit au plus grand et réitérer dessus
            sorted_actions = sorted(state.get_possible_actions(), key=lambda a: h(a.next_game_state, player), reverse=False)
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
    
    def score_heuristic(self, state: GameState, player: Player, multiplier=20):
        scores = state.get_scores()
        actual_player_score = scores[player.get_id()]
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]
        other_player_score = scores[other_player_id]
        return (actual_player_score - other_player_score) * multiplier
    
    def gravity_center_heuristic(self, state: GameState, player: Player, multiplier=1):
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
    
    def board_heuristic(self, state: GameState, player: Player, g_multiplier=1, b_multiplier=1):
        board = state.get_rep().get_env()
        actual_player_id = player.get_id()
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]

        actual_score = 0
        other_score = 0

        border_keys = [(4,0), (3,1), (2,2), (1,3), (0,4), (1,5), (2,6), (3,7), (4,8), (6,8), (8,8), (10,8), (12,8), (13,7), (14,6), (15,5), (16,4), (15,3), (14,2), (13,1), (12,0), (10,0), (8,0), (6,0)]
        border_score = 0

        for key in board.keys():
            if board[key].get_owner_id() == actual_player_id:
                actual_score += abs(key[0] - 8) + abs(key[1] - 4)
                if key in border_keys:
                    border_score -= 1
            elif board[key].get_owner_id() == other_player_id:
                other_score += abs(key[0] - 8) + abs(key[1] - 4)
                if key in border_keys:
                    border_score += 2

        return ((other_score - actual_score) * g_multiplier) + (border_score * b_multiplier)
    
    def combined_heuristic(self, state: GameState, player: Player):
        score_heuristic = self.score_heuristic(state, player, 100)
        #gravity_center_heuristic = self.gravity_center_heuristic(state, player)
        return score_heuristic + self.board_heuristic(state, player, 2, 5)
    

    ############################################################################################################################
    ###########                           code pour l'heuristique de 3 en ligne                                      ########### 
    ############################################################################################################################
    def split_list(self, lst, value):
        return [list(group) for key, group in groupby(lst, lambda x: x == value) if not key]
    
    def trim_count(self, consecutive_counts):
        return [max(count) for count in self.split_list(consecutive_counts, 0)]
    
    def calculate_score(self, counts, multiplier):
        score = 0
        for count in counts:
            if count > 3 or count == 2:
                score += 1 * multiplier
            elif count == 3:
                score += 2 * multiplier
        return score
    
    def count_row(self, key_row, board, player_id, opponent_id):
        player_consecutive_counts = []
        opponent_consecutive_counts = []

        consecutive_count_player = 0
        consecutive_count_opponent = 0

        for key in key_row:
            if board[key].get_owner_id() == player_id:
                consecutive_count_player += 1
                consecutive_count_opponent = 0
            elif board[key].get_owner_id() == opponent_id:
                consecutive_count_opponent += 1
                consecutive_count_player = 0
            else:
                consecutive_count_player = 0
                consecutive_count_opponent = 0

            player_consecutive_counts.append(consecutive_count_player)
            opponent_consecutive_counts.append(consecutive_count_opponent)
        
        score = 0
        score += self.calculate_score(self.trim_count(player_consecutive_counts), 1)
        score += self.calculate_score(self.trim_count(opponent_consecutive_counts), -1)
        return score
    
    def separate_consecutive_keys(self, row, step=1):
        if len(row) == 0:
            return []

        consecutive_groups = []
        current_group = [row[0]]

        for i in range(1, len(row)):
            if row[i][0] == current_group[-1][0] + step:
                current_group.append(row[i])
            else:
                consecutive_groups.append(current_group)
                current_group = [row[i]]

        consecutive_groups.append(current_group)

        return consecutive_groups
    
    def three_in_a_row_heuristic(self, state: GameState, player: Player, multiplier=2):
        board = state.get_rep().get_env()
        actual_player_id = player.get_id()
        other_player_id = [p.get_id() for p in state.get_players() if p.get_id() != player.get_id()][0]

        score = 0

        keys = board.keys()

        # horizontal
        for sum_ij in range(4, 21, 2):  # 4 to 20
            keys_with_sum_ij = [key for key in keys if key[0] + key[1] == sum_ij]
            keys_with_sum_ij.sort(key=lambda x: x[0])
            for consecutive_keys in self.separate_consecutive_keys(keys_with_sum_ij):
                score += self.count_row(consecutive_keys, board, actual_player_id, other_player_id)

        # diagonal 1
        for j in range(0, 9):  # 0 to 8
            keys_with_j = [key for key in keys if key[1] == j]
            keys_with_j.sort(key=lambda x: x[0])
            for consecutive_keys in self.separate_consecutive_keys(keys_with_j, 2):
                score += self.count_row(consecutive_keys, board, actual_player_id, other_player_id)

        # diagonal 2
        for sub_ij in range(-4, 13, 2):  # -4 to 12
            keys_with_sub_ij = [key for key in keys if key[0] - key[1] == sub_ij]
            keys_with_sub_ij.sort(key=lambda x: x[0])
            for consecutive_keys in self.separate_consecutive_keys(keys_with_sub_ij, 2):
                score += self.count_row(consecutive_keys, board, actual_player_id, other_player_id)

        return score * multiplier
    