import numpy as np

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanSemilPlayer():
    def __init__(self, game):
        self.game = game
        self.move_map = {
            'n': 0, 'e': 1, 's': 2, 'w': 3
        }

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        
        print('Valid Actions (as integers):')
        print(np.where(valid)[0])
        print("Enter move as 'move <n|e|s|w>', 'push <n|e|s|w>', or 'place <row> <col>'")


        while True:
            input_move = input()
            try:
                parts = input_move.split()
                action_type = parts[0]
                
                if action_type == "move" and len(parts) == 2:
                    direction = parts[1].lower()
                    a = self.move_map.get(direction)
                    if a is not None and valid[a]:
                        return a
                elif action_type == "push" and len(parts) == 2:
                    direction = parts[1].lower()
                    a = self.move_map.get(direction)
                    if a is not None and valid[a + 4]:
                        return a + 4
                elif action_type == "place" and len(parts) == 3:
                    y, x = int(parts[1]), int(parts[2])
                    # action = 8 + row*3 + col
                    if 0 <= y < 4 and 0 <= x < 3:
                        a = 8 + y * 3 + x
                        if valid[a]:
                            return a

                print('Invalid move')
            except Exception as e:
                print(e)

class GreedySemilPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==0:
                continue
            nextBoard, _ = self.game.getNextState(board, 1, a)
            score = self.game.getScore(nextBoard, 1)
            candidates += [(score, a)]
        candidates.sort()
        return candidates[-1][1]
