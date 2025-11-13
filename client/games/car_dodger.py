import pygame, random, sys

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("🚗 Car Dodger")
    clock = pygame.time.Clock()
    car = pygame.Rect(400,500,50,100)
    obstacles = []
    speed = 5
    score = 0
    font = pygame.font.SysFont(None,36)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return score
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car.left > 0: car.x -= 7
        if keys[pygame.K_RIGHT] and car.right < 800: car.x += 7

        if random.randint(1,20) == 1:
            x = random.randint(0,750)
            obstacles.append(pygame.Rect(x,-100,50,100))

        for o in obstacles:
            o.y += speed
            if o.y > 600:
                obstacles.remove(o)
                score += 1
            if o.colliderect(car):
                return score

        screen.fill((40,40,40))
        pygame.draw.rect(screen, (0,255,0), car)
        for o in obstacles:
            pygame.draw.rect(screen, (255,0,0), o)
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))
        pygame.display.flip()
        clock.tick(30)
