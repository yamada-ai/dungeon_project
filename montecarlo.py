from simulator import *
import random
import numpy as np


def learnCellMove():
    random.seed(0)
    sim = CellMoveSimulator({})
    sim

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
    r = random.random();
    if r < eps:
        return random.randint(0, 4)
    return q.argmax()

def main():
    alpha = 0.1
    gamma = 0.8
    q = np.zeros((5, 13, 12, 5, 5, 5, 5, 5))
    eps = np.full((5, 13, 12, 5, 5, 5, 5), 0.99)
    # sum_r = np.zeros((5, 13, 12, 5, 5, 5, 5, 5))
    # sum_c = np.zeros((5, 13, 12, 5, 5, 5, 5, 5), dtype=np.int64)
    random.seed(0)
    sim = CellMoveSimulator({'firstRoom': 2})
    
    for _ in range(10000):
        state = sim.info()
        e = enemy(state)
        sum_reward = 0
        while not state['isEnd']:
            action = select_action(q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]], eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]]);
            eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]] *= eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]]

            reward = sim.action(int(action))
            next_state = sim.info()
            e2 = enemy(next_state)

            sum_reward += reward
            q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1], action] = (1.0-alpha)*q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1], action] + alpha*(reward + gamma*q[next_state['roomId'], next_state['x'], next_state['y'], e2[0][0], e2[0][1], e2[1][0], e2[1][1]].max())
            state = next_state
            e = e2
        sim.reset()
        print(sum_reward)

    random.seed(0)
    sim = Simulator2({'firstRoom': 2})
    state = sim.info()
    e = enemy(state)
    sum_reward = 0
    while not state['isEnd']:
        action = select_action(q[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]], eps[state['roomId'], state['x'], state['y'], e[0][0], e[0][1], e[1][0], e[1][1]]);

        reward = sim.action(int(action))
        next_state = sim.info()
        e2 = enemy(next_state)

        state = next_state
        e = e2


if __name__ == '__main__':
    main()
