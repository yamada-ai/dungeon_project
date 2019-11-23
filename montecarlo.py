import time

from simulator import *
import random
import numpy as np
import pickle


def select_action1(actions, eps):
    a = random.random()
    if a <= eps:
        return random.randint(0, len(actions)-1)
    return actions.argmax()


def learn_room_move():
    q = np.random.random((5, 5))
    eps = [0.99]*5
    sum_r = [[0.0]*5 for _ in range(5)]
    sum_c = [[0]*5 for _ in range(5)]

    log = []
    random.seed(0)
    sim = RoomGraphSimulator()
    random.seed()

    for step in range(100):
        state = sim.info()
        is_end = False
        sum_reward = 0
        while not is_end:
            action = select_action1(q[state['roomId']], eps[state['roomId']])
            eps[state['roomId']] *= eps[state['roomId']]
            log.append((
                state['roomId'],
                action
            ))
            reward = sim.action(int(action))
            next_state = sim.info()
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
        sim.reset()
    destination_room = [int(e.argmax()) for e in q]
    destination_room[sim.goal_room_id] = -1
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
    q1 = np.array(learn_room_move())
    print(q1)
    # alpha = 0.1
    # gamma = 0.8
    q = np.random.random((5, 13, 12, 5, 5, 5, 5, 5))
    # q = np.zeros((5, 13, 12, 5, 5, 5, 5, 5))
    eps = np.full((5, 13, 12, 5, 5, 5, 5), 0.99)
    sum_r = np.zeros((5, 13, 12, 5, 5, 5, 5, 5))
    sum_c = np.zeros((5, 13, 12, 5, 5, 5, 5, 5), dtype=np.int64)
    random.seed(0)
    dungeon = Dungeon(30, 40)
    with open('dungeon.dump', 'wb') as file: 
        pickle.dump(dungeon, file)
    sim = CellMoveSimulator({}, dungeon=dungeon)
    t = Simulator2({}, dungeon=dungeon)
    random.seed()

    max_step = 200000

    # log = set()
    log = []

    file = open('log.csv', 'w')
    for step in range(max_step):
        state = sim.info()
        e = enemy(state)
        sum_reward = 0
        episode_reward = 0
        turn = 0
        while not state['isEnd']:
            # print(state['roomId'], state['x'], state['y'], '\r', end='')
            action = select_action(q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]], eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]])
            action = int(action)
            eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]] *= 0.999
            # log.add((
            #     state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1],
            #     action
            # ))
            log.append((
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
            # q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1], action] = (1.0-alpha)*q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1], action] + alpha*(reward + gamma*q[next_state['roomId'], next_state['x'], next_state['y'], e2[0][0], e2[0][1], e2[1][0], e2[1][1]].max())
            # if reward < -1 or 0 < reward:
            #     for rule in log:
            #         # print(rule)
            #         sum_r[rule] += sum_reward
            #         sum_c[rule] += 1
            #         q[rule] = sum_r[rule] / sum_c[rule]
            #     log.clear()
            #     episode_reward += sum_reward
            #     sum_reward = 0
            state = next_state
            e = e2
            turn += 1
        for rule in log:
            # print(rule)
            sum_r[rule] += sum_reward
            sum_c[rule] += 1
            q[rule] = sum_r[rule] / sum_c[rule]
        log.clear()
        sim.reset()
        # print(step, '/', max_step, 'reward:', episode_reward, 'turn:', turn)
        print(step, '/', max_step, 'reward:', sum_reward, 'turn:', turn)
        file.write(f'{step},{sum_reward},{turn}\n')
        if step % (max_step // 10) == 0:
            test(t, q)

    np.save('q_table1.npy', q1)
    np.save('q_table2.npy', q)
    file.close()

    for _ in range(15):
        test(t, q)
        time.sleep(1)


def load():
    q1 = np.load('q_table1.npy')
    q = np.load('q_table2.npy')
    random.seed(0)
    sim = Simulator2({})
    for _ in range(5):
        test(sim, q)
        time.sleep(1)


if __name__ == '__main__':
    main()
    # load()
