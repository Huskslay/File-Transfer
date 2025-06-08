import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from collections.abc import Callable
from threading import Thread
import os, socket, shutil

SIZE = 1048576
BYTEORDER_LENGTH = 8
FORMAT = "utf-8"

def get_int_from_window(title: str, prompt: str) -> int:
    root = tk.Tk()
    root.withdraw()

    user_input = simpledialog.askinteger(title, prompt)

    if user_input is not None:
        return user_input
    return -1

class App:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.geometry("500x300")
        self.data = ("", "", 0)
        self.set_window(self.window_main)
    
    def set_window(self, window: Callable[[], None]) -> None:
        for i in self.master.winfo_children():
            i.destroy()
        self.frame1 = tk.Frame(self.master, width=500, height=300)
        self.frame1.pack()
        window()

    def upload(self, label: ttk.Label, go_button: ttk.Button, type: int) -> None:
        if type == 1: name = filedialog.askopenfilename(filetypes=[("Zip file", "*.zip")])
        elif type == 2: name = filedialog.askdirectory()
        else: name = filedialog.askopenfilename()
        if name == "": return
        go_button.config(state="normal")
        label.config(text=name)
    def send(self, label: ttk.Label, ip_port: tk.Text, warning_label: ttk.Label, type: int) -> None:
        try:
            ip_port_text = ip_port.get("1.0","end-1c").strip().split(":")
            ip, port = ip_port_text[0], int(ip_port_text[1])
            filepath = label["text"]
            filename = os.path.basename(filepath)
            if type == 2:
                if not os.path.exists("Temp"): os.makedirs("Temp")
                shutil.make_archive(os.path.join("Temp","Data"), "zip", os.path.dirname(filepath), filename)
                filepath = os.path.join("Temp","Data.zip")
            if os.path.exists(filepath) and len(ip) >= 9 and port >= 0:
                self.data = (filepath, ip, port)
                self.set_window(self.window_send_zip_file_active)
                return
        except: pass
        warning_label.config(text=
"An issue occured with your inputs!\nExample with 127.0.0.1 as example ip and\n5555 as example port -> 127.0.0.1:5555")

    def delete_temp(self) -> None:
        if os.path.exists(os.path.join("Temp","Data.zip")): 
            os.remove(os.path.join("Temp","Data.zip"))
        if os.path.exists("Temp"): os.removedirs("Temp")

    def quit_socket(self) -> None:
        try: self.socket.close()
        except: pass
        self.set_window(self.window_main)



    def window_main(self) -> None:
        self.delete_temp()

        ttk.Label(self.frame1, text="Main").pack()
        ttk.Button(self.frame1, text="Send zip file", 
                    command=lambda: self.set_window(self.window_send_zip_file), 
                    width=100).pack()
        ttk.Button(self.frame1, text="Recieve zip file", 
                    command=lambda: self.set_window(self.window_recieve_zip_file), 
                    width=100).pack()


    def window_send_zip_file(self) -> None:
        ttk.Label(self.frame1, text="Send Zip File").pack()
        ttk.Button(self.frame1, text="Go to Main", 
                    command=lambda: self.set_window(self.window_main),
                    width=100).pack()
        canvas = tk.Canvas(self.frame1, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        select_frame = tk.Frame(self.frame1, width=500, height=100)
        ip_port_frame = tk.Frame(self.frame1, width=500, height=100)
        warning_label = ttk.Label(ip_port_frame, text="Enter Ip:port and choose file\n\n")
        ip_port = tk.Text(ip_port_frame, width=20, height=1, wrap="none")
        ip_port_label = ttk.Label(ip_port_frame, text="Ip:port ")

        lower_frame = tk.Frame(self.frame1, width=500, height=100, pady=5)
        file_label = ttk.Label(lower_frame, text="No file selected")
        go_button = ttk.Button(self.frame1, text="Go!",
                   command=lambda: self.send(file_label, ip_port, warning_label, var.get()),
                    width=10, state="disabled", padding=10)
        upload_button = ttk.Button(lower_frame, text="Upload Zip",
                        command=lambda: self.upload(file_label, go_button, var.get()),
                        width=15)

        def sel() -> None:
            val = var.get()
            file_label.config(text="No file selected")
            go_button.config(state="disabled")
            upload_button.config(text=f"Upload {"Zip" if val==1 else "Folder" if val==2 else "File"}")
        var = tk.IntVar(None, 1)
        R1 = tk.Radiobutton(select_frame, text="Zip file", variable=var, value=1, command=sel)
        R1.pack(anchor=tk.W,side=tk.LEFT)
        R2 = tk.Radiobutton(select_frame, text="Folder", variable=var, value=2, command=sel)
        R2.pack(anchor=tk.W,side=tk.LEFT)
        R3 = tk.Radiobutton(select_frame, text="File", variable=var, value=3, command=sel)
        R3.pack(anchor=tk.W,side=tk.LEFT)
        select_frame.pack(pady=2)

        warning_label.pack()
        ip_port_label.pack(side=tk.LEFT)
        ip_port.pack(side=tk.LEFT)
        ip_port_frame.pack()
        upload_button.pack(side=tk.LEFT)
        file_label.pack(side=tk.LEFT)
        lower_frame.pack()
        go_button.pack()
    def window_send_zip_file_active(self) -> None:
        ttk.Label(self.frame1, text="Send Zip File").pack()
        return_button = ttk.Button(self.frame1, text="Go to Main", 
                    command=self.quit_socket,
                    width=100)
        return_button.pack()
        canvas = tk.Canvas(self.frame1, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        filepath, ip, port = self.data
        try:
            filename = os.path.basename(filepath)
            ttk.Label(self.frame1, text="Sending Zip File").pack()
            ttk.Label(self.frame1, text=filepath).pack()

            self.socket = socket.socket()
            ttk.Label(self.frame1, text=f"Connecting to {ip}:{port}").pack()
            self.socket.connect((ip, port))
            return_button.config(state="disabled")
            ttk.Label(self.frame1, text=f"Connected! Preparing to send {filename}").pack()

            ttk.Label(self.frame1, text="Sending file size and name").pack()
            file_size = os.path.getsize(filepath)
            file_size_in_bytes = file_size.to_bytes(BYTEORDER_LENGTH, 'big')
            self.socket.send(file_size_in_bytes)
            msg = self.socket.recv(SIZE).decode(FORMAT)
            self.socket.send(filename.encode(FORMAT))           
            msg = self.socket.recv(SIZE).decode(FORMAT)

            ttk.Label(self.frame1, text=f"Sending data...").pack()
            with open(filepath,'rb') as f1:
                self.socket.send(f1.read())
            msg = self.socket.recv(SIZE).decode(FORMAT)
            ttk.Label(self.frame1, text=f"Finished!").pack()

            self.socket.close()
            return_button.config(state="normal")
        except: pass
        self.delete_temp()
        

    def window_recieve_zip_file(self) -> None:
        port = get_int_from_window("Choose port", "Port: ")
        if port <= 0: 
            self.set_window(self.window_main)
            return

        ttk.Label(self.frame1, text="Recieve Zip File").pack()
        return_button = ttk.Button(self.frame1, text="Go to Main", 
                    command=self.quit_socket,
                    width=100)
        return_button.pack()
        thread = Thread(target=self.window_recieve_zip_file_active, args=(port,return_button,))

        self.canvas = tk.Canvas(self.frame1, height=20)
        self.canvas.create_line(0, 10, 500, 10)
        self.canvas.pack(fill=tk.BOTH)

        thread.start()
    def window_recieve_zip_file_active(self, port: int, return_button: ttk.Button) -> None:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.socket.bind((ip, port))
            ttk.Label(self.frame1, text=f"Ipv4: {ip}:{port}").pack()
            ttk.Label(self.frame1, text="Waiting for 1 connection...").pack()
            self.socket.listen(1)

            clientSocket, returnAddress = self.socket.accept()
            return_button.config(state="disabled")
            ttk.Label(self.frame1, text=f"Connection from: {returnAddress[0]}:{returnAddress[1]}").pack()

            ttk.Label(self.frame1, text="Getting preliminary data...").pack()
            file_size_in_bytes = clientSocket.recv(BYTEORDER_LENGTH)
            file_size = int.from_bytes(file_size_in_bytes, 'big')
            clientSocket.send("File size received.".encode(FORMAT))
            filename = clientSocket.recv(SIZE).decode(FORMAT)
            clientSocket.send("Filename received.".encode(FORMAT))

            progress_label = ttk.Label(self.frame1, text=f"Getting file data for {filename}...0%")
            progress_label.pack()
            packet = b""
            progress: float = 0
            while len(packet) < file_size:
                if len(packet)/file_size > progress:
                    progress_label.config(text=f"Getting file data for {filename}...{round(len(packet) * 100 / file_size)}%")
                    progress += 0.01
                if(file_size - len(packet)) > SIZE: buffer = clientSocket.recv(SIZE)
                else: buffer = clientSocket.recv(file_size - len(packet))
                if not buffer: raise Exception("Incomplete file received")
                packet += buffer

            ttk.Label(self.frame1, text=f"Writing {filename}").pack()
            if not os.path.exists("Recieved"): os.makedirs("Recieved")
            with open(os.path.join("Recieved", filename), 'wb') as f:
                f.write(packet)
                
            clientSocket.send("File data received".encode(FORMAT))
            clientSocket.close()
            self.socket.close()
            
            return_button.config(state="normal")
            ttk.Label(self.frame1, text=f"Finished!").pack()
        except: pass

root = tk.Tk()
App(root)
root.mainloop()