import pygame
import random
import sys
import math

pygame.init()

# ── [기존 시스템 그대로] 폰트 및 설정 ──
def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
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

# 색상 (기존 유지)
WHITE, BLACK, GRAY, RED = (255, 255, 255), (0, 0, 0), (40, 40, 40), (220, 50, 50)
C_GOLD, C_PURPLE = (255, 215, 0), (160, 80, 255)

# 폰트
ft_main = get_font(42, bold=True)
ft_sub  = get_font(18)
ft_btn  = get_font(24, bold=True)

# ── [완전 교체] 타이틀 전용 렌더링 시스템 ──
class TitleParticle:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(HEIGHT, HEIGHT + 100)
        self.speed = random.uniform(1.0, 3.0)
        self.size = random.randint(2, 5)
        self.color = random.choice([(255, 255, 200), (200, 200, 255), (255, 200, 255)])
    def update(self):
        self.y -= self.speed
        if self.y < -10: self.reset()
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

PARTICLES = [TitleParticle() for _ in range(50)]

def draw_fancy_title_bg(t):
    # 역동적인 다크 퍼플 그라데이션
    for i in range(HEIGHT):
        r = int(10 + 10 * math.sin(t * 0.02))
        g = int(5 + 5 * math.cos(t * 0.01))
        b = int(30 + i * 0.1)
        pygame.draw.line(screen, (min(255, r), min(255, g), min(255, b)), (0, i), (WIDTH, i))

def title_screen():
    t = 0
    while True:
        clock.tick(60); t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE): return

        # 1. 배경 & 파티클
        draw_fancy_title_bg(t)
        for p in PARTICLES:
            p.update()
            p.draw(screen)

        # 2. 타이틀 텍스트 애니메이션 (둥둥 뜨는 효과)
        mx = WIDTH // 2
        bounce = math.sin(t * 0.05) * 10
        
        # 외곽선 효과 함수
        def draw_text(txt, font, col, x, y, out_col=(0,0,0)):
            for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
                screen.blit(font.render(txt, True, out_col), (x+dx, y+dy))
            screen.blit(font.render(txt, True, col), (x, y))

        txt1 = "평범한 뱀이었던 내가"
        draw_text(txt1, ft_sub, (200, 255, 200), mx - ft_sub.size(txt1)[0]//2, 150 + bounce)
        
        txt2 = "이세계 뱀 기사단"
        draw_text(txt2, ft_main, C_GOLD, mx - ft_main.size(txt2)[0]//2, 180 + bounce)
        
        txt3 = "알고 보니 공주를 구할 기사?"
        draw_text(txt3, ft_sub, (255, 200, 200), mx - ft_sub.size(txt3)[0]//2, 240 + bounce)

        # 3. 보석 같은 장식
        pygame.draw.rect(screen, C_PURPLE, (mx-150, 300, 300, 2), border_radius=1)
        
        # 4. 시작 버튼 깜빡임
        if (t // 30) % 2 == 0:
            btn_txt = "PRESS SPACE TO START"
            draw_text(btn_txt, ft_btn, WHITE, mx - ft_btn.size(btn_txt)[0]//2, 400, (100, 0, 100))

        # 하단 미니 뱀 기사
        sx = (t * 3) % (WIDTH + 100) - 50
        for i in range(5):
            pygame.draw.circle(screen, (50, 200, 50), (int(sx - i*15), int(HEIGHT-50 + math.sin(t*0.1+i)*5)), 10)

        pygame.display.flip()

# ── [기존 시스템 그대로] 게임 메인 로직 ──
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
        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT or head in snake:
            # 죽으면 타이틀로 돌아가기
            return 

        snake.insert(0, head)
        if head == food:
            score += 10
            food = (random.randrange(0, WIDTH//CELL)*CELL, random.randrange(0, HEIGHT//CELL)*CELL)
        else: snake.pop()

        screen.fill(GRAY)
        # 그리드
        for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (50,50,50), (x,0), (x,HEIGHT))
        for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (50,50,50), (0,y), (WIDTH,y))
        
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        for seg in snake: pygame.draw.rect(screen, (50, 200, 50), (*seg, CELL-2, CELL-2))
        
        # 스코어 표시
        screen.blit(get_korean_font(24).render(f"Score: {score}", True, WHITE), (10, 10))
        pygame.display.flip()

# ── 실행 루프 ──
while True:
    title_screen()
    main()