import pygame, sys, threading, time, requests, socketio, random, math , time ,importlib, json, os

SERVER = "http://127.0.0.1:5000"
ASSETS = "assets/"
sio = socketio.Client()

# =====================================
# SOCKET EVENTS
# =====================================
@sio.event
def connect():
    print("Connected to chat server")

@sio.event
def message(data):
    print(f"[CHAT] {data.get('username')}: {data.get('msg')}")

def start_socket(username):
    sio.connect(SERVER)
    sio.emit('join', {'username': username, 'room': 'lobby'})

# =====================================
# API HELPERS
# =====================================
def register(username, password):
    r = requests.post(SERVER + "/register", json={'username': username, 'password': password})
    return r.json(), r.status_code

def login(username, password):
    r = requests.post(SERVER + "/login", json={'username': username, 'password': password})
    return r.json(), r.status_code

def submit_score(user_id, game, score):
    r = requests.post(SERVER + "/submit_score", json={'user_id': user_id, 'game': game, 'score': score})
    print("Score saved:", r.json())

def get_settings(user_id):
    r = requests.get(f"{SERVER}/settings/{user_id}")
    if r.status_code == 200:
        return r.json()
    return {}

def save_settings(user_id, settings):
    requests.post(f"{SERVER}/settings/{user_id}", json=settings)

# =====================================
# SETTINGS MENU
# =====================================
def settings_menu(user):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("⚙️ Settings")
    font = pygame.font.SysFont(None, 40)

    # Load or default
    user_settings = get_settings(user["user_id"])
    volume = user_settings.get("volume", 0.5)
    difficulty = user_settings.get("difficulty", "Medium")

    clock = pygame.time.Clock()
    selected = 0
    options = ["Volume", "Difficulty", "Save & Back"]

    click_sound = pygame.mixer.Sound(ASSETS + "click.wav")

    while True:
        screen.fill((25, 25, 35))
        title = font.render("⚙️ SETTINGS", True, (255, 255, 255))
        screen.blit(title, (300, 60))

        small_font = pygame.font.SysFont(None, 32)
        for i, option in enumerate(options):
            color = (0, 255, 120) if i == selected else (200, 200, 200)
            if option == "Volume":
                txt = small_font.render(f"Volume: {int(volume*100)}%", True, color)
            elif option == "Difficulty":
                txt = small_font.render(f"Difficulty: {difficulty}", True, color)
            else:
                txt = small_font.render(option, True, color)
            screen.blit(txt, (250, 200 + i*60))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    click_sound.play()
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    click_sound.play()
                if e.key == pygame.K_RIGHT:
                    if options[selected] == "Volume" and volume < 1:
                        volume += 0.1; pygame.mixer.music.set_volume(volume)
                    if options[selected] == "Difficulty":
                        difficulty = "Hard" if difficulty == "Medium" else "Medium"
                if e.key == pygame.K_LEFT:
                    if options[selected] == "Volume" and volume > 0:
                        volume -= 0.1; pygame.mixer.music.set_volume(volume)
                    if options[selected] == "Difficulty":
                        difficulty = "Medium" if difficulty == "Hard" else "Easy"
                if e.key == pygame.K_RETURN and options[selected] == "Save & Back":
                    new_settings = {"volume": round(volume,1), "difficulty": difficulty}
                    save_settings(user["user_id"], new_settings)
                    click_sound.play()
                    return

        pygame.display.flip()
        clock.tick(30)

# =====================================
# MAIN MENU
# =====================================
def show_menu(user):
    pygame.init()
    screen = pygame.display.set_mode((900,600))
    pygame.display.set_caption("🎮 Gaming Hub - Main Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Load sounds & music
    if os.path.exists(ASSETS + "menu_music.mp3"):
        pygame.mixer.music.load(ASSETS + "menu_music.mp3")
        # Try to load user's saved volume
        user_settings = get_settings(user["user_id"])
        vol = user_settings.get("volume", 0.5)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(-1)
    click_sound = pygame.mixer.Sound(ASSETS + "click.wav")

    games = ["pong", "snake", "flappy", "car_dodger", "settings", "exit"]
    selected = 0

    # Animated background: parallax layers + particles
    width, height = screen.get_size()

    # Parallax layers (simple colored rectangles moving at different speeds)
    layers = [
        {'y': 0, 'speed': 0.2, 'color': (8, 14, 24)},
        {'y': 0, 'speed': 0.5, 'color': (12, 22, 36)},
        {'y': 0, 'speed': 1.0, 'color': (18, 34, 56)},
    ]

    # particles
    particles = []
    for i in range(60):
        particles.append({
            'x': random.randint(0, width),
            'y': random.randint(0, height),
            'r': random.randint(1,3),
            'vx': random.uniform(-0.2, -1.0),
            'vy': random.uniform(-0.1, 0.1),
            'alpha': random.uniform(0.2, 0.9)
        })

    small_font = pygame.font.SysFont(None, 34)
    info_font = pygame.font.SysFont(None, 22)

    t0 = time.time()
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(games)
                    click_sound.play()
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(games)
                    click_sound.play()
                if event.key == pygame.K_RETURN:
                    click_sound.play()
                    if games[selected] == "exit":
                        pygame.quit(); sys.exit()
                    elif games[selected] == "settings":
                        settings_menu(user)
                        # update music volume after settings change
                        s = get_settings(user["user_id"])
                        pygame.mixer.music.set_volume(s.get("volume", 0.5))
                    else:
                        game_module = importlib.import_module(f"games.{games[selected]}")
                        score = game_module.run_game()
                        submit_score(user['user_id'], games[selected], score)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # move parallax layers vertically (subtle up/down)
        for i,layer in enumerate(layers):
            layer['y'] += layer['speed'] * dt * 20 * (1 + 0.2*i)
            if layer['y'] > height:
                layer['y'] = -height

        # update particles
        for p in particles:
            p['x'] += p['vx'] * 60 * dt
            p['y'] += p['vy'] * 60 * dt
            if p['x'] < -10:
                p['x'] = width + 10
                p['y'] = random.randint(0, height)
                p['vx'] = random.uniform(-0.2, -1.0)
            if p['y'] < -10 or p['y'] > height + 10:
                p['y'] = random.randint(0, height)

        # draw background
        screen.fill((10, 12, 20))
        # draw layered bands
        for idx,layer in enumerate(layers):
            rect_h = int(height * (0.3 + 0.05*idx))
            y = int((layer['y']) % height) - rect_h
            # draw twice for continuous motion
            pygame.draw.rect(screen, layer['color'], (0, y, width, rect_h))
            pygame.draw.rect(screen, layer['color'], (0, y + rect_h + 20, width, rect_h))

        # draw subtle glow circles
        elapsed = time.time() - t0
        glow_x = int(width * 0.75 + (math.sin(elapsed*0.6) * 60))
        glow_y = int(height * 0.25 + (math.cos(elapsed*0.4) * 20))
        pygame.draw.circle(screen, (7,90,80,40), (glow_x, glow_y), 120, 0)

        # draw particles
        for p in particles:
            surf = pygame.Surface((p['r']*2, p['r']*2), pygame.SRCALPHA)
            alpha = int(255 * p['alpha'])
            pygame.draw.circle(surf, (255,255,255,alpha), (p['r'], p['r']), p['r'])
            screen.blit(surf, (int(p['x']), int(p['y'])))

        # draw title
        title = font.render("🎮 Gaming Hub", True, (230, 250, 240))
        screen.blit(title, (40, 40))

        # menu list
        for i, g in enumerate(games):
            x = 60
            y = 160 + i*54
            is_selected = (i == selected)
            color = (0,220,140) if is_selected else (200,200,200)
            txt = small_font.render(f"{i+1}. {('⚙️ Settings' if g=='settings' else '❌ Exit' if g=='exit' else g.title())}", True, color)
            # slightly float selected item
            if is_selected:
                wob = int(math.sin(elapsed*4)*4)
                screen.blit(txt, (x + wob, y))
                # draw a soft selector circle
                pygame.draw.circle(screen, (0,220,140,30), (x - 30, y + 12), 12)
            else:
                screen.blit(txt, (x, y))

        # hint
        hint = info_font.render("↑ ↓ select | ENTER play | ESC quit | Visit /leaderboards in browser", True, (160,160,170))
        screen.blit(hint, (40, height-40))

        pygame.display.flip()
        clock.tick(60)


# =====================================
# MAIN
# =====================================
if __name__ == '__main__':
    uname = input("Username: ")
    pwd = input("Password: ")

    r, code = register(uname, pwd)
    if code == 400:
        print("User exists, logging in...")

    user, code = login(uname, pwd)
    print("Logged in as:", user['username'])

    t = threading.Thread(target=start_socket, args=(uname,), daemon=True)
    t.start()

    show_menu(user)
