import asyncio
from json import dump, load
from kasa import SmartDevice
from kasa.discover import Discover
from kasa.exceptions import SmartDeviceException
import nest_asyncio
from random import randint
from threading import Event, Thread
from time import sleep
from typing import Optional, Union

# value is optional, so we either have a tuple of hue, saturation, value or just hue, saturation
ColorType = Union[tuple[int, int], tuple[int, int, int]]
nest_asyncio.apply()

class BulbManager:
    '''
    Class for managing a single bulb.
    We'll have more advanced functionality in the future but for now it just wraps functions from the library
    '''
    def __init__(self, target: str):
        self.target: str = target
        self.device: SmartDevice = None
        self.connected: bool = False

        # These are for the random color loop
        self._previous_color: Optional[ColorType] = None
        self._color_event: Optional[Event] = None

    async def connect(self):
        try:
            self.device = await BulbManager.get_device(self.target)
            await self.device.update()
            self.connected = True
        except:
            self.connected = False

    async def off(self):
        await self.device.update()
        await self.device.turn_off()

    async def on(self):
        await self.device.update()
        await self.device.turn_on()

    async def set_hsv(self, hue: int, saturation: int, value: Optional[int] = None, transition: Optional[int] = None):
        await self.device.update()
        await self.device.set_hsv(hue, saturation, value, transition=transition)

        # We need to sleep for the transition time
        # If not, the bulb becomes unresponsive and future connection attempts fail (not sure exactly why)
        if transition is not None:
            sleep(transition / 1000)

    def start_random(self, colors: list[ColorType], interval: int):
        '''
        Start a random color loop
        '''
        self._color_event = Event()

        t = Thread(target=self._get_color_setter_task(colors, interval), args=(self._color_event,))
        t.start()

    def stop_random(self):
        '''
        Stop the random color loop
        '''
        if self._color_event is not None:
            self._color_event.set()


    def _get_color_setter_task(self, colors: list[ColorType], interval: int):
        '''
        Get the task that sets the color
        '''

        def _run_color_change(event: Event):
            # We'll have a loop that runs indefinitely until the event to stop is set
            loop = asyncio.get_event_loop()

            while not event.is_set():
                color = colors[randint(0, len(colors) - 1)]

                # Make sure we don't set the same color twice in a row
                while color == self._previous_color:
                    color = colors[randint(0, len(colors) - 1)]

                loop.run_until_complete(self.set_hsv(*color, transition=interval))

        return _run_color_change

    @staticmethod
    async def get_device(target: str):
        # We'll have the target address passed in to make it easier since discover is finicky
        devices = await Discover.discover(target=target)

        return devices.get(target, None)

    @staticmethod
    async def populate_cache():
        '''
        Discover all devices and cache them
        I'm not sure why, but this version of discover is less reliable so we just get the addresses so we have them, and 
        then pass in the address for the specific device we want.
        This implementation also means we don't have to always have the devices loaded; we can just load them when we need them.
        This should eventually go into some kind of database
        '''
        # Try to discover devices
        devices = await Discover.discover()

        # If we don't find any, try again, waiting 5 seconds in between
        while len(devices) == 0:
            print("No devices found. Trying again in 5 seconds...")
            devices = await Discover.discover()
            sleep(5)

        data = {}

        for addr, device in devices.items():
            # We'll just store the alias and type so we know which address is which device + what type it is
            data[addr] = {
                "alias": device.alias,
                "type": device.hw_info.get("mic_type", None)
            }

        with open("cache.json", "w") as f:
            dump(data, f, indent=4)

    @staticmethod
    def get_cached_data():
        '''
        Get the cached addresses
        '''
        try:
            with open("cache.json", "r") as f:
                data = load(f)
    
            return data
        except:
            return {}

async def main():
    # We'll have a list of bulb managers
    # First, get the cached data
    data = BulbManager.get_cached_data()

    managers = [BulbManager(target) for target in data if data[target]["type"] == "IOT.SMARTBULB"]

    # Connect to all the bulbs
    for manager in managers:
        try:
            print(f"Connecting to {manager.target}...")
            await manager.connect()
            await manager.on()
            print(f"Connected.")
        except:
            print(f"Failed to connect to {manager.target}.")

    # Loop forever and set the bulbs to random colors
    while True:
        for i in range(len(managers)):
            try:
                if managers[i].connected:
                    hue = randint(0, 360)
                    value = randint(10, 30)
                    await managers[i].set_hsv(hue, 100, value, 1000)
            except SmartDeviceException:
                print(f"Failed to set {managers[i].target}.")
                managers[i].connected = False

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())