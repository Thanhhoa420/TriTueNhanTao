class GameLogic:
    """
    Lớp xử lý luật chơi cơ bản và kiểm tra thắng/thua của trò chơi cờ caro.
    Phần logic tìm nước đi cho bot đã được chuyển sang file ai.py.
    """

    def __init__(self, board_size):
        """
        Khởi tạo logic trò chơi

        Args:
            board_size: Kích thước bàn cờ (board_size x board_size)
        """
        self.board_size = board_size

        # Số quân liên tiếp cần để thắng (thay đổi theo kích thước bàn cờ)
        if board_size == 3:
            self.win_condition = 3  # 3x3 cần 3 quân liên tiếp
        elif board_size == 5:
            self.win_condition = 4  # 5x5 cần 4 quân liên tiếp
        else:  # Giả sử mặc định cho 7x7 hoặc lớn hơn
            self.win_condition = 5

    def check_win(self, grid, last_row, last_col, player):
        """
        Kiểm tra xem người chơi có thắng sau nước đi cuối cùng không

        Args:
            grid: Ma trận bàn cờ (dạng list of lists, 0: trống, 1: X, 2: O)
            last_row: Hàng của nước đi cuối cùng
            last_col: Cột của nước đi cuối cùng
            player: Người chơi (1 cho X, 2 cho O)

        Returns:
            bool: True nếu người chơi thắng, False nếu chưa thắng
        """
        # Kiểm tra chiến thắng theo 4 hướng:
        return (
            self._check_direction(grid, last_row, last_col, 0, 1, player)  # Ngang
            or self._check_direction(grid, last_row, last_col, 1, 0, player)  # Dọc
            or self._check_direction(
                grid, last_row, last_col, 1, 1, player
            )  # Chéo chính
            or self._check_direction(
                grid, last_row, last_col, 1, -1, player
            )  # Chéo phụ
        )

    def _check_direction(self, grid, row, col, d_row, d_col, player):
        """
        Kiểm tra chiến thắng theo một hướng cụ thể

        Args:
            grid: Ma trận bàn cờ
            row: Hàng của nước đi
            col: Cột của nước đi
            d_row: Hướng kiểm tra dòng (-1, 0, 1)
            d_col: Hướng kiểm tra cột (-1, 0, 1)
            player: Người chơi (1 hoặc 2)

        Returns:
            bool: True nếu người chơi thắng theo hướng đó, False nếu không
        """
        count = 1  # Bắt đầu từ 1 (quân vừa đặt xuống)

        # Kiểm tra theo hướng (d_row, d_col)
        r, c = row + d_row, col + d_col
        while (
            0 <= r < self.board_size
            and 0 <= c < self.board_size
            and grid[r][c] == player  # Kiểm tra quân của người chơi hiện tại
        ):
            count += 1
            r += d_row
            c += d_col

        # Kiểm tra theo hướng ngược lại (-d_row, -d_col)
        r, c = row - d_row, col - d_col
        while (
            0 <= r < self.board_size
            and 0 <= c < self.board_size
            and grid[r][c] == player  # Kiểm tra quân của người chơi hiện tại
        ):
            count += 1
            r -= d_row
            c -= d_col

        # Nếu số quân liên tiếp >= điều kiện thắng
        return count >= self.win_condition
