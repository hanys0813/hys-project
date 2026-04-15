import pygame
import random
import sys
import math

pygame.init()

# ── 폰트 및 기본 설정 (기존 유지) ──
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

# 기존 색상 유지
WHITE, BLACK, GREEN, DARK, RED, GRAY = (255, 255, 255), (0, 0, 0), (50, 200, 50), (30, 150, 30), (220, 50, 50), (40, 40, 40)
C_GOLD, C_GOLD_DIM, C_PURPLE, C_STAR_CLR = (255, 215, 0), (180, 140, 0), (160, 80, 255), (220, 200, 255)

# 새로운 화사한 톤 (타이틀용)
C_PINK_SOFT = (255, 182, 193)
C_SKY_SOFT  = (135, 206, 235)
C_LIME_SOFT = (200, 255, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

font     = get_korean_font(36)
font_big = get_korean_font(72)
ft_tag   = get_font(16, bold=True)
ft_sub   = get_font(15)
ft_main  = get_font(32, bold=True)
ft_btn   = get_font(22, bold=True)

# ── 헬퍼 함수: 테두리 텍스트 (화려함 추가) ──
def render_fancy_text(text, font, color, outline_color, x, y, b_size=3):
    for dx in range(-b_size, b_size + 1):
        for dy in range(-b_size, b_size + 1):
            if dx != 0 or dy != 0:
                osurf = font.render(text, True, outline_color)
                screen.blit(osurf, (x + dx, y + dy))
    tsurf = font.render(text, True, color)
    screen.blit(tsurf, (x, y))

# ── 타이틀 효과 클래스 (별 애니메이션 강화) ──
class TitleStar:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 10
        self.size = random.uniform(2, 5)
        self.color = random.choice([C_GOLD, C_STAR_CLR, WHITE, (255, 200, 255)])
        self.speed = random.uniform(0.5, 1.5)

    def draw(self, surf, t):
        self.y -= self.speed
        if self.y < -10: self.reset()
        glow = abs(math.sin(t * 0.05 + self.x)) * 2
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size + glow))

TITLE_STARS = [TitleStar() for _ in range(60)]

def draw_fancy_bg():
    """파스텔톤 무지개 그라데이션 배경"""
    for y in range(HEIGHT):
        r = int(255 - (y / HEIGHT) * 50)
        g = int(220 - (y / HEIGHT) * 30)
        b = int(255 - (abs(HEIGHT//2 - y) / HEIGHT) * 100)
        pygame.draw.line(screen, (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))), (0, y), (WIDTH, y))

# ── 스프라이트 로드 ──
def load_sprite(path, size=(CELL, CELL)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except: return None

HEAD_IMG = load_sprite("player.png")
BODY_IMG = load_sprite("body.png")

# ── 타이틀 화면 ──
def title_screen():
    t = 0
    while True:
        clock.tick(60); t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE): return
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

        # 1. 배경 및 입자 효과
        draw_fancy_bg()
        for s in TITLE_STARS: s.draw(screen, t)

        # 2. 메인 패널 (반투명 화이트)
        pw, ph = 700, 380
        px, py = (WIDTH - pw) // 2, 100
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 140))
        pygame.draw.rect(panel, WHITE, (0, 0, pw, ph), 2, border_radius=20)
        screen.blit(panel, (px, py))

        # 3. 타이틀 텍스트 (기존 문구 유지 + 디자인 업그레이드)
        mx = WIDTH // 2
        render_fancy_text("♥ 이세계 뱀 기사단 ♥", ft_tag, (255, 80, 150), WHITE, mx - ft_tag.size("♥ 이세계 뱀 기사단 ♥")[0]//2, py + 25)

        l1 = "평범한 뱀이었던 내가"
        render_fancy_text(l1, ft_main, (255, 230, 100), (150, 100, 0), mx - ft_main.size(l1)[0]//2, py + 65)
        
        l2 = "알고 보니 공주를 구할 기사?"
        render_fancy_text(l2, ft_main, (255, 150, 200), (100, 20, 80), mx - ft_main.size(l2)[0]//2, py + 115)

        sub_txt = "~ 1000점 모아 보스를 물리치고 해피엔딩을 맞이하겠어 ~"
        render_fancy_text(sub_txt, ft_sub, (100, 100, 255), WHITE, mx - ft_sub.size(sub_txt)[0]//2, py + 175, b_size=1)

        # 4. 기존 아이콘 시스템 (디자인 조화)
        icons = [((50, 200, 50), "기사", "용감한 뱀 기사"), ((200, 160, 255), "공주", "납치된 공주님"), ((220, 80, 80), "보스", "최종 보스")]
        for idx, (dot_c, short, label) in enumerate(icons):
            ix = px + 80 + idx * 190
            iy = py + 210
            pygame.draw.rect(screen, WHITE, (ix, iy, 160, 60), border_radius=10)
            pygame.draw.circle(screen, dot_c, (ix + 25, iy + 30), 10)
            screen.blit(ft_sub.render(short, True, dot_c), (ix + 45, iy + 12))
            screen.blit(ft_tag.render(label, True, GRAY), (ix + 45, iy + 34))

        # 5. 시작 안내
        if (t // 30) % 2 == 0:
            btn_txt = "▶ SPACE / ENTER TO START ◀"
            render_fancy_text(btn_txt, ft_btn, WHITE, (255, 100, 150), mx - ft_btn.size(btn_txt)[0]//2, py + 310)

        # 6. 하단 기사 뱀 애니메이션
        sx = (t * 4) % (WIDTH + 100) - 100
        for bi in range(6):
            bx = sx - bi * 20
            by = HEIGHT - 40 + math.sin(t * 0.1 + bi) * 10
            pygame.draw.rect(screen, (50, 220, 80), (bx, by, 18, 18), border_radius=4)

        pygame.display.flip()

# ── 게임 핵심 로직 (기존 시스템 그대로 유지) ──
LEVELS = {3: {"speed": 18, "label": "Hard"}}

def new_food(snake):
    while True:
        pos = (random.randrange(0, WIDTH // CELL) * CELL, random.randrange(0, HEIGHT // CELL) * CELL)
        if pos not in snake: return pos

def draw_snake(snake, direction):
    for i, seg in enumerate(snake):
        if i == 0:
            if HEAD_IMG:
                angle = { (CELL,0):0, (-CELL,0):180, (0,-CELL):90, (0,CELL):270 }.get(direction, 0)
                screen.blit(pygame.transform.rotate(HEAD_IMG, angle), seg)
            else: pygame.draw.rect(screen, DARK, (*seg, CELL, CELL))
        else:
            if BODY_IMG: screen.blit(BODY_IMG, seg)
            else: pygame.draw.rect(screen, GREEN, (*seg, CELL, CELL))

def main():
    level = 3 # Hard 시작
    speed = LEVELS[level]["speed"]
    snake, direction = [(WIDTH // 2, HEIGHT // 2)], (CELL, 0)
    food, score = new_food(snake), 0

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
            main(); return

        snake.insert(0, head)
        if head == food:
            score += 10
            food = new_food(snake)
        else: snake.pop()

        screen.fill(GRAY)
        for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        draw_snake(snake, direction)
        
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        pygame.display.flip()

# ── 실행 ──
title_screen()
main()