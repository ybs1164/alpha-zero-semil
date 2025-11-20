import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Arena
from semil.SemilGame import SemilGame
from semil.SemilPlayers import HumanSemilPlayer

"""
use this script to play a game of Semil with two human players.
"""

# Create a game instance
g = SemilGame()

# Create two human players
player1 = HumanSemilPlayer(g).play
player2 = HumanSemilPlayer(g).play

# Setup the arena
arena = Arena.Arena(player1, player2, g, display=g.display)

# Play the game
# The first argument is the number of games to play.
# verbose=True will print the board after each move.
print(arena.playGames(2, verbose=True))
