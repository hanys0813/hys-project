import pygame
import random
import sys
import math

pygame.init()

# ── 폰트 및 설정 (기존 유지) ──
def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

def get_font(size, bold=False):
    paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for p in paths:
        try: return pygame.font.Font(p, size)
        except: pass
    return get_korean_font(size)

WIDTH, HEIGHT = 800, 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

# 색상 (기존 다크 테마 유지)
WHITE, BLACK, GRAY, RED = (255, 255, 255), (0, 0, 0), (40, 40, 40), (220, 50, 50)
C_BG_TOP, C_BG_MID, C_BG_BOT = (8, 4, 28), (20, 8, 50), (10, 25, 10)
C_CASTLE, C_CAST_LIT = (30, 20, 60), (255, 220, 100)

# 타이틀 폰트 (이미지 느낌 반영)
ft_main = get_font(32, bold=True)
ft_big  = get_font(70, bold=True)
ft_tag  = get_font(16, bold=True)
ft_btn  = get_font(22, bold=True)

# ── 텍스트 테두리 효과 (이미지 스타일) ──
def render_bordered_text(text, font, color, outline_color, x, y, b_size=3):
    for dx in range(-b_size, b_size+1):
        for dy in range(-b_size, b_size+1):
            if dx!=0 or dy!=0:
                screen.blit(font.render(text, True, outline_color), (x+dx, y+dy))
    screen.blit(font.render(text, True, color), (x, y))

# ── 기존 시스템: 별, 배경, 성, 땅 (그대로 유지) ──
class TitleStar:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(0, int(HEIGHT*0.75))
        self.r, self.phase, self.spd = random.uniform(0.6, 2.2), random.uniform(0, math.pi*2), random.uniform(0.02, 0.06)
    def draw(self, surf, t):
        bright = int(130 + 110 * math.sin(self.phase + t * self.spd))
        pygame.draw.circle(surf, (bright, bright, min(255, bright+30)), (int(self.x), int(self.y)), max(1, int(self.r)))

TITLE_STARS = [TitleStar() for _ in range(80)]

def draw_title_elements(t):
    # 배경 그라데이션
    for i in range(24):
        ratio = i/24
        col = [int(C_BG_TOP[j] + (C_BG_MID[j] if ratio < 0.6 else C_BG_BOT[j] - C_BG_TOP[j]) * ratio) for j in range(3)]
        pygame.draw.rect(screen, col, (0, int(HEIGHT*ratio), WIDTH, int(HEIGHT/24)+1))
    # 별
    for s in TITLE_STARS: s.draw(screen, t)
    # 성 (Castle)
    cx, by = 590, HEIGHT-70
    pygame.draw.rect(screen, C_CASTLE, (cx-90, by-130, 28, 130))
    pygame.draw.rect(screen, C_CASTLE, (cx+62, by-150, 28, 150))
    pygame.draw.rect(screen, C_CASTLE, (cx-62, by-90, 124, 90))
    pygame.draw.rect(screen, C_CAST_LIT, (cx-55, by-70, 10, 14)) # 성 불빛
    # 땅
    pygame.draw.rect(screen, (12, 45, 12), (0, HEIGHT-55, WIDTH, 55))

# ── 타이틀 화면 ──
def title_screen():
    t = 0
    while True:
        clock.tick(60); t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE): return
        
        # 1. 기존 시스템 렌더링
        draw_title_elements(t)

        # 2. 루루핑 스타일 텍스트 레이아웃
        mx = WIDTH // 2
        render_bordered_text("♥ 즈큥도큥 바큥부큥 ♥", ft_tag, (255, 100, 200), WHITE, mx-100, 120)
        
        l1 = "평범한 뱀이었던 내가"
        render_bordered_text(l1, ft_main, (255, 255, 120), (150, 80, 0), mx - ft_main.size(l1)[0]//2, 160)
        
        l2 = "알고 보니 공주를 구할 기사?"
        render_bordered_text(l2, ft_main, (255, 180, 220), (100, 30, 80), mx - ft_main.size(l2)[0]//2, 210)
        
        l3 = "루 루 핑"
        render_bordered_text(l3, ft_big, (180, 255, 180), (20, 80, 40), mx - ft_big.size(l3)[0]//2, 270)

        if (t // 30) % 2 == 0:
            btn_txt = "▶ SPACE TO START"
            render_bordered_text(btn_txt, ft_btn, WHITE, (200, 50, 150), mx - ft_btn.size(btn_txt)[0]//2, 400)

        # 하단 뱀 애니메이션
        sx = (t * 3) % (WIDTH + 100) - 100
        for bi in range(6):
            pygame.draw.rect(screen, (50, 200, 70), (sx - bi*20, HEIGHT-30, 18, 18), border_radius=4)
            
        pygame.display.flip()

# ── 게임 메인 (Hard 고정) ──
def main():
    speed = 18 # Hard
    snake, direction = [(WIDTH//2, HEIGHT//2)], (CELL, 0)
    food = (random.randrange(0, WIDTH//CELL)*CELL, random.randrange(0, HEIGHT//CELL)*CELL)
    score = 0

    while True:
        clock.tick(speed)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direction != (0, CELL): direction = (0, -CELL)
                if e.key == pygame.K_DOWN and direction != (0, -CELL): direction = (0, CELL)
                if e.key == pygame.K_LEFT and direction != (CELL, 0): direction = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0): direction = (CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT or head in snake:
            main(); return

        snake.insert(0, head)
        if head == food:
            score += 10
            food = (random.randrange(0, WIDTH//CELL)*CELL, random.randrange(0, HEIGHT//CELL)*CELL)
        else: snake.pop()

        screen.fill(GRAY)
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        for seg in snake: pygame.draw.rect(screen, (50, 200, 50), (*seg, CELL-2, CELL-2))
        pygame.display.flip()

title_screen()
main()