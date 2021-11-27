"""
Goal here is to create a system that polls the soundbar 700 periodically for current volume
and displays the result in case of a change as a timed overlay in windows.
Probably also experiment with setting volume later.
Should be implemented in a way that makes display easily exchangeable to also support raspi with tft display.
"""
import asyncio
import concurrent
import tkinter
import tkinter as tk
from collections import namedtuple
from random import randint
from typing import Callable

import pywintypes
import upnpclient as upnpclient
import win32api
import win32con
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpRequester


class UpnpRequester:
    """
    This class finds the soundbar in a local network and then periodically requests the volume
    and hands this information to a consumer via a registered callback.
    """
    def __init__(self, loop, volume_callback: Callable, refresh_delay=0.2):
        self.refresh_delay = refresh_delay
        self.soundbar = None
        loop.create_task(self.discover_soundbar())
        loop.create_task(self.volume_loop(volume_callback))

    async def discover_soundbar(self):

        while True:
            if self.soundbar is None:
                devices = upnpclient.discover()
                for d in devices:
                    if d.model_name == 'Bose Soundbar 700':
                        print(f"Soundbar discovered: {d.device_name}")
                        self.soundbar = d
                print("Soundbar 700 not found, retrying...")
            await asyncio.sleep(2)

    async def volume_loop(self, cb_func):
        """
        Main loop of the Requester: Query the Volume via UPNP client, and the forward it to the callback.
        Args:
            cb_func: the callback
        """
        get_volume = None
        while True:
            if self.soundbar is not None:
                if get_volume is None:
                    print("creating device...")
                    # create the factory
                    requester = AiohttpRequester()
                    factory = UpnpFactory(requester)

                    # create a device
                    device = await factory.async_create_device(self.soundbar.device_name)
                    service = device.service('urn:schemas-upnp-org:service:RenderingControl:1')
                    # perform GetVolume action
                    get_volume = service.action('GetVolume')
                    print("done.")

                try:
                    result = await get_volume.async_call(InstanceID=0, Channel='Master')
                    cb_func(result['CurrentVolume'])
                    # happens when soundbar gets switched off
                except (concurrent.futures.CancelledError, concurrent.futures.TimeoutError):
                    self.soundbar = None
                    get_volume = None

            await asyncio.sleep(self.refresh_delay)


class FakeRequester:
    def __init__(self, loop, volume_callback: Callable, refresh_delay=0.2):
        self.refresh_delay = refresh_delay
        loop.create_task(self.volume_loop(volume_callback))

    async def volume_loop(self, cb_func):
        while True:
            cb_func(randint(0, 100))
            await asyncio.sleep(self.refresh_delay)


Dtext = namedtuple('Dtext', 'text delay')


class Display(tk.Tk):
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
        super().__init__()
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

        hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
                  win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

        label.pack()
        self.label = label

    async def _updater(self, interval):
        while True:
            self.lift()
            self.wm_attributes("-topmost", True)

            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()

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


class VolumeCtrl:
    """
    Main Class that holds the requester and a Display.
    """
    def __init__(self):
        self.last_volume: int = 0
        loop = asyncio.get_event_loop()
        self.requester = UpnpRequester(loop, self.volume_callback)
        # self.requester = FakeRequester(loop, self.volume_callback)
        self.display = Display(loop)
        loop.run_forever()
        loop.close()

    def volume_callback(self, vol: int):
        """
        Callback that forwards from the requester to the display.
        Args:
            vol: the volume.
        """
        if vol != self.last_volume:
            self.last_volume = vol
            self.display.set_text(Dtext(f"{vol}", 0.5))


if __name__ == '__main__':
    vc = VolumeCtrl()
