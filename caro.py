from offline import OfflineGame
from online import OnlineGame


def main():
    while True:
        print("\nChọn chế độ chơi:")
        print("1. Chơi offline")
        print("2. Chơi online")
        print("0. Thoát")
        choice = input("Lựa chọn của bạn: ")

        if choice == "1":
            while True:
                try:
                    size = int(input("Nhập kích thước bàn cờ (3 / 5 / 7): "))
                    if size in [3, 5, 7]:
                        break
                    else:
                        print("Kích thước không hợp lệ. Chỉ được nhập 3, 5 hoặc 7.")
                except ValueError:
                    print("Vui lòng nhập một số hợp lệ.")

            mode = input("Chơi với bạn (friend) hay với bot (bot)? ").strip().lower()
            if mode not in ["friend", "bot"]:
                print("Chế độ không hợp lệ. Mặc định sẽ chơi với bạn (friend).")
                mode = "friend"

            game = OfflineGame(size, mode)
            game.play()

        elif choice == "2":
            online_game = OnlineGame()
            if online_game.login():
                online_game.play_online()

        elif choice == "0":
            print("Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")


if __name__ == "__main__":
    main()
