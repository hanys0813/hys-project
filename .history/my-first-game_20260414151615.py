import pygame
import random
import sys
import math

pygame.init()

# ── 폰트 설정 ──
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

# ── 상수 및 색상 설정 (마법소녀 테마) ──
WIDTH, HEIGHT = 800, 600
CELL = 20

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (40, 40, 40)
RED    = (255, 80, 80)
GREEN  = (50, 220, 100)

# 파스텔 테마 색상
C_PINK       = (255, 182, 193)
C_MINT       = (189, 252, 201)
C_LEMON      = (255, 250, 205)
C_SKY        = (135, 206, 235)
C_PURPLE_L   = (230, 190, 255)
C_ST_OUTLINE = (80, 20, 100) # 진한 보라색 테두리

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("마법소녀 즈큥도큥 루루핑 뱀 기사")
clock = pygame.time.Clock()

# 폰트 객체 생성
font_big = get_font(70, bold=True)
ft_main  = get_font(35, bold=True)
ft_btn   = get_font(22, bold=True)
ft_tag   = get_font(18, bold=True)
hud_font = get_korean_font(24)

# ── 텍스트 테두리 효과 함수 (루루핑 스타일 가독성) ──
def render_bordered_text(text, font, color, outline_color, x, y, border_size=3):
    """글자 주변에 두꺼운 테두리를 그려 만화 같은 느낌을 줍니다."""
    for dx in range(-border_size, border_size + 1):
        for dy in range(-border_size, border_size + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, (x, y))

# ── 타이틀 별 애니메이션 ──
class RainbowStar:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 20
        self.size = random.randint(6, 14)
        self.color = random.choice([C_PINK, C_MINT, C_LEMON, WHITE, C_PURPLE_L])
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.randint(0, 360)

    def draw(self, surf):
        self.y -= self.speed
        self.angle += 3
        if self.y < -20: self.reset()

        points = []
        for i in range(10):
            r = self.size if i % 2 == 0 else self.size // 2
            ang = math.radians(self.angle + i * 36)
            points.append((self.x + r * math.cos(ang), self.y + r * math.sin(ang)))
        
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, WHITE, points, 2)

RAINBOW_STARS = [RainbowStar() for _ in range(35)]

def draw_fancy_gradient():
    """배경에 무지개 파스텔 그라데이션을 그립니다."""
    colors = [C_PINK, C_LEMON, C_MINT, C_SKY]
    section_h = HEIGHT // (len(colors) - 1)
    for i in range(len(colors) - 1):
        for y in range(section_h):
            ratio = y / section_h
            r = int(colors[i][0] + (colors[i+1][0] - colors[i][0]) * ratio)
            g = int(colors[i][1] + (colors[i+1][1] - colors[i][1]) * ratio)
            b = int(colors[i][2] + (colors[i+1][2] - colors[i][2]) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, i * section_h + y), (WIDTH, i * section_h + y))

# ── 타이틀 화면 ──
def title_screen():
    t = 0
    while True:
        clock.tick(60)
        t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE): return
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

        draw_fancy_gradient()
        for s in RAINBOW_STARS: s.draw(screen)

        # 투명한 중앙 패널
        panel = pygame.Surface((720, 380), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 130))
        pygame.draw.rect(panel, WHITE, (0, 0, 720, 380), 3, border_radius=30)
        screen.blit(panel, (40, 90))

        # 메인 제목 및 텍스트
        mid_x = WIDTH // 2
        tag_text = "♥ 카와이 러블리 즈큥도큥 바큥부큥 ♥"
        render_bordered_text(tag_text, ft_tag, (255, 50, 150), WHITE, mid_x - ft_tag.size(tag_text)[0]//2, 110)

        l1 = "평범한 뱀이었던 내가"
        render_bordered_text(l1, ft_main, (255, 255, 100), (180, 100, 0), mid_x - ft_main.size(l1)[0]//2, 150)
        
        l2 = "알고 보니 공주를 구할 기사?"
        render_bordered_text(l2, ft_main, (255, 150, 200), (120, 20, 100), mid_x - ft_main.size(l2)[0]//2, 205)

        l3 = "루 루 핑"
        render_bordered_text(l3, font_big, (150, 255, 180), (20, 100, 50), mid_x - font_big.size(l3)[0]//2, 260)

        # 시작 버튼 깜빡임
        if (t // 30) % 2 == 0:
            start_msg = "★ [SPACE] 를 눌러 마법의 모험 시작 ★"
            render_bordered_text(start_msg, ft_btn, WHITE, (255, 80, 180), mid_x - ft_btn.size(start_msg)[0]//2, 385)

        # 하단 뱀 애니메이션
        sx = (t * 5) % (WIDTH + 200) - 100
        for bi in range(10):
            bx = sx - bi * 22
            by = HEIGHT - 50 + math.sin(t * 0.1 + bi * 0.6) * 15
            color = (255, 180, 230) if bi == 0 else (255, 220, 240)
            pygame.draw.circle(screen, color, (int(bx), int(by)), 12)
            pygame.draw.circle(screen, WHITE, (int(bx), int(by)), 12, 2)

        pygame.display.flip()

# ── 게임 로직 ──
LEVELS = {3: {"speed": 18, "label": "Hard"}}

def new_food(snake):
    while True:
        pos = (random.randrange(0, WIDTH // CELL) * CELL, random.randrange(0, HEIGHT // CELL) * CELL)
        if pos not in snake: return pos

def main():
    level = 3 # Hard 난이도 고정
    speed = LEVELS[level]["speed"]
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food = new_food(snake)
    score = 0

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
            # 게임 오버 시 다시 루프
            main()
            return

        snake.insert(0, head)
        if head == food:
            score += 10
            food = new_food(snake)
        else:
            snake.pop()

        # 게임 화면 그리기
        screen.fill((30, 30, 30))
        # 그리드
        for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))
        
        # 먹이 (마법의 보석 느낌)
        pygame.draw.circle(screen, (255, 100, 200), (food[0]+10, food[1]+10), 9)
        pygame.draw.circle(screen, WHITE, (food[0]+10, food[1]+10), 9, 2)

        # 뱀 (기사 뱀)
        for i, seg in enumerate(snake):
            color = (255, 200, 255) if i == 0 else (200, 150, 255)
            pygame.draw.rect(screen, color, (*seg, CELL-2, CELL-2), border_radius=5)

        # HUD
        score_txt = hud_font.render(f"Score: {score}", True, WHITE)
        lv_txt = hud_font.render(f"Mode: Hard", True, C_PINK)
        screen.blit(score_txt, (15, 15))
        screen.blit(lv_txt, (15, 45))
        
        pygame.display.flip()

# 실행
title_screen()
main()