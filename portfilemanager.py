import os
from tkinter import simpledialog

class PortFileManager:
    def __init__(self) -> None:
        self.path = os.path.join(os.path.expanduser("~"), "Documents", "FileTransferInfo")
        self.filename = "data.txt"
        self.port = self.get_port()

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