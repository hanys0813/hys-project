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

# ── 상수 및 색상 설정 ──
WIDTH, HEIGHT = 800, 600
CELL = 20

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (40,  40,  40)
RED        = (255, 80,  80)
GREEN      = (50,  220, 100)

# 마법소녀 테마 (타이틀용)
C_PINK       = (255, 182, 193)
C_MINT       = (189, 252, 201)
C_LEMON      = (255, 250, 205)
C_SKY        = (135, 206, 235)
C_PURPLE_L   = (230, 190, 255)
C_ST_OUTLINE = (80,  20,  100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("마법소녀 즈큥도큥 루루핑 뱀 기사")
clock = pygame.time.Clock()

# 폰트 객체
font_big = get_font(70, bold=True)
ft_main  = get_font(35, bold=True)
ft_btn   = get_font(22, bold=True)
ft_tag   = get_font(18, bold=True)
hud_font = get_korean_font(24)
font_go  = get_korean_font(72)
font_ui  = get_korean_font(36)

# ── 스프라이트 로드 ──
def load_sprite(path, size=(CELL, CELL)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        return None

HEAD_IMG = load_sprite("player.png")
BODY_IMG = load_sprite("body.png")

# ── 사운드 로드 ──
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
#  타이틀 전용 요소
# ══════════════════════════════════════════

def render_bordered_text(text, font, color, outline_color, x, y, border_size=3):
    for dx in range(-border_size, border_size + 1):
        for dy in range(-border_size, border_size + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, (x, y))

class RainbowStar:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 20
        self.size  = random.randint(6, 14)
        self.color = random.choice([C_PINK, C_MINT, C_LEMON, WHITE, C_PURPLE_L])
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.randint(0, 360)

    def draw(self, surf):
        self.y -= self.speed
        self.angle += 3
        if self.y < -20:
            self.reset()
        points = []
        for i in range(10):
            r = self.size if i % 2 == 0 else self.size // 2
            ang = math.radians(self.angle + i * 36)
            points.append((self.x + r * math.cos(ang), self.y + r * math.sin(ang)))
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, WHITE, points, 2)

RAINBOW_STARS = [RainbowStar() for _ in range(35)]

def draw_fancy_gradient():
    colors = [C_PINK, C_LEMON, C_MINT, C_SKY]
    section_h = HEIGHT // (len(colors) - 1)
    for i in range(len(colors) - 1):
        for y in range(section_h):
            ratio = y / section_h
            r = int(colors[i][0] + (colors[i+1][0] - colors[i][0]) * ratio)
            g = int(colors[i][1] + (colors[i+1][1] - colors[i][1]) * ratio)
            b = int(colors[i][2] + (colors[i+1][2] - colors[i][2]) * ratio)
            pygame.draw.line(screen, (r, g, b),
                             (0, i * section_h + y), (WIDTH, i * section_h + y))

# ══════════════════════════════════════════
#  타이틀 화면
# ══════════════════════════════════════════
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
                    return
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        draw_fancy_gradient()
        for s in RAINBOW_STARS:
            s.draw(screen)

        # 중앙 패널
        panel = pygame.Surface((720, 380), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 130))
        pygame.draw.rect(panel, WHITE, (0, 0, 720, 380), 3, border_radius=30)
        screen.blit(panel, (40, 90))

        mid_x = WIDTH // 2

        tag_text = "♥ 카와이 러블리 즈큥도큥 바큥부큥 ♥"
        render_bordered_text(tag_text, ft_tag, (255, 50, 150), WHITE,
                             mid_x - ft_tag.size(tag_text)[0] // 2, 110)

        l1 = "평범한 뱀이었던 내가"
        render_bordered_text(l1, ft_main, (255, 255, 100), (180, 100, 0),
                             mid_x - ft_main.size(l1)[0] // 2, 150)

        l2 = "알고 보니 공주를 구할 기사?"
        render_bordered_text(l2, ft_main, (255, 150, 200), (120, 20, 100),
                             mid_x - ft_main.size(l2)[0] // 2, 205)

        l3 = "루 루 핑"
        render_bordered_text(l3, font_big, (150, 255, 180), (20, 100, 50),
                             mid_x - font_big.size(l3)[0] // 2, 260)

        if (t // 30) % 2 == 0:
            start_msg = "★ [SPACE] 를 눌러 마법의 모험 시작 ★"
            render_bordered_text(start_msg, ft_btn, WHITE, (255, 80, 180),
                                 mid_x - ft_btn.size(start_msg)[0] // 2, 385)

        # 하단 뱀 애니메이션
        sx = (t * 5) % (WIDTH + 200) - 100
        for bi in range(10):
            bx = sx - bi * 22
            by = HEIGHT - 50 + math.sin(t * 0.1 + bi * 0.6) * 15
            color = (255, 180, 230) if bi == 0 else (255, 220, 240)
            pygame.draw.circle(screen, color, (int(bx), int(by)), 12)
            pygame.draw.circle(screen, WHITE,  (int(bx), int(by)), 12, 2)

        pygame.display.flip()

# ══════════════════════════════════════════
#  게임 유틸
# ══════════════════════════════════════════
def new_food(snake):
    while True:
        pos = (
            random.randrange(0, WIDTH  // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake:
            return pos

def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def draw_snake(snake, direction):
    for i, seg in enumerate(snake):
        if i == 0:
            if HEAD_IMG:
                angle   = DIR_ANGLE.get(direction, 0)
                rotated = pygame.transform.rotate(HEAD_IMG, angle)
                screen.blit(rotated, seg)
            else:
                pygame.draw.rect(screen, (255, 200, 255), (*seg, CELL - 2, CELL - 2), border_radius=5)
        else:
            if BODY_IMG:
                screen.blit(BODY_IMG, seg)
            else:
                pygame.draw.rect(screen, (200, 150, 255), (*seg, CELL - 2, CELL - 2), border_radius=5)

def draw_hud(score):
    score_txt = hud_font.render(f"Score: {score}", True, WHITE)
    lv_txt    = hud_font.render("Mode: Hard",      True, C_PINK)
    screen.blit(score_txt, (15, 15))
    screen.blit(lv_txt,    (15, 45))

# ══════════════════════════════════════════
#  게임 오버 화면  ← 핵심 수정 부분
#  반환값: "title" | "restart"
# ══════════════════════════════════════════
def game_over_screen(score):
    # 버튼 정의 (rect는 나중에 계산)
    BTN_W, BTN_H = 260, 56
    mid_x = WIDTH  // 2
    mid_y = HEIGHT // 2

    btn_restart = pygame.Rect(mid_x - BTN_W - 20, mid_y + 60, BTN_W, BTN_H)
    btn_title   = pygame.Rect(mid_x + 20,          mid_y + 60, BTN_W, BTN_H)

    # 선택 상태 (0 = restart 하이라이트, 1 = title 하이라이트)
    selected = 0
    t = 0

    while True:
        clock.tick(60)
        t += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                # 좌우 방향키로 버튼 이동
                if e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    selected = 1 - selected
                # Enter / Space → 현재 선택된 버튼 실행
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "restart" if selected == 0 else "title"
                # 단축키
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_t:
                    return "title"
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

            if e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                if btn_restart.collidepoint(mx, my):
                    selected = 0
                elif btn_title.collidepoint(mx, my):
                    selected = 1

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if btn_restart.collidepoint(mx, my):
                    return "restart"
                if btn_title.collidepoint(mx, my):
                    return "title"

        # ── 배경: 마법소녀 그라데이션 + 반투명 오버레이 ──
        draw_fancy_gradient()
        for s in RAINBOW_STARS:
            s.draw(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # ── GAME OVER 텍스트 ──
        render_bordered_text("GAME OVER", font_go,
                             (255, 80, 80), (80, 0, 0),
                             mid_x - font_go.size("GAME OVER")[0] // 2,
                             mid_y - 130, border_size=4)

        score_surf = font_ui.render(f"Score : {score}", True, WHITE)
        screen.blit(score_surf, (mid_x - score_surf.get_width() // 2, mid_y - 30))

        # ── 버튼 그리기 ──
        def draw_btn(rect, label, active):
            color  = (255, 80, 180)  if active else (60, 30, 80)
            border = (255, 220, 255) if active else (180, 100, 200)
            pygame.draw.rect(screen, color,  rect, border_radius=14)
            pygame.draw.rect(screen, border, rect, 3, border_radius=14)
            # 깜빡임 효과 (선택된 버튼)
            if active and (t // 20) % 2 == 0:
                glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 40))
                screen.blit(glow, rect.topleft)
            txt = ft_btn.render(label, True, WHITE if active else (180, 140, 200))
            screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                              rect.centery - txt.get_height() // 2))

        draw_btn(btn_restart, "▶  다시 시작  [R]",    selected == 0)
        draw_btn(btn_title,   "★  타이틀로  [T]",    selected == 1)

        # ── 조작 안내 ──
        hint = ft_tag.render("← → 방향키로 선택  /  Enter 로 확인  /  Q 종료", True, (200, 180, 220))
        screen.blit(hint, (mid_x - hint.get_width() // 2, mid_y + 135))

        pygame.display.flip()

# ══════════════════════════════════════════
#  메인 게임 루프  (Hard 고정)
# ══════════════════════════════════════════
def main():
    level     = 3  # Hard 고정
    speed     = LEVELS[level]["speed"]
    snake     = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food      = new_food(snake)
    score     = 0

    while True:
        clock.tick(speed)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP    and direction != (0,  CELL): direction = (0, -CELL)
                if e.key == pygame.K_DOWN  and direction != (0, -CELL): direction = (0,  CELL)
                if e.key == pygame.K_LEFT  and direction != (CELL,  0): direction = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0): direction = ( CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if (head[0] < 0 or head[0] >= WIDTH
                or head[1] < 0 or head[1] >= HEIGHT
                or head in snake):
            result = game_over_screen(score)
            if result == "restart":
                main()      # 재시작
            else:
                title_screen()  # 타이틀로
                main()
            return

        snake.insert(0, head)
        if head == food:
            if EAT_SOUND:
                EAT_SOUND.play()
            score += 10
            food = new_food(snake)
        else:
            snake.pop()

        # 게임 화면 그리기
        screen.fill((30, 30, 30))
        draw_grid()

        # 먹이 (마법의 보석)
        pygame.draw.circle(screen, (255, 100, 200), (food[0] + 10, food[1] + 10), 9)
        pygame.draw.circle(screen, WHITE,            (food[0] + 10, food[1] + 10), 9, 2)

        draw_snake(snake, direction)
        draw_hud(score)
        pygame.display.flip()

# ── 엔트리포인트 ──
title_screen()
main()