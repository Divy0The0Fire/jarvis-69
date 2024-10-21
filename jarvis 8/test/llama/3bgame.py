import pygame
import sys
import random
import time

# Game Variables
direction = 'RIGHT'
score = 0
block_size = 20
grid_size = 20
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
food_pos = [random.randrange(1, (grid_size * block_size)) * block_size, random.randrange(1, (grid_size * block_size)) * block_size]
directions = {'UP': (0, -block_size), 'DOWN': (0, block_size), 'LEFT': (-block_size, 0), 'RIGHT': (block_size, 0)}

# Pygame Initialization
pygame.init()
pygame.display.set_caption('Snake Game')
screen = pygame.display.set_mode((grid_size * block_size, grid_size * block_size))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                direction = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                direction = 'DOWN'
            elif event.key == pygame.K_LEFT and direction != 'LEFT':
                direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'RIGHT':
                direction = 'RIGHT'

    # Move the snake
    for i in range(len(snake_body) - 1, 0, -1):
        snake_body[i] = snake_body[i - 1]
    if direction == 'UP':
        snake_body[0] = [snake_body[0][0], snake_body[0][1] - block_size]
    elif direction == 'DOWN':
        snake_body[0] = [snake_body[0][0], snake_body[0][1] + block_size]
    elif direction == 'LEFT':
        snake_body[0] = [snake_body[0][0] - block_size, snake_body[0][1]]
    elif direction == 'RIGHT':
        snake_body[0] = [snake_body[0][0] + block_size, snake_body[0][1]]

    # Check collision with food
    if snake_body[0] == food_pos:
        score += 1
        food_pos = [random.randrange(1, (grid_size * block_size)) * block_size, random.randrange(1, (grid_size * block_size)) * block_size]
    else:
        snake_body.pop()

    # Check collision with walls or itself
    if (snake_body[0][0] < 0 or snake_body[0][0] >= grid_size * block_size or
        snake_body[0][1] < 0 or snake_body[0][1] >= grid_size * block_size or
        snake_body[0] in snake_body[1:]):
        print("Game Over! Your score is:", score)
        pygame.quit()
        sys.exit()

    # Draw everything
    screen.fill((0, 0, 0))
    for pos in snake_body:
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pos[0], pos[1], block_size, block_size))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food_pos[0], food_pos[1], block_size, block_size))
    pygame.display.update()

    # Cap the frame rate
    clock.tick(10)
