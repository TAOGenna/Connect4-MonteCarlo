# Connect4 - MonteCarlo
A Monte Carlo Tree Search based bot for the game of Connect4

<p align="center">
  <img src="https://github.com/user-attachments/assets/c75f6d27-96ff-476d-965f-c20e25b6ae5c" width="350"/>  
</p>

I wanted to learn Reinforcement Learning so I thought this would be a good [~first~](https://github.com/TAOGenna/ai-notebooks-implementations/blob/main/10armed_bandit.ipynb) exercise. Plus, the algorithm used in this project is present in _MuZero_ and _AlphaGo_ so really wanted to learn about it! 

Previously [I did](https://github.com/TAOGenna/ai-notebooks-implementations/blob/main/monte_carlo_tictactoc.py) a minimal version with a simpler game: tictactoe or "michi"(for spanish speakers).

## The Game
Connect Four is a two-player strategy game in which players take turns dropping colored discs into a vertical grid, aiming to be the first to form a horizontal, vertical, or diagonal line of four discs of the same color.

## Monte Carlo Tree Search
Monte Carlo Tree Search (MCTS) is a decision-making algorithm that builds a search tree by simulating random playouts from a given state, progressively refining its choices based on the results. It combines exploration of new moves with exploitation of known successful moves to find optimal actions. In particular, we employ the _Upper Bound Confidence_ to set weights between these two. 

Depending on the amount of computation budget that you give the program it may behave better or worse as it can have the opportunity to explore a larger space of possible states.

## Usage 
```
git clone https://github.com/TAOGenna/Connect4-MonteCarlo.git
python3 interface.py
```
If you want the algorithm to search for deeper states, you can change that number in `interface.py`. Search for 
```
 def ai_move(self, budget=3000):
        if self.game_over:
            return
```
and change the variable `budget` to a bigger number.

## Future Work

There is room for improvement beyond the UBC policy. See papers:
- Monte-Carlo Tree Search and Minimax Hybrids, Hendrik Baier and Mark H.M. Winands
- Score Bounded Monte-Carlo Tree Search, Tristan Cazenave and Abdallah Saffidine

## Acknowledgments
- Principal reference: A Survey of Monte Carlo Tree Search Methods, Cameron Browne et al.
- To [Alfredo de la Fuente](https://github.com/Alfo5123/Connect4). I was looking through his projects and this one seemed suitable for someone trying to learn the basics of RL, so thanks for open-source it and also for the references
