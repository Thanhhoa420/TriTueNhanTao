class Board:
    """
    Lớp quản lý bàn cờ caro (console)
    """

    def __init__(self, master, size, cell_size=60):
        """
        Khởi tạo bàn cờ

        Args:
            master: Không sử dụng trong console, giữ để tương thích
            size: Kích thước bàn cờ (size x size)
            cell_size: Không sử dụng trong console, giữ để tương thích
        """
        self.master = master
        self.size = size
        self.cell_size = cell_size

        # Khởi tạo ma trận bàn cờ (0: trống, 1: X, 2: O)
        self.grid = [[0 for _ in range(size)] for _ in range(size)]

        # Biến lưu trữ callback khi người chơi click vào ô (không dùng trong console)
        self.click_callback = None

    def display(self):
        """Hiển thị bàn cờ ra console"""
        print("   " + " ".join(str(i) for i in range(self.size)))
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if self.grid[i][j] == 1:
                    row.append("X")
                elif self.grid[i][j] == 2:
                    row.append("O")
                else:
                    row.append(".")
            print(f"{i:2} " + " ".join(row))

    def set_click_callback(self, callback):
        """Không sử dụng trong console, giữ để tương thích"""
        self.click_callback = callback

    def place_marker(self, row, col, player):
        """
        Đặt quân cờ lên bàn cờ

        Args:
            row: Vị trí hàng
            col: Vị trí cột
            player: Người chơi (1: X, 2: O)

        Returns:
            bool: True nếu đặt thành công, False nếu vị trí đã có quân
        """
        if self.grid[row][col] != 0:
            return False
        self.grid[row][col] = player
        return True

    def reset(self):
        """Làm mới bàn cờ"""
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

    def is_full(self):
        """Kiểm tra xem bàn cờ đã đầy chưa"""
        for row in self.grid:
            if 0 in row:
                return False
        return True

    def get_grid(self):
        """Lấy ma trận bàn cờ hiện tại"""
        return [row[:] for row in self.grid]
