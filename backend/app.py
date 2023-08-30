from flask import Flask
from flask_cors import CORS
from typing import Awaitable

from lighting.bulb import BulbManager

bulbs: dict[str, BulbManager] = {}

app = Flask(__name__)
CORS(app)

@app.route('/<target>/new')
async def new(target):
    bulbs[target] = BulbManager(target)

    await bulbs[target].connect()

    if bulbs[target].connected:
        return {"success": True, "message": "success"}
    
    return {"success": False, "message": "failed to connect"}


@app.route('/<target>/on')
async def on(target):
    if target not in bulbs:
        return {"success": False, "message": "not connected"}
    
    return await _wrap_action(bulbs[target].on())

@app.route('/<target>/off')
async def off(target):
    if target not in bulbs:
        return {"success": False, "message": "not connected"}

    return await _wrap_action(bulbs[target].off())


@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>')
@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>/<int:value>')
@app.route('/<target>/set_hsv/<int:hue>/<int:saturation>/<int:value>/<int:transition>')
async def set_hsv(target, hue, saturation, value=None, transition=None):
    if target not in bulbs:
        return {"success": False, "message": "not connected"}

    return await _wrap_action(bulbs[target].set_hsv(hue, saturation, value=value, transition=transition))

@app.route('/<target>/start_random/<int:interval>')
def start_random(target, interval):
    if target not in bulbs:
        return {"success": False, "message": "not connected"}

    bulbs[target].start_random([[0, 100], [120, 100], [240, 100]], interval)
    return {"success": True, "message": "success"}

@app.route('/<target>/stop_random')
async def stop_random(target):
    if target not in bulbs:
        return {"success": False, "message": "not connected"}

    bulbs[target].stop_random()
    return {"success": True, "message": "success"}

@app.route('/discover_all')
async def discover_all():
    await BulbManager.populate_cache()
    return _processed_cached_data()


@app.route('/get_all')
def get_all():
    return _processed_cached_data()

def _processed_cached_data():
    cached = BulbManager.get_cached_data()

    for target in cached:
        # mark if the bulb is connected
        cached[target]["connected"] = target in bulbs

    return cached

async def _wrap_action(action: Awaitable):
    '''
    Wraps an async action in a try/catch block and get a return value to be sent back to the client
    '''
    try:
        await action
        return {"success": True, "message": "success"}
    except:
        return {"success": False, "message": "failed"}