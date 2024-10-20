# Abalone Competitive Agent

This is an implementation of a competitive agent for the Abalone game.

## What is Abalone?

Abalone is a two-player abstract strategy board game where the objective is to push six of the opponent's marbles off the edge of the board. Players take turns moving one, two, or three of their marbles in a straight line or laterally.

<div align="center">
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSF00I4acHY56YUJJOg8fN-d_meUwbK0CEmJQ&s" alt="Abalone Game">
</div>

## Code

You can find my MiniMax implementation in the following file:
[Link to my_MiniMax.py](Abalone/my_MiniMax.py)

This is the only relevant file for this code sample.

## Project Overview

We conducted a tournament against other competitive agents, and our agent emerged victorious. This was a team project where my teammate implemented the Monte Carlo Tree Search (MCTS) algorithm, and I implemented the MiniMax algorithm. After comparing both approaches, we found that MiniMax performed better, so we used it for the tournament.

For this code sample, I have removed the MCTS implementation and only kept the MiniMax algorithm, as it is part of my master's application.

You can visualize the tournament results (brackets) by visiting the following link: [Tournament Results](https://challonge.com/fr/ykol0oke). My team name was "mayoman".

## Minimax Heuristics

The minimax algorithm, while effective, suffers from the limitation of traversing the entire game tree to the end, which is excessively time-consuming and resource-intensive. So, to evaluate the state of a game and determine whether a player is winning, four heuristics have been developed. Of these, heuristics H1, H2 and H3 have been retained and combined as the final heuristic.

### Center of gravity (H1) [[1](https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/JET/report_abalone.pdf)]

While playing Abalone, we noticed the strategic advantage of controlling the center squares for several reasons. Firstly, marbles positioned in the center of the board are protected from loss. Secondly, by dominating the center, it's easier to push the opponent towards the edges of the board. Thirdly, in the event of a tie, the player with the most centered marbles wins the game. This strategy is implemented via a Manhattan distance calculation, where the difference between the sum of the distances of the opponent's marbles and those of the player's own marbles determines the dominant position. This calculation is made in relation to the central square of the board. This approach encourages the agent to avoid the edges and conquer the center by pushing the opponent back. Although this strategy is rather defensive, it can be effectively combined with more aggressive approaches to form a balanced strategic compromise.

### Attack (H2) [[1](https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/JET/report_abalone.pdf)]
This heuristic, complementary to the previous one, is rather simple. It boils down to subtracting one's score from that of the opponent in a given state. This more aggressive approach encourages the agent to maximize its score while decreasing that of its opponent.

### Sumito potential (H3)

This third heuristic aims to assess Sumito's potential (ejection or risk of ejection from the board) at a given moment. It simply involves scanning the board to determine which player has the most balls at the ends of the game. To do this, we recorded all the squares at the ends of the board in a static data structure. If an opponent's marble is present on one of these squares, we add 2 to the score. On the other hand, if one of our marbles occupies one of these squares, we subtract 1 from the score (in order to avoid a complete cancellation of the score, as 2 - 2 would give 0, in which case our agent would have less incentive to push his opponent towards the edges of the board). This relatively aggressive approach encourages the agent to push his opponent towards the edges of the board, thus increasing Sumito's potential.