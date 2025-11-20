from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .SemilLogic import Board
import numpy as np

class SemilGame(Game):
    """
    Semil Game class implementing the alpha-zero-general Game interface.
    """

    def __init__(self):
        self.n = 3
        self.m = 7

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board()
        return b.pieces, b.coins, b.coins_off_board

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.m)

    def getActionSize(self):
        # return number of actions
        return 41

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        pieces, coins, coins_off = board
        b = Board()
        b.pieces = np.copy(pieces)
        b.coins = np.copy(coins)
        b.coins_off_board = coins_off

        # In SemilLogic, the board is not canonical, so we don't need to flip player
        b.execute_move(action, player)
        return ((b.pieces, b.coins, b.coins_off_board), -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        canonical_board = self.getCanonicalForm(board, player)
        pieces, coins, coins_off = canonical_board
        b = Board()
        b.pieces = np.copy(pieces)
        b.coins = np.copy(coins)
        b.coins_off_board = coins_off
        # Legal moves are always calculated for player 1 on the canonical board
        return np.array(b.get_legal_moves(1))


    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player won, -1 if player lost
        pieces, coins, _ = board

        # Win condition for player 1: coin in row 6
        if np.any(coins[:, self.m - 1] > 0):
            return 1 if player == 1 else -1
        # Win condition for player -1: coin in row 0
        if np.any(coins[:, 0] > 0):
            return -1 if player == 1 else 1

        # Check for no valid moves for the current player
        if not np.any(self.getValidMoves(board, player)):
            # Check if the other player also has no moves
            if not np.any(self.getValidMoves(board, -player)):
                return 1e-4 # Draw
            # If only current player has no moves, they lose.
            # This can happen if a player's piece is trapped.
            return -1

        # Not ended
        return 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        pieces, coins, coins_off = board
        if player == -1:
            # Flip board horizontally and vertically for player -1
            canon_pieces = np.fliplr(np.flipud(pieces * -1))
            canon_coins = np.fliplr(np.flipud(coins))
            return canon_pieces, canon_coins, coins_off
        return pieces, coins, coins_off

    def getSymmetries(self, board, pi):
        # mirror, rotational
        # Semil only has one symmetry: horizontal flip.
        # The action policy `pi` also needs to be transformed.
        # This is complex due to the action space encoding.
        # Moves/Pushes are directional, flip would change them.
        # Placements are location-based, flip would change them.
        # For now, returning no symmetries.
        return [(board, pi)]

    def stringRepresentation(self, board):
        pieces, coins, coins_off = board
        s = f"Coins off board: {coins_off}\n"
        for i in range(self.n):
            row_str = []
            for j in range(self.m):
                p = pieces[i,j]
                c = int(coins[i,j])
                player_char = '.'
                if p == 1: player_char = '1'
                elif p == -1: player_char = '2'
                row_str.append(f"{player_char}({c})")
            s += " ".join(row_str) + "\n"
        return s

def display(board):
    pieces, coins, coins_off = board
    n = pieces.shape[0]
    m = pieces.shape[1]

    print(f"Coins off board: {coins_off}")
    print("   ", end="")
    for y in range(m):
        print(y, end=" ")
    print("")
    print("-----------------------")
    for y in range(n):
        print(y, "|", end="")    # print the row #
        for x in range(m):
            p = pieces[y,x]
            c = int(coins[y,x])
            if p == 1:
                print("1", end="")
            elif p == -1:
                print("2", end="")
            else:
                print(".", end="")
            print(f"({c})", end=" ")
        print("|")

    print("-----------------------")
