import tkinter as tk
from tkinter import ttk
from tendo import singleton

import winreg, sys, os

from windows import App, KEYBIND
from systray import SysTray


def make_on_startup() -> None:
    if getattr(sys, "frozen", False): exe_path = sys.executable
    else: exe_path = os.path.abspath(__file__)
    REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    name = "File-Transfer"
    value = f'"{os.path.abspath(exe_path)}" withdraw'
    try:    
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                        winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
    except WindowsError: pass
        
def is_only_version() -> bool:
    try:
        singleton.SingleInstance()
        return True
    except: return False


if __name__ == "__main__":
    make_on_startup()

    root = tk.Tk()
    if is_only_version():
        SysTray(App(root))
        root.mainloop()
    else:
        fail = True
        ttk.Label(root, text="Warning, instance already open!").pack()
        ttk.Label(root, text=f"If it is hidden, use {KEYBIND} to show it").pack()
        ttk.Button(root, text="Close", command=lambda: root.destroy()).pack()
        root.mainloop()  

   