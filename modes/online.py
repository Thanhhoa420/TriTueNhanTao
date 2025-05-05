import threading
import random

from game.board import Board
from game.logic import GameLogic
from utils.network import NetworkManager


class OnlineGame:
    """
    Lớp quản lý chế độ chơi online (console)
    """

    def __init__(self, master, board_size):
        """
        Khởi tạo trò chơi online

        Args:
            master: Không sử dụng trong console, giữ để tương thích
            board_size: Kích thước bàn cờ
        """
        self.master = master
        self.board_size = board_size

        # Khởi tạo trạng thái game
        self.current_player = 1  # Người chơi 1 (X) đi trước
        self.game_over = False
        self.my_turn = False  # Có phải lượt của mình không
        self.my_marker = None  # Quân cờ của mình (1: X, 2: O)

        # Khởi tạo bàn cờ
        self.board = Board(master, board_size)

        # Khởi tạo logic game
        self.logic = GameLogic(board_size)

        # Khởi tạo network manager
        self.network = NetworkManager()
        self.network.on_data_received = self.handle_server_message
        self.network.on_disconnected = self.handle_disconnection

        # Thông tin người chơi
        self.player_name = ""
        self.opponent_name = ""

    def start(self):
        """Bắt đầu trò chơi"""
        self.player_name = input("Nhập tên của bạn: ").strip()
        if not self.player_name:
            self.player_name = f"Player{random.randint(1000, 9999)}"

        if not self.network.connect():
            print("Không thể kết nối đến server!")
            return

        print("Đang tìm trận đấu...")
        if not self.network.find_match(self.player_name, self.board_size):
            print("Không thể gửi yêu cầu tìm trận!")
            return

        while not self.game_over:
            if self.my_turn:
                self.board.display()
                print(f"Lượt của bạn ({'X' if self.my_marker == 1 else 'O'})")
                try:
                    row = int(input("Nhập hàng: "))
                    col = int(input("Nhập cột: "))
                except ValueError:
                    print("Vui lòng nhập số hợp lệ!")
                    continue

                if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                    print("Vị trí không hợp lệ!")
                    continue

                if self.board.grid[row][col] != 0:
                    print("Ô đã có người đánh!")
                    continue

                current_player = self.my_marker
                success = self.board.place_marker(row, col, current_player)

                if success:
                    self.network.send_move(row, col)

                    if self.logic.check_win(self.board.grid, row, col, current_player):
                        self.board.display()
                        print("Bạn thắng!")
                        self.game_over = True
                        break

                    if self.board.is_full():
                        self.board.display()
                        print("Hòa!")
                        self.game_over = True
                        break

                    self.my_turn = False
            else:
                pass  # Chờ server gửi nước đi đối thủ

    def handle_server_message(self, message):
        """Xử lý tin nhắn từ server"""
        message_type = message.get("type")

        if message_type == "match_found":
            self.opponent_name = message["opponent_name"]
            self.my_marker = message["marker"]
            self.my_turn = self.my_marker == 1
            self.match_found()
        elif message_type == "move":
            row, col = message["row"], message["col"]
            self.execute_opponent_move(row, col)

    def handle_disconnection(self):
        """Xử lý khi mất kết nối"""
        print("Mất kết nối đến server!")
        self.game_over = True

    def match_found(self):
        """Xử lý khi tìm thấy trận đấu"""
        self.board.reset()
        my_marker_text = "X" if self.my_marker == 1 else "O"
        opponent_marker_text = "O" if self.my_marker == 1 else "X"
        print(f"Đã kết nối với: {self.opponent_name}")
        print(f"Bạn chơi: {my_marker_text} | Đối thủ: {opponent_marker_text}")
        print(f"{'Bạn đi trước.' if self.my_turn else 'Đối thủ đi trước.'}")

    def on_cell_click(self, row, col):
        """Không sử dụng trong console, giữ để tương thích"""
        pass

    def execute_opponent_move(self, row, col):
        """Thực hiện nước đi của đối thủ"""
        opponent_marker = 2 if self.my_marker == 1 else 1
        self.board.place_marker(row, col, opponent_marker)
        print(f"Đối thủ đánh vào ({row}, {col})")
        self.board.display()

        if self.logic.check_win(self.board.grid, row, col, opponent_marker):
            print("Đối thủ thắng!")
            self.game_over = True
            return

        if self.board.is_full():
            print("Hòa!")
            self.game_over = True
            return

        self.my_turn = True

    def update_info_label(self):
        """Không sử dụng trong console, giữ để tương thích"""
        pass
