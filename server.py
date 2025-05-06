# --- START OF FILE server.py ---
import socket
import threading
import json
import time  # Thêm time
import pygame 
import os
class GameServer:
    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Server đang chạy trên {self.host}:{self.port}")

        # *** SỬA ĐỔI QUAN TRỌNG: Dùng dictionary cho hàng đợi ***
        self.waiting_clients = {}  # {board_size: (client, player_name), ...}
        self.rooms = (
            {}
        )  # room_id: {"clients": {client1: name1, client2: name2}, "board_size": size}
        self.client_to_room = {}  # client: room_id (Để dễ tìm phòng khi client thoát)

        self.lock = threading.Lock()

    def start(self):
        while True:
            try:
                client, address = self.server.accept()
                print(f"Kết nối từ {address}")
                thread = threading.Thread(
                    target=self.handle_client, args=(client, address), daemon=True
                )
                thread.start()
            except Exception as e:
                print(f"Lỗi khi chấp nhận kết nối: {e}")

    def handle_client(self, client, address):
        room_id = None
        player_name = f"Guest_{address[1]}"
        buffer = b""  # Buffer để xử lý message đáng tin cậy hơn

        try:
            while True:
                try:
                    chunk = client.recv(4096)
                    print(
                        f"SERVER DEBUG: Nhận được chunk từ {player_name} ({address}): {chunk}"
                    )
                    if not chunk:
                        print(f"Client {address} ({player_name}) đã ngắt kết nối.")
                        break

                    buffer += chunk
                    # *** SỬA ĐỔI QUAN TRỌNG: Xử lý buffer bằng delimiter '\n' ***
                    while b"\n" in buffer:
                        message_data, buffer = buffer.split(b"\n", 1)
                        message_data = message_data.strip()
                        if not message_data:
                            continue

                        try:
                            message = json.loads(message_data.decode("utf-8"))
                            print(f"Server nhận từ {player_name}: {message}")  # Debug

                            msg_type = message.get("type")

                            if msg_type == "find_match":
                                player_name = message.get("player_name", player_name)
                                board_size = message.get("board_size")
                                if board_size is None:
                                    continue  # Bỏ qua nếu thiếu size

                                # Xóa client khỏi phòng/hàng đợi cũ trước khi tìm mới
                                self.remove_client(client)  # Gọi hàm dọn dẹp chung

                                # Tìm hoặc chờ theo size
                                room_id = self.find_or_wait(
                                    client, player_name, board_size
                                )
                                # Lưu room_id vào self.client_to_room nếu ghép cặp thành công
                                if room_id:
                                    with self.lock:  # Cần lock khi sửa client_to_room
                                        self.client_to_room[client] = room_id
                                else:
                                    # Nếu phải chờ, đảm bảo client không còn trong client_to_room
                                    with self.lock:
                                        if client in self.client_to_room:
                                            del self.client_to_room[client]

                            elif msg_type == "move":
                                current_room_id = self.client_to_room.get(
                                    client
                                )  # Lấy room_id từ dict
                                if current_room_id:
                                    self.handle_move(client, current_room_id, message)
                                else:
                                    print(
                                        f"Cảnh báo: {player_name} gửi 'move' khi chưa trong phòng."
                                    )
                                    self.send_to_client(
                                        client,
                                        {"type": "error", "message": "Not in a room"},
                                    )

                        except json.JSONDecodeError:
                            print(
                                f"Lỗi decode JSON từ {player_name}: '{message_data.decode('utf-8', errors='ignore')}'"
                            )
                            # Có thể đóng kết nối nếu lỗi liên tục
                            # buffer = b"" # Xóa buffer lỗi
                            # break # Thoát vòng lặp trong
                        except Exception as e:
                            print(f"Lỗi xử lý message từ {player_name}: {e}")
                            # break # Thoát vòng lặp trong

                except ConnectionResetError:
                    print(f"Client {address} ({player_name}) reset kết nối.")
                    break
                except socket.timeout:
                    # Nên đặt timeout nếu cần xử lý client treo
                    print(f"Socket timeout với {player_name}. Tiếp tục chờ...")
                    continue
                except Exception as e:
                    print(f"Lỗi recv từ {player_name}: {e}")
                    break
        finally:
            print(f"Dọn dẹp cho client {address} ({player_name}).")
            self.remove_client(client)  # Gọi hàm dọn dẹp chung
            try:
                client.close()
            except:
                pass

    # *** SỬA ĐỔI QUAN TRỌNG: Gửi với delimiter '\n' ***
    def send_to_client(self, client, data_dict):
        try:
            message = json.dumps(data_dict).encode("utf-8")
            client.sendall(message + b"\n")  # Thêm '\n'
            return True
        except (socket.error, BrokenPipeError) as e:
            print(f"Lỗi gửi tới client: {e}.")
            # Không tự động xóa client ở đây, handle_client sẽ xử lý
            return False
        except Exception as e:
            print(f"Lỗi không xác định khi gửi: {e}")
            return False

    # *** SỬA ĐỔI QUAN TRỌNG: Dùng self.waiting_clients dictionary ***
    # Trong file server.py
    def find_or_wait(self, client, player_name, board_size):
        """Tìm đối thủ cùng kích thước bàn cờ hoặc đưa vào hàng đợi"""
        room_created_id = None
        with self.lock:
            # print(f"DEBUG: find_or_wait called for {player_name}. board_size={board_size}, type={type(board_size)}")
            # print(f"DEBUG: Before check, waiting_clients keys = {list(self.waiting_clients.keys())}")

            if board_size in self.waiting_clients:
                # print(f"DEBUG: Found key {board_size} in waiting_clients.")
                opponent_client, opponent_name = self.waiting_clients.pop(board_size)

                if opponent_client == client:
                    print(
                        f"Cảnh báo: Client {player_name} cố gắng tự ghép cặp. Đưa lại vào hàng đợi."
                    )
                    self.waiting_clients[board_size] = (client, player_name)
                    self.send_to_client(client, {"type": "waiting"})
                    return None

                print(
                    f"Ghép cặp {player_name} (size {board_size}) với {opponent_name} (size {board_size})."
                )

                room_id = id(client) ^ id(opponent_client)
                self.rooms[room_id] = {
                    "clients": {client: player_name, opponent_client: opponent_name},
                    "board_size": board_size,
                }

                # *** SỬA ĐỔI QUAN TRỌNG: Cập nhật client_to_room cho CẢ HAI client Ở ĐÂY ***
                self.client_to_room[client] = room_id
                self.client_to_room[opponent_client] = room_id
                # ************************************************************************

                self.send_to_client(
                    client,
                    {
                        "type": "match_found",
                        "opponent_name": opponent_name,
                        "marker": 1,
                    },
                )
                self.send_to_client(
                    opponent_client,
                    {"type": "match_found", "opponent_name": player_name, "marker": 2},
                )
                room_created_id = room_id
            else:
                # print(f"DEBUG: Key {board_size} NOT found in waiting_clients. Adding client to wait.")
                print(f"{player_name} (size {board_size}) bắt đầu chờ.")
                is_already_waiting_this_size = False
                if (
                    board_size in self.waiting_clients
                    and self.waiting_clients[board_size][0] == client
                ):
                    is_already_waiting_this_size = True

                if not is_already_waiting_this_size:
                    self.waiting_clients[board_size] = (client, player_name)

                self.send_to_client(client, {"type": "waiting"})
                room_created_id = None

        return room_created_id

    def handle_move(self, sender_client, room_id, message):
        # Hàm này gần như giữ nguyên, chỉ cần đảm bảo lấy đúng opponent từ dict
        if room_id not in self.rooms:
            print(f"Lỗi: handle_move với room_id không hợp lệ: {room_id}")
            return

        row, col = message["row"], message["col"]
        opponent_client = None
        sender_name = "Unknown"

        with self.lock:
            if room_id not in self.rooms:
                return
            room_data = self.rooms[room_id]
            sender_name = room_data["clients"].get(sender_client, "Unknown")
            # Tìm đối thủ trong dictionary clients
            for c in room_data["clients"]:
                if c != sender_client:
                    opponent_client = c
                    break

        if opponent_client:
            opponent_name = room_data["clients"].get(
                opponent_client, "Unknown"
            )  # Lấy tên opponent
            move_data = {"type": "move", "row": row, "col": col}
            print(f"Chuyển tiếp move từ {sender_name} tới {opponent_name}")
            if not self.send_to_client(opponent_client, move_data):
                print(f"Lỗi gửi move tới {opponent_name}. Xóa {opponent_name}.")
                self.remove_client(opponent_client)  # Gọi hàm dọn dẹp chung
        else:
            print(f"Không tìm thấy đối thủ để gửi move trong phòng {room_id}")

    # *** SỬA ĐỔI QUAN TRỌNG: Hàm dọn dẹp chung ***
    def remove_client(self, client):
        """Xóa client khỏi hàng đợi và/hoặc phòng chơi hiện tại."""
        with self.lock:
            removed_from_waiting = False
            # Xóa khỏi hàng đợi (bất kỳ size nào)
            for size, waiting_data in list(self.waiting_clients.items()):
                if waiting_data[0] == client:
                    del self.waiting_clients[size]
                    print(f"Client {waiting_data[1]} bị xóa khỏi hàng đợi size {size}.")
                    removed_from_waiting = True
                    break  # Client chỉ chờ ở 1 size

            # Xóa khỏi phòng chơi (nếu có)
            room_id = self.client_to_room.pop(
                client, None
            )  # Lấy và xóa khỏi dict tra cứu
            if room_id is not None and room_id in self.rooms:
                room_data = self.rooms[room_id]
                client_name = room_data["clients"].pop(
                    client, "Unknown"
                )  # Xóa khỏi dict phòng
                print(f"Xóa {client_name} khỏi phòng {room_id}.")

                # Tìm và thông báo cho đối thủ còn lại
                if room_data["clients"]:  # Nếu còn người chơi khác
                    opponent_client = list(room_data["clients"].keys())[0]
                    opponent_name = room_data["clients"][opponent_client]

                    print(f"Thông báo cho {opponent_name} rằng {client_name} đã thoát.")
                    self.send_to_client(
                        opponent_client, {"type": "opponent_disconnected"}
                    )

                    # Xóa đối thủ này khỏi client_to_room vì phòng sẽ bị xóa
                    if opponent_client in self.client_to_room:
                        del self.client_to_room[opponent_client]
                # else: # Không còn ai khác

                # Xóa phòng
                print(f"Xóa phòng {room_id}.")
                del self.rooms[room_id]
            elif room_id is not None:
                print(
                    f"Cảnh báo: room_id {room_id} được tìm thấy cho client nhưng không có trong self.rooms."
                )


if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Đang tắt server...")
    finally:
        print("Server đã dừng.")
# --- END OF FILE server.py ---
