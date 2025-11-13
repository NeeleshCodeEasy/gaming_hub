import pygame, random, sys

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("🐍 Snake Game")
    clock = pygame.time.Clock()

    snake = [(100,100)]
    direction = (20,0)
    food = (200,200)
    score = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return score
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: direction = (0,-20)
                if e.key == pygame.K_DOWN: direction = (0,20)
                if e.key == pygame.K_LEFT: direction = (-20,0)
                if e.key == pygame.K_RIGHT: direction = (20,0)

        new_head = (snake[0][0]+direction[0], snake[0][1]+direction[1])

        if new_head in snake or not (0 <= new_head[0] < 800) or not (0 <= new_head[1] < 600):
            return score

        snake.insert(0, new_head)
        if new_head == food:
            score += 10
            food = (random.randrange(0,800,20), random.randrange(0,600,20))
        else:
            snake.pop()

        screen.fill((0,0,0))
        for s in snake:
            pygame.draw.rect(screen, (0,255,0), (*s,20,20))
        pygame.draw.rect(screen, (255,0,0), (*food,20,20))
        pygame.display.flip()
        clock.tick(10)
