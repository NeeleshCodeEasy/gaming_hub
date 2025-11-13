import pygame, sys, random

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("🐤 Flappy Bird")
    clock = pygame.time.Clock()
    gravity = 0.5
    bird_y = 300
    velocity = 0
    pipes = []
    for i in range(3):
        x = 800 + i*300
        h = random.randint(150,400)
        pipes.append([x,h])
    score = 0
    font = pygame.font.SysFont(None,36)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return score
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                velocity = -8

        velocity += gravity
        bird_y += velocity

        for p in pipes:
            p[0] -= 5
            if p[0] < -80:
                p[0] = 800
                p[1] = random.randint(150,400)
                score += 1

        screen.fill((135,206,235))
        for p in pipes:
            pygame.draw.rect(screen, (0,200,0), (p[0], 0, 80, p[1]-100))
            pygame.draw.rect(screen, (0,200,0), (p[0], p[1]+100, 80, 600))
        pygame.draw.circle(screen, (255,255,0), (100, int(bird_y)), 20)
        screen.blit(font.render(f"Score: {score}", True, (0,0,0)), (10,10))
        pygame.display.flip()

        if bird_y > 600 or bird_y < 0:
            return score
        for p in pipes:
            if 80 < p[0] < 120 and not (p[1]-100 < bird_y < p[1]+100):
                return score
        clock.tick(30)
