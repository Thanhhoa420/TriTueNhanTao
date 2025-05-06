# --- START OF FILE manhinh2.py ---

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import pygame 
# Import các hàm dialog đã chỉnh sửa và các lớp game logic
from hopthoai import choose_difficulty, choose_board_size, toss_coin
from modes.offline import OfflineGame
from modes.online import OnlineGame  # Cần có NetworkManager hoạt động

# Giả sử có GameScreen trong manhinh3_refactored.py
# from manhinh3_refactored import GameScreen

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
class MainMenu:
    def __init__(self, master, username):
        self.master = master
        self.username = username if username else "Khách"
        self.master.title(f"Tic-Tac-Toe - Menu Chính ({self.username})")
        self.master.geometry("500x450")  # Tăng chiều cao một chút
        self.master.configure(bg="#ffc0cb")  # Màu hồng làm nền

        # Lưu trữ lựa chọn game
        self.selected_mode = None  # "ai", "friend", "online"
        self.selected_size = None  # 3, 5, 7
        self.selected_difficulty = None  # "easy", "medium", "hard" (chỉ cho mode "ai")

        self.setup_ui()

    def setup_ui(self):
        # Tạo menu bar (giữ nguyên)
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Hướng dẫn",
            command=lambda: messagebox.showinfo(
                "Hướng dẫn",
                "Chọn chế độ chơi, cấu hình (nếu cần) và nhấn 'Bắt đầu game'!",
                parent=self.master,
            ),
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="Giới thiệu",
            command=lambda: messagebox.showinfo(
                "Giới thiệu", "Tic-Tac-Toe GUI tích hợp", parent=self.master
            ),
        )
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)

        # Phần chính
        tk.Label(
            self.master,
            text="Chọn chế độ chơi",
            font=("Arial", 16, "bold"),
            bg="#ffc0cb",
            fg="black",
        ).pack(pady=15)

        button_frame = tk.Frame(self.master, bg="#ffc0cb")
        button_frame.pack(pady=10)

        common_button_options = {
            "font": ("Arial", 12),
            "width": 20,
            "bg": "white",
            "fg": "black",
            "bd": 2,
            "relief": "raised",
            "highlightbackground": "#ffc0cb",
            "highlightcolor": "#ffc0cb",
            "highlightthickness": 1,
            "pady": 5,
        }

        # Nút chọn chế độ (dùng Radiobutton hoặc Button để thay đổi trạng thái)
        self.btn_ai = tk.Button(
            button_frame,
            text="Đấu với máy (AI)",
            **common_button_options,
            command=self.select_mode_ai,
        )
        self.btn_ai.pack(pady=5)

        self.btn_friend = tk.Button(
            button_frame,
            text="Đấu với bạn (Offline)",
            **common_button_options,
            command=self.select_mode_friend,
        )
        self.btn_friend.pack(pady=5)

        self.btn_online = tk.Button(
            button_frame,
            text="Chơi Online",
            **common_button_options,
            command=self.select_mode_online,
        )
        self.btn_online.pack(pady=5)

        # Label hiển thị lựa chọn hiện tại
        self.status_label = tk.Label(
            self.master,
            text="Vui lòng chọn chế độ chơi",
            font=("Arial", 11),
            bg="#ffc0cb",
            fg="#333",
        )
        self.status_label.pack(pady=10)

        # --- LOẠI BỎ NÚT XẾP HẠNG VÀ LỊCH SỬ ---
        # tk.Button(button_frame, text="Xếp hạng", ...).pack(pady=5)
        # tk.Button(button_frame, text="Lịch sử", ...).pack(pady=5)

        # Footer
        footer_frame = tk.Frame(self.master, bg="#ffc0cb")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

        self.start_button = tk.Button(
            footer_frame,
            text="Bắt đầu game",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            bd=2,
            relief="raised",
            height=2,
            state=tk.DISABLED,
            command=self.start_game,
        )
        self.start_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        logout_button = tk.Button(
            footer_frame,
            text="Đăng xuất",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            bd=2,
            relief="raised",
            height=2,
            width=15,
            command=self.logout,
        )
        logout_button.pack(side=tk.RIGHT, padx=10)

    def update_status(self):
        """Cập nhật label trạng thái và trạng thái nút Start"""
        status_text = "Chưa chọn chế độ"
        start_enabled = False

        if self.selected_mode == "ai":
            diff_text = f"Độ khó: {self.selected_difficulty.capitalize() if self.selected_difficulty else 'Chưa chọn'}"
            size_text = f"Kích thước: {str(self.selected_size)+'x'+str(self.selected_size) if self.selected_size else 'Chưa chọn'}"
            status_text = f"Chế độ: Đấu với AI | {diff_text} | {size_text}"
            if self.selected_difficulty and self.selected_size:
                start_enabled = True
        elif self.selected_mode == "friend":
            size_text = f"Kích thước: {str(self.selected_size)+'x'+str(self.selected_size) if self.selected_size else 'Chưa chọn'}"
            status_text = f"Chế độ: Đấu với Bạn | {size_text}"
            if self.selected_size:
                start_enabled = True
        elif self.selected_mode == "online":
            size_text = f"Kích thước: {str(self.selected_size)+'x'+str(self.selected_size) if self.selected_size else 'Chưa chọn'}"
            status_text = f"Chế độ: Chơi Online | {size_text}"
            # Online cần thêm logic kiểm tra kết nối server, nhưng tạm thời chỉ cần size
            if self.selected_size:
                start_enabled = True  # Sẽ xử lý kết nối khi nhấn Start

        self.status_label.config(text=status_text)
        self.start_button.config(state=tk.NORMAL if start_enabled else tk.DISABLED)

        # Đổi màu nút được chọn (đơn giản)
        self.btn_ai.config(
            relief=tk.SUNKEN if self.selected_mode == "ai" else tk.RAISED
        )
        self.btn_friend.config(
            relief=tk.SUNKEN if self.selected_mode == "friend" else tk.RAISED
        )
        self.btn_online.config(
            relief=tk.SUNKEN if self.selected_mode == "online" else tk.RAISED
        )

    def select_mode_ai(self):
        self.selected_mode = "ai"
        # Hỏi độ khó và kích thước
        difficulty = choose_difficulty(self.master)
        if difficulty:
            self.selected_difficulty = difficulty
            size = choose_board_size(self.master)
            if size:
                self.selected_size = size
            else:  # Nếu đóng cửa sổ chọn size
                self.selected_mode = None  # Reset lựa chọn
                self.selected_difficulty = None
        else:  # Nếu đóng cửa sổ chọn difficulty
            self.selected_mode = None  # Reset lựa chọn
        self.update_status()

    def select_mode_friend(self):
        self.selected_mode = "friend"
        self.selected_difficulty = None  # Không cần độ khó
        # Hỏi kích thước
        size = choose_board_size(self.master)
        if size:
            self.selected_size = size
        else:
            self.selected_mode = None
        self.update_status()

    def select_mode_online(self):
        self.selected_mode = "online"
        self.selected_difficulty = None  # Không cần độ khó
        # Hỏi kích thước
        size = choose_board_size(self.master)
        if size:
            self.selected_size = size
        else:
            self.selected_mode = None  # Reset lựa chọn
        # Cần thêm bước kết nối server ở đây hoặc lúc nhấn Start
        self.update_status()

    def start_game(self):
        """Khởi tạo và bắt đầu game dựa trên lựa chọn"""
        print(
            f"Bắt đầu game: Mode={self.selected_mode}, Size={self.selected_size}, Difficulty={self.selected_difficulty}"
        )

        # Tạo instance game tương ứng
        game_instance = None
        if self.selected_mode == "ai":
            # Truyền master=None vì OfflineGame không dùng master
            game_instance = OfflineGame(
                master=None,
                board_size=self.selected_size,
                opponent="bot",
                difficulty=self.selected_difficulty,
            )
        elif self.selected_mode == "friend":
            # Truyền master=None
            game_instance = OfflineGame(
                master=None, board_size=self.selected_size, opponent="friend"
            )
        elif self.selected_mode == "online":
            # Truyền master=None, OnlineGame cần NetworkManager hoạt động
            # Việc kết nối sẽ thực hiện bên trong OnlineGame hoặc màn hình game
            game_instance = OnlineGame(master=None, board_size=self.selected_size)
            # Cần truyền username vào OnlineGame để nó biết tên người chơi
            game_instance.player_name = self.username

        if game_instance:
            # Đóng cửa sổ menu
            self.master.destroy()
            # Mở màn hình game (manhinh3) và truyền game_instance vào
            # Giả sử có GameScreen trong manhinh3_refactored.py
            try:
                # Chạy màn hình game trong tiến trình mới để tránh lỗi Tkinter lồng nhau
                # Lưu cài đặt vào file tạm để manhinh3 đọc
                # Đây là cách đơn giản, cách tốt hơn là dùng IPC hoặc cấu trúc class tốt hơn
                settings_path = "temp_game_settings.dat"  # Dùng file tạm khác
                import pickle

                game_data = {
                    "mode": self.selected_mode,
                    "size": self.selected_size,
                    "difficulty": self.selected_difficulty,
                    "username": self.username,
                }
                with open(settings_path, "wb") as f:
                    pickle.dump(game_data, f)

                # Gọi màn hình game bằng subprocess
                subprocess.Popen([sys.executable, "manhinh3_refactored.py"])

            except ImportError:
                messagebox.showerror(
                    "Lỗi",
                    "Không tìm thấy file màn hình game (manhinh3_refactored.py)",
                    parent=self.master,
                )
            except Exception as e:
                messagebox.showerror(
                    "Lỗi",
                    f"Không thể khởi động màn hình game:\n{e}",
                    parent=self.master,
                )

        else:
            messagebox.showerror(
                "Lỗi", "Không thể khởi tạo game instance.", parent=self.master
            )

    def logout(self):
        """Quay lại màn hình đăng nhập"""
        if messagebox.askyesno(
            "Đăng xuất", "Bạn có muốn đăng xuất?", parent=self.master
        ):
            self.master.destroy()
            # Chạy lại dangnhap.py
            subprocess.Popen(
                [sys.executable, "dangnhap.py"]
            )  # Dùng sys.executable cho chắc chắn


def main(username=None):
    """Hàm chính để khởi chạy màn hình menu"""
    root = tk.Tk()
    app = MainMenu(root, username)
    root.mainloop()


if __name__ == "__main__":
    # Chạy thử nghiệm với tên người dùng giả
    main(username="TestUser")

# --- END OF FILE manhinh2.py ---
