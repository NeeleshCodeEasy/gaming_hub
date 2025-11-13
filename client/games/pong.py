import pygame, sys, random

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("🏓 Pong")
    clock = pygame.time.Clock()

    ball = pygame.Rect(400,300,20,20)
    player = pygame.Rect(780,250,10,100)
    opponent = pygame.Rect(10,250,10,100)
    ball_speed = [5,5]
    player_speed = 0
    score = 0

    font = pygame.font.SysFont(None,36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: player_speed = -7
                if event.key == pygame.K_DOWN: player_speed = 7
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]: player_speed = 0

        ball.x += ball_speed[0]
        ball.y += ball_speed[1]
        player.y += player_speed

        if ball.top <= 0 or ball.bottom >= 600:
            ball_speed[1] *= -1
        if ball.left <= 0:
            score += 1
            ball.x, ball.y = 400,300
            ball_speed[0] *= random.choice([-1,1])
        if ball.right >= 800:
            return score
        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed[0] *= -1

        opponent.y = ball.y - 50

        screen.fill((30,30,30))
        pygame.draw.rect(screen, (255,255,255), player)
        pygame.draw.rect(screen, (255,255,255), opponent)
        pygame.draw.ellipse(screen, (255,0,0), ball)
        txt = font.render(f"Score: {score}", True, (200,200,200))
        screen.blit(txt, (10,10))

        pygame.display.flip()
        clock.tick(60)
