import time

from simulator import *
import random
import numpy as np
import pickle
import sys


def select_action1(actions, eps):
    a = random.random()
    if a <= eps:
        return random.randint(0, len(actions)-1)
    return actions.argmax()


def learn_room_move(simulator):
    q = np.random.random((5, 5))
    eps = [0.99]*5
    sum_r = [[0.0]*5 for _ in range(5)]
    sum_c = [[0]*5 for _ in range(5)]

    log = []

    for step in range(100):
        state = simulator.info()
        is_end = False
        sum_reward = 0
        while not is_end:
            action = select_action1(q[state['roomId']], eps[state['roomId']])
            eps[state['roomId']] *= eps[state['roomId']]
            log.append((
                state['roomId'],
                action
            ))
            reward = simulator.action(int(action))
            next_state = simulator.info()
            sum_reward += reward
            if reward != 0:
                for rule in log:
                    sum_r[rule[0]][rule[1]] += sum_reward
                    sum_c[rule[0]][rule[1]] += 1
                    q[rule[0]][rule[1]] = sum_r[rule[0]][rule[1]] / sum_c[rule[0]][rule[1]]
                    log.clear()
                    sum_reward = 0
            if reward == 100:
                is_end = True
            state = next_state
        simulator.reset()
    destination_room = [int(e.argmax()) for e in q]
    destination_room[simulator.goal_room_id] = -1
    return destination_room


def enemy(state):
    out = []
    for e in state['enemies']:
        if e['x'] != -1 and e['y'] != -1:
            x = e['x'] - state['x']
            y = e['y'] - state['y']
            if -2 <= x <= 2 and -2 <= y <= 2:
                out.append((
                    x + 2,
                    y + 2
                ))
    while len(out) < 2:
        out.append((2, 2))
    return out


def select_action(q, eps):
    r = random.random()
    if r < eps:
        return random.randint(0, 4)
    return q.argmax()


def test(sim, q):
    state = sim.info()
    e = enemy(state)
    while not state['isEnd']:
        action = select_action(q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]], 0)

        sim.action(int(action))
        next_state = sim.info()
        e2 = enemy(next_state)

        state = next_state
        e = e2
    sim.reset()


def main():
    random.seed(0)
    dungeon = Dungeon(30, 40)
    with open('dungeon.dump', 'wb') as file: 
        pickle.dump(dungeon, file)
    room_graph_simulator = RoomGraphSimulator(dungeon)
    q1 = np.array(learn_room_move(room_graph_simulator))
    q = np.random.random((5, 13, 12, 5, 5, 5, 5, 5))
    eps = np.full((5, 13, 12, 5, 5, 5, 5), 0.99)
    sum_r = np.zeros((5, 13, 12, 5, 5, 5, 5, 5))
    sum_c = np.zeros((5, 13, 12, 5, 5, 5, 5, 5), dtype=np.int64)
    sim = CellMoveSimulator({}, dungeon=dungeon)
    t = Simulator2({}, dungeon=dungeon)
    random.seed()

    max_step = 400000

    log = set()

    file = open(sys.argv[1], 'w')
    for step in range(max_step):
        state = sim.info()
        e = enemy(state)
        sum_reward = 0
        episode_reward = 0
        turn = 0
        while not state['isEnd']:
            action = select_action(q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]], eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]])
            action = int(action)
            eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]] *= 0.999
            log.add((
                state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1],
                action
            ))

            reward = sim.action({'action': action, 'nextRoomId': q1[state['roomId']]})
            next_state = sim.info()
            e2 = enemy(next_state)

            if reward == -1:
                sum_reward += 0.1*reward
            else:
                sum_reward += reward
            state = next_state
            e = e2
            turn += 1
        for rule in log:
            sum_r[rule] += sum_reward
            sum_c[rule] += 1
            q[rule] = sum_r[rule] / sum_c[rule]
        log.clear()
        sim.reset()
        print(step, '/', max_step, 'reward:', sum_reward, 'turn:', turn)
        file.write(f'{step},{sum_reward},{turn}\n')
        if step % (max_step // 10) == 0:
            test(t, q)

    np.save(sys.argv[2], q1)
    np.save(sys.argv[3], q)
    file.close()

    for _ in range(15):
        test(t, q)
        time.sleep(1)


def load(dungeon, q_table_1, q_table_2, num_episodes):
    with open(dungeon, 'rb') as f:
        dungeon = pickle.load(f)
    q1 = np.load(q_table_1)
    q = np.load(q_table_2)
    sim = Simulator2({}, dungeon)
    for _ in range(num_episodes):
        test(sim, q)
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('invalid parameters')
        print('montecarlo2.py log_file_name q_table1_file_name q_table2_file_name')
        sys.exit(1)
    if len(sys.argv) == 5:
        load(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        sys.exit(0)
    main()
