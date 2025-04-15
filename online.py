class OnlineGame:
    def login(self):
        print("\n===== LOGIN =====")
        username = input("Enter username: ")
        password = input("Enter password: ")  # Thực tế cần mã hóa/ẩn
        # Giả lập đăng nhập thành công
        print(f"Welcome, {username}!\n")
        return True

    def play_online(self):
        print("Chế độ chơi online đang được phát triển...")
