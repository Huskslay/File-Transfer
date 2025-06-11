from infi.systray import SysTrayIcon

from base import BaseApp, BaseSysTray, SysTrayMenuType

class SysTray(BaseSysTray):
    def __init__(self, app: BaseApp) -> None:
        self.app = app
        self.sysTrayIcon = SysTrayIcon(self.app.port_manager.icon_location(), "File-Transfer", self.menu_options(), on_quit=self.quit, default_menu_index=1)
        self.sysTrayIcon.start()
        self.app.systray = self
    def menu_options(self) -> tuple[SysTrayMenuType, ...]:
        return tuple([("Hide/Show", None, self.hideshow)])
    def hideshow(self, sysTrayIcon: SysTrayIcon) -> None:
        if self.app.home_window.hidden: self.app.home_window.hotkey_callback()
        else: self.app.minimise()
    def quit(self, sysTrayIcon: SysTrayIcon) -> None:
        if not self.app.has_quit: self.app.has_quit = True