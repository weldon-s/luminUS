import asyncio
from kasa import SmartBulb
from kasa.discover import Discover
from random import randint
from time import sleep
from typing import Optional

TARGETS = ["10.0.0.218", "10.0.0.122", "10.0.0.62", "10.0.0.128", "10.0.0.237", "10.0.0.52"]

class BulbManager:
    '''
    Class for managing a single bulb
    We'll have more advanced functionality in the future but for now it just wraps functions from the library
    '''
    def __init__(self, target: str):
        self.target: str = target
        self.device: Optional[SmartBulb] = None

    async def connect(self):
        self.device = await BulbManager.get_device(self.target)
        await self.device.update()

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

async def main():
    # We'll have a list of bulb managers
    managers = [BulbManager(target) for target in TARGETS]

    # Connect to all the bulbs
    for manager in managers:
        print(f"Connecting to {manager.target}...")
        await manager.connect()
        await manager.on()
        print(f"Connected.")

    # Loop forever and set the bulbs to random colors
    while True:
        for manager in managers:
            hue = randint(0, 360)

            await manager.set_hsv(hue, 100, 100)

        sleep(0.1)
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())