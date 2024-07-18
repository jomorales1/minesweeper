from enum import Enum

import random


class Cell:
    def __init__(self, value: int, is_mine: bool):
        """
            Possible values:\n
            -1 -> Mine\n
            [0 - 8] -> Number of mines around
        """
        self.value = value
        self.is_mine = is_mine
        self.revealed = False
        self.flagged = False
        self.exploded = False

class BoardState(Enum):
    EMPTY = 0
    STARTED = 1
    FINISHED = 2

class BoardResult(Enum):
    PENDING = 0
    LOST = 1
    WON = 2

class Board:
    def __init__(self, rows: int, columns: int, mines_percentage : float = 0.16):
        # Initial parameters
        self.rows = rows
        self.columns = columns
        self.state = BoardState.EMPTY
        self.result = BoardResult.PENDING
        self.flags_count = 0
        self.mines_count = int(self.rows * self.columns * mines_percentage)

        # Cells initialization
        self.cells = [[Cell(value=0, is_mine=False) for _ in range(self.columns)] for _ in range(self.rows)]
    
    def fill(self, start_x: int, start_y: int):
        # Select mine cells
        for _ in range(self.mines_count):
            # Generate random location for the mine
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.columns - 1)

            # If the cell its already a mine or its 
            while self.cells[x][y].is_mine or (x == start_x and y == start_y):
                x = random.randint(0, self.rows - 1)
                y = random.randint(0, self.columns - 1)
            self.cells[x][y].value = -1
            self.cells[x][y].is_mine = True
        
        # Fill the rest of the board
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cells[i][j].is_mine:
                    continue
                adjacent_mines = 0
                for x_step in [-1, 0, 1]:
                    x_adjacent = i + x_step
                    if x_adjacent < 0 or x_adjacent >= self.rows:
                        continue
                    for y_step in [-1, 0, 1]:
                        y_adjacent = j + y_step
                        if y_adjacent < 0 or y_adjacent >= self.columns:
                            continue
                        if x_adjacent == i and y_adjacent == j:
                            continue
                        adjacent_mines += 1 if self.cells[x_adjacent][y_adjacent].is_mine else 0
                self.cells[i][j].value = adjacent_mines
        
        # Reveal start cell
        self.reveal_cell(start_x, start_y)

        self.state = BoardState.STARTED
    
    def reveal_all(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if not self.cells[i][j].flagged:
                    self.cells[i][j].revealed = True
    
    def check_result(self):
        mines_flagged = 0
        cells_revealed = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cells[i][j].is_mine and self.cells[i][j].flagged:
                    mines_flagged += 1
                if not self.cells[i][j].is_mine and self.cells[i][j].revealed:
                    cells_revealed += 1
        if mines_flagged == self.mines_count and cells_revealed == self.rows * self.columns - self.mines_count:
            self.state = BoardState.FINISHED
            self.result = BoardResult.WON
    
    def place_flag(self, x: int, y: int):
        if not self.cells[x][y].revealed:
            if not self.cells[x][y].flagged and self.flags_count == self.mines_count:
                return
            self.cells[x][y].flagged = not self.cells[x][y].flagged
            self.flags_count += 1 if self.cells[x][y].flagged else -1

    def reveal_neightbors(self, x: int, y: int):
        # Count if the number of adjacent flags is geq than the cell value
        adjacent_flags = 0
        for x_step in [-1, 0, 1]:
            x_adjacent = x + x_step
            if x_adjacent < 0 or x_adjacent >= self.rows:
                continue
            for y_step in [-1, 0, 1]:
                y_adjacent = y + y_step
                if y_adjacent < 0 or y_adjacent >= self.columns:
                    continue
                if x_adjacent == x and y_adjacent == y:
                    continue
                adjacent_flags += 1 if self.cells[x_adjacent][y_adjacent].flagged else 0
        if adjacent_flags < self.cells[x][y].value:
            return
        
        # Perform BFS traverse
        q = [(x, y)]
        visited = set((x, y))
        while len(q) > 0:
            node = q.pop(0)
            self.cells[node[0]][node[1]].revealed = True
            if self.cells[node[0]][node[1]].is_mine:
                self.cells[node[0]][node[1]].exploded = True
                self.state = BoardState.FINISHED
                self.result = BoardResult.LOST
                self.reveal_all()
                break
            if self.cells[node[0]][node[1]].value == 0 or node == (x, y):
                for x_step in [-1, 0, 1]:
                    x_adjacent = node[0] + x_step
                    if x_adjacent < 0 or x_adjacent >= self.rows:
                        continue
                    for y_step in [-1, 0, 1]:
                        y_adjacent = node[1] + y_step
                        if y_adjacent < 0 or y_adjacent >= self.columns:
                            continue
                        if x_adjacent == node[0] and y_adjacent == node[1]:
                            continue
                        if not self.cells[x_adjacent][y_adjacent].revealed and not self.cells[x_adjacent][y_adjacent].flagged and not (x_adjacent, y_adjacent) in visited:
                            visited.add((x_adjacent, y_adjacent))
                            q.append((x_adjacent, y_adjacent))
        
        # Check if board was cleared
        self.check_result()
    
    def reveal_cell(self, x: int, y: int):
        if self.cells[x][y].flagged:
            return
        if self.cells[x][y].revealed:
            self.reveal_neightbors(x, y)
            return
        self.cells[x][y].revealed = True
        if self.cells[x][y].is_mine:
            self.cells[x][y].exploded = True
            self.state = BoardState.FINISHED
            self.result = BoardResult.LOST
            self.reveal_all()
            return
        if self.cells[x][y].value == 0:
            self.reveal_neightbors(x, y)
        
        # Check if board was cleared
        self.check_result()
        
    
    def __str__(self) -> str:
        board = ''
        for i in range(self.rows):
            for j in range(self.columns):
                board += f'{self.cells[i][j].value}\t' if not self.cells[i][j].is_mine else 'M\t'
            board += '\n'
        return board


if __name__ == '__main__':
    b = Board(rows=10, columns=10)
    b.fill(start_x=0, start_y=0)
    print(str(b))