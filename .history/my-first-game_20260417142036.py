import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

# ══════════════════════════════════════════
#  폰트 설정
# ══════════════════════════════════════════
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
    return pygame.font.SysFont(None, size)

# ══════════════════════════════════════════
#  상수
# ══════════════════════════════════════════
WIDTH, HEIGHT   = 900, 660
HUD_H           = 60          # 상단 HUD 높이
PLAY_TOP        = HUD_H       # 플레이 영역 시작 y
PLAY_H          = HEIGHT - HUD_H
CELL            = 22

COLS = WIDTH  // CELL
ROWS = PLAY_H // CELL

FPS = 60

# 색상
BG_DARK      = (10,  12,  20)
BG_GRID      = (18,  22,  36)
COL_GRID     = (25,  30,  50)
COL_WHITE    = (255, 255, 255)
COL_BLACK    = (0,   0,   0)
COL_RED      = (255, 60,  60)
COL_GREEN    = (60,  220, 120)
COL_YELLOW   = (255, 220, 60)
COL_CYAN     = (60,  220, 255)
COL_ORANGE   = (255, 140, 40)
COL_PURPLE   = (160, 80,  255)
COL_HUD_BG   = (8,   10,  18)
COL_GUARD    = (220, 80,  60)
COL_VISION   = (220, 80,  60, 40)   # RGBA (시야)
COL_KEY      = (255, 210, 60)
COL_DIA      = (120, 200, 255)

# 라운드 설정: (경비원 수, 이동속도, 시야반경, 뱀속도)
ROUND_CONFIG = {
    1: {"guards": 2, "guard_spd": 1.0, "vision_r": 80,  "snake_spd": 7,  "label": "ROUND 1"},
    2: {"guards": 3, "guard_spd": 1.2, "vision_r": 90,  "snake_spd": 8,  "label": "ROUND 2"},
    3: {"guards": 4, "guard_spd": 1.5, "vision_r": 100, "snake_spd": 9,  "label": "ROUND 3"},
    4: {"guards": 5, "guard_spd": 1.8, "vision_r": 110, "snake_spd": 10, "label": "ROUND 4"},
    5: {"guards": 6, "guard_spd": 2.2, "vision_r": 125, "snake_spd": 11, "label": "ROUND 5"},
}
MAX_ROUND = 5

# 방향
DIR_RIGHT = ( CELL,  0)
DIR_LEFT  = (-CELL,  0)
DIR_UP    = (0, -CELL)
DIR_DOWN  = (0,  CELL)

DIR_ANGLE = {
    DIR_RIGHT:   0,
    DIR_LEFT:  180,
    DIR_UP:     90,
    DIR_DOWN:  270,
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 지렁이의 탈출 : 보석 도둑 대작전")
clock  = pygame.time.Clock()

# 폰트
ft_title   = get_font(72, bold=True)
ft_title2  = get_font(36, bold=True)
ft_sub     = get_font(24, bold=True)
ft_small   = get_font(18, bold=True)
ft_hud     = get_font(22, bold=True)
ft_big     = get_font(64, bold=True)
ft_mid     = get_font(32, bold=True)
ft_btn     = get_font(24, bold=True)

# ══════════════════════════════════════════
#  스프라이트 / 사운드 로드
# ══════════════════════════════════════════
def load_img(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        return None

HEAD_IMG = load_img("player.png", (CELL, CELL))
BODY_IMG = load_img("body.png",   (CELL, CELL))
KEY_IMG  = load_img("key.png",    (CELL, CELL))
DIA_IMG  = load_img("dia.png",    (CELL, CELL))

try:
    EAT_SND = pygame.mixer.Sound("eat.wav")
except Exception:
    EAT_SND = None

# ══════════════════════════════════════════
#  유틸 함수
# ══════════════════════════════════════════
def grid_rect(gx, gy):
    """격자 좌표 → 화면 Rect"""
    return pygame.Rect(gx * CELL, PLAY_TOP + gy * CELL, CELL, CELL)

def grid_center(gx, gy):
    r = grid_rect(gx, gy)
    return r.centerx, r.centery

def random_grid_pos(occupied=None):
    while True:
        gx = random.randrange(1, COLS - 1)
        gy = random.randrange(1, ROWS - 1)
        if occupied is None or (gx, gy) not in occupied:
            return gx, gy

def snake_cells_set(snake):
    return set(snake)

def draw_text_centered(surf, text, font, color, cx, cy, outline=None, outline_w=2):
    if outline:
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx or dy:
                    s = font.render(text, True, outline)
                    surf.blit(s, (cx - s.get_width()//2 + dx, cy - s.get_height()//2 + dy))
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ══════════════════════════════════════════
#  타이틀 파티클
# ══════════════════════════════════════════
class GemParticle:
    COLORS = [(120,200,255),(180,240,255),(255,220,100),(100,255,180),(200,140,255)]
    def __init__(self):
        self.reset(init=True)

    def reset(self, init=False):
        self.x  = random.randint(0, WIDTH)
        self.y  = HEIGHT + 20 if not init else random.randint(0, HEIGHT)
        self.vy = random.uniform(-1.5, -0.5)
        self.vx = random.uniform(-0.4,  0.4)
        self.size = random.randint(3, 8)
        self.color = random.choice(self.COLORS)
        self.alpha = 255
        self.rot = random.randint(0, 360)
        self.rot_spd = random.uniform(-3, 3)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.rot += self.rot_spd
        self.alpha = max(0, self.alpha - 1)
        if self.y < -20 or self.alpha <= 0:
            self.reset()

    def draw(self, surf):
        s = self.size
        pts = []
        for i in range(8):
            r = s if i % 2 == 0 else s * 0.45
            a = math.radians(self.rot + i * 45)
            pts.append((self.x + r * math.cos(a), self.y + r * math.sin(a)))
        tmp = pygame.Surface((s*4, s*4), pygame.SRCALPHA)
        shifted = [(p[0]-self.x+s*2, p[1]-self.y+s*2) for p in pts]
        pygame.draw.polygon(tmp, (*self.color, self.alpha), shifted)
        surf.blit(tmp, (self.x - s*2, self.y - s*2))

PARTICLES = [GemParticle() for _ in range(60)]

# ══════════════════════════════════════════
#  타이틀 화면 (완전 새 디자인)
#  컨셉: 지하 금고 / 보석 도둑 / 누아르 + 형광
# ══════════════════════════════════════════
def title_screen():
    t = 0

    # 타이틀 뱀 (좌우 미끄러짐)
    worm_len = 12

    while True:
        dt = clock.tick(FPS)
        t += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        # ── 배경 ──
        screen.fill((5, 7, 14))

        # 그리드 패턴
        for gx in range(0, WIDTH, 30):
            pygame.draw.line(screen, (15, 18, 30), (gx, 0), (gx, HEIGHT))
        for gy in range(0, HEIGHT, 30):
            pygame.draw.line(screen, (15, 18, 30), (0, gy), (WIDTH, gy))

        # 파티클
        for p in PARTICLES:
            p.update()
            p.draw(screen)

        # 중앙 패널
        panel = pygame.Surface((820, 440), pygame.SRCALPHA)
        panel.fill((10, 14, 28, 200))
        pygame.draw.rect(panel, (60, 220, 255, 80), (0, 0, 820, 440), 2, border_radius=20)
        screen.blit(panel, (40, 100))

        # 금고 원형 장식
        cx, cy = WIDTH // 2, 200
        for r in range(90, 110, 5):
            alpha = 40 + (r - 90) * 8
            s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(s, (60, 220, 255, alpha), (r+2, r+2), r, 2)
            screen.blit(s, (cx - r - 2, cy - r - 2))

        # 자물쇠 아이콘 (간단히 그리기)
        lk_x, lk_y = cx - 22, cy - 30
        pygame.draw.rect(screen, (255, 210, 60), (lk_x, lk_y + 16, 44, 30), border_radius=6)
        pygame.draw.rect(screen, (200, 160, 20), (lk_x, lk_y + 16, 44, 30), 3, border_radius=6)
        pygame.draw.arc(screen, (255, 210, 60), (lk_x + 6, lk_y, 32, 32), 0, math.pi, 4)
        pygame.draw.circle(screen, (10, 12, 20), (cx, lk_y + 30), 7)

        # 메인 타이틀
        draw_text_centered(screen, "지렁이의  탈출", ft_title,
                           (60, 220, 255), cx, 340,
                           outline=(5, 30, 60), outline_w=4)

        draw_text_centered(screen, "— 보석 도둑 대작전 —", ft_sub,
                           (255, 210, 60), cx, 400)

        # 설명
        lines = [
            "🔑  열쇠를 먹어야  💎  보석을 획득할 수 있다",
            "👁  경비원의 시야를 피해  5라운드를 돌파하라!",
        ]
        for i, line in enumerate(lines):
            draw_text_centered(screen, line, ft_small, (160, 200, 220),
                               cx, 450 + i * 28)

        # 깜빡 시작 안내
        if (t // 35) % 2 == 0:
            draw_text_centered(screen, "[ SPACE ] 또는 [ ENTER ] 로 시작",
                               ft_sub, (60, 255, 160), cx, 530,
                               outline=(0, 40, 20), outline_w=2)

        # 하단 미끄러지는 뱀
        wx = (t * 3) % (WIDTH + worm_len * CELL * 2) - worm_len * CELL
        wy = HEIGHT - 35
        for bi in range(worm_len):
            bx = wx - bi * (CELL + 2)
            by_off = math.sin(t * 0.08 + bi * 0.5) * 10
            col = lerp_color((60, 220, 255), (100, 255, 160), bi / worm_len)
            if HEAD_IMG and bi == 0:
                screen.blit(HEAD_IMG, (int(bx), int(wy + by_off)))
            elif BODY_IMG and bi > 0:
                screen.blit(BODY_IMG, (int(bx), int(wy + by_off)))
            else:
                r = 10 if bi == 0 else 8
                pygame.draw.circle(screen, col, (int(bx + CELL//2), int(wy + by_off + CELL//2)), r)
                pygame.draw.circle(screen, COL_WHITE, (int(bx + CELL//2), int(wy + by_off + CELL//2)), r, 1)

        pygame.display.flip()

# ══════════════════════════════════════════
#  경비원 클래스
# ══════════════════════════════════════════
class Guard:
    def __init__(self, gx, gy, vision_r, speed):
        self.gx       = float(gx)
        self.gy       = float(gy)
        self.vision_r = vision_r   # 픽셀 단위
        self.speed    = speed      # 픽셀/프레임

        # 순찰 경로: 랜덤 웨이포인트
        self.waypoints = self._gen_waypoints()
        self.wp_idx    = 0
        self.timer     = 0         # 대기 타이머

        # 시각적 각도 (부드러운 회전용)
        self.angle     = random.uniform(0, 360)

    def _gen_waypoints(self):
        wps = []
        for _ in range(random.randint(3, 6)):
            wx = random.randint(2, COLS - 3)
            wy = random.randint(2, ROWS - 3)
            wps.append((float(wx), float(wy)))
        return wps

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            return

        tx, ty = self.waypoints[self.wp_idx]
        dx = tx - self.gx
        dy = ty - self.gy
        dist = math.hypot(dx, dy)

        move_px = self.speed  # 격자 단위 이동
        step = move_px / CELL

        if dist < 0.15:
            self.wp_idx = (self.wp_idx + 1) % len(self.waypoints)
            self.timer  = random.randint(20, 60)
        else:
            nx = dx / dist * min(step, dist)
            ny = dy / dist * min(step, dist)
            self.gx += nx
            self.gy += ny
            self.angle = math.degrees(math.atan2(dy, dx))

    def screen_pos(self):
        """격자 좌표 → 화면 중심 좌표"""
        sx = self.gx * CELL + CELL // 2
        sy = PLAY_TOP + self.gy * CELL + CELL // 2
        return int(sx), int(sy)

    def draw(self, surf):
        sx, sy = self.screen_pos()

        # 시야 원 (반투명)
        vision_surf = pygame.Surface((self.vision_r * 2 + 4,
                                      self.vision_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(vision_surf, (220, 80, 60, 28),
                           (self.vision_r + 2, self.vision_r + 2), self.vision_r)
        pygame.draw.circle(vision_surf, (220, 80, 60, 60),
                           (self.vision_r + 2, self.vision_r + 2), self.vision_r, 2)
        surf.blit(vision_surf, (sx - self.vision_r - 2, sy - self.vision_r - 2))

        # 경비원 몸체 (삼각형 방향 화살표 + 원)
        pygame.draw.circle(surf, (220, 80, 60), (sx, sy), 11)
        pygame.draw.circle(surf, (255, 130, 100), (sx, sy), 11, 2)

        # 방향 삼각형
        a = math.radians(self.angle)
        tip   = (sx + math.cos(a) * 14, sy + math.sin(a) * 14)
        left  = (sx + math.cos(a + 2.4) * 7, sy + math.sin(a + 2.4) * 7)
        right = (sx + math.cos(a - 2.4) * 7, sy + math.sin(a - 2.4) * 7)
        pygame.draw.polygon(surf, (255, 200, 180), [tip, left, right])

        # 눈 (흰 점)
        eye_x = sx + int(math.cos(a) * 5)
        eye_y = sy + int(math.sin(a) * 5)
        pygame.draw.circle(surf, COL_WHITE, (eye_x, eye_y), 3)

    def sees_point(self, wx, wy):
        """월드 격자 좌표 (wx, wy)가 시야 안에 있으면 True"""
        sx = self.gx * CELL + CELL // 2
        sy = self.gy * CELL + CELL // 2
        px = wx * CELL + CELL // 2
        py = wy * CELL + CELL // 2
        return math.hypot(px - sx, py - sy) <= self.vision_r

    def sees_pixel(self, px, py):
        """픽셀 좌표가 시야 안에 있으면 True"""
        sx, sy = self.screen_pos()
        return math.hypot(px - sx, py - sy) <= self.vision_r

# ══════════════════════════════════════════
#  게임 그리기 유틸
# ══════════════════════════════════════════
def draw_grid_bg():
    screen.fill(BG_DARK)
    for gx in range(COLS):
        for gy in range(ROWS):
            r = grid_rect(gx, gy)
            shade = (gx + gy) % 2
            c = (12, 15, 26) if shade == 0 else (14, 18, 30)
            pygame.draw.rect(screen, c, r)
    # 경계선
    for gx in range(COLS):
        pygame.draw.line(screen, COL_GRID,
                         (gx * CELL, PLAY_TOP), (gx * CELL, HEIGHT))
    for gy in range(ROWS):
        pygame.draw.line(screen, COL_GRID,
                         (0, PLAY_TOP + gy * CELL), (WIDTH, PLAY_TOP + gy * CELL))

    # 외벽 테두리
    pygame.draw.rect(screen, (60, 220, 255),
                     (0, PLAY_TOP, WIDTH, PLAY_H), 3)

def draw_hud(score, round_num, has_key):
    pygame.draw.rect(screen, COL_HUD_BG, (0, 0, WIDTH, HUD_H))
    pygame.draw.line(screen, (60, 220, 255), (0, HUD_H), (WIDTH, HUD_H), 2)

    cfg = ROUND_CONFIG[round_num]

    # 라운드
    draw_text_centered(screen, cfg["label"], ft_hud, (60, 220, 255),
                       80, HUD_H // 2)

    # 점수
    draw_text_centered(screen, f"SCORE  {score:04d}", ft_hud, COL_YELLOW,
                       WIDTH // 2, HUD_H // 2)

    # 열쇠 상태
    key_col  = (255, 210, 60)  if has_key  else (80, 80, 80)
    key_text = "🔑 KEY  ✔" if has_key else "🔑 KEY  ✘"
    draw_text_centered(screen, key_text, ft_hud, key_col,
                       WIDTH - 140, HUD_H // 2)

def draw_snake(snake, direction):
    for i, (gx, gy) in enumerate(snake):
        r = grid_rect(gx, gy)
        if i == 0:
            if HEAD_IMG:
                angle   = DIR_ANGLE.get(direction, 0)
                rotated = pygame.transform.rotate(HEAD_IMG, angle)
                screen.blit(rotated, r.topleft)
            else:
                col = (60, 220, 255)
                pygame.draw.rect(screen, col, r.inflate(-2, -2), border_radius=6)
                pygame.draw.rect(screen, COL_WHITE, r.inflate(-2, -2), 1, border_radius=6)
        else:
            if BODY_IMG:
                screen.blit(BODY_IMG, r.topleft)
            else:
                t = i / max(len(snake) - 1, 1)
                col = lerp_color((60, 220, 255), (40, 140, 80), t)
                pygame.draw.rect(screen, col, r.inflate(-2, -2), border_radius=5)

def draw_item(surf, gx, gy, img, fallback_color, fallback_r=8):
    r = grid_rect(gx, gy)
    if img:
        surf.blit(img, r.topleft)
    else:
        cx, cy = r.centerx, r.centery
        pygame.draw.circle(surf, fallback_color, (cx, cy), fallback_r)
        pygame.draw.circle(surf, COL_WHITE, (cx, cy), fallback_r, 2)

# ══════════════════════════════════════════
#  게임 오버 / 라운드 클리어 / 엔딩 화면
# ══════════════════════════════════════════
def overlay_screen(title_txt, title_col, sub_lines, btn_labels):
    """
    범용 결과 화면
    btn_labels: list of str (최대 2개)
    반환: 선택된 인덱스 (0 or 1)
    """
    BTN_W, BTN_H = 240, 52
    mid_x = WIDTH // 2
    mid_y = HEIGHT // 2

    n = len(btn_labels)
    total_w = n * BTN_W + (n - 1) * 20
    btn_rects = []
    for i in range(n):
        bx = mid_x - total_w // 2 + i * (BTN_W + 20)
        btn_rects.append(pygame.Rect(bx, mid_y + 80, BTN_W, BTN_H))

    selected = 0
    t = 0

    while True:
        clock.tick(FPS)
        t += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_RIGHT) and n > 1:
                    selected = 1 - selected
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEMOTION:
                for i, r in enumerate(btn_rects):
                    if r.collidepoint(e.pos):
                        selected = i
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(btn_rects):
                    if r.collidepoint(e.pos):
                        return i

        # 배경 (현재 화면 위 오버레이)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        # 제목
        draw_text_centered(screen, title_txt, ft_big, title_col,
                           mid_x, mid_y - 100, outline=(0, 0, 0), outline_w=4)

        # 부제
        for i, line in enumerate(sub_lines):
            draw_text_centered(screen, line, ft_sub, (200, 220, 255),
                               mid_x, mid_y - 20 + i * 32)

        # 버튼
        for i, (r, label) in enumerate(zip(btn_rects, btn_labels)):
            active = (i == selected)
            bcol   = (60, 180, 255) if active else (30, 40, 70)
            border = (120, 220, 255) if active else (60, 80, 120)
            pygame.draw.rect(screen, bcol, r, border_radius=12)
            pygame.draw.rect(screen, border, r, 2, border_radius=12)
            if active and (t // 25) % 2 == 0:
                glow = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 30))
                screen.blit(glow, r.topleft)
            draw_text_centered(screen, label, ft_btn,
                               COL_WHITE if active else (120, 140, 180),
                               r.centerx, r.centery)

        # 조작 힌트
        draw_text_centered(screen, "← →  이동  /  ENTER  확인  /  Q  종료",
                           ft_small, (100, 120, 160),
                           mid_x, mid_y + 150)

        pygame.display.flip()

# ══════════════════════════════════════════
#  라운드 시작 연출
# ══════════════════════════════════════════
def round_intro(round_num):
    cfg = ROUND_CONFIG[round_num]
    for frame in range(90):
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        alpha = min(255, frame * 6)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, max(0, 200 - frame * 4)))
        screen.blit(s, (0, 0))

        draw_text_centered(screen, cfg["label"], ft_big, (60, 220, 255),
                           WIDTH // 2, HEIGHT // 2 - 50,
                           outline=(0, 20, 50), outline_w=5)
        draw_text_centered(screen, f"경비원 {cfg['guards']}명  |  시야 반경 {cfg['vision_r']}px",
                           ft_sub, (200, 200, 255),
                           WIDTH // 2, HEIGHT // 2 + 20)
        draw_text_centered(screen, "🔑 열쇠 → 💎 보석 → 다음 라운드",
                           ft_sub, (255, 210, 60),
                           WIDTH // 2, HEIGHT // 2 + 60)

        if frame > 50 and (frame // 20) % 2 == 0:
            draw_text_centered(screen, "SPACE 또는 ENTER 로 시작",
                               ft_small, (120, 200, 120),
                               WIDTH // 2, HEIGHT // 2 + 110)

        pygame.display.flip()

        if frame > 50:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                return

# ══════════════════════════════════════════
#  라운드 게임 루프
#  반환값: "next" | "gameover" | "quit"
# ══════════════════════════════════════════
def play_round(round_num, score):
    cfg = ROUND_CONFIG[round_num]

    # ── 초기화 ──
    start_gx = COLS // 2
    start_gy = ROWS // 2
    snake     = [(start_gx - i, start_gy) for i in range(5)]   # 길이 5
    direction = DIR_RIGHT
    next_dir  = DIR_RIGHT

    has_key   = False
    occupied  = snake_cells_set(snake)

    # 열쇠 위치
    key_pos = random_grid_pos(occupied)
    occupied.add(key_pos)

    # 보석 위치 (처음엔 잠김 - has_key=False)
    dia_pos = random_grid_pos(occupied)
    occupied.add(dia_pos)

    # 경비원 생성 (뱀 근처 제외)
    guards = []
    guard_occ = snake_cells_set(snake) | {key_pos, dia_pos}
    for _ in range(cfg["guards"]):
        while True:
            gx = random.randint(2, COLS - 3)
            gy = random.randint(2, ROWS - 3)
            # 뱀 머리에서 10칸 이상 떨어진 위치
            if math.hypot(gx - start_gx, gy - start_gy) > 10:
                break
        guards.append(Guard(gx, gy, cfg["vision_r"], cfg["guard_spd"]))

    # 이동 타이머
    move_timer   = 0
    move_interval = FPS / cfg["snake_spd"]  # 프레임 단위

    while True:
        dt = clock.tick(FPS)
        move_timer += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP    and direction != DIR_DOWN:  next_dir = DIR_UP
                if e.key == pygame.K_DOWN  and direction != DIR_UP:    next_dir = DIR_DOWN
                if e.key == pygame.K_LEFT  and direction != DIR_RIGHT: next_dir = DIR_LEFT
                if e.key == pygame.K_RIGHT and direction != DIR_LEFT:  next_dir = DIR_RIGHT
                if e.key == pygame.K_ESCAPE:
                    return "quit"

        # ── 경비원 업데이트 ──
        for g in guards:
            g.update()

        # ── 뱀 이동 ──
        if move_timer >= move_interval:
            move_timer = 0
            direction  = next_dir

            hx = snake[0][0] + direction[0] // CELL
            hy = snake[0][1] + direction[1] // CELL

            # 벽 충돌
            if hx < 0 or hx >= COLS or hy < 0 or hy >= ROWS:
                # 게임 오버 연출 후 반환
                _draw_game(screen, snake, direction, guards, key_pos,
                           dia_pos, has_key, score, round_num)
                pygame.display.flip()
                result = overlay_screen(
                    "GAME  OVER", COL_RED,
                    [f"Score : {score}", "벽에 부딪혔다!"],
                    ["▶  다시 시작  [R]", "★  타이틀로  [T]"]
                )
                return "gameover" if result == 0 else "title"

            # 자기 몸 충돌
            if (hx, hy) in snake[:-1]:
                _draw_game(screen, snake, direction, guards, key_pos,
                           dia_pos, has_key, score, round_num)
                pygame.display.flip()
                result = overlay_screen(
                    "GAME  OVER", COL_RED,
                    [f"Score : {score}", "자기 몸을 깨물었다!"],
                    ["▶  다시 시작  [R]", "★  타이틀로  [T]"]
                )
                return "gameover" if result == 0 else "title"

            head = (hx, hy)

            # 먹이 획득
            grew = False
            if not has_key and head == key_pos:
                # 열쇠 획득
                has_key = True
                score  += 50
                if EAT_SND: EAT_SND.play()
                grew = True
                # 새 열쇠 위치 (보석 먹을 때 다음 라운드 → 불필요, 그냥 재배치)
                key_pos = None

            elif has_key and head == dia_pos:
                # 보석 획득 → 라운드 클리어
                score += 200
                if EAT_SND: EAT_SND.play()
                _draw_game(screen, snake, direction, guards, key_pos,
                           dia_pos, has_key, score, round_num)
                pygame.display.flip()

                if round_num < MAX_ROUND:
                    result = overlay_screen(
                        "ROUND  CLEAR!", (60, 255, 160),
                        [f"Score : {score}", f"ROUND {round_num} 완료!  다음 라운드로 이동"],
                        ["▶  다음 라운드"]
                    )
                    return "next"
                else:
                    result = overlay_screen(
                        "🏆  탈출 성공!  🏆", COL_YELLOW,
                        [f"최종 Score : {score}", "모든 라운드를 클리어했다!"],
                        ["★  타이틀로"]
                    )
                    return "title"

            snake.insert(0, head)
            if not grew:
                snake.pop()

        # ── 경비원 시야 감지 ──
        hx, hy = snake[0]
        head_px = hx * CELL + CELL // 2
        head_py = PLAY_TOP + hy * CELL + CELL // 2
        for g in guards:
            if g.sees_pixel(head_px, head_py):
                _draw_game(screen, snake, direction, guards, key_pos,
                           dia_pos, has_key, score, round_num)
                pygame.display.flip()
                result = overlay_screen(
                    "CAUGHT!", COL_RED,
                    [f"Score : {score}", "경비원에게 발각됐다!"],
                    ["▶  다시 시작", "★  타이틀로"]
                )
                return "gameover" if result == 0 else "title"

        # ── 그리기 ──
        _draw_game(screen, snake, direction, guards, key_pos,
                   dia_pos, has_key, score, round_num)
        pygame.display.flip()

    return "quit"


def _draw_game(surf, snake, direction, guards, key_pos, dia_pos, has_key, score, round_num):
    draw_grid_bg()

    # 경비원 시야 + 몸체
    for g in guards:
        g.draw(surf)

    # 열쇠 (미획득시)
    if key_pos:
        draw_item(surf, key_pos[0], key_pos[1], KEY_IMG, COL_KEY)

    # 보석 (열쇠 있을 때 강조, 없을 때 어둡게)
    if dia_pos:
        if has_key:
            draw_item(surf, dia_pos[0], dia_pos[1], DIA_IMG, COL_DIA)
            # 보석 강조 테두리
            r = grid_rect(dia_pos[0], dia_pos[1])
            t = pygame.time.get_ticks() // 200 % 8
            glow_col = (60 + t * 20, 180 + t * 8, 255)
            pygame.draw.rect(surf, glow_col, r.inflate(4, 4), 2, border_radius=4)
        else:
            # 열쇠 없을 때 보석 회색 처리
            r = grid_rect(dia_pos[0], dia_pos[1])
            if DIA_IMG:
                dark = DIA_IMG.copy()
                dark.fill((80, 80, 80, 180), special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(dark, r.topleft)
            else:
                pygame.draw.circle(surf, (60, 60, 80),
                                   (r.centerx, r.centery), 8)
            pygame.draw.rect(surf, (60, 60, 80), r.inflate(2, 2), 1, border_radius=3)

    # 뱀
    draw_snake(snake, direction)

    # HUD
    draw_hud(score, round_num, has_key)

# ══════════════════════════════════════════
#  메인 진입점
# ══════════════════════════════════════════
def main():
    score     = 0
    round_num = 1

    while True:
        title_screen()

        score     = 0
        round_num = 1

        while round_num <= MAX_ROUND:
            round_intro(round_num)

            # 라운드 플레이
            result = play_round(round_num, score)

            if result == "next":
                round_num += 1
                score_bonus = round_num * 100
            elif result == "gameover":
                # 점수 유지하고 같은 라운드 재시작
                break
            elif result == "title":
                break
            elif result == "quit":
                pygame.quit(); sys.exit()

        # title로 돌아가면 다시 루프
        # (while True 로 타이틀 재시작)

if __name__ == "__main__":
    main()