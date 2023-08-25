import asyncio
from json import dump, load
from kasa import SmartBulb
from kasa.discover import Discover
from random import randint
from time import sleep
from typing import Optional

class BulbManager:
    '''
    Class for managing a single bulb
    We'll have more advanced functionality in the future but for now it just wraps functions from the library
    '''
    def __init__(self, target: str):
        self.target: str = target
        self.device: Optional[SmartBulb] = None
        self.connected: bool = False

    async def connect(self):
        self.device = await BulbManager.get_device(self.target)
        await self.device.update()
        self.connected = True

    async def off(self):
        await self.device.turn_off()

    async def on(self):
        await self.device.turn_on()

    async def set_hsv(self, hue: int, saturation: int, value: Optional[int] = None, transition: Optional[int] = None):
        await self.device.set_hsv(hue, saturation, value, transition=transition)

        # We need to sleep for the transition time
        # If not, the bulb becomes unresponsive and future connection attempts fail (not sure exactly why)
        if transition is not None:
            sleep(transition / 1000)

    @staticmethod
    async def get_device(target: str):
        # We'll have the target address passed in to make it easier since discover is finicky
        # In the future, maybe we'll have cached device addresses
        devices = await Discover.discover(target=target)

        return devices[target]
    
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
            # We'll just store the alias so we know which address is which device
            data[addr] = device.alias

        with open("cache.json", "w") as f:
            dump(data, f, indent=4)

    @staticmethod
    def get_cached_data():
        '''
        Get the cached addresses
        '''
        with open("cache.json", "r") as f:
            data = load(f)

        return data

async def main():
    # We'll have a list of bulb managers
    # First, get the cached data
    data = BulbManager.get_cached_data()

    managers = [BulbManager(target) for target in data]

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
        for manager in managers:
            if manager.connected:
                hue = randint(0, 360)
                await manager.set_hsv(hue, 100, 100)

        sleep(0.1)
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())