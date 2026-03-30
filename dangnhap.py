# --- START OF FILE dangnhap.py ---

import tkinter as tk
from tkinter import messagebox, PhotoImage
from PIL import Image, ImageTk
from tkinter import ttk
import re
import os
import sys
import random

# Xác định đường dẫn script để tìm file ảnh
script_dir = os.path.dirname(__file__)

def play_background_music():
    # Tạm tắt nhạc nền để tránh lỗi tương thích pygame trên macOS.
    return
play_background_music()

def validate_input(text):
    return bool(re.match("^[a-zA-Z0-9]*$", text))

def start_next_screen(username=None):
    root.destroy()
    import manhinh2
    manhinh2.main(username)

def start_as_guest():
    if messagebox.askyesno(
        "Xác nhận",
        "Bạn sẽ chơi với tư cách khách.\nLịch sử và điểm số sẽ không được lưu lại.\nTiếp tục?",
    ):
        guest_name = "Khach_" + str(random.randint(1000, 9999))
        start_next_screen(username=guest_name)

accounts = {}

def login():
    def toggle_password(entry, btn):
        if entry.cget("show") == "*":
            entry.config(show="")
            btn.config(text="👁")
        else:
            entry.config(show="*")
            btn.config(text="🔒")

    def check_login():
        username = entry_username.get().strip()
        if username:
            messagebox.showinfo("Thành công", f"Chào mừng {username}!")
            login_window.destroy()
            start_next_screen(username=username)
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên đăng nhập.")

    login_window = tk.Toplevel(root)
    login_window.title("Đăng Nhập")
    login_window.geometry("500x400")
    login_window.configure(bg="#FFE4E1")
    login_window.transient(root)
    login_window.grab_set()

    vcmd = (login_window.register(validate_input), "%P")

    login_frame = tk.Frame(login_window, bg="#FFE4E1")
    login_frame.pack(expand=True, fill="both", padx=50, pady=50)

    tk.Label(
        login_frame, text="ĐĂNG NHẬP", font=("Helvetica", 24, "bold"), bg="#FFE4E1", fg="#FF1493"
    ).pack(pady=10)
    tk.Label(
        login_frame, text="Tên đăng nhập:", bg="#FFE4E1", font=("Helvetica", 14), fg="#FF1493"
    ).pack()
    entry_username = ttk.Entry(
        login_frame, font=("Helvetica", 14), validate="key", validatecommand=vcmd
    )
    entry_username.pack(pady=10, fill="x")

    tk.Label(
        login_frame, text="Mật khẩu:", bg="#FFE4E1", font=("Helvetica", 14), fg="#FF1493"
    ).pack()
    password_frame = tk.Frame(login_frame, bg="#FFE4E1")
    password_frame.pack(fill="x", pady=5)
    entry_password = ttk.Entry(
        password_frame,
        show="*",
        font=("Helvetica", 14),
        validate="key",
        validatecommand=vcmd,
    )
    entry_password.pack(side="left", expand=True, fill="x")
    btn_show = tk.Button(password_frame, text="🔒", bg="#FFE4E1", fg="#FF1493")
    btn_show.pack(side="right", padx=5)
    btn_show.config(command=lambda e=entry_password, b=btn_show: toggle_password(e, b))

    btn_login = ttk.Button(login_frame, text="ĐĂNG NHẬP", command=check_login)
    btn_login.pack(pady=20, ipadx=10, ipady=10)

def register():
    def save_account():
        username = entry_new_username.get().strip()
        password = entry_new_password.get().strip()
        confirm_password = entry_confirm_password.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Lỗi",
                "Tên đăng nhập và mật khẩu không được để trống!",
                parent=register_window,
            )
            return
        if username in accounts:
            messagebox.showerror("Lỗi", "Tài khoản đã tồn tại!", parent=register_window)
        elif password != confirm_password:
            messagebox.showerror(
                "Lỗi", "Mật khẩu nhập lại không khớp!", parent=register_window
            )
        else:
            accounts[username] = password
            messagebox.showinfo(
                "Thành công",
                "Đăng ký thành công! Bạn có thể đăng nhập ngay.",
                parent=register_window,
            )
            register_window.destroy()

    def toggle_password(entry, button):
        if entry["show"] == "*":
            entry.config(show="")
            button.config(text="🔒")
        else:
            entry.config(show="*")
            button.config(text="👁️")

    register_window = tk.Toplevel(root)
    register_window.title("Đăng Ký")
    register_window.geometry("600x500")
    register_window.configure(bg="#FFE4E1")
    register_window.transient(root)
    register_window.grab_set()

    vcmd = (register_window.register(validate_input), "%P")

    register_frame = tk.Frame(register_window, bg="#FFE4E1")
    register_frame.pack(expand=True, fill="both", padx=50, pady=50)

    tk.Label(
        register_frame, text="ĐĂNG KÝ", font=("Helvetica", 24, "bold"), bg="#FFE4E1", fg="#FF1493"
    ).pack(pady=10)
    tk.Label(
        register_frame, text="Tên đăng nhập:", bg="#FFE4E1", font=("Helvetica", 14), fg="#FF1493"
    ).pack()
    entry_new_username = ttk.Entry(
        register_frame, font=("Helvetica", 14), validate="key", validatecommand=vcmd
    )
    entry_new_username.pack(pady=10, fill="x")

    tk.Label(
        register_frame, text="Mật khẩu:", bg="#FFE4E1", font=("Helvetica", 14), fg="#FF1493"
    ).pack()
    pw_frame = tk.Frame(register_frame, bg="#FFE4E1")
    pw_frame.pack(fill="x", pady=5)
    entry_new_password = ttk.Entry(
        pw_frame,
        show="*",
        font=("Helvetica", 14),
        validate="key",
        validatecommand=vcmd,
    )
    entry_new_password.pack(side="left", expand=True, fill="x")
    btn_show_new = tk.Button(pw_frame, text="🔒", bg="#FFE4E1", fg="#FF1493")
    btn_show_new.pack(side="right", padx=5)
    btn_show_new.config(command=lambda e=entry_new_password, b=btn_show_new: toggle_password(e, b))

    tk.Label(
        register_frame, text="Nhập lại mật khẩu:", bg="#FFE4E1", font=("Helvetica", 14), fg="#FF1493"
    ).pack()
    confirm_pw_frame = tk.Frame(register_frame, bg="#FFE4E1")
    confirm_pw_frame.pack(fill="x", pady=5)
    entry_confirm_password = ttk.Entry(
        confirm_pw_frame,
        show="*",
        font=("Helvetica", 14),
        validate="key",
        validatecommand=vcmd,
    )
    entry_confirm_password.pack(side="left", expand=True, fill="x")
    btn_show_confirm = tk.Button(confirm_pw_frame, text="🔒", bg="#FFE4E1", fg="#FF1493")
    btn_show_confirm.pack(side="right", padx=5)
    btn_show_confirm.config(command=lambda e=entry_confirm_password, b=btn_show_confirm: toggle_password(e, b))

    btn_register = ttk.Button(register_frame, text="ĐĂNG KÝ", command=save_account)
    btn_register.pack(pady=20, ipadx=10, ipady=10)

def exit_game():
    if messagebox.askyesno("Thoát", "Bạn có chắc muốn thoát game?"):
        root.quit()

# --- Giao diện màn hình chính ---
root = tk.Tk()
root.title("Tic-Tac-Toe - Đăng nhập")
root.geometry("1000x700")

def load_image(filename, size):
    try:
        img_path = os.path.join(script_dir, filename)
        if not os.path.exists(img_path):
            print(f"Lỗi: Không tìm thấy file ảnh: {img_path}")
            return None
        img = Image.open(img_path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải ảnh {filename}: {e}")
        return None

# Thêm ảnh nền
bg_photo = load_image("modau.jpg", (1000, 700))
if bg_photo:
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
else:
    root.configure(bg="lightblue")

# Tiêu đề
title_label = tk.Label(
    root,
    text="GAME CỜ CARO",
    font=("Helvetica", 40, "bold"),
    fg="#FF1493",
    bg="#FFC0CB",
    highlightthickness=2,
    highlightbackground="#FF69B4",
    padx=20,
    pady=10,
)
title_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

# Tải hình ảnh nút
button_size = (60, 60)
icon_size = (40, 40)
button_width = 350
button_height = 70

login_icon = load_image("O.jpg", icon_size)
register_icon = load_image("O.jpg", icon_size)
exit_icon = load_image("X.jpg", icon_size)
play_icon = load_image("O.jpg", icon_size)

# Nút Chơi Ngay (Khách)
btn_play = tk.Button(
    root,
    text=" CHƠI NGAY (Khách)",
    image=play_icon,
    compound="left",
    font=("Helvetica", 16, "bold"),
    bg="#FFB6D9",
    fg="#FF1493",
    width=button_width,
    height=button_height,
    anchor="w",
    padx=20,
    relief="flat",
    borderwidth=0,
    activebackground="#FF8FC7",
    activeforeground="#FF1493",
    command=start_as_guest,
)
btn_play.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

# Nút Đăng nhập
btn1 = tk.Button(
    root,
    text=" ĐĂNG NHẬP",
    image=login_icon,
    compound="left",
    font=("Helvetica", 16, "bold"),
    bg="#FFB6D9",
    fg="#FF1493",
    width=button_width,
    height=button_height,
    anchor="w",
    padx=20,
    relief="flat",
    borderwidth=0,
    activebackground="#FF8FC7",
    activeforeground="#FF1493",
    command=login,
)
btn1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Nút Đăng ký
btn2 = tk.Button(
    root,
    text=" ĐĂNG KÝ",
    image=register_icon,
    compound="left",
    font=("Helvetica", 16, "bold"),
    bg="#FFB6D9",
    fg="#FF1493",
    width=button_width,
    height=button_height,
    anchor="w",
    padx=20,
    relief="flat",
    borderwidth=0,
    activebackground="#FF8FC7",
    activeforeground="#FF1493",
    command=register,
)
btn2.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Nút Thoát
btn3 = tk.Button(
    root,
    text=" THOÁT",
    image=exit_icon,
    compound="left",
    font=("Helvetica", 16, "bold"),
    bg="#FFB6D9",
    fg="#FF1493",
    width=button_width,
    height=button_height,
    anchor="w",
    padx=20,
    relief="flat",
    borderwidth=0,
    activebackground="#FF8FC7",
    activeforeground="#FF1493",
    command=exit_game,
)
btn3.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# Đảm bảo ảnh không bị thu gom rác
root.login_icon = login_icon
root.register_icon = register_icon
root.exit_icon = exit_icon
root.play_icon = play_icon
root.bg_photo = bg_photo

if __name__ == "__main__":
    root.mainloop()

# --- END OF FILE dangnhap.py ---
