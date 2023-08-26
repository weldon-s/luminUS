import asyncio
from flask import Flask
from lighting.bulb import BulbManager

bulbs: dict[str, BulbManager] = {}

app = Flask(__name__)

@app.route('/<target>/new')
async def new(target):
    bulbs[target] = BulbManager(target)

    await bulbs[target].connect()

    return "success"

@app.route('/<target>/on')
async def on(target):
    if target not in bulbs:
        return "not connected"
    
    await bulbs[target].on()

    return "success"

@app.route('/<target>/off')
async def off(target):
    if target not in bulbs:
        return "not connected"
    
    await bulbs[target].off()

    return "success"

@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>')
@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>/<int:value>')
@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>/<int:value>/<int:transition>')
async def set_hsv(target, hue, saturation, value=None, transition=None):
    if target not in bulbs:
        return "not connected"
    
    await bulbs[target].set_hsv(hue, saturation, value=value, transition=transition)

    return "success"

@app.route('/discover_all')
async def discover_all():
    await BulbManager.populate_cache()
    return BulbManager.get_cached_data()

@app.route('/get_all')
def get_all():
    return BulbManager.get_cached_data()