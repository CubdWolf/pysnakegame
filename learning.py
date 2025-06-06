import numpy as np
import random

# Environment has 10 states and 4 actions
Q = np.zeros((10, 4))  # Q-table

alpha = 0.1    # learning rate
gamma = 0.9    # discount factor
epsilon = 0.1  # exploration chance

for episode in range(1000):
    state = env.reset()
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()  # Explore
        else:
            action = np.argmax(Q[state])        # Exploit

        next_state, reward, done, _ = env.step(action)

        Q[state, action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[state, action])
        state = next_state