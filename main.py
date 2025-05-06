import sys
import os
from game.board import Board
from modes.offline import OfflineGame
from modes.online import OnlineGame
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

def main():
    print("GAME CỜ CARO (Console)")
    print("1. Chơi Offline với bạn")
    print("2. Chơi Offline với máy (AI)")
    print("3. Chơi Online")
    while True:
        try:
            mode_choice = int(input("Chọn chế độ (1-3): "))
            if mode_choice in [1, 2, 3]:
                break
        except ValueError:
            pass
        print("Vui lòng chọn 1, 2 hoặc 3")

    print("Chọn kích thước bàn cờ:")
    print("1. 3x3")
    print("2. 5x5")
    print("3. 7x7")
    while True:
        try:
            size_choice = int(input("Chọn kích thước (1-3): "))
            if size_choice in [1, 2, 3]:
                break
        except ValueError:
            pass
        print("Vui lòng chọn 1, 2 hoặc 3")
    size = {1: 3, 2: 5, 3: 7}[size_choice]

    if mode_choice == 1:
        # Chơi Offline với bạn
        game = OfflineGame(None, size, opponent="friend")
        game.start()
    elif mode_choice == 2:
        # Chơi Offline với máy (AI)
        # --- THÊM LỰA CHỌN ĐỘ KHÓ ---
        print("Chọn độ khó AI:")
        print("1. Dễ (Easy)")
        print("2. Trung bình (Medium)")
        print("3. Khó (Hard - DQN)")
        while True:
            try:
                difficulty_choice = int(input("Chọn độ khó (1-3): "))
                if difficulty_choice in [1, 2, 3]:
                    break
            except ValueError:
                pass
            print("Vui lòng chọn 1, 2 hoặc 3")
        difficulty = {1: "easy", 2: "medium", 3: "hard"}[difficulty_choice]
        # Truyền difficulty vào OfflineGame
        game = OfflineGame(None, size, opponent="bot", difficulty=difficulty)
        # --- KẾT THÚC THÊM LỰA CHỌN ĐỘ KHÓ ---
        game.start()
    elif mode_choice == 3:
        game = OnlineGame(None, size)  # Giả sử constructor chỉ cần size
        game.start()

    else:
        print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
