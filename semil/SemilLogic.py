import numpy as np

class Board():
    """
    Board class for the game Semil.
    Default board size is 3x7.
    Board data:
        - pieces: 3x7 numpy array with values 1, -1, 0
        - coins: 3x7 numpy array with values 0-3 (stack height)
        - coins_off_board: integer
        - player_turn: 1 or -1
    """

    # list of all 4 directions on the board, as (x,y) offsets (N, E, S, W)
    __directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def __init__(self):
        "Set up initial board configuration."
        self.n = 3
        self.m = 7
        self.pieces = np.zeros((self.n, self.m))
        self.coins = np.zeros((self.n, self.m))

        # Initial piece positions
        self.pieces[1, 0] = 1
        self.pieces[1, 6] = -1

        self.coins_off_board = 9

    def __getitem__(self, index):
        return self.pieces[index], self.coins[index]

    def get_legal_moves(self, color):
        """
        Returns a fixed size binary vector representing all legal moves.
        Action space (size 41):
        - 0-3: Push in 4 directions
        - 4-7: Simple Move in 4 directions (to empty square)
        - 8-28: Capture opponent and place them on one of 21 squares
        - 29-40: Place coin in one of the 12 home zone squares
        """
        moves = [0] * 41
        my_piece_pos = self.find_piece(color)
        if my_piece_pos is None:
            return moves

        x, y = my_piece_pos

        # Check for pushes (0-3) and simple moves (4-7)
        for i, d in enumerate(self.__directions):
            dx, dy = d
            nx, ny = x + dx, y + dy

            if self.is_valid_location(nx, ny):
                # Simple Move (to square with no piece and no coins)
                if self.pieces[nx, ny] == 0 and self.coins[nx, ny] == 0:
                    moves[i + 4] = 1

                # Push (to square with coins)
                if self.pieces[nx, ny] == 0 and self.coins[nx, ny] > 0:
                    nnx, nny = nx + dx, ny + dy
                    can_push = True
                    if self.is_valid_location(nnx, nny):
                        if self.pieces[nnx, nny] != 0 or self.coins[nnx, nny] > 0:
                            can_push = False
                    if can_push:
                        moves[i] = 1
        
        # Check for captures (8-28)
        # First, find if an opponent is adjacent
        adjacent_opponent_pos = None
        for d in self.__directions:
            dx, dy = d
            ox, oy = x + dx, y + dy
            if self.is_valid_location(ox, oy) and self.pieces[ox, oy] == -color:
                adjacent_opponent_pos = (ox, oy)
                break
        
        if adjacent_opponent_pos:
            # Find all truly empty squares to place the opponent
            for r in range(self.n):
                for c in range(self.m):
                    # The placement square must be empty of pieces and coins
                    if self.pieces[r, c] == 0 and self.coins[r, c] == 0:
                        # The placement square cannot be where my piece is currently
                        if (r,c) != (x,y):
                            action_idx = 8 + c * self.n + r
                            moves[action_idx] = 1

        # Check for placements (29-40)
        if self.coins_off_board > 0:
            for i in range(4): # First 4 rows for home zone
                for j in range(3): # 3 columns
                    if self.pieces[j, i] == 0 and self.coins[j, i] < 3:
                        moves[29 + i*3 + j] = 1

        return moves

    def is_valid_location(self, x, y):
        return 0 <= x < self.n and 0 <= y < self.m

    def find_piece(self, color):
        for i in range(self.n):
            for j in range(self.m):
                if self.pieces[i, j] == color:
                    return (i, j)
        return None

    def execute_move(self, move, color):
        """
        Execute a given move and return the new board state.
        'move' is an integer from 0 to 40.
        'color' is the current player.
        """
        my_piece_pos = self.find_piece(color)
        x, y = my_piece_pos

        if move < 4: # Push
            direction = self.__directions[move]
            dx, dy = direction
            nx, ny = x + dx, y + dy
            
            self.pieces[x, y] = 0
            self.pieces[nx, ny] = color

            pushed_coins = self.coins[nx, ny]
            self.coins[nx, ny] = 0
            nnx, nny = nx + dx, ny + dy
            if self.is_valid_location(nnx, nny):
                self.coins[nnx, nny] += pushed_coins
                if self.coins[nnx, nny] > 3:
                    self.coins_off_board += self.coins[nnx, nny] - 3
                    self.coins[nnx, nny] = 3
            else:
                self.coins_off_board += pushed_coins

        elif move < 8: # Simple Move
            direction = self.__directions[move - 4]
            dx, dy = direction
            nx, ny = x + dx, y + dy

            coins_under_piece = self.coins[x, y]
            if coins_under_piece > 0:
                self.coins[x, y] = 0
                self.coins_off_board += int(coins_under_piece)

            self.pieces[x, y] = 0
            self.pieces[nx, ny] = color

        elif move < 29: # Capture
            # Find opponent
            opp_pos = None
            for d in self.__directions:
                dx, dy = d
                ox, oy = x + dx, y + dy
                if self.is_valid_location(ox, oy) and self.pieces[ox, oy] == -color:
                    opp_pos = (ox, oy)
                    break
            
            # Move my piece to opponent's spot
            self.pieces[x, y] = 0
            self.pieces[opp_pos] = color
            # Handle coins under my original spot
            coins_under_piece = self.coins[x, y]
            if coins_under_piece > 0:
                self.coins[x, y] = 0
                self.coins_off_board += int(coins_under_piece)

            # Place opponent in new spot
            placement_idx = move - 8
            c = placement_idx // self.n
            r = placement_idx % self.n
            self.pieces[r, c] = -color

        else: # Place Coin
            move_idx = move - 29
            row = move_idx // 3
            col = move_idx % 3
            self.coins[col, row] += 1
            self.coins_off_board -= 1
