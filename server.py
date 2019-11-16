import random
from typing import Dict
from bottle import *
from simulator import Simulator, RoomGraphSimulator, CellMoveSimulator, Simulator2

simulators: Dict[int, Simulator] = {}


@get('/')
def index():
    return static_file('index.html', './static')


@get('/<filename>')
def file(filename):
    return static_file(filename, './static')


@post('/init')
def init():
    data = request.json
    seed = data.get('seed', None)
    mode = data['mode']
    if seed is not None:
        random.seed(seed)

    if mode == 1:
        simulator = RoomGraphSimulator()
    elif mode == 2:
        simulator = CellMoveSimulator()
    else:
        simulator = Simulator2()
    simulators[id(simulator)] = simulator
    return {'id': id(simulator)}


@get('/info/<_id:int>')
def get_dungeon_info(_id: int = -1):
    if simulators.get(_id, None) is None:
        return {}
    return simulators[_id].info()


@post('/action/<_id:int>')
def action(_id: int):
    data = request.json
    reward = simulators[_id].action(data['action'])
    info = simulators[_id].info()
    info['reward'] = reward
    return info


@post('/reset/<_id:int>')
def reset(_id: int):
    simulators[_id].reset()


if __name__ == '__main__':
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
