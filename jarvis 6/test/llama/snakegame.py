# Import required libraries
import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
FPS = 10
GRID_SIZE = 20

# Set up some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Set up the font
font = pygame.font.SysFont("Arial", 30)

# Set up the clock
clock = pygame.time.Clock()

# Set up the snake
class Snake:
    def __init__(self):
        self.body = [(200, 200), (220, 200), (240, 200)]
        self.direction = "RIGHT"

    def move(self):
        if self.direction == "RIGHT":
            new_head = (self.body[-1][0] + GRID_SIZE, self.body[-1][1])
        elif self.direction == "LEFT":
            new_head = (self.body[-1][0] - GRID_SIZE, self.body[-1][1])
        elif self.direction == "UP":
            new_head = (self.body[-1][0], self.body[-1][1] - GRID_SIZE)
        elif self.direction == "DOWN":
            new_head = (self.body[-1][0], self.body[-1][1] + GRID_SIZE)

        self.body.append(new_head)
        self.body.pop(0)

    def change_direction(self, new_direction):
        if new_direction != "RIGHT" and new_direction != "LEFT":
            new_direction = "UP" if new_direction == "DOWN" else "DOWN"
        self.direction = new_direction

# Set up the snake
snake = Snake()

# Set up the apple
class Apple:
    def __init__(self):
        self.position = (random.randint(0, WIDTH - GRID_SIZE) // GRID_SIZE * GRID_SIZE,
                         random.randint(0, HEIGHT - GRID_SIZE) // GRID_SIZE * GRID_SIZE)

    def move(self):
        self.position = (random.randint(0, WIDTH - GRID_SIZE) // GRID_SIZE * GRID_SIZE,
                         random.randint(0, HEIGHT - GRID_SIZE) // GRID_SIZE * GRID_SIZE)

# Set up the apple
apple = Apple()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != "DOWN":
                snake.change_direction("UP")
            elif event.key == pygame.K_DOWN and snake.direction != "UP":
                snake.change_direction("DOWN")
            elif event.key == pygame.K_LEFT and snake.direction != "RIGHT":
                snake.change_direction("LEFT")
            elif event.key == pygame.K_RIGHT and snake.direction != "LEFT":
                snake.change_direction("RIGHT")

    # Move the snake
    snake.move()

    # Check for collision with apple
    if snake.body[-1] == apple.position:
        apple.move()
    else:
        # Check for collision with boundary or itself
        if (snake.body[-1][0] < 0 or snake.body[-1][0] >= WIDTH or
            snake.body[-1][1] < 0 or snake.body[-1][1] >= HEIGHT or
            snake.body[-1] in snake.body[:-1]):
            pygame.quit()
            sys.exit()

    # Draw everything
    win.fill(BLACK)
    for pos in snake.body:
        pygame.draw.rect(win, GREEN, (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(win, RED, (apple.position[0], apple.position[1], GRID_SIZE, GRID_SIZE))
    pygame.display.update()

    # Cap the frame rate
    clock.tick(FPS)