from typing import Dict
from bottle import *
from simulator import Simulator

simulators: Dict[int, Simulator] = {}


@get('/')
def index():
    return static_file('index.html', './static')


@get('/<filename>')
def file(filename):
    return static_file(filename, './static')


@get('/create')
def create_dungeon():
    simulator = Simulator(30, 40)
    simulators[id(simulator)] = simulator
    return {'id': id(simulator)}


@get('/info')
@get('/info/<_id:int>')
def get_dungeon_info(_id: int = -1):
    # デバッグ用
    if _id == -1:
        return {
            'simulators': [sim.dump2json() for sim in simulators.values()]
        }

    if simulators.get(_id, None) is None:
        return {}
    return simulators[_id].dump2json()


@post('/action/<_id:int>')
def action(_id: int):
    data = request.json
    simulators[_id].action(data['action'])
    return simulators[_id].dump2json()


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
