from logic import Board

# Import lớp bot nếu đã hoàn thiện
# from bot_player import BotPlayer
import random


class OfflineGame:
    def __init__(self, size, mode):
        self.board = Board(size)
        self.current_player = "X"
        self.mode = mode  # 'friend' hoặc 'bot'

        # Nếu chế độ chơi là với bot thì khởi tạo bot
        # self.bot = BotPlayer() if mode == "bot" else None
        self.bot = None  # ← Sẽ thay thế bằng BotPlayer() sau khi phát triển xong bot

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def play(self):
        while True:
            self.board.display()

            # Nếu đang ở chế độ bot và lượt của bot
            if self.mode == "bot" and self.current_player == "O":
                # Khi phát triển xong bot, thay thế đoạn dưới bằng:
                # row, col = self.bot.choose_move(self.board)

                # Tạm thời dùng random để chọn nước đi
                size = self.board.size
                empty_cells = [
                    (i, j)
                    for i in range(size)
                    for j in range(size)
                    if self.board.grid[i][j] == " "
                ]
                row, col = random.choice(empty_cells)

                print(f"Bot chose: {row} {col}")
            else:
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
