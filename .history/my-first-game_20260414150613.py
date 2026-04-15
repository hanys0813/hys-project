import pygame
import random
import sys
import math

pygame.init()

# ── 원본 설정 그대로 ──
def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold
        else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for p in paths:
        try:
            return pygame.font.Font(p, size)
        except Exception:
            pass
    return get_korean_font(size)

WIDTH, HEIGHT = 800, 600
CELL = 20
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK  = (30, 150, 30)
RED   = (220, 50, 50)
GRAY  = (40, 40, 40)

C_BG_TOP   = (8,   4,  28)
C_BG_MID   = (20,  8,  50)
C_BG_BOT   = (10, 25,  10)
C_GOLD     = (255, 215,   0)
C_GOLD_DIM = (180, 140,   0)
C_PURPLE   = (160,  80, 255)
C_PURP_DIM = (100,  50, 180)
C_STAR_CLR = (220, 200, 255)
C_CASTLE   = (30,  20,  60)
C_CAST_LIT = (255, 220, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

font     = get_korean_font(36)
font_big = get_korean_font(72)
ft_tag  = get_font(14)
ft_sub  = get_font(15)
ft_main = get_font(27, bold=True)
ft_btn  = get_font(20, bold=True)

def load_sprite(path, size=(CELL, CELL)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        return None

HEAD_IMG = load_sprite("player.png")
BODY_IMG = load_sprite("body.png")

pygame.mixer.init()
try:
    EAT_SOUND = pygame.mixer.Sound("eat.wav")
except (FileNotFoundError, pygame.error):
    EAT_SOUND = None

DIR_ANGLE = {
    ( CELL,  0):   0,
    (-CELL,  0): 180,
    (0, -CELL):  90,
    (0,  CELL): 270,
}

LEVELS = {
    1: {"speed":  8, "label": "Easy"},
    2: {"speed": 12, "label": "Normal"},
    3: {"speed": 18, "label": "Hard"},
}

# ══════════════════════════════════════════
#  타이틀 전용 헬퍼
# ══════════════════════════════════════════
class TitleStar:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, int(HEIGHT * 0.75))
        self.r = random.uniform(0.6, 2.2)
        self.phase = random.uniform(0, math.pi * 2)
        self.spd   = random.uniform(0.02, 0.06)

    def draw(self, surf, t):
        bright = int(130 + 110 * math.sin(self.phase + t * self.spd))
        pygame.draw.circle(surf, (bright, bright, min(255, bright + 30)),
                           (int(self.x), int(self.y)), max(1, int(self.r)))

TITLE_STARS = [TitleStar() for _ in range(80)]

def draw_title_sky(surf):
    segs = 24
    for i in range(segs):
        ratio = i / segs
        if ratio < 0.6:
            tt = ratio / 0.6
            r = int(C_BG_TOP[0] + (C_BG_MID[0] - C_BG_TOP[0]) * tt)
            g = int(C_BG_TOP[1] + (C_BG_MID[1] - C_BG_TOP[1]) * tt)
            b = int(C_BG_TOP[2] + (C_BG_MID[2] - C_BG_TOP[2]) * tt)
        else:
            tt = (ratio - 0.6) / 0.4
            r = int(C_BG_MID[0] + (C_BG_BOT[0] - C_BG_MID[0]) * tt)
            g = int(C_BG_MID[1] + (C_BG_BOT[1] - C_BG_MID[1]) * tt)
            b = int(C_BG_MID[2] + (C_BG_BOT[2] - C_BG_MID[2]) * tt)
        y0 = int(HEIGHT * ratio)
        y1 = int(HEIGHT * (ratio + 1 / segs)) + 1
        pygame.draw.rect(surf, (r, g, b), (0, y0, WIDTH, y1 - y0))

def draw_title_castle(surf):
    cx, base_y = 590, HEIGHT - 70
    c = C_CASTLE
    def block(x, y, w, h):
        pygame.draw.rect(surf, c, (cx + x, y, w, h))
    block(-90, base_y - 130, 28, 130)
    for mx in range(-90, -62, 11): block(mx, base_y - 152, 8, 22)
    block(62,  base_y - 150, 28, 150)
    for mx in range(62, 90, 11):   block(mx, base_y - 172, 8, 22)
    block(-62, base_y - 90, 124, 90)
    for mx in range(-62, 62, 12):  block(mx, base_y - 108, 8, 18)
    for wx, wy in [(-55, base_y - 70), (38, base_y - 90), (-10, base_y - 50)]:
        pygame.draw.rect(surf, C_CAST_LIT, (cx + wx, wy, 10, 14))

def draw_title_ground(surf):
    pygame.draw.rect(surf, (12, 45, 12), (0, HEIGHT - 55, WIDTH, 55))
    pygame.draw.rect(surf, (18, 65, 18), (0, HEIGHT - 57, WIDTH, 6))

_ground_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
draw_title_ground(_ground_surf)

def title_screen():
    t = 0
    while True:
        clock.tick(60)
        t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return # 스페이스나 엔터 누르면 main()으로 넘어감
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        draw_title_sky(screen)
        for s in TITLE_STARS: s.draw(screen, t)
        draw_title_castle(screen)
        screen.blit(_ground_surf, (0, 0))

        pw, ph = 660, 310
        px, py = (WIDTH - pw) // 2, 108
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((10, 5, 35, 210))
        pygame.draw.rect(panel, C_GOLD_DIM, (0, 0, pw, ph), 1, border_radius=14)
        screen.blit(panel, (px, py))

        glow = abs(math.sin(t * 0.04))
        gc = (int(255 * glow), int(160 * glow), 0)
        pygame.draw.line(screen, gc, (px + 24, py + 14), (px + pw - 24, py + 14), 1)
        pygame.draw.line(screen, gc, (px + 24, py + ph - 14), (px + pw - 24, py + ph - 14), 1)

        tag = ft_tag.render("~ 이세계 뱀 기사단 ~", True, C_PURPLE)
        screen.blit(tag, (WIDTH // 2 - tag.get_width() // 2, py + 22))

        lines = ["평범한 뱀이었던 내가", "알고 보니 공주를 구할 기사?"]
        for i, line in enumerate(lines):
            wave = int(3 * math.sin(t * 0.05 + i * 1.3))
            alpha = int(200 + 55 * abs(math.sin(t * 0.04 + i * 0.5)))
            col = (alpha, int(alpha * 0.85), 0)
            surf = ft_main.render(line, True, col)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, py + 52 + i * 40 + wave))

        sub = ft_sub.render("~ 1000점 모아 보스를 물리치고 해피엔딩을 맞이하겠어 ~", True, (160, 200, 255))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, py + 142))

        icons = [
            ((50, 200, 50),   "기사",  "용감한 뱀 기사"),
            ((200, 160, 255), "공주",  "납치된 공주님"),
            ((220, 80,  80),  "보스",  "최종 보스"),
        ]
        borders = [C_GOLD, C_PURPLE, RED]
        for idx, ((dot_c, short, label), border_c) in enumerate(zip(icons, borders)):
            ix = px + 60 + idx * 190
            iy = py + 175
            box = pygame.Surface((160, 60), pygame.SRCALPHA)
            box.fill((25, 12, 60, 190))
            pygame.draw.rect(box, border_c, (0, 0, 160, 60), 1, border_radius=8)
            screen.blit(box, (ix, iy))
            pygame.draw.circle(screen, dot_c, (ix + 22, iy + 30), 11)
            s1 = ft_sub.render(short, True, dot_c)
            screen.blit(s1, (ix + 40, iy + 8))
            s2 = ft_tag.render(label, True, C_STAR_CLR)
            screen.blit(s2, (ix + 40, iy + 32))

        info = ft_tag.render("목표: 1000점  |  난이도: Hard", True, (170, 150, 210))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, py + 252))

        if (t // 28) % 2 == 0:
            btn = ft_btn.render("▶  SPACE / ENTER  로 모험 시작", True, C_GOLD)
            screen.blit(btn, (WIDTH // 2 - btn.get_width() // 2, py + 278))

        sx = (t * 3) % (WIDTH + 100) - 100
        for bi in range(6):
            bx = sx - bi * CELL
            if -CELL < bx < WIDTH:
                col = (50, 220, 70) if bi == 0 else (35, 160, 50)
                pygame.draw.rect(screen, col, (bx, HEIGHT - 28, CELL - 2, CELL - 2), border_radius=4)
        pygame.display.flip()

# ══════════════════════════════════════════
#  게임 핵심 로직 (수정됨)
# ══════════════════════════════════════════
def new_food(snake):
    while True:
        pos = (random.randrange(0, WIDTH // CELL) * CELL, random.randrange(0, HEIGHT // CELL) * CELL)
        if pos not in snake: return pos

def draw_grid():
    for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (20, 20, 20), (0, y), (WIDTH, y))

def draw_snake(snake, direction):
    for i, seg in enumerate(snake):
        if i == 0:
            if HEAD_IMG:
                angle = DIR_ANGLE.get(direction, 0)
                rotated = pygame.transform.rotate(HEAD_IMG, angle)
                screen.blit(rotated, seg)
            else:
                pygame.draw.rect(screen, DARK, (*seg, CELL, CELL))
        else:
            if BODY_IMG: screen.blit(BODY_IMG, seg)
            else: pygame.draw.rect(screen, GREEN, (*seg, CELL, CELL))

def draw_hud(score, level):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {LEVELS[level]['label']}", True, WHITE), (10, 40))

def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    # --- 수정 포인트: 난이도 선택 화면을 삭제하고 바로 Hard(3)로 시작 ---
    level = 3 
    speed = LEVELS[level]["speed"]

    snake     = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food      = new_food(snake)
    score     = 0

    while True:
        clock.tick(speed)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP    and direction != (0,  CELL): direction = (0, -CELL)
                if e.key == pygame.K_DOWN  and direction != (0, -CELL): direction = (0,  CELL)
                if e.key == pygame.K_LEFT  and direction != (CELL,  0): direction = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0): direction = ( CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if (head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake):
            if game_over_screen(score):
                main() # 재시작 시에도 다시 main으로
            return

        snake.insert(0, head)
        if head == food:
            if EAT_SOUND: EAT_SOUND.play()
            score += 10
            food = new_food(snake)
            # 점수에 따른 자동 난이도 상승 로직은 이미 최고 난이도(3)이므로 유지해도 무방함
        else:
            snake.pop()

        screen.fill(GRAY)
        draw_grid()
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        draw_snake(snake, direction)
        draw_hud(score, level)
        pygame.display.flip()

# ── 엔트리포인트 ──
title_screen() # 멋진 타이틀 실행
main()         # 끝나면 바로 게임 실행 (Hard 난이도)