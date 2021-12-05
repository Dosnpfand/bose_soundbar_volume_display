"""
Goal here is to create a system that polls the soundbar 700 periodically for current volume
and displays the result in case of a change as a timed overlay in windows.
Probably also experiment with setting volume later.
Should be implemented in a way that makes display easily exchangeable to also support raspi with tft display.
"""
import asyncio
import concurrent
import os
from random import randint
from typing import Callable

import upnpclient as upnpclient
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpRequester

from displays import DisplayWindows, DisplayPi, Dtext
import logging


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
                    logging.getLogger("vc").debug(f"checking device: {d.device_name}")
                    if 'bose' in d.model_name.lower():
                        logging.getLogger("vc").info(f"Soundbar discovered: {d.device_name}")
                        self.soundbar = d
                logging.getLogger("vc").warning("Soundbar not found, retrying...")
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
                    logging.getLogger("vc").info("Creating device...")
                    # create the factory
                    requester = AiohttpRequester()
                    factory = UpnpFactory(requester)

                    # create a device
                    device = await factory.async_create_device(self.soundbar.device_name)
                    service = device.service('urn:schemas-upnp-org:service:RenderingControl:1')
                    # perform GetVolume action
                    get_volume = service.action('GetVolume')
                    logging.getLogger("vc").info("DEvice and Volume Request Service created.")

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


class VolumeCtrl:
    """
    Main Class that holds the requester and a Display.
    """
    def __init__(self):
        self._setup_logging()
        self.last_volume: int = 0
        loop = asyncio.get_event_loop()
        self.requester = UpnpRequester(loop, self.volume_callback)
        # self.requester = FakeRequester(loop, self.volume_callback)

        if os.name == 'nt':
            logging.getLogger().info("Windows detected")
            self.display = DisplayWindows(loop)
        elif os.name == 'posix':
            logging.getLogger("vc").info("Linux detected")
            self.display = DisplayPi(loop)

        loop.run_forever()
        loop.close()

    @staticmethod
    def _setup_logging():
        logger = logging.getLogger("vc")
        logger.setLevel(logging.DEBUG)  # need to also set this to get output, default is WARNING

        # config stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_format = logging.Formatter('%(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(stream_format)
        logger.addHandler(stream_handler)

        # config file-handler
        if os.getenv('INSIDE_DOCKER', False):
            file_handler = logging.FileHandler('/logs/logfile.log')
        else:
            file_handler = logging.FileHandler('logfile.log')

        file_handler.setFormatter(file_format)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        logger.debug("Logging configured")


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
