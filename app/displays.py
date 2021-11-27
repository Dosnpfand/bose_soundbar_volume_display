import asyncio
import tkinter
import tkinter as tk
from collections import namedtuple

Dtext = namedtuple('Dtext', 'text delay')


class AsyncTK(tk.Tk):

    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.tasks = []
        self.tasks.append(loop.create_task(self._updater(0.05)))

    async def _updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


class DisplayWindows(AsyncTK):
    """
    This class paints text on top of applications using pywin and tkinter.

    Inspiration fullscreen overlay writing:
    https://stackoverflow.com/questions/21840133/how-to-display-text-on-the-screen-without-a-window-using-python

    tkinter mainloop exchanged by custom asyncio mechanic:
    https://stackoverflow.com/questions/47895765/
    use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
    """
    def __init__(self, loop):
        """
        Args:
            loop: asyncio.get_event_loop()
        """
        super().__init__(loop)
        self.loop = loop
        self.tasks = []
        self.tasks.append(loop.create_task(self._draw_volume()))
        self.tasks.append(loop.create_task(self._updater(0.05)))
        self.startup_text: Dtext = Dtext('Starting up volume ctrl', 2)
        self.text: Dtext = None

        label = tkinter.Label(text='', font=('Times New Roman', '80'), fg='white', bg='black')
        label.master.overrideredirect(True)
        label.master.geometry("+50+50")
        label.master.lift()
        label.master.wm_attributes("-topmost", True)
        label.master.wm_attributes("-topmost", False)
        label.master.wm_attributes("-transparentcolor", "black")

        import pywintypes
        import win32api
        import win32con

        hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
                  win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

        label.pack()
        self.label = label

    async def _updater(self, interval):
        """
        With window lifting for Windows0
        Args:
            interval:
        """
        while True:
            self.lift()
            self.wm_attributes("-topmost", True)
            self.update()
            await asyncio.sleep(interval)

    def set_text(self, s: Dtext):
        self.text = s

    async def _draw_volume(self, interval=0.5):
        """
        This is the update-mainloop: Check if 'self.text' has changed and if so display for requested time
        Args:
            interval: how long this loop pauses before checking / drawing
        """
        while await asyncio.sleep(interval, True):
            if self.startup_text is not None:
                self.label.config(text=self.startup_text.text)
                await asyncio.sleep(self.startup_text.delay)
                self.label.config(text='')
                self.startup_text = None
            if self.text is not None:
                self.label.config(text=self.text.text)
                tmp_delay = self.text.delay  # need to tmp store bc need to None immediately
                self.text = None
                await asyncio.sleep(tmp_delay)
                self.label.config(text='')
