# --- START OF FILE manhinh3_refactored.py ---

import tkinter as tk
from tkinter import messagebox
import os
import sys
import random
import subprocess
import pickle
import threading
import queue

# Import các lớp game logic và board
from game.board import Board
from game.logic import GameLogic
from modes.offline import OfflineGame
from modes.online import OnlineGame
from hopthoai import toss_coin
import pygame
script_dir = os.path.dirname(__file__)
def play_background_music():
    global music_on
    try:
        pygame.mixer.init()
        music_path = os.path.join(script_dir, "funny-kids-cartoon-background-music-333104.mp3")
        if not os.path.exists(music_path):
            print(f"Lỗi: Không tìm thấy file nhạc: {music_path}")
            return
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.03)  # Âm lượng 30%
        pygame.mixer.music.play(-1)  # Lặp vô hạn
        music_on = True
    except Exception as e:
        print(f"Lỗi khi phát nhạc: {e}")
play_background_music()

# Cần import NetworkManager nếu OnlineGame dùng trực tiếp
# from utils.network import NetworkManager

# Hằng số
CELL_SIZE = 80  # Kích thước mỗi ô
PLAYER_SYMBOLS = {1: "X", 2: "♡"}  # Sử dụng 1 và 2 như trong logic
PLAYER_COLORS = {1: "red", 2: "purple"}
AI_PLAYER_NUM = 2  # AI luôn là người chơi 2 (O)
HUMAN_PLAYER_NUM = 1  # Người chơi luôn là 1 (X) trong chế độ vs AI


class GameScreen:
    def __init__(self, master, game_settings):
        self.master = master
        self.settings = game_settings
        self.mode = self.settings["mode"]
        self.board_size = self.settings["size"]
        self.difficulty = self.settings["difficulty"]
        self.username = self.settings["username"]

        self.game_instance = None
        self.game_logic = GameLogic(self.board_size)  # Logic kiểm tra thắng/thua
        self.game_over = False
        self.message_queue = queue.Queue()  # Queue cho network messages

        self.master.title(
            f"Tic-Tac-Toe - {self.board_size}x{self.board_size} ({self.mode.capitalize()})"
        )
        self.master.configure(bg="#ffe6f0")  # Màu nền hồng nhạt

        self.canvas_size = CELL_SIZE * self.board_size
        self.canvas = tk.Canvas(
            self.master,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#fff0f5",
            highlightthickness=1,
            highlightbackground="gray",
        )
        self.canvas.pack(pady=20, padx=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.info_frame = tk.Frame(self.master, bg="#ffe6f0")
        self.info_frame.pack(pady=5, fill=tk.X, padx=20)

        self.status_label = tk.Label(
            self.info_frame,
            text="Đang khởi tạo...",
            font=("Arial", 14, "bold"),
            fg="#ff4d88",
            bg="#ffe6f0",
            wraplength=self.canvas_size,  # Giới hạn chiều rộng
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.control_frame = tk.Frame(self.master, bg="#ffe6f0")
        self.control_frame.pack(pady=15, fill=tk.X, padx=20)

        self.reset_button = tk.Button(
            self.control_frame,
            text="🔁 Chơi lại",
            font=("Arial", 12),
            width=15,
            bg="#ffb3d9",
            command=self.reset_game,
            state=tk.DISABLED,  # Sẽ enable sau khi initialize
        )
        self.reset_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.back_button = tk.Button(
            self.control_frame,
            text="⏪ Thoát về Menu",
            font=("Arial", 12),
            width=15,
            bg="#ffb3d9",
            command=self.back_to_menu,
        )
        self.back_button.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)

        self.master.protocol(
            "WM_DELETE_WINDOW", self.on_closing
        )  # Xử lý khi đóng cửa sổ

        # Khởi tạo game
        self.initialize_game()
        # Vẽ lưới ban đầu
        self.draw_grid()

        # Bắt đầu xử lý message queue cho chế độ online
        if self.mode == "online":
            self.master.after(100, self.process_message_queue)

    def initialize_game(self):
        """Khởi tạo instance game dựa trên chế độ"""
        self.game_over = False
        self.reset_button.config(state=tk.NORMAL)  # Enable nút reset
        # Xóa thuộc tính cũ không còn dùng trên GameScreen
        if hasattr(self, "current_player_num"):
            del self.current_player_num

        if self.mode == "ai":
            self.game_instance = OfflineGame(
                master=None,
                board_size=self.board_size,
                opponent="bot",
                difficulty=self.difficulty,
            )
            # *** Gán player bắt đầu cho đối tượng OfflineGame ***
            self.game_instance.current_player = (
                HUMAN_PLAYER_NUM  # Player 1 (X) đi trước
            )
            print(
                f"DEBUG: Initialized AI mode. Game instance player: {self.game_instance.current_player}"
            )
        elif self.mode == "friend":
            self.game_instance = OfflineGame(
                master=None, board_size=self.board_size, opponent="friend"
            )
            # *** Gán player bắt đầu cho đối tượng OfflineGame ***
            self.game_instance.current_player = toss_coin(self.master)  # 1 hoặc 2
            print(
                f"DEBUG: Initialized Friend mode. Game instance player: {self.game_instance.current_player}"
            )
        elif self.mode == "online":
            self.game_instance = OnlineGame(master=None, board_size=self.board_size)
            self.game_instance.player_name = self.username
            # Gán callbacks
            self.game_instance.network.on_data_received = self.handle_server_message_gui
            self.game_instance.network.on_disconnected = self.handle_disconnection_gui
            # Cập nhật trạng thái và bắt đầu kết nối trong thread
            self.update_status_label("Đang kết nối server...")
            threading.Thread(target=self.connect_and_find_match, daemon=True).start()
        else:
            messagebox.showerror(
                "Lỗi", f"Chế độ chơi không hợp lệ: {self.mode}", parent=self.master
            )
            self.back_to_menu()
            return  # Ngăn không chạy tiếp

        # Reset lại canvas và cập nhật label trạng thái ban đầu
        self.canvas.delete("all")
        self.draw_grid()
        # Gọi update_status_label sau khi đã gán current_player cho offline modes
        self.update_status_label()

    # Trong class GameScreen của file manhinh3_refactored.py
    def connect_and_find_match(self):
        """Thực hiện kết nối và tìm trận cho chế độ Online"""
        print("CLIENT MANHINH3 DEBUG: Hàm connect_and_find_match ĐƯỢC GỌI.")
        if not self.game_instance or not isinstance(self.game_instance, OnlineGame):
            print("CLIENT MANHINH3 DEBUG: Lỗi - game_instance không hợp lệ.")
            return

        print("CLIENT MANHINH3 DEBUG: Bắt đầu gọi network.connect()...")
        try:
            connection_success = self.game_instance.network.connect()
        except Exception as e:
            print(
                f"CLIENT MANHINH3 DEBUG: Lỗi xảy ra TRONG KHI gọi network.connect(): {e}"
            )
            self.game_over = True
            # self.master.after(0, self.update_status_label, "Lỗi kết nối nghiêm trọng!")
            return

        if not connection_success:
            print("CLIENT MANHINH3 DEBUG: network.connect() trả về False.")
            self.game_over = True
            return

        print(
            "CLIENT MANHINH3 DEBUG: network.connect() thành công. Chuẩn bị gọi find_match..."
        )
        self.master.after(0, self.update_status_label, "Đã kết nối. Đang tìm trận...")

        try:
            print(
                f"CLIENT MANHINH3 DEBUG: Chuẩn bị gọi network.find_match(name='{self.username}', size={self.board_size})..."
            )
            find_match_success = self.game_instance.network.find_match(
                self.username, self.board_size
            )

            if not find_match_success:
                print(
                    "CLIENT MANHINH3 DEBUG: network.find_match() trả về False (Gửi thất bại!)."
                )
                self.game_over = True
                # self.master.after(0, self.update_status_label, "Lỗi gửi yêu cầu tìm trận!")
                return
            else:
                print(
                    "CLIENT MANHINH3 DEBUG: network.find_match() trả về True (Đã gửi thành công, chờ server phản hồi)."
                )
        except Exception as e:
            print(
                f"CLIENT MANHINH3 DEBUG: Lỗi xảy ra TRONG KHI gọi network.find_match(): {e}"
            )
            self.game_over = True
            # self.master.after(0, self.update_status_label, f"Lỗi nghiêm trọng khi tìm trận: {e}")
            return

        print(
            "CLIENT MANHINH3 DEBUG: Thread connect_and_find_match kết thúc bình thường."
        )

    def draw_grid(self):
        """Vẽ lưới bàn cờ"""
        for i in range(self.board_size + 1):
            self.canvas.create_line(
                0, i * CELL_SIZE, self.canvas_size, i * CELL_SIZE, fill="#999", width=2
            )
            self.canvas.create_line(
                i * CELL_SIZE, 0, i * CELL_SIZE, self.canvas_size, fill="#999", width=2
            )

    def draw_symbol(self, row, col, player_num):
        """Vẽ ký hiệu X hoặc O vào ô"""
        if player_num not in PLAYER_SYMBOLS:
            return
        x_center = col * CELL_SIZE + CELL_SIZE / 2
        y_center = row * CELL_SIZE + CELL_SIZE / 2
        symbol = PLAYER_SYMBOLS[player_num]
        color = PLAYER_COLORS[player_num]
        font_size = CELL_SIZE // 2
        self.canvas.create_text(
            x_center,
            y_center,
            text=symbol,
            font=("Arial", font_size, "bold"),
            fill=color,
            tags="symbol",
        )

    # Trong class GameScreen của file manhinh3_refactored.py
    def update_status_label(self, message=None):
        """Cập nhật nhãn trạng thái/lượt chơi"""
        if self.game_over and not message:
            return
        if message:
            self.status_label.config(text=message)
            return

        status = "Trạng thái không xác định"
        try:  # Thêm try-except để bắt lỗi tiềm ẩn khi truy cập game_instance
            if self.mode == "online":
                if self.game_instance and isinstance(self.game_instance, OnlineGame):
                    if self.game_instance.my_marker is None:
                        status = "Đang chờ ghép trận..."
                    elif self.game_instance.my_turn:
                        my_sym = PLAYER_SYMBOLS.get(self.game_instance.my_marker, "?")
                        status = f"Lượt của bạn ({my_sym})"
                    else:
                        opponent_marker = 3 - self.game_instance.my_marker
                        opp_sym = PLAYER_SYMBOLS.get(opponent_marker, "?")
                        opp_name = (
                            self.game_instance.opponent_name
                            if self.game_instance.opponent_name
                            else "Đối thủ"
                        )
                        status = f"Đợi {opp_name} ({opp_sym}) đi..."
                else:
                    status = "Đang khởi tạo Online..."
            elif self.mode == "ai":
                # Đọc từ game_instance
                if self.game_instance and hasattr(self.game_instance, "current_player"):
                    current_player = self.game_instance.current_player
                    current_symbol = PLAYER_SYMBOLS.get(current_player, "?")
                    if current_player == HUMAN_PLAYER_NUM:
                        status = f"Lượt của bạn ({current_symbol})"
                    else:
                        status = f"Máy ({current_symbol}) đang nghĩ..."
                else:
                    status = "Đang khởi tạo AI..."
            elif self.mode == "friend":
                # Đọc từ game_instance
                if self.game_instance and hasattr(self.game_instance, "current_player"):
                    current_player = self.game_instance.current_player
                    current_symbol = PLAYER_SYMBOLS.get(current_player, "?")
                    status = f"Lượt của Người chơi {current_player} ({current_symbol})"
                else:
                    status = "Đang khởi tạo Friend..."
        except Exception as e:
            print(f"Lỗi trong update_status_label: {e}")
            status = "Lỗi hiển thị trạng thái"

        self.status_label.config(text=status)

    def on_canvas_click(self, event):
        """Xử lý khi click vào ô trên bàn cờ"""
        if self.game_over:
            return
        if (
            self.mode == "ai"
            and self.game_instance
            and self.game_instance.current_player == AI_PLAYER_NUM
        ):
            print("Không phải lượt của bạn (AI đang đi).")
            return  # Ngăn click khi AI đang đi

        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return

        # Xử lý theo mode
        if self.mode == "online":
            if self.game_instance and self.game_instance.my_turn:
                self.handle_human_move(row, col)
            else:
                print("Không phải lượt của bạn (Online) hoặc chưa kết nối!")
        elif self.mode == "ai" or self.mode == "friend":
            # Offline: Luôn xử lý nếu không phải lượt AI (đã kiểm tra ở trên)
            self.handle_human_move(row, col)

    def handle_human_move(self, row, col):
        """Xử lý nước đi của người chơi (chung cho các mode)"""
        player_to_move = None
        if self.mode == "online":
            if self.game_instance and self.game_instance.my_marker is not None:
                player_to_move = self.game_instance.my_marker
            else:
                print("Lỗi handle_human_move (online): my_marker chưa được xác định!")
                return False
        elif self.mode == "ai" or self.mode == "friend":
            # Truy cập vào game_instance
            if self.game_instance and hasattr(self.game_instance, "current_player"):
                player_to_move = self.game_instance.current_player
            else:
                print(
                    f"Lỗi handle_human_move ({self.mode}): game_instance hoặc current_player không tồn tại!"
                )
                return False
        else:
            print(f"Lỗi handle_human_move: Chế độ không xác định '{self.mode}'")
            return False

        if player_to_move is None:
            print(
                "Lỗi handle_human_move: Không xác định được player_to_move (sau khi kiểm tra mode)."
            )
            return False

        if not self.game_instance or not hasattr(self.game_instance, "board"):
            print("Lỗi handle_human_move: game_instance hoặc board không hợp lệ.")
            return False
        board_grid = self.game_instance.board.grid

        if board_grid[row][col] != 0:
            print(f"Ô ({row},{col}) đã được đánh!")
            return False

        # 1. Thực hiện nước đi trên board logic của game_instance
        success = self.game_instance.board.place_marker(row, col, player_to_move)
        if not success:
            print(f"Lỗi: Không thể đặt quân vào ({row},{col})?")
            return False

        # 2. Vẽ quân cờ lên GUI
        self.draw_symbol(row, col, player_to_move)

        # 3. Xử lý sau nước đi (Gửi/Chuyển lượt)
        if self.mode == "online":
            self.game_instance.my_turn = False
            self.update_status_label()
            print(f"CLIENT DEBUG: Chuẩn bị gửi move ({row},{col}) sau khi đi.")
            send_success = self.game_instance.network.send_move(row, col)
            if not send_success:
                print("Lỗi gửi nước đi lên server!")
        else:  # Offline
            # Gọi hàm switch_player của GameScreen
            self.switch_player()  # Hàm này sẽ cập nhật self.game_instance.current_player và label
            # Nếu là AI và đến lượt AI
            # Kiểm tra lại player sau khi switch
            if self.mode == "ai" and self.game_instance.current_player == AI_PLAYER_NUM:
                self.trigger_ai_move()  # Hàm này của GameScreen

        # 4. Kiểm tra thắng/hòa
        game_ended = self.check_game_end(row, col, player_to_move)
        if game_ended:
            print(
                f"Game kết thúc sau nước đi của player {player_to_move} tại ({row},{col})"
            )

        return True

    def check_game_end(self, last_row, last_col, player_num):
        """Kiểm tra thắng hoặc hòa sau nước đi"""
        # Luôn kiểm tra từ grid của game_instance
        if not self.game_instance:
            return False
        board_grid = self.game_instance.board.grid
        is_win = self.game_logic.check_win(board_grid, last_row, last_col, player_num)

        if is_win:
            self.game_over = True
            win_message = ""
            winner_symbol = PLAYER_SYMBOLS.get(
                player_num, "?"
            )  # Lấy symbol để hiển thị
            if self.mode == "online":
                if player_num == self.game_instance.my_marker:
                    win_message = "Chúc mừng! Bạn đã thắng!"
                else:
                    opp_name = (
                        self.game_instance.opponent_name
                        if self.game_instance.opponent_name
                        else "Đối thủ"
                    )
                    win_message = f"Bạn đã thua! {opp_name} ({winner_symbol}) thắng."
            elif self.mode == "ai":
                win_message = (
                    "Bạn thắng!"
                    if player_num == HUMAN_PLAYER_NUM
                    else f"Máy ({winner_symbol}) thắng!"
                )
            elif self.mode == "friend":
                win_message = f"Người chơi {player_num} ({winner_symbol}) thắng!"

            self.status_label.config(
                text=win_message
            )  # Cập nhật label trạng thái thắng/thua
            messagebox.showinfo("Kết thúc game", win_message, parent=self.master)
            self.reset_button.config(state=tk.NORMAL)  # Cho phép reset
            return True
        elif self.game_instance.board.is_full():
            self.game_over = True
            draw_message = "Hòa!"
            self.status_label.config(text=draw_message)  # Cập nhật label hòa
            messagebox.showinfo("Kết thúc game", draw_message, parent=self.master)
            self.reset_button.config(state=tk.NORMAL)  # Cho phép reset
            return True

        return False

    def switch_player(self):
        """Đổi lượt chơi (chỉ cho offline) và cập nhật trạng thái game_instance"""
        if (
            self.mode != "online"
            and self.game_instance
            and hasattr(self.game_instance, "current_player")
        ):
            self.game_instance.current_player = (
                3 - self.game_instance.current_player
            )  # Đổi người chơi trong instance
            self.update_status_label()  # Cập nhật label GUI

    def trigger_ai_move(self):
        """Kích hoạt nước đi của AI (chạy trong thread để không treo GUI)"""
        if (
            self.game_over
            or not self.mode == "ai"
            or not self.game_instance
            or self.game_instance.current_player != AI_PLAYER_NUM
        ):
            return

        # Cập nhật label trong main thread trước khi chạy thread AI
        self.master.after(0, self.update_status_label)  # Đảm bảo chạy trong main thread
        threading.Thread(target=self.execute_ai_move_thread, daemon=True).start()

    def execute_ai_move_thread(self):
        """Thread thực hiện việc tính toán nước đi của AI"""
        try:
            # --- Logic tính toán AI giữ nguyên, truy cập self.game_instance ---
            if not self.game_instance or not hasattr(self.game_instance, "ai_instance"):
                print("Lỗi thread AI: game_instance hoặc ai_instance không tồn tại.")
                return

            # Lấy trạng thái board từ game_instance.board
            current_grid_1_2 = self.game_instance.board.get_grid()
            ai_board_state = self.game_instance._convert_board_to_ai_format(
                current_grid_1_2
            )
            self.game_instance.ai_instance.board = ai_board_state

            move = None
            ai_marker_for_logic = -1
            if self.difficulty == "easy":
                move = self.game_instance.ai_instance.easy_move(ai_marker_for_logic)
            elif self.difficulty == "medium":
                move = self.game_instance.ai_instance.medium_move(ai_marker_for_logic)
            elif self.difficulty == "hard":
                move = self.game_instance.ai_instance.hard_move(ai_marker_for_logic)

            if move is None:
                # ... (Xử lý AI không tìm được nước đi như cũ) ...
                available_moves = []
                for r in range(self.board_size):
                    for c in range(self.board_size):
                        if self.game_instance.board.grid[r][c] == 0:
                            available_moves.append((r, c))
                if available_moves:
                    move = random.choice(available_moves)

            if move:
                # Gửi nước đi về main thread để áp dụng
                self.master.after(0, self.apply_ai_move, move[0], move[1])
            else:
                print("Lỗi: AI không tìm được nước đi và không còn ô trống!")
                # Check hòa trong main thread nếu cần
                if self.game_instance.board.is_full():
                    self.master.after(0, self.check_game_end, -1, -1, 0)

        except Exception as e:
            print(f"Lỗi nghiêm trọng trong thread AI: {e}")
            self.master.after(0, self.update_status_label, f"Lỗi AI: {e}")

    def apply_ai_move(self, row, col):
        """Thực hiện nước đi của AI trên GUI và logic (trong main thread)"""
        if self.game_over or not self.game_instance:
            return

        ai_player = AI_PLAYER_NUM

        # 1. Thực hiện trên board logic của game_instance
        success = self.game_instance.board.place_marker(row, col, ai_player)
        if not success:
            print(f"Lỗi nghiêm trọng: AI chọn ô đã đánh ({row},{col})")
            # Không nên chuyển lượt ở đây, AI cần tính lại hoặc dừng game
            # self.switch_player()
            return

        # 2. Vẽ lên GUI
        self.draw_symbol(row, col, ai_player)

        # 3. Kiểm tra thắng/hòa
        game_ended = self.check_game_end(row, col, ai_player)
        if game_ended:
            return  # Game kết thúc

        # 4. Chuyển lượt lại cho người chơi (chỉ nếu game chưa kết thúc)
        self.switch_player()  # Hàm này của GameScreen, sẽ cập nhật game_instance

    # --- Xử lý Network cho GUI (Giữ nguyên) ---
    def handle_server_message_gui(self, message):
        self.message_queue.put(message)

    def process_message_queue(self):
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                print(
                    f"CLIENT GUI DEBUG: Processing message: {message}"
                )  # Giữ lại DEBUG
                message_type = message.get("type")

                if message_type == "waiting":
                    self.update_status_label("Đang chờ đối thủ...")
                elif message_type == "match_found":
                    print(
                        "CLIENT GUI DEBUG: Processing 'match_found' message."
                    )  # Giữ lại DEBUG
                    self.game_instance.opponent_name = message["opponent_name"]
                    self.game_instance.my_marker = message["marker"]
                    self.game_instance.my_turn = self.game_instance.my_marker == 1
                    self.game_over = False
                    self.canvas.delete("all")
                    self.draw_grid()
                    self.reset_button.config(state=tk.DISABLED)
                    match_msg = f"Đã ghép cặp với {self.game_instance.opponent_name}! Bạn chơi '{PLAYER_SYMBOLS[self.game_instance.my_marker]}'."
                    # Tạm thời hiển thị message này trước khi cập nhật lượt
                    self.status_label.config(text=match_msg)  # Cập nhật tạm thời
                    messagebox.showinfo("Tìm thấy trận!", match_msg, parent=self.master)
                    # Gọi update_status_label để hiển thị đúng lượt đi ban đầu
                    self.update_status_label()
                elif message_type == "move":
                    if self.game_instance and not self.game_instance.my_turn:
                        row, col = message["row"], message["col"]
                        self.execute_opponent_move_gui(row, col)
                    else:
                        print(
                            "Nhận được move message khi đang là lượt mình hoặc game_instance lỗi?"
                        )
                elif message_type == "opponent_disconnected":
                    self.handle_disconnection_gui(opponent_left=True)
                elif message_type == "error":  # Xử lý message lỗi từ server nếu có
                    error_msg = message.get("message", "Lỗi không xác định từ server.")
                    print(f"Lỗi từ Server: {error_msg}")
                    messagebox.showerror("Lỗi Server", error_msg, parent=self.master)
                    # Có thể cần xử lý thêm tùy lỗi

        except queue.Empty:
            pass
        except Exception as e:  # Bắt lỗi chung khi xử lý queue
            print(f"Lỗi trong process_message_queue: {e}")
        finally:
            if self.mode == "online" and not self.game_over:
                self.master.after(100, self.process_message_queue)

    def execute_opponent_move_gui(self, row, col):
        """Thực hiện nước đi của đối thủ online trên GUI"""
        if (
            self.game_over
            or not self.game_instance
            or not isinstance(self.game_instance, OnlineGame)
            or self.game_instance.my_marker is None
        ):  # Thêm kiểm tra my_marker
            return

        opponent_marker = 3 - self.game_instance.my_marker  # 1->2, 2->1

        if self.game_instance.board.grid[row][col] != 0:
            print(f"Lỗi: Đối thủ đánh vào ô đã có quân ({row},{col})")
            return

        # Đặt quân lên logic board
        self.game_instance.board.place_marker(row, col, opponent_marker)
        # Vẽ lên GUI
        self.draw_symbol(row, col, opponent_marker)

        # Kiểm tra thắng/hòa
        game_ended = self.check_game_end(row, col, opponent_marker)
        if game_ended:
            return  # Game kết thúc

        # Đến lượt mình (chỉ nếu game chưa kết thúc)
        self.game_instance.my_turn = True
        self.update_status_label()

    def handle_disconnection_gui(self, opponent_left=False):
        """Xử lý khi mất kết nối server hoặc đối thủ thoát"""
        if self.game_over:
            return
        self.game_over = True
        disconnect_message = "Mất kết nối đến server!"
        if opponent_left:
            disconnect_message = "Đối thủ đã thoát trận!"
        self.status_label.config(text=disconnect_message)
        messagebox.showwarning("Mất kết nối", disconnect_message, parent=self.master)
        self.reset_button.config(state=tk.DISABLED)
        self.back_button.config(text="⏪ Thoát về Menu")

    def reset_game(self):
        """Reset lại game (chỉ cho offline)"""
        if self.mode == "online":
            messagebox.showinfo(
                "Thông báo",
                "Không thể chơi lại trong chế độ Online.",
                parent=self.master,
            )
            return

        # Đảm bảo game_instance tồn tại và đúng chế độ
        if self.game_instance and (self.mode == "ai" or self.mode == "friend"):
            print(f"Resetting game for mode: {self.mode}")
            self.game_instance.board.reset()
            self.game_over = False
            self.canvas.delete("symbol")

            # *** Gán lại current_player cho game_instance ***
            if self.mode == "ai":
                self.game_instance.current_player = HUMAN_PLAYER_NUM
                print(
                    f"DEBUG: Reset AI mode. Game instance player: {self.game_instance.current_player}"
                )
            elif self.mode == "friend":
                self.game_instance.current_player = toss_coin(self.master)
                print(
                    f"DEBUG: Reset Friend mode. Game instance player: {self.game_instance.current_player}"
                )

            # Cập nhật GUI
            self.update_status_label()
            # Vẽ lại lưới nếu cần (thường không cần vì chỉ xóa symbols)
            # self.draw_grid()
        else:
            print(
                f"Lỗi reset_game: game_instance ({self.game_instance}) không hợp lệ hoặc chế độ ({self.mode}) không phải offline."
            )
            # Có thể thử initialize lại nếu muốn
            # self.initialize_game()

    def back_to_menu(self):
        """Quay lại màn hình menu chính"""
        self.on_closing(ask=False)
        self.master.destroy()
        subprocess.Popen([sys.executable, "manhinh2.py"])

    def on_closing(self, ask=True):
        """Xử lý khi người dùng đóng cửa sổ"""
        do_close = False
        if ask:
            if messagebox.askokcancel(
                "Thoát", "Bạn có chắc muốn thoát trận đấu?", parent=self.master
            ):
                do_close = True
        else:  # Nếu không hỏi (ví dụ từ back_to_menu)
            do_close = True

        if do_close:
            # Đóng kết nối nếu là online và đang kết nối
            if (
                self.mode == "online"
                and self.game_instance
                and hasattr(self.game_instance, "network")
                and self.game_instance.network.connected
            ):
                print("Đang đóng kết nối mạng...")
                self.game_instance.network.disconnect()

            # Hủy cửa sổ chính
            if not ask:  # Nếu gọi từ back_to_menu, master đã destroy rồi
                pass
            else:
                self.master.destroy()


if __name__ == "__main__":
    settings_path = "temp_game_settings.dat"
    game_settings = None
    try:
        with open(settings_path, "rb") as f:
            game_settings = pickle.load(f)
        # Không xóa file ở đây nữa, để test dễ hơn
        # os.remove(settings_path)
        print(f"Đã đọc cài đặt từ {settings_path}: {game_settings}")
    except FileNotFoundError:
        print(f"Không tìm thấy {settings_path}. Sử dụng cài đặt mặc định.")
        game_settings = {
            "mode": "ai",
            "size": 3,
            "difficulty": "easy",
            "username": "TestGuest",
        }
    except Exception as e:
        print(f"Lỗi khi đọc file cài đặt: {e}")
        sys.exit(1)

    if game_settings:
        root = tk.Tk()
        app = GameScreen(root, game_settings)
        root.mainloop()
    else:
        print("Không có cài đặt game để chạy.")

# --- END OF FILE manhinh3_refactored.py ---
