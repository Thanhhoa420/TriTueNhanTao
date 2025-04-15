class Board:
    def __init__(self, size):
        if size not in [3, 5, 7]:
            raise ValueError("Board size must be 3 or 5 or 7.")
        self.size = size
        self.grid = [[" " for _ in range(size)] for _ in range(size)]

    def display(self):
        print("\n".join([" | ".join(row) for row in self.grid]))
        print("-" * (self.size * 4 - 1))

    def is_full(self):
        return all(cell != " " for row in self.grid for cell in row)

    def place_mark(self, row, col, mark):
        if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] == " ":
            self.grid[row][col] = mark
            return True
        return False

    def check_winner(self, mark):
        win_length = 3 if self.size == 3 else 4 if self.size == 5 else 5

        for i in range(self.size):
            for j in range(self.size - win_length + 1):
                if all(self.grid[i][j + k] == mark for k in range(win_length)) or all(
                    self.grid[j + k][i] == mark for k in range(win_length)
                ):
                    return True

        for i in range(self.size - win_length + 1):
            for j in range(self.size - win_length + 1):
                if all(
                    self.grid[i + k][j + k] == mark for k in range(win_length)
                ) or all(
                    self.grid[i + k][j + (win_length - 1 - k)] == mark
                    for k in range(win_length)
                ):
                    return True

        return False
