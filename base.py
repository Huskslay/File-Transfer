import tkinter as tk
from tkinter import ttk
from typing import Union, TypeAlias
from threading import Thread
from collections.abc import Callable
from infi.systray import SysTrayIcon

from server import Server, Client, Communicator
from files import PortIconFileManager

class Window:
    def __init__(self) -> None:
        self.frames: list[tk.Frame] = []
        self.base_frame: ttk.Frame
        self.app: BaseApp

    def go(self, app: "BaseApp") -> None:
        self.app = app
        self.base_frame = ttk.Frame(app.master, width=500, height=300)
        self.setup()
        self.base_frame.pack()
    def setup(self) -> None:
        pass

    def end(self) -> None:
        self.on_end()
        for widget in self.base_frame.winfo_children():
            widget.destroy()
        self.base_frame.pack_forget()
    def on_end(self) -> None:
        pass

class BaseHomeWindow(Window):
    def __init__(self) -> None:
        self.hidden = False
        super().__init__()

    def hotkey_callback(self) -> None:
        pass
    def hide_and_set_hotkey(self) -> None:
        pass
        
    def change_port(self) -> None:
        pass

    def setup(self) -> None:
        self.can_hide = True
        self.running = True
        self.server = Server()
        self.thread = Thread(target=self.server_loop)
        self.after = self.app.master.after(100, self.listen_for_result)
    def listen_for_result(self) -> None:
        pass
    
    def server_loop(self) -> None:
        pass

    def on_end(self) -> None:
        pass


class BaseChooseFilesWindow(Window):
    def upload(self, label: ttk.Label, go_button: ttk.Button, type: int) -> None:
        pass
    def send(self, label: ttk.Label, ip_port: tk.Text, warning_label: ttk.Label, type: int) -> None:
        pass

    def setup(self) -> None:
        pass

    def on_end(self) -> None:
        pass

class BaseCommunicationWindow(Window):
    def set_error(self, error: str):
        pass
    def set_way_back(self, run: Union[Callable[[],None], None]):
        pass

    def recv_thread(self, communicator: Communicator) -> None:
        pass
    def file_thread_client(self, client: Client) -> None:
        pass
    def file_thread_server(self, server: Server, label: ttk.Label) -> None:
        pass

    def send_data_start(self, filepath: str, ip: str, port: int) -> None:
        pass
    def send_data_size(self) -> None:
        pass
    def send_data_name(self) -> None:
        pass
    def send_data_data(self) -> None:
        pass

    def recieve_data_start(self, server: Server) -> None:
        pass
    def recieve_data_size(self) -> None:
        pass
        pass
    def recieve_data_data(self) -> None:
        pass

    def on_end(self) -> None:
        pass

class BaseApp:
    def __init__(self, master: tk.Tk, version: str, keybind: str) -> None:
        self.master = master
        self.window: Union[Window, None] = None
        self.first_open: bool = True
        self.keybind = keybind
        self.systray: Union[BaseSysTray, None] = None
        self.has_quit = False
        self.port_manager = PortIconFileManager()

        self.home_window = BaseHomeWindow()
        self.send_files_window = BaseChooseFilesWindow()
        self.communication_window = BaseCommunicationWindow()
        self.set_window(self.home_window)

        self.after = self.master.after(100, self.quit_loop)
    def quit_loop(self) -> None:
        pass

    def on_close(self) -> None:
        pass
    def quit(self) -> None:
        pass
    def minimise(self) -> None:
        pass

    def set_window(self, window: Window) -> None:
        pass

SysTrayMenuRecurse: TypeAlias = "SysTrayMenuType"
SysTrayMenuType: TypeAlias = tuple[str, Union[str, None], Union[Callable[[SysTrayIcon], None], SysTrayMenuRecurse]]
class BaseSysTray:
    def __init__(self, app: BaseApp) -> None:
        self.app = app
        self.sysTrayIcon = SysTrayIcon(None, "File-Transfer", self.menu_options(), on_quit=self.quit, default_menu_index=1)
        self.app.systray = self
    def menu_options(self) -> tuple[SysTrayMenuType, ...]:
        return tuple([("Hide/Show", None, self.hideshow)])
    def hideshow(self, sysTrayIcon: SysTrayIcon) -> None:
        pass
    def quit(self, sysTrayIcon: SysTrayIcon) -> None:
        pass