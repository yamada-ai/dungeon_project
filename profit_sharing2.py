import time

import numpy as np
import random

from Dungeon import Dungeon
from simulator import Simulator2, RoomGraphSimulator, CellMoveSimulator


def select_action(actions, eps):
    a = random.random()
    if a < eps:
        return random.randint(0, len(actions)-1)
    return actions.argmax()


def learn_room_move(simulator: RoomGraphSimulator):
    c_bid = 0.1
    q = np.random.random((5, 5))
    eps = np.full((5,), 0.99)

    for step in range(500):
        state = simulator.info()
        is_end = False
        sum_reward = 0
        rules = []
        while not is_end:
            action = select_action(q[state['roomId']], eps[state['roomId']])
            eps[state['roomId']] *= eps[state['roomId']]
            rules.append((state['roomId'], action))

            reward = simulator.action(int(action))
            next_state = simulator.info()
            sum_reward += reward

            if reward != 0:
                for rule in rules:
                    q[rule] = q[rule] + c_bid * (sum_reward - q[rule])
                sum_reward = 0

            if reward == 100:
                is_end = True
            state = next_state
        simulator.reset()

    destination_map = [int(s.argmax()) for s in q]
    destination_map[simulator.goal_room_id] = -1
    return destination_map


def enemy_state(state):
    result = []
    for e in state['enemies']:
        if e['x'] != -1 and e['y'] != -1:
            x = e['x'] - state['x']
            y = e['y'] - state['y']
            if -2 <= x <= 2 and -2 <= y <= 2:
                result.append((
                    x + 2,
                    y + 2
                ))
    while len(result) < 2:
        result.append((2, 2))
    return result


def state_tuple(state):
    e = enemy_state(state)
    return (
        state['roomId'],
        state['x'],
        state['y'],
        e[0][0],
        e[0][1],
        e[1][0],
        e[1][1]
    )


def test(simulator, q):
    state = simulator.info()
    while not state['isEnd']:
        s = state_tuple(state)
        action = select_action(q[s], 0)

        simulator.action(int(action))
        state = simulator.info()
    simulator.reset()


def main():
    c_bid = 0.1
    random.seed(0)
    dungeon = Dungeon(30, 40)
    random.seed()
    simulator1 = RoomGraphSimulator(dungeon)
    simulator2 = CellMoveSimulator({}, dungeon)
    simulator3 = Simulator2({}, dungeon)

    destination_map = learn_room_move(simulator1)
    print(destination_map)

    q = np.random.random((5, 13, 12, 5, 5, 5, 5, 5))
    eps = np.full((5, 13, 12, 5, 5, 5, 5), 0.99)

    max_step = 400000

    file = open('profit_sharing_log_0_.csv', "w")
    for step in range(max_step):
        state = simulator2.info()
        sum_reward = 0
        turn = 0
        rules = []
        while not state['isEnd']:
            s = state_tuple(state)
            action = int(select_action(q[s], eps[s]))
            eps[s] *= 0.99
            rules.append((*s, action))

            reward = simulator2.action({'action': action, 'nextRoomId': destination_map[state['roomId']]})
            if reward == -1:
                sum_reward += reward
            else:
                sum_reward += reward
            state = simulator2.info()
            turn += 1
        for rule in rules:
            q[rule] = q[rule] + c_bid * (sum_reward - q[rule])
        simulator2.reset()
        print(step, '/', max_step, 'reward:', sum_reward, 'turn:', turn)
        file.write(f'{step},{sum_reward},{turn}\n')
        if step % (max_step // 10) == 0:
            test(simulator3, q)
    file.close()
    
    np.save('q_table1_0_.npy', destination_map)
    np.save('q_table2_0_.npy', q)

    for _ in range(15):
        test(simulator3, q)
        time.sleep(1)


if __name__ == '__main__':
    main()
