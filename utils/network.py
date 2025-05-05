# --- START OF FILE utils/network.py ---

import socket
import threading
import json
import time  # Thêm time để sleep nếu cần


class NetworkManager:
    """
    Lớp quản lý kết nối mạng cho chế độ chơi online
    """

    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        self.receive_thread = None  # Thêm để quản lý thread
        self.lock = threading.Lock()  # Thêm lock để bảo vệ socket access

        # Callback khi nhận được dữ liệu
        self.on_data_received = None
        # Callback khi mất kết nối
        self.on_disconnected = None

    def connect(self):
        if self.connected:
            return True  # Đã kết nối
        try:
            print(f"Đang kết nối tới {self.host}:{self.port}...")
            with self.lock:  # Lock khi tạo socket mới
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.settimeout(5)  # Đặt timeout cho kết nối
                self.client.connect((self.host, self.port))
                self.client.settimeout(None)  # Bỏ timeout sau khi kết nối
                self.connected = True

            print("Kết nối thành công!")
            # Bắt đầu thread nhận dữ liệu
            self.receive_thread = threading.Thread(
                target=self._receive_data, daemon=True
            )
            self.receive_thread.start()
            return True

        except socket.timeout:
            print("Lỗi kết nối: Timeout.")
            self.client = None
            self.connected = False
            return False
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            self.client = None  # Đảm bảo client là None nếu lỗi
            self.connected = False
            return False

    def disconnect(self):
        print("Yêu cầu ngắt kết nối...")
        needs_callback = False
        with self.lock:
            if self.connected:
                needs_callback = True  # Chỉ gọi callback nếu đang connected
                self.connected = False  # Ngừng vòng lặp nhận trước
            if self.client:
                try:
                    # Shutdown trước khi close để gửi tín hiệu kết thúc
                    self.client.shutdown(socket.SHUT_RDWR)
                except (socket.error, OSError):
                    pass  # Bỏ qua lỗi nếu socket đã đóng hoặc lỗi
                try:
                    self.client.close()
                    print("Socket đã đóng.")
                except (socket.error, OSError) as e:
                    print(f"Lỗi khi đóng socket: {e}")
                finally:
                    self.client = None

        # Chờ thread nhận kết thúc (sau khi giải phóng lock)
        if self.receive_thread and self.receive_thread.is_alive():
            print("Đang chờ thread nhận kết thúc...")
            self.receive_thread.join(timeout=2.0)  # Chờ tối đa 2 giây
            if self.receive_thread.is_alive():
                print("Cảnh báo: Thread nhận không kết thúc kịp thời.")
        self.receive_thread = None

        # Gọi callback sau khi đã dọn dẹp xong
        # if needs_callback and self.on_disconnected:
        #     print("Gọi on_disconnected callback.")
        #     try: # Gọi callback an toàn
        #          self.on_disconnected()
        #     except Exception as e:
        #          print(f"Lỗi trong on_disconnected callback: {e}")

    # --- START OF FILE utils/network.py ---
    # ... (các phần khác) ...
    def send_data(self, data):
        # DEBUG PRINT A: Xác nhận hàm send_data được gọi
        print(f"CLIENT NETWORK DEBUG: send_data được gọi với data: {data}")
        with self.lock:
            if not self.connected or not self.client:
                print("CLIENT NETWORK DEBUG: Lỗi gửi: Chưa kết nối!")
                return False
            try:
                # DEBUG PRINT B: Trước khi json.dumps
                print("CLIENT NETWORK DEBUG: Chuẩn bị json.dumps...")
                message = json.dumps(data).encode("utf-8")
                # DEBUG PRINT C: Trước khi sendall
                print(f"CLIENT NETWORK DEBUG: Chuẩn bị sendall: {message + b'\\n'}")
                self.client.sendall(message + b"\n")
                # DEBUG PRINT D: Sau khi sendall thành công
                print("CLIENT NETWORK DEBUG: sendall hoàn thành.")
                return True
            except (socket.error, BrokenPipeError) as e:
                # DEBUG PRINT E: Nếu có lỗi socket
                print(f"CLIENT NETWORK DEBUG: Lỗi socket trong send_data: {e}")
                self._handle_disconnection_internal()
                return False
            except Exception as e:
                # DEBUG PRINT F: Nếu có lỗi khác (ví dụ json.dumps)
                print(f"CLIENT NETWORK DEBUG: Lỗi khác trong send_data: {e}")
                return False

    # ... (các phần khác) ...
    # --- END OF FILE utils/network.py ---
    # --- START OF FILE utils/network.py ---
    # ... (các phần khác) ...

    def _receive_data(self):
        """Thread nhận dữ liệu từ server"""
        buffer = b""
        is_connected = True  # Biến cục bộ cho vòng lặp
        print("CLIENT NETWORK DEBUG: Thread _receive_data bắt đầu.")

        while is_connected:
            chunk = b""
            acquired_lock = False  # Không thực sự cần thiết nữa khi dùng 'with'

            try:  # Khối try bao quanh toàn bộ logic trong vòng lặp
                # --- Phần kiểm tra trạng thái trong Lock ---
                # print("CLIENT NETWORK DEBUG: _receive_data chuẩn bị chiếm lock...")
                with self.lock:
                    # print("CLIENT NETWORK DEBUG: _receive_data đã chiếm lock.")
                    if not self.connected or not self.client:
                        # print("CLIENT NETWORK DEBUG: _receive_data thấy disconnected trong lock, thoát...")
                        is_connected = False
                        break  # Thoát vòng lặp while
                # --- Hết phần kiểm tra trong Lock ---

                # Nếu is_connected vẫn là True sau khi kiểm tra lock
                if is_connected:
                    # --- Thực hiện recv() ngoài Lock ---
                    try:
                        # print("CLIENT NETWORK DEBUG: _receive_data chuẩn bị recv() (ngoài lock)...")
                        # Đặt timeout cho recv nếu socket chưa có timeout toàn cục
                        # self.client.settimeout(1.0) # Ví dụ 1 giây timeout
                        chunk = self.client.recv(4096)
                        # print(f"CLIENT NETWORK DEBUG: _receive_data nhận được chunk (ngoài lock): {len(chunk)} bytes")
                    except socket.timeout:
                        # print("CLIENT NETWORK DEBUG: _receive_data timeout recv() (ngoài lock).")
                        continue  # Quay lại đầu vòng lặp while để kiểm tra connected
                    except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                        print(
                            f"CLIENT NETWORK DEBUG: Lỗi socket khi recv() (ngoài lock): {e}"
                        )
                        is_connected = False  # Đánh dấu để thoát while
                        self._handle_disconnection_internal()  # Xử lý disconnect
                        # Không cần break ở đây vì is_connected đã là False
                    # finally:
                    # Bỏ timeout nếu đã đặt tạm thời
                    # if self.client: self.client.settimeout(None)

                # --- Xử lý chunk nhận được ---
                if (
                    not chunk and is_connected
                ):  # Nếu chunk rỗng và chưa bị đánh dấu disconnect
                    print("CLIENT NETWORK DEBUG: Server đóng kết nối (chunk rỗng).")
                    is_connected = False
                    self._handle_disconnection_internal()
                    # Không cần break vì is_connected đã False

                if chunk:
                    buffer += chunk
                    # Xử lý buffer để tách các message JSON dựa vào '\n'
                    while b"\n" in buffer:
                        message_data, buffer = buffer.split(b"\n", 1)
                        message_data = message_data.strip()
                        if not message_data:
                            continue

                        try:
                            message = json.loads(message_data.decode("utf-8"))
                            # print(f"DEBUG: Client nhận: {message}")
                            if self.on_data_received:
                                try:
                                    self.on_data_received(message)
                                except Exception as e:
                                    print(f"Lỗi trong on_data_received callback: {e}")
                        except json.JSONDecodeError:
                            print(
                                f"Lỗi decode JSON: '{message_data.decode('utf-8', errors='ignore')}'"
                            )
                        except Exception as e:
                            print(f"Lỗi xử lý message nhận được: {e}")

            except Exception as e:  # Bắt lỗi chung không mong muốn cho toàn bộ vòng lặp
                with self.lock:  # Kiểm tra trạng thái an toàn
                    if self.connected:
                        print(
                            f"CLIENT NETWORK DEBUG: Lỗi không xác định trong _receive_data loop: {e}"
                        )
                is_connected = False  # Dừng vòng lặp nếu có lỗi lạ
                self._handle_disconnection_internal()
                # Không cần break vì is_connected đã False

            # Thêm một khoảng nghỉ nhỏ để tránh CPU load cao nếu có lỗi liên tục hoặc không có dữ liệu
            if is_connected and not chunk and not buffer:  # Nếu không có gì xảy ra
                time.sleep(0.05)

        # Kết thúc vòng lặp while
        print("CLIENT NETWORK DEBUG: Thread _receive_data kết thúc.")

    # ... (phần còn lại của file network.py) ...

    def _handle_disconnection_internal(self):
        """Hàm nội bộ để xử lý mất kết nối và gọi callback một cách an toàn."""
        needs_callback = False
        with self.lock:
            if self.connected:  # Chỉ xử lý nếu đang là connected
                self.connected = False
                needs_callback = True
                if self.client:
                    try:
                        self.client.close()  # Đóng socket ngay lập tức
                    except:
                        pass
                    self.client = None
                print("Đã xử lý mất kết nối nội bộ.")

        # Gọi callback bên ngoài lock
        if needs_callback and self.on_disconnected:
            print("Gọi on_disconnected callback từ xử lý nội bộ.")
            try:
                self.on_disconnected()
            except Exception as e:
                print(f"Lỗi trong on_disconnected callback: {e}")

    def find_match(self, player_name, board_size):
        data = {
            "type": "find_match",
            "player_name": player_name,
            "board_size": board_size,
        }
        return self.send_data(data)

    def send_move(self, row, col):
        data = {"type": "move", "row": row, "col": col}
        return self.send_data(data)


# --- END OF FILE utils/network.py ---
