# Connect4 - MonteCarlo
A Monte Carlo Tree Search based bot for the game of Connect4

<p align="center">
  <img src="https://github.com/user-attachments/assets/c75f6d27-96ff-476d-965f-c20e25b6ae5c" width="350"/>  
</p>

I wanted to learn Reinforcement Learning so I thought this would be a good [~first~](https://github.com/TAOGenna/ai-notebooks-implementations/blob/main/10armed_bandit.ipynb) exercise. Plus, the algorithm used in this project is present in _MuZero_ and _AlphaGo_ so really wanted to learn about it! 

## The Game
Connect Four is a two-player strategy game in which players take turns dropping colored discs into a vertical grid, aiming to be the first to form a horizontal, vertical, or diagonal line of four discs of the same color.

## Monte Carlo Tree Search
Monte Carlo Tree Search (MCTS) is a decision-making algorithm that builds a search tree by simulating random playouts from a given state, progressively refining its choices based on the results. It combines exploration of new moves with exploitation of known successful moves to find optimal actions. In particular, we employ the _Upper Bound Confidence_ to set weights between these two. 

Depending on the amount of computation budget that you give the program it may behave better or worse as it can have the opportunity to explore a larger space of possible states.

## Acknowledgments
To Alfredo de la Fuente for letting us know about this project and for putting very good references. See his [repo](https://github.com/Alfo5123/Connect4).
