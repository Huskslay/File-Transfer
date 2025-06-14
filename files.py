import os
from tkinter import simpledialog
from typing import Union

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

    def get_new_port(self, issues: str = "") -> Union[int, None]:
        if issues == "":
            return simpledialog.askinteger("Enter port", "Port:")
        return simpledialog.askinteger("Enter port", f"{issues}\nPort:")
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
            new_port = self.get_new_port()
            while new_port == None or not self.port_allowed(new_port): 
                new_port = self.get_new_port(f"Port `{new_port}` not allowed")
            if new_port == None: return -1
            self.write_port(new_port)
        with open(os.path.join(self.path, self.filename), "r") as file:
           return (int)(file.readlines()[0])
    def port_allowed(self, port: Union[int, None]) -> bool:
        if port == None: return True
        return port > 0 and port not in [1337]
        
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