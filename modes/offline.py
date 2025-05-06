# modes/offline.py

from game.board import Board
from game.logic import GameLogic
import time
import numpy as np  # Thêm import numpy
import sys
import os
from modes.ai import TicTacToeAI


class OfflineGame:
    """
    Lớp quản lý chế độ chơi offline (console)
    """

    # --- THAY ĐỔI BẮT ĐẦU ---
    def __init__(self, master, board_size, opponent="friend", difficulty="medium"):
        """
        Khởi tạo trò chơi offline

        Args:
            master: Không sử dụng trong console, giữ để tương thích
            board_size: Kích thước bàn cờ
            opponent: Đối thủ ("friend" hoặc "bot")
            difficulty: Độ khó của AI ("easy", "medium", "hard") nếu opponent="bot"
        """
        self.master = master
        self.board_size = board_size
        self.opponent = opponent
        self.difficulty = difficulty  # Lưu độ khó

        # Khởi tạo trạng thái game
        self.current_player = 1  # Người chơi 1 (X) đi trước
        self.game_over = False

        # Khởi tạo bàn cờ (sử dụng Board từ game/board.py)
        # Board này dùng 0=trống, 1=X, 2=O
        self.board = Board(None, board_size)  # Bỏ master vì không dùng trong console

        # Khởi tạo logic game (chủ yếu dùng để check win)
        self.logic = GameLogic(board_size)

        # Khởi tạo AI nếu chơi với bot
        self.ai_instance = None
        if self.opponent == "bot":
            # AI dùng 0=trống, 1=X (người), -1=O (AI)
            # mode được truyền để AI biết khi nào cần tải mô hình DQN (chế độ hard)
            self.ai_instance = TicTacToeAI(size=board_size, mode=self.difficulty)
            print(f"Đã khởi tạo AI với độ khó: {self.difficulty}")

    # --- THAY ĐỔI KẾT THÚC ---

    def _convert_board_to_ai_format(self, grid_1_2):
        """Chuyển đổi bàn cờ từ [0, 1, 2] sang numpy [0, 1, -1]"""
        grid_1_neg1 = np.zeros((self.board_size, self.board_size), dtype=np.int8)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if grid_1_2[r][c] == 1:  # Player X
                    grid_1_neg1[r, c] = 1
                elif grid_1_2[r][c] == 2:  # Player O (AI)
                    grid_1_neg1[r, c] = -1
                # else 0 (empty) remains 0
        return grid_1_neg1

    def start(self):
        """Bắt đầu trò chơi"""
        self.board.display()
        while not self.game_over:
            # --- THAY ĐỔI: Kiểm tra đối thủ và lượt chơi ---
            if self.opponent == "bot" and self.current_player == 2:  # Lượt của AI (O)
                self.make_bot_move()
                if self.game_over:  # Kiểm tra lại game_over sau nước đi của bot
                    break
                continue  # Bỏ qua phần nhập của người chơi

            # Lượt của người chơi (X hoặc O nếu là friend vs friend)
            player_symbol = "X" if self.current_player == 1 else "O"
            print(f"Lượt: Người chơi {player_symbol}")
            try:
                move_input = input(f"Nhập hàng và cột (vd: 1 2) cho {player_symbol}: ")
                row, col = map(int, move_input.strip().split())
            except ValueError:
                print(
                    "Định dạng không hợp lệ! Vui lòng nhập dạng 'hàng cột' (vd: 1 2)."
                )
                continue
            except Exception as e:
                print(f"Lỗi nhập liệu: {e}")
                continue

            if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                print(
                    f"Vị trí ({row}, {col}) không hợp lệ! Hàng và cột phải từ 0 đến {self.board_size - 1}."
                )
                continue

            # Sử dụng place_marker của self.board (dùng player 1 hoặc 2)
            if not self.board.place_marker(row, col, self.current_player):
                print(f"Ô ({row}, {col}) đã có người đánh!")
                continue

            self.board.display()

            # Kiểm tra thắng/hòa bằng logic.check_win (dùng player 1 hoặc 2)
            if self.logic.check_win(self.board.grid, row, col, self.current_player):
                print(f"Người chơi {player_symbol} thắng!")
                self.game_over = True
                break  # Kết thúc game

            if self.board.is_full():
                print("Hòa!")
                self.game_over = True
                break  # Kết thúc game

            # Đổi lượt chơi
            self.current_player = 2 if self.current_player == 1 else 1

    def make_bot_move(self):
        """Bot (AI) thực hiện nước đi"""
        if not self.ai_instance:
            print("Lỗi: AI chưa được khởi tạo.")
            self.game_over = True  # Nên dừng game nếu có lỗi
            return

        print(f"Bot (O) đang suy nghĩ với độ khó {self.difficulty}...")
        start_time = time.time()

        # --- THAY ĐỔI BẮT ĐẦU ---
        # 1. Lấy trạng thái bàn cờ hiện tại (định dạng 0, 1, 2)
        current_grid_1_2 = self.board.get_grid()

        # 2. Chuyển đổi sang định dạng AI (numpy 0, 1, -1)
        ai_board_state = self._convert_board_to_ai_format(current_grid_1_2)

        # 3. Cập nhật trạng thái bàn cờ bên trong AI instance
        self.ai_instance.board = ai_board_state

        # 4. Gọi phương thức AI tương ứng
        # AI luôn chơi với quân -1 (O)
        if self.difficulty == "easy":
            move = self.ai_instance.easy_move(-1)
        elif self.difficulty == "medium":
            move = self.ai_instance.medium_move(-1)
        elif self.difficulty == "hard":
            # Có thể cần điều chỉnh tham số episode nếu muốn epsilon khác nhau
            move = self.ai_instance.hard_move(-1)
        else:  # Mặc định hoặc lỗi
            print(f"Độ khó '{self.difficulty}' không hợp lệ, dùng Medium.")
            move = self.ai_instance.medium_move(-1)

        # Xử lý trường hợp AI không tìm được nước đi (nên không xảy ra nếu còn ô trống)
        if move is None:
            available_moves = []
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board.grid[r][c] == 0:
                        available_moves.append((r, c))
            if available_moves:
                move = available_moves[0]  # Chọn đại ô trống đầu tiên
            else:
                print("Lỗi: AI không thể tìm nước đi và bàn cờ không còn ô trống?")
                self.game_over = True
                return

        row, col = move
        # --- THAY ĐỔI KẾT THÚC ---

        end_time = time.time()
        print(f"Bot đã chọn ({row}, {col}) sau {end_time - start_time:.2f} giây.")

        # 5. Thực hiện nước đi trên bàn cờ chính (dùng execute_bot_move)
        self.execute_bot_move(row, col)

    def execute_bot_move(self, row, col):
        """Thực hiện nước đi của bot và kiểm tra kết quả"""
        # Đặt quân trên bàn cờ chính (dùng player 2 là 'O')
        success = self.board.place_marker(row, col, self.current_player)

        if not success:
            print(f"Lỗi nghiêm trọng: AI chọn ô đã đánh ({row}, {col})")
            # Cố gắng tìm nước đi khác nếu có thể, hoặc dừng game
            # Đây là dấu hiệu lỗi trong logic AI hoặc đồng bộ trạng thái
            self.game_over = True
            return

        print(f"Bot (O) đánh vào ({row}, {col})")
        self.board.display()

        # Kiểm tra thắng/hòa bằng logic.check_win (dùng player 2)
        if self.logic.check_win(self.board.grid, row, col, self.current_player):
            print("Bot (O) thắng!")
            self.game_over = True
            return  # Game kết thúc

        if self.board.is_full():
            print("Hòa!")
            self.game_over = True
            return  # Game kết thúc

        # Nếu chưa kết thúc, chuyển lượt lại cho người chơi 1
        self.current_player = 1
