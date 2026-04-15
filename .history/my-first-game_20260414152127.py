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
    paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for p in paths:
        try: return pygame.font.Font(p, size)
        except: pass
    return get_korean_font(size)

# 상수 설정
WIDTH, HEIGHT = 800, 600
CELL = 20
WHITE, BLACK, GRAY, RED = (255, 255, 255), (0, 0, 0), (40, 40, 40), (220, 50, 50)
GREEN, DARK = (50, 200, 50), (30, 150, 30)
C_BG_TOP, C_BG_MID, C_BG_BOT = (8, 4, 28), (20, 8, 50), (10, 25, 10)
C_CASTLE, C_CAST_LIT = (30, 20, 60), (255, 220, 100)
C_GOLD, C_PURPLE = (255, 215, 0), (160, 80, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

# 폰트 객체
font_hud = get_korean_font(28)
ft_main = get_font(32, bold=True)
ft_big  = get_font(70, bold=True)
ft_tag  = get_font(16, bold=True)
ft_sub  = get_font(15)
ft_btn  = get_font(22, bold=True)

# ── 텍스트 테두리 렌더러 (루루핑 스타일 융합) ──
def render_bordered_text(text, font, color, outline_color, x, y, b_size=3):
    for dx in range(-b_size, b_size+1):
        for dy in range(-b_size, b_size+1):
            if dx!=0 or dy!=0:
                screen.blit(font.render(text, True, outline_color), (x+dx, y+dy))
    screen.blit(font.render(text, True, color), (x, y))

# ── 타이틀 밤하늘 시스템 ──
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
    pygame.draw.rect(screen, C_CAST_LIT, (cx-55, by-70, 10, 14))
    # 땅
    pygame.draw.rect(screen, (12, 45, 12), (0, HEIGHT-55, WIDTH, 55))

# ── 스프라이트 및 사운드 ──
def load_sprite(path, size=(CELL, CELL)):
    try: return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
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

        # 1. 밤하늘 배경 (네가 좋아한 버전)
        draw_title_elements(t)

        # 2. 텍스트 레이아웃 (세련된 버전)
        mx = WIDTH // 2
        render_bordered_text("♥ 이세계 뱀 기사단 ♥", ft_tag, (255, 100, 200), WHITE, mx-90, 100)
        
        l1 = "평범한 뱀이었던 내가"
        render_bordered_text(l1, ft_main, (255, 255, 120), (150, 80, 0), mx - ft_main.size(l1)[0]//2, 140)
        
        l2 = "알고 보니 공주를 구할 기사?"
        render_bordered_text(l2, ft_main, (255, 180, 220), (100, 30, 80), mx - ft_main.size(l2)[0]//2, 190)

        # 하단 서브 정보 구역
        sub_txt = "~ 1000점 모아 보스를 물리치고 해피엔딩을 맞이하겠어 ~"
        render_bordered_text(sub_txt, ft_sub, (160, 200, 255), BLACK, mx - ft_sub.size(sub_txt)[0]//2, 250, b_size=1)

        # 아이콘 박스
        icons = [((50, 200, 50), "기사"), ((255, 150, 200), "공주"), ((220, 50, 50), "보스")]
        for i, (col, lab) in enumerate(icons):
            ix = 130 + i * 190
            pygame.draw.rect(screen, (255, 255, 255, 150), (ix, 290, 160, 50), border_radius=10)
            pygame.draw.circle(screen, col, (ix + 25, 315), 10)
            screen.blit(ft_sub.render(lab, True, BLACK), (ix + 45, 305))

        if (t // 30) % 2 == 0:
            render_bordered_text("▶ SPACE TO START", ft_btn, WHITE, (200, 50, 150), mx - 100, 400)

        # 하단 뱀 애니메이션
        sx = (t * 3) % (WIDTH + 100) - 100
        for bi in range(6):
            pygame.draw.rect(screen, (50, 220, 70), (sx - bi*20, HEIGHT-35, 18, 18), border_radius=4)
            
        pygame.display.flip()

# ── 게임 메인 로직 ──
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
        
        # 사망 시 리턴 (다시 타이틀로 가기 위함)
        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT or head in snake:
            return

        snake.insert(0, head)
        if head == food:
            score += 10
            food = (random.randrange(0, WIDTH//CELL)*CELL, random.randrange(0, HEIGHT//CELL)*CELL)
        else: snake.pop()

        # 인게임 렌더링
        screen.fill(GRAY)
        for x in range(0, WIDTH, CELL): pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))
        
        pygame.draw.rect(screen, RED, (*food, CELL, CELL), border_radius=4)
        
        for i, seg in enumerate(snake):
            if i == 0:
                if HEAD_IMG:
                    angle = {(CELL,0):0, (-CELL,0):180, (0,-CELL):90, (0,CELL):270}.get(direction, 0)
                    screen.blit(pygame.transform.rotate(HEAD_IMG, angle), seg)
                else: pygame.draw.rect(screen, DARK, (*seg, CELL, CELL))
            else:
                if BODY_IMG: screen.blit(BODY_IMG, seg)
                else: pygame.draw.rect(screen, GREEN, (*seg, CELL-2, CELL-2), border_radius=4)
        
        screen.blit(font_hud.render(f"Score: {score}", True, WHITE), (15, 15))
        pygame.display.flip()

# ── 최종 무한 실행 루프 ──
def game_loop():
    while True:
        title_screen()  # 타이틀 화면
        main()          # 게임 시작 (죽으면 리턴되어 다시 위로 올라감)

if __name__ == "__main__":
    game_loop()