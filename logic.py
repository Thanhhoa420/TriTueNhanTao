class Board:
    def __init__(self, size):
        if size not in [3, 5]:
            raise ValueError("Board size must be 3 or 5.")
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
        win_length = 3

        # Kiểm tra hàng và cột
        for i in range(self.size):
            for j in range(self.size - win_length + 1):
                if all(self.grid[i][j + k] == mark for k in range(win_length)) or all(
                    self.grid[j + k][i] == mark for k in range(win_length)
                ):
                    return True

        # Kiểm tra đường chéo chính và phụ
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


class Main:
    def __init__(self, size):
        self.board = Board(size)
        self.current_player = "X"

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def play_game(self):
        while True:
            self.board.display()
            try:
                row, col = map(
                    int,
                    input(
                        f"Player {self.current_player}, enter your move (row col): "
                    ).split(),
                )
            except ValueError:
                print("Invalid input. Enter two numbers separated by a space.")
                continue

            if not self.board.place_mark(row, col, self.current_player):
                print("Invalid move. Try again.")
                continue

            if self.board.check_winner(self.current_player):
                self.board.display()
                print(f"Player {self.current_player} wins!")
                break

            if self.board.is_full():
                self.board.display()
                print("It's a draw!")
                break

            self.switch_player()


if __name__ == "__main__":
    while True:
        try:
            size = int(input("Enter the size of the board (3 or 5): "))
            if size in [3, 5]:
                break
            print("Invalid size. Please enter 3 or 5.")
        except ValueError:
            print("Invalid input. Enter a number.")

    game = Main(size)
    game.play_game()
