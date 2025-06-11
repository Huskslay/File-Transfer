import os
from tkinter import simpledialog

from icon import ICONDATA

class PortIconFileManager:
    def __init__(self) -> None:
        location = os.getenv('APPDATA')
        if location == None: location = self.path = os.path.join(os.path.expanduser("~"), "Documents", "FileTransferInfo")
        else: self.path = os.path.join(location, "FileTransferInfo")
        self.filename = "data.txt"
        self.port = -1

        self.iconname = "icon.ico"
        self.save_icon()

    def get_new_port(self) -> int:
        user_input = simpledialog.askinteger("Enter port", "Port:")
        if user_input is not None:
            return user_input
        return -1
    def write_port(self, new_port: int) -> None:
        if os.path.exists(os.path.join(self.path, self.filename)):
            os.remove(os.path.join(self.path, self.filename))
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(os.path.join(self.path, self.filename), "w") as file:
            file.truncate(0)
            file.writelines(f"{new_port}\n")
    def get_port(self) -> int:
        if not os.path.exists(os.path.join(self.path, self.filename)):  
            new_port = -1 
            while new_port < 0: new_port = self.get_new_port()
            self.write_port(new_port)
        with open(os.path.join(self.path, self.filename), "r") as file:
           return (int)(file.readlines()[0])
        
    def save_icon(self) -> None:
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.icon_location(), "wb") as f:
            f.truncate(0)
            f.write(ICONDATA)
    def icon_location(self) -> str:
        return os.path.join(self.path, self.iconname)
    

class FileData:
    def __init__(self) -> None:
        self.filename = ""
        self.filesize = 0
        self.data = b""

    def set_size(self, size_in_bytes: bytes) -> None:
        self.filesize = int.from_bytes(size_in_bytes, "big")

    def save(self, folder_name: str) -> None:
        if not os.path.exists(folder_name): os.makedirs(folder_name)
        with open(os.path.join(folder_name, self.filename), "wb") as f:
            f.write(self.data)

    def __str__(self) -> str:
        return f"{self.filename}: {self.filesize} -> <{self.data}>"