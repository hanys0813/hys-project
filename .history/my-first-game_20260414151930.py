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
    paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]
    for p in paths:
        try: return pygame.font.Font(p, size)
        except: pass
    return get_korean_font(size)

# 상수 및 색상
WIDTH, HEIGHT = 800, 600
CELL = 20
WHITE, BLACK, GREEN, DARK, RED, GRAY = (255, 255, 255), (0, 0, 0), (50, 200, 50), (30, 150, 30), (220, 50, 50), (40, 40, 40)
C_GOLD, C_PURPLE, C_PINK = (255, 215, 0), (160, 80, 255), (255, 105, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

font_big = get_font(80, bold=True)
ft_main  = get_font(36, bold=True)
ft_tag   = get_font(18, bold=True)
ft_btn   = get_font(24, bold=True)
ft_sub   = get_font(16)

# ── 텍스트 테두리 렌더러 (비주얼 핵심) ──
def draw_text_bordered(text, font, color, o_color, x, y, b_size=3):
    for dx in range(-b_size, b_size+1):
        for dy in range(-b_size, b_size+1):
            if dx!=0 or dy!=0: screen.blit(font.render(text, True, o_color), (x+dx, y+dy))
    screen.blit(font.render(text, True, color), (x, y))

# ── 타이틀 파티클 ──
class ShineParticle:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)
    def reset(self):
        self.x, self.y = random.randint(0, WIDTH), HEIGHT + 10
        self.size = random.uniform(1, 4)
        self.speed = random.uniform(0.5, 2.0)
        self.alpha = random.randint(100, 255)
    def update(self):
        self.y -= self.speed
        if self.y < -10: self.reset()
    def draw(self, surf):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (self.x, self.y))

PARTICLES = [ShineParticle() for _ in range(50)]

# ── 스프라이트 로드 ──
def load_sprite(path, size=(CELL, CELL)):
    try: return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except: return None

HEAD_IMG = load_sprite("player.png")
BODY_IMG = load_sprite("body.png")

# ── 타이틀 배경 그라데이션 ──
def draw_magical_bg(t):
    for y in range(HEIGHT):
        r = int(240 + 15 * math.sin(t*0.02 + y*0.01))
        g = int(210 + 20 * math.cos(t*0.02 + y*0.01))
        b = int(255)
        pygame.draw.line(screen, (min(255, r), min(255, g), min(255, b)), (0, y), (WIDTH, y))

# ── 타이틀 화면 ──
def title_screen():
    t = 0
    while True:
        clock.tick(60); t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE): return

        draw_magical_bg(t)
        for p in PARTICLES:
            p.update()
            p.draw(screen)

        # 중앙 카드 패널
        panel = pygame.Surface((720, 420), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 160))
        pygame.draw.rect(panel, (255, 255, 255), (0, 0, 720, 420), 4, border_radius=25)
        screen.blit(panel, (40, 80))

        mx = WIDTH // 2
        float_y = math.sin(t * 0.05) * 8

        # 텍스트 레이아웃
        tag = "♥ THE LEGEND OF SNAKE KNIGHT ♥"
        draw_text_bordered(tag, ft_tag, C_PINK, WHITE, mx - ft_tag.size(tag)[0]//2, 100)

        l1 = "평범한 뱀이었던 내가"
        draw_text_bordered(l1, ft_main, (255, 200, 0), (100, 50, 0), mx - ft_main.size(l1)[0]//2, 140 + float_y)
        
        l2 = "알고 보니 공주를 구할 기사?"
        draw_text_bordered(l2, ft_main, (255, 100, 180), (80, 0, 50), mx - ft_main.size(l2)[0]//2, 200 + float_y)

        # 게임 정보 아이콘 구역
        info_y = 280
        icons = [((50, 200, 50), "용맹한 기사"), ((255, 150, 200), "납치된 공주"), ((220, 50, 50), "거대 보스")]
        for i, (col, lab) in enumerate(icons):
            ix = 110 + i * 200
            pygame.draw.rect(screen, WHITE, (ix, info_y, 180, 50), border_radius=15)
            pygame.draw.circle(screen, col, (ix + 25, info_y + 25), 10)
            screen.blit(ft_sub.render(lab, True, GRAY), (ix + 45, info_y + 15))

        if (t // 30) % 2 == 0:
            msg = "▶ PRESS SPACE TO ADVENTURE ◀"
            draw_text_bordered(msg, ft_btn, WHITE, C_PINK, mx - ft_btn.size(msg)[0]//2, 410)

        # 하단 뱀 애니메이션
        sx = (t * 4) % (WIDTH + 200) - 100
        for bi in range(8):
            bx = sx - bi * 22
            by = HEIGHT - 40 + math.sin(t*0.1 + bi)*12
            pygame.draw.circle(screen, (100, 255, 150), (int(bx), int(by)), 12)
            pygame.draw.circle(screen, WHITE, (int(bx), int(by)), 12, 2)

        pygame.display.flip()

# ── 게임 메인 로직 ──
def main():
    speed = 18 # Hard 고정
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
        
        # 사망 조건 (벽 또는 몸 충돌)
        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT or head in snake:
            # 핵심: return을 하여 다시 game_loop()로 돌아가게 함
            return 

        snake.insert(0, head)
        if head == food:
            score += 10
            food = (random.randrange(0, WIDTH//CELL)*CELL, random.randrange(0, HEIGHT//CELL)*CELL)
        else: snake.pop()

        # 그리기 로직
        screen.fill((20, 20, 25))
        for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (40, 40, 45), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (40, 40, 45), (0, y), (WIDTH, y))
        
        pygame.draw.rect(screen, RED, (*food, CELL, CELL), border_radius=4)
        for i, seg in enumerate(snake):
            col = (100, 255, 100) if i == 0 else (50, 180, 50)
            pygame.draw.rect(screen, col, (*seg, CELL-2, CELL-2), border_radius=5)
            
        screen.blit(get_korean_font(24).render(f"Score: {score}", True, WHITE), (15, 15))
        pygame.display.flip()

# ── 무한 실행 루프 ──
def game_loop():
    while True:
        title_screen() # 1. 타이틀 보여주기
        main()         # 2. 게임 시작 (죽으면 main이 종료됨)
                       # 3. 죽으면 다시 title_screen으로 올라감

if __name__ == "__main__":
    game_loop()