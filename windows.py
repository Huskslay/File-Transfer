import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Union
from threading import Thread
from collections.abc import Callable

import keyboard, os, sys, shutil, pyperclip, time

from server import Server, Client, Communicator, SIZE, FORMAT
from files import PortIconFileManager, FileData
from base import Window, BaseChooseFilesWindow, BaseCommunicationWindow, BaseHomeWindow, BaseApp, BaseSysTray

KEYBIND = "ctrl+f10"
VERSION = "v1.1.2"

class HomeWindow(BaseHomeWindow):
    def __init__(self) -> None:
        self.hidden = False
        super().__init__()

    def hotkey_callback(self) -> None:
        if not self.hidden: return
        self.hidden = False
        keyboard.remove_hotkey(KEYBIND)
        keyboard.add_hotkey(KEYBIND, self.hide_and_set_hotkey)
        self.app.master.deiconify()    
        self.app.master.attributes("-topmost", True)
        self.app.master.attributes("-topmost", False)
        self.app.master.focus_force()  
    def hide_and_set_hotkey(self) -> None:
        if self.hidden or not self.can_hide: return
        self.hidden = True
        keyboard.remove_hotkey(KEYBIND)
        keyboard.add_hotkey(KEYBIND, self.hotkey_callback)
        self.app.master.withdraw()
        
    def change_port(self) -> None:
        self.can_hide = False
        new_port = self.app.port_manager.get_new_port()
        if new_port < 0: 
            self.can_hide = True
            return
        self.app.port_manager.write_port(new_port)
        self.app.port_manager.port = new_port
        self.address_label.config(text=f"Listening on {self.server.ip}:{self.app.port_manager.port}")
        self.server.close()
        self.can_hide = True

    def setup(self) -> None:
        if os.path.exists("Temp"): shutil.rmtree("Temp")

        self.can_hide = True
        self.running = True
        self.server = Server()
        self.thread = Thread(target=self.server_loop)
        self.thread.start()

        label = ttk.Label(self.base_frame, text="Home Menu")
        button = ttk.Button(self.base_frame, text=f"Hide window ({KEYBIND} to return)", command=self.hide_and_set_hotkey, width=100)

        frame = ttk.Frame(self.base_frame, width=500, height=20)
        self.address_label = ttk.Label(frame, text=f"Listening on {self.server.ip}:{self.app.port_manager.port}")
        button2 = ttk.Button(frame, text="Copy Ip:Port", command=lambda: pyperclip.copy(f"{self.server.ip}:{self.app.port_manager.port}"), width=20)
        button3 = ttk.Button(frame, text="Change Port", command=self.change_port, width=20)
        self.address_label.pack(side=tk.LEFT, padx=25)
        button2.pack(side=tk.LEFT)
        button3.pack(side=tk.LEFT)

        label.pack()
        button.pack()
        frame.pack()

        canvas = tk.Canvas(self.base_frame, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        label = ttk.Button(self.base_frame, text="Stop server and send file",
                           command=lambda: self.app.set_window(self.app.send_files_window), width=100)
        label.pack()

        keyboard.add_hotkey(KEYBIND, self.hide_and_set_hotkey)
        if len(sys.argv) > 1: 
            if sys.argv[1] == "withdraw" and self.app.first_open: 
                self.hide_and_set_hotkey()
        self.app.first_open = False
        self.after = self.app.master.after(100, self.listen_for_result)
    def listen_for_result(self) -> None:
        if not self.running:
            if self.hidden: self.hotkey_callback()
            self.app.set_window(self.app.communication_window)
            self.app.communication_window.recieve_data_start(self.server)
        else: self.after = self.app.master.after(100, self.listen_for_result)
    
    def server_loop(self) -> None:
        while self.running:
            try:
                self.server.setup(self.app.port_manager.port)
                self.running = False
            except: pass

    def on_end(self) -> None:
        self.app.master.after_cancel(self.after)
        keyboard.remove_hotkey(KEYBIND)
        if self.running:
            self.running = False
            self.server.close()
            self.thread.join()


class ChooseFilesWindow(BaseChooseFilesWindow):
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
            if type == 2: # If folder, make zip folder
                if not os.path.exists("Temp"): os.makedirs("Temp")
                shutil.make_archive(os.path.join("Temp",filename), "zip", os.path.dirname(filepath), filename)
                filepath = os.path.join("Temp",filename+".zip")
            if os.path.exists(filepath) and len(ip) >= 9 and port >= 0:
                self.app.set_window(self.app.communication_window)
                self.app.communication_window.send_data_start(filepath, ip, port)
                return
        except: pass
        warning_label.config(text=
"An issue occured with your inputs!\nExample with 127.0.0.1 as example ip and\n5555 as example port -> 127.0.0.1:5555")


    def setup(self) -> None:
        label = ttk.Label(self.base_frame, text="Send Files Menu")
        button = ttk.Button(self.base_frame, text="Back to home", 
                            command=lambda: self.app.set_window(self.app.home_window), width=100)

        label.pack()
        button.pack()

        canvas = tk.Canvas(self.base_frame, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        label = ttk.Label(self.base_frame, text="Send Zip/Folder/File?")
        label.pack()


        select_frame = tk.Frame(self.base_frame, width=500, height=100)
        ip_port_frame = tk.Frame(self.base_frame, width=500, height=100)
        warning_label = ttk.Label(ip_port_frame, text="Enter Ip:port and choose file\n\n")
        ip_port = tk.Text(ip_port_frame, width=20, height=1, wrap="none")
        ip_port_label = ttk.Label(ip_port_frame, text="Ip:port ")

        lower_frame = tk.Frame(self.base_frame, width=500, height=100, pady=5)
        file_label = ttk.Label(lower_frame, text="No file selected")
        go_button = ttk.Button(self.base_frame, text="Go!",
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
        R2 = tk.Radiobutton(select_frame, text="Folder (to zip)", variable=var, value=2, command=sel)
        R2.pack(anchor=tk.W,side=tk.LEFT)
        R3 = tk.Radiobutton(select_frame, text="File", variable=var, value=3, command=sel)
        R3.pack(anchor=tk.W,side=tk.LEFT)
        select_frame.pack(pady=10)

        warning_label.pack()
        ip_port_label.pack(side=tk.LEFT)
        ip_port.pack(side=tk.LEFT)
        ip_port_frame.pack()
        upload_button.pack(side=tk.LEFT)
        file_label.pack(side=tk.LEFT)
        lower_frame.pack()
        go_button.pack()

    def on_end(self) -> None:
        pass

class CommunicationWindow(BaseCommunicationWindow):
    def set_error(self, error: str):
        for widget in self.base_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.base_frame, text="Error!").pack()
        ttk.Label(self.base_frame, text=error).pack()
        self.set_way_back(None)
    def set_way_back(self, run: Union[Callable[[],None], None]):
        if run != None: run()
        ttk.Button(self.base_frame, text="Back to home", command=lambda: self.app.set_window(self.app.home_window)).pack()

    def recv_thread(self, communicator: Communicator) -> None:
        self.data = communicator.recieve()
    def file_thread_client(self, client: Client) -> None:
        with open(self.filepath, "rb") as f:
            while self.filesize > 0:
                reading = min(SIZE // 3, self.filesize)
                self.filesize -= reading
                client.send(f.read(reading))
                self.data = client.recieve()
    def file_thread_server(self, server: Server) -> None:
        to_read = self.file_data.filesize
        while to_read > 0:
            recieved = server.recieve()
            self.file_data.data += recieved
            to_read -= len(recieved)
            server.send(b"c")

    def send_data_start(self, filepath: str, ip: str, port: int) -> None:
        ttk.Label(self.base_frame, text="Sending Data!").pack()

        canvas = tk.Canvas(self.base_frame, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        if not os.path.exists(filepath):
            self.set_error(f"File '{filepath}' does not exist")
            return
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        try:
            self.client = Client()
            self.client.connect(ip, port)
        except:
            self.set_error("Could not connect and exchange with server")
            return
        
        ttk.Label(self.base_frame, text="Waiting for confirmation...").pack()
        self.thread = Thread(target=self.recv_thread, args=(self.client,))
        self.thread.start()
        self.app.master.after(100, self.send_data_size)
    def send_data_size(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.send_data_size)
            return
        
        if self.data == b"n":
            ttk.Label(self.base_frame, text="Connection refused.").pack()
            self.set_way_back(self.client.close)
            return
        ttk.Label(self.base_frame, text="Connection accepted.").pack()

        ttk.Label(self.base_frame, text="Sending size data...").pack()
        self.filesize = os.path.getsize(self.filepath)
        file_size_in_bytes = self.filesize.to_bytes(8, "big")
        self.client.send(file_size_in_bytes)

        self.thread = Thread(target=self.recv_thread, args=(self.client,))
        self.thread.start()
        self.app.master.after(100, self.send_data_name)
    def send_data_name(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.send_data_name)
            return
        
        ttk.Label(self.base_frame, text=f"Sending name data `{self.filename}` ...").pack()
        self.client.send_str(self.filename)

        ttk.Label(self.base_frame, text="Sending data...").pack()
        self.thread = Thread(target=self.file_thread_client, args=(self.client,))
        self.thread.start()
        self.app.master.after(100, self.send_data_data)
    def send_data_data(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.send_data_data)
            return
        
        ttk.Label(self.base_frame, text="Data sent!").pack()
        if os.path.exists("Temp"): shutil.rmtree("Temp")
        self.set_way_back(self.client.close)

        


    def recieve_data_start(self, server: Server) -> None:
        ttk.Label(self.base_frame, text="Recieving Data!").pack()
        
        canvas = tk.Canvas(self.base_frame, height=20)
        canvas.create_line(0, 10, 500, 10)
        canvas.pack(fill=tk.BOTH)

        ttk.Label(self.base_frame, text="Selecting choice...").pack()
        time.sleep(0.1)
        if not messagebox.askokcancel("Accept", f"Accept from {server.returnAddress[0]}:{server.returnAddress[1]}?"):
            server.send(b"n")
            self.set_way_back(server.close)
            return
        server.send(b"y")
        self.server = server
        self.file_data = FileData()

        ttk.Label(self.base_frame, text="Getting size data...").pack()
        self.thread = Thread(target=self.recv_thread, args=(self.server,))
        self.thread.start()
        self.app.master.after(100, self.recieve_data_size)
    def recieve_data_size(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.recieve_data_size)
            return
        
        self.file_data.set_size(self.data)
        self.server.send(b"c")

        ttk.Label(self.base_frame, text="Getting name data...").pack()
        self.thread = Thread(target=self.recv_thread, args=(self.server,))
        self.thread.start()
        self.app.master.after(100, self.recieve_data_name)
    def recieve_data_name(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.recieve_data_name)
            return
        
        self.file_data.filename = self.data.decode(FORMAT)
        ttk.Label(self.base_frame, text=f"Recieved name: `{self.file_data.filename}`").pack()
        self.server.send(b"c")

        ttk.Label(self.base_frame, text="Getting file data...").pack()
        self.thread = Thread(target=self.file_thread_server, args=(self.server,))
        self.thread.start()
        self.app.master.after(100, self.recieve_data_data)
    def recieve_data_data(self) -> None:
        if self.thread.is_alive():
            self.app.master.after(100, self.recieve_data_data)
            return
        
        ttk.Label(self.base_frame, text="Saving data...").pack()
        self.file_data.save("Recieved")
        ttk.Label(self.base_frame, text="Finished!").pack()
        self.set_way_back(self.server.close)

    def on_end(self) -> None:
        try: self.server.close()
        except: pass
        try: self.client.close()
        except: pass



class OptionDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, title: str, questions: list[str], options: list[str]):
        tk.Toplevel.__init__(self,parent)
        self.title(title)
        self.questions, self.options = questions, options
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW",self.cancel)
        self.result = "_"
        self.geometry("+%d+%d" %(parent.winfo_x()+200,parent.winfo_y()+200))
        self.createWidgets()
        self.grab_set()
        self.wait_window()
    def createWidgets(self):
        row = 1
        for question in self.questions:
            frmQuestion = tk.Frame(self)
            tk.Label(frmQuestion,text=question).grid()
            frmQuestion.grid(row=row)
            row += 1
        frmButtons = tk.Frame(self)
        frmButtons.grid(row=row)
        column = 0
        for option in self.options:
            btn = tk.Button(frmButtons,text=option,command=lambda x=option:self.setOption(x))
            btn.grid(column=column,row=0)
            column += 1 
    def setOption(self,optionSelected):
        self.result = optionSelected
        self.destroy()
    def cancel(self):
        self.result = None
        self.destroy()


class App(BaseApp):
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.geometry("500x400")
        self.master.title("File-Transfer")
        self.window: Union[Window, None] = None
        self.first_open: bool = True

        ttk.Label(self.master, text=VERSION).pack(side=tk.BOTTOM)

        self.systray: Union[BaseSysTray, None] = None
        self.has_quit = False

        self.port_manager = PortIconFileManager()
        self.master.iconbitmap(self.port_manager.icon_location())
        self.port_manager.port = -1
        while self.port_manager.port < 0:
            self.port_manager.port = self.port_manager.get_port()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.home_window = HomeWindow()
        self.send_files_window = ChooseFilesWindow()
        self.communication_window = CommunicationWindow()
        self.set_window(self.home_window)

        self.after = self.master.after(100, self.quit_loop)
    def quit_loop(self) -> None:
        if not self.has_quit:
            self.after = self.master.after(100, self.quit_loop)
            return
        self.quit()

    def on_close(self) -> None:
        dlg = OptionDialog(self.master, "Quit", ["Do you want to quit or minimise", f"(Unminimise with {KEYBIND})"], ["Quit", "Minimise", "No"])
        if dlg.result == "Quit": 
            if self.systray != None: self.systray.sysTrayIcon.shutdown()
            else: self.quit()
        elif dlg.result == "Minimise": self.minimise()
    def quit(self) -> None:
        self.master.after_cancel(self.after)
        self.has_quit = True
        if self.window != None: self.window.end()
        self.master.destroy()
    def minimise(self) -> None:
        if self.window != self.home_window: self.set_window(self.home_window)
        self.home_window.hide_and_set_hotkey()
        
    def set_window(self, window: Window) -> None:
        if self.window != None: self.window.end()
        self.window = window
        self.window.go(self)