# Import required libraries
import pygame  # For rendering and handling game events
import random  # For generating random fruit positions
import numpy as np  # For Q-learning calculations (e.g. argmax, max)
import pickle  # For saving/loading the Q-table
import time  # To control rendering speed (for visualization)
random.seed(42)

# Define the Snake Environment class
class SnakeEnv:
    def __init__(self, grid_size=30, cell_size=25, render_mode=False):
        pygame.init()  # Initialize pygame module
        self.grid_size = grid_size  # Grid size (number of cells in one row/column)
        self.cell_size = cell_size  # Size of each grid cell in pixels
        self.render_mode = render_mode  # Whether to visually render the game
        self.screen = pygame.display.set_mode((grid_size * cell_size, grid_size * cell_size))  # Pygame display window
        pygame.display.set_caption("Silly Audie - Q-Learning Snake")  # Title of the window
        self.clock = pygame.time.Clock()  # Clock to manage game frame 

        # Define colors used for rendering
        self.bg_cell_color = (128, 192, 255)  # Checkerboard background color 1
        self.bg_cell_color2 = (118, 182, 245)  # Checkerboard background color 2
        self.snake_color = (0, 200, 0)  # Color of snake body
        self.head_color = (0, 135,0 )  # Color of snake head
        self.fruit_color = (255, 0, 0)  # Color of the fruit

        self.reset()  # Initialize/reset the environment

    def reset(self):
        initial_length = 4
        head_x = self.grid_size // 2
        head_y = self.grid_size // 2
        self.snake = [(head_x, head_y + i) for i in range(initial_length)]# Start snake in center
        self.direction = (0, -1)  # Initial movement direction is up
        self.spawn_fruit()  # Place the first fruit
        self.done = False  # Game is not over
        self.score = 0 # Initialize score
        self.steps = 0  # Step counter
        return self.get_state()  # Return the initial state

    def spawn_fruit(self):
        # Keep generating a new fruit position until it does not collide with the snake
        while True:
            self.fruit = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if self.fruit not in self.snake:
                break

    def step(self, action):
        if self.done:
            return self.get_state(), 0, self.done  # Return if the game is already over

        self.change_direction(action)  # Update the snake's direction based on action
        new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        # Check for collision with self or walls
        if (new_head in self.snake or
            not 0 <= new_head[0] < self.grid_size or
            not 0 <= new_head[1] < self.grid_size):
            self.done = True
            return self.get_state(), -100, self.done  # Negative reward for dying

        # Distance to fruit before moving
        old_dist = abs(self.snake[0][0] - self.fruit[0]) + abs(self.snake[0][1] - self.fruit[1])

        self.snake.insert(0, new_head)  # Move head

        # Distance to fruit after moving
        new_dist = abs(new_head[0] - self.fruit[0]) + abs(new_head[1] - self.fruit[1])

        # Base reward
        if new_head == self.fruit:  # Fruit eaten
            self.score += 1
            self.spawn_fruit()
            reward = 10  # Positive reward
        else:
            self.snake.pop()  # Remove tail (normal movement)
            reward = -0.1  # Small penalty to encourage faster fruit collection

        # Reward shaping: give small positive reward for getting closer to fruit
        if new_dist < old_dist:
            reward += 0.3
        elif new_dist > old_dist:
            reward -= 0.4

        self.steps += 1
        return self.get_state(), reward, self.done

    def change_direction(self, action):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        idx = directions.index(self.direction)  # Current direction index
        if action == 0:
            self.direction = directions[(idx - 1) % 4]  # Turn left
        elif action == 2:
            self.direction = directions[(idx + 1) % 4]  # Turn right
        # action == 1: continue straight (no change)

    def get_state(self):
        head_x, head_y = self.snake[0]  # Current head position
        dir_x, dir_y = self.direction  # Current direction

        # Check danger in 3 directions
        danger_straight = self.check_collision((dir_x, dir_y))
        danger_left = self.check_collision((-dir_y, dir_x))
        danger_right = self.check_collision((dir_y, -dir_x))

        # Fruit location relative to head
        fruit_left = self.fruit[0] < head_x
        fruit_right = self.fruit[0] > head_x
        fruit_up = self.fruit[1] < head_y
        fruit_down = self.fruit[1] > head_y

        # Include direction in state
        direction_state = [dir_x, dir_y]

        return tuple([danger_straight, danger_left, danger_right, fruit_left, fruit_right, fruit_up, fruit_down] + direction_state)

    def check_collision(self, dir):
        # Predict next position
        new_x = self.snake[0][0] + dir[0]
        new_y = self.snake[0][1] + dir[1]
        # Collision if out of bounds or hits itself
        if (new_x, new_y) in self.snake or not (0 <= new_x < self.grid_size) or not (0 <= new_y < self.grid_size):
            return 1
        return 0

    def render(self, title=None):
        # Fill background with base color
        self.screen.fill(self.bg_cell_color2)
        # Draw checkerboard pattern
        for y in range(self.grid_size):
            for x in range((y + 1) % 2, self.grid_size, 2):
                pygame.draw.rect(self.screen, self.bg_cell_color,
                                 (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

        # Draw fruit
        fx, fy = self.fruit
        pygame.draw.rect(self.screen, self.fruit_color,
                         (fx * self.cell_size, fy * self.cell_size, self.cell_size, self.cell_size))

        # Draw snake (head has different color)
        for i, (x, y) in enumerate(self.snake):
            color = self.head_color if i == 0 else self.snake_color
            pygame.draw.rect(self.screen, color,
                             (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

        if title:
            pygame.display.set_caption(title)  # Update window title
        pygame.display.update()  # Update display with new frame
        self.clock.tick(120)  # Cap rendering to 15 FPS

    def close(self):
        pygame.quit()  # Clean up pygame

# Only run this block when executing the file directly
if __name__ == '__main__':
    #rdm rdv
    env = SnakeEnv(render_mode=False)  # Create environment with rendering enabled
    # Q-table for storing state-action values
    start_episode = 0  # Default
    try:
        with open("q_table.pkl", "rb") as f:
            data = pickle.load(f)
            q_table = data.get("q_table", {})
            start_episode = data.get("episode", 0)
            epsilon = data.get("epsilon", 1.0)
        print(f"Q-table loaded successfully. Resuming from episode {start_episode}.")
    except FileNotFoundError:
        q_table = {}
        start_episode = 0
        epsilon = 1.0
        print("No saved Q-table found, starting fresh.")
    episodes = 900  # Number of episodes to train
    alpha = 0.1  # Learning rate
    gamma = 0.9  # Discount factor
    doExplore = True
    if doExplore ==False:
        epsilon =0
        epsilon_decay = 0.995  # Decay rate for exploration
        epsilon_min = 0.00  # Minimum exploration threshold
    else:
        #epsilon = 1.0  # Initial exploration rate
        epsilon_decay = 0.995  # Decay rate for exploration
        epsilon_min = 0.01  # Minimum exploration threshold

    max_score = float('-inf')
    min_score = float('inf')
    recentscore = []

    actions = [0, 1, 2]  # 0 = left, 1 = straight, 2 = right

    for ep in range(start_episode, start_episode + episodes):
        state = env.reset()  # Start a new episode
        done = False  # Whether the game is over
        total_reward = 0  # Accumulate rewards for reporting

        while not done:
            for event in pygame.event.get(): # Allow quitting during training
                if event.type == pygame.QUIT:
                    print("Quitting and saving Q-table...")
                    with open("q_table.pkl", "wb") as f:
                        pickle.dump({
                            "q_table": q_table,
                            "episode": ep + 1,
                            "epsilon": epsilon
                        }, f)
                    pygame.quit()
                    exit()
            if state not in q_table:
                q_table[state] = [0, 0, 0]  # Initialize Q-values if unseen state

            if random.random() < epsilon:
                action = random.choice(actions)  # Explore
            else:
                action = np.argmax(q_table[state])  # Exploit

            next_state, reward, done = env.step(action)  # Perform action

            if next_state not in q_table:
                q_table[next_state] = [0, 0, 0]  # Initialize next state if unseen

            # Update Q-value using Bellman equation
            if done:
                target = reward
            else:
                target = reward + gamma * max(q_table[next_state])

            q_table[state][action] += alpha * (target - q_table[state][action])

            state = next_state  # Move to next state
            total_reward += reward  # Update total reward

            # Visualize current episode (optional)
            if env.render_mode:
                env.render(title=f"Episode: {ep+1}  Score: {env.score}")
                time.sleep(0.00003)  # Slow down visualization

        # Decay exploration rate
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        max_score = max(max_score, env.score)
        recentscore.append(env.score)  # or total_reward if you prefer
        # Keep only the last 100 scores
        if len(recentscore) > 100:
            recentscore.clear()
        try:
            last100score = int(sum(recentscore) / len(recentscore))
        except:
            pass
        print(f"Episode {ep+1},fruit {env.score} ,  Total Reward: {total_reward}, Epsilon: {epsilon:.3f}, Highest: {max_score}, last 100: {last100score}")

    # Save Q-table to file
    with open("q_table.pkl", "wb") as f:
        pickle.dump({
            "q_table": q_table,
            "episode": ep + 1,
            "epsilon": epsilon
        }, f)


    env.close()  # Close pygame window
