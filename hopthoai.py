# --- START OF FILE hopthoai.py ---

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import os
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
        pygame.mixer.music.set_volume(0.3)  # Âm lượng 30%
        pygame.mixer.music.play(-1)  # Lặp vô hạn
        music_on = True
    except Exception as e:
        print(f"Lỗi khi phát nhạc: {e}")
play_background_music()

# Biến tạm để lưu lựa chọn (sẽ bị loại bỏ dần nếu có thể)
# Tốt hơn là truyền dữ liệu qua các hàm
temp_selected_difficulty = None
temp_selected_board_size = None


def toss_coin(parent):
    """Tung đồng xu để quyết định ai đi trước"""
    first_player_num = random.choice([1, 2])  # 1 hoặc 2
    first_player_name = f"Người chơi {first_player_num}"
    messagebox.showinfo(
        "Tung đồng xu", f"{first_player_name} sẽ đi trước!", parent=parent
    )
    return first_player_num  # Trả về 1 hoặc 2


# --- LOẠI BỎ CÁC HÀM LIÊN QUAN ĐẾN HISTORY/LEADERBOARD ---
# def save_to_file...
# def load_from_file...
# def update_leaderboard...
# def save_match_history...
# def show_leaderboard...
# def show_history...
# def show_result... (Kết quả sẽ hiển thị trực tiếp trên màn hình game)


def choose_difficulty(parent):
    """
    Mở cửa sổ chọn độ khó AI và trả về lựa chọn.

    Args:
        parent: Cửa sổ cha để Toplevel hiển thị đúng cách.

    Returns:
        str: "easy", "medium", "hard" hoặc None nếu cửa sổ bị đóng.
    """
    result = {"difficulty": None}  # Dùng dictionary để truyền tham chiếu

    dialog = tk.Toplevel(parent)
    dialog.title("Chọn độ khó AI")
    dialog.geometry("300x250")
    dialog.configure(bg="lightblue")
    dialog.transient(parent)
    dialog.grab_set()

    tk.Label(dialog, text="Chọn độ khó:", font=("Arial", 14), bg="lightblue").pack(
        pady=15
    )

    def select_difficulty(diff_value):
        result["difficulty"] = diff_value
        dialog.destroy()

    tk.Button(
        dialog,
        text="Dễ (Easy)",
        font=("Arial", 12),
        width=15,
        command=lambda: select_difficulty("easy"),
    ).pack(pady=10)
    tk.Button(
        dialog,
        text="Trung bình (Medium)",
        font=("Arial", 12),
        width=15,
        command=lambda: select_difficulty("medium"),
    ).pack(pady=10)
    tk.Button(
        dialog,
        text="Khó (Hard - DQN)",
        font=("Arial", 12),
        width=15,
        command=lambda: select_difficulty("hard"),
    ).pack(pady=10)

    # Chờ cho đến khi dialog bị đóng
    parent.wait_window(dialog)

    return result["difficulty"]


def choose_board_size(parent):
    """
    Mở cửa sổ chọn kích thước bàn cờ và trả về lựa chọn.

    Args:
        parent: Cửa sổ cha.

    Returns:
        int: 3, 5, 7 hoặc None nếu cửa sổ bị đóng.
    """
    result = {"size": None}

    dialog = tk.Toplevel(parent)
    dialog.title("Chọn kích thước bàn cờ")
    dialog.geometry("300x250")
    dialog.configure(bg="lightgreen")
    dialog.transient(parent)
    dialog.grab_set()

    tk.Label(
        dialog, text="Chọn kích thước bàn cờ:", font=("Arial", 14), bg="lightgreen"
    ).pack(pady=15)

    def select_size(size_value):
        result["size"] = size_value
        dialog.destroy()

    tk.Button(
        dialog, text="3x3", font=("Arial", 12), width=10, command=lambda: select_size(3)
    ).pack(pady=10)
    tk.Button(
        dialog, text="5x5", font=("Arial", 12), width=10, command=lambda: select_size(5)
    ).pack(pady=10)
    tk.Button(
        dialog, text="7x7", font=("Arial", 12), width=10, command=lambda: select_size(7)
    ).pack(pady=10)

    parent.wait_window(dialog)

    return result["size"]


# --- LOẠI BỎ CÁC HÀM KHÔNG CẦN THIẾT KHÁC ---
# def choose_server_mode... (Sẽ tích hợp vào manhinh2)
# def get_selected_options... (Sẽ lấy trực tiếp từ hàm chọn)
# def get_first_player... (Hàm toss_coin trả về trực tiếp)

# --- END OF FILE hopthoai.py ---
