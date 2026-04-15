import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

# ── 화면 설정 ──
WIDTH, HEIGHT = 800, 600
CELL = 20
FPS_TITLE = 60
FPS_GAME  = 12

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("평범한 뱀이었던 내가 알고 보니 공주를 구할 기사?")
clock = pygame.time.Clock()

# ── 색상 팔레트 (이세계 판타지) ──
C_BG_TOP      = (8,  4, 28)
C_BG_MID      = (20, 8, 50)
C_BG_BOT      = (10, 25, 10)
C_GOLD        = (255, 215, 0)
C_GOLD_DIM    = (180, 140, 0)
C_PURPLE      = (160, 80, 255)
C_PURPLE_DIM  = (100, 50, 180)
C_STAR        = (220, 200, 255)
C_WHITE       = (255, 255, 255)
C_RED         = (220, 60, 60)
C_GREEN_HEAD  = (60, 220, 80)
C_GREEN_BODY  = (40, 170, 55)
C_GREEN_DARK  = (25, 110, 35)
C_FOOD        = (255, 80,  80)
C_FOOD2       = (255, 180,  0)  # 보너스 아이템
C_GRID        = (20, 15, 45)
C_CASTLE      = (30, 20, 60)
C_CASTLE_LIT  = (255, 220, 100)
C_HUD_BG      = (15, 8, 40, 180)
C_BOSS        = (180, 30, 30)

TARGET_SCORE = 1000

# ── 폰트 로드 ──
def get_korean_font(size, bold=False):
    candidates = ["malgungothicbold" if bold else "malgungothic",
                  "applegothic", "nanumgothicbold" if bold else "nanumgothic",
                  "notosanscjk"]
    for name in candidates:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font.get_ascent() > 0:
                return font
        except Exception:
            pass
    return pygame.font.SysFont(None, size, bold=bold)

font_title_big  = get_korean_font(28, bold=True)
font_title_sub  = get_korean_font(16)
font_title_tag  = get_korean_font(13)
font_hud        = get_korean_font(20, bold=True)
font_hud_sm     = get_korean_font(15)
font_msg        = get_korean_font(52, bold=True)
font_msg_sub    = get_korean_font(22)

# ── 사운드 (없으면 무시) ──
def try_load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

SND_EAT   = try_load_sound("eat.wav")
SND_MISS  = try_load_sound("miss.wav")
SND_CLEAR = try_load_sound("clear.wav")

def play(snd):
    if snd:
        snd.play()

# ══════════════════════════════════════════
#  별 / 파티클 시스템
# ══════════════════════════════════════════
class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT * 2 // 3)
        self.r = random.uniform(0.5, 2.2)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.02, 0.06)

    def draw(self, surf, t):
        alpha = int(140 + 100 * math.sin(self.phase + t * self.speed))
        c = (min(255, C_STAR[0]), min(255, C_STAR[1]), min(255, C_STAR[2]))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), int(self.r))

STARS = [Star() for _ in range(90)]

class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.randint(18, 35)
        self.max_life = self.life
        self.r = random.randint(2, 5)
        self.color = color

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha_ratio = self.life / self.max_life
        r = int(self.color[0] * alpha_ratio)
        g = int(self.color[1] * alpha_ratio)
        b = int(self.color[2] * alpha_ratio)
        pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), self.r)

particles = []

def spawn_particles(x, y, color, count=12):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# ══════════════════════════════════════════
#  배경 렌더 함수
# ══════════════════════════════════════════
def draw_sky(surf):
    # 위에서 아래로 그라데이션 (세그먼트)
    segs = 30
    for i in range(segs):
        ratio = i / segs
        if ratio < 0.6:
            t = ratio / 0.6
            r = int(C_BG_TOP[0] + (C_BG_MID[0] - C_BG_TOP[0]) * t)
            g = int(C_BG_TOP[1] + (C_BG_MID[1] - C_BG_TOP[1]) * t)
            b = int(C_BG_TOP[2] + (C_BG_MID[2] - C_BG_TOP[2]) * t)
        else:
            t = (ratio - 0.6) / 0.4
            r = int(C_BG_MID[0] + (C_BG_BOT[0] - C_BG_MID[0]) * t)
            g = int(C_BG_MID[1] + (C_BG_BOT[1] - C_BG_MID[1]) * t)
            b = int(C_BG_MID[2] + (C_BG_BOT[2] - C_BG_MID[2]) * t)
        y0 = int(HEIGHT * ratio)
        y1 = int(HEIGHT * (ratio + 1/segs)) + 1
        pygame.draw.rect(surf, (r, g, b), (0, y0, WIDTH, y1 - y0))

def draw_castle_silhouette(surf):
    # 성 실루엣 (우측 배경)
    cx = 600
    base_y = HEIGHT - 80
    c = C_CASTLE

    def rect(x, y, w, h):
        pygame.draw.rect(surf, c, (cx + x, y, w, h))

    def tower(x, tw, th, mh=20, mw=8):
        rect(x, base_y - th, tw, th)
        # 성벽 총안구
        for mx in range(x, x + tw, mw + 4):
            rect(mx, base_y - th - mh, mw, mh)

    tower(-80, 30, 120, 25, 7)
    tower(50,  30, 140, 28, 7)
    tower(-20, 20,  80, 20, 6)
    pygame.draw.rect(surf, c, (cx - 80, base_y - 80, 160, 80))  # 본체

    # 창문 빛
    for wx, wy in [(-50, base_y - 110), (30, base_y - 130), (-10, base_y - 60)]:
        pygame.draw.rect(surf, C_CASTLE_LIT, (cx + wx, wy, 10, 14))

def draw_ground(surf):
    # 풀밭 지면
    pygame.draw.rect(surf, (15, 50, 15), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.rect(surf, (20, 70, 20), (0, HEIGHT - 62, WIDTH, 8))
    # 풀 디테일
    for gx in range(0, WIDTH, 18):
        h = random.randint(4, 10) if (gx // 18) % 3 == 0 else 4
        pygame.draw.line(surf, (30, 100, 30),
                         (gx, HEIGHT - 62), (gx + 3, HEIGHT - 62 - h), 1)

# 지면은 매 프레임 재생성하면 깜빡임 → 미리 구워두기
ground_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
draw_ground(ground_surf)

def draw_game_grid(surf):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(surf, C_GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(surf, C_GRID, (0, y), (WIDTH, y), 1)

# ══════════════════════════════════════════
#  HUD 렌더
# ══════════════════════════════════════════
def draw_hud(surf, score, length):
    # 반투명 상단 바
    hud = pygame.Surface((WIDTH, 44), pygame.SRCALPHA)
    hud.fill((10, 5, 30, 200))
    surf.blit(hud, (0, 0))

    # 점수 게이지 바
    bar_x, bar_y, bar_w, bar_h = 10, 6, 260, 12
    pygame.draw.rect(surf, (40, 20, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    fill_w = int(bar_w * min(score / TARGET_SCORE, 1.0))
    if fill_w > 0:
        gc = C_GOLD if score < TARGET_SCORE else C_RED
        pygame.draw.rect(surf, gc, (bar_x, bar_y, fill_w, bar_h), border_radius=6)
    pygame.draw.rect(surf, C_GOLD_DIM, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

    score_txt = font_hud.render(f"  {score} / {TARGET_SCORE}", True, C_GOLD)
    surf.blit(score_txt, (bar_x + bar_w + 6, 2))

    len_txt = font_hud_sm.render(f"길이: {length}", True, C_PURPLE)
    surf.blit(len_txt, (WIDTH - 100, 10))

    title_txt = font_hud_sm.render("공주를 구출하라!", True, C_STAR)
    surf.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 10))

# ══════════════════════════════════════════
#  뱀 렌더
# ══════════════════════════════════════════
DIR_ANGLE = {
    ( CELL,  0): 0,
    (-CELL,  0): 180,
    (0, -CELL): 90,
    (0,  CELL): 270,
}

def draw_snake(surf, snake, direction):
    for i, seg in enumerate(snake):
        if i == 0:
            # 머리: 눈 그리기
            pygame.draw.rect(surf, C_GREEN_HEAD,
                             (*seg, CELL, CELL), border_radius=5)
            pygame.draw.rect(surf, C_GREEN_DARK,
                             (*seg, CELL, CELL), 1, border_radius=5)
            # 눈
            dx, dy = direction
            ex1 = seg[0] + CELL//2 + dy * 4 - 2
            ey1 = seg[1] + CELL//2 - dx * 4 - 2
            ex2 = seg[0] + CELL//2 - dy * 4 - 2
            ey2 = seg[1] + CELL//2 + dx * 4 - 2
            pygame.draw.circle(surf, C_WHITE, (ex1, ey1), 3)
            pygame.draw.circle(surf, C_WHITE, (ex2, ey2), 3)
            pygame.draw.circle(surf, (0, 0, 0), (ex1, ey1), 1)
            pygame.draw.circle(surf, (0, 0, 0), (ex2, ey2), 1)
        else:
            ratio = 1 - (i / max(len(snake), 1)) * 0.4
            rc = (int(C_GREEN_BODY[0]*ratio), int(C_GREEN_BODY[1]*ratio), int(C_GREEN_BODY[2]*ratio))
            pygame.draw.rect(surf, rc,
                             (seg[0]+1, seg[1]+1, CELL-2, CELL-2), border_radius=4)
            pygame.draw.rect(surf, C_GREEN_DARK,
                             (seg[0]+1, seg[1]+1, CELL-2, CELL-2), 1, border_radius=4)

# ══════════════════════════════════════════
#  먹이 렌더
# ══════════════════════════════════════════
def draw_food(surf, food, bonus_food, t):
    # 일반 먹이 (빨간 사과 느낌)
    pulse = int(3 * math.sin(t * 0.08))
    fx, fy = food
    pygame.draw.circle(surf, C_FOOD,
                       (fx + CELL//2, fy + CELL//2), CELL//2 - 1 + pulse)
    pygame.draw.circle(surf, (255, 150, 150),
                       (fx + CELL//2 - 2, fy + CELL//2 - 3), 3)

    if bonus_food:
        bx, by = bonus_food
        spin = int(4 * math.sin(t * 0.12))
        pygame.draw.rect(surf, C_FOOD2,
                         (bx + 2 + spin, by + 2, CELL-4, CELL-4), border_radius=4)
        star = font_hud_sm.render("★", True, (255, 255, 200))
        surf.blit(star, (bx + 2, by + 1))

# ══════════════════════════════════════════
#  타이틀 화면
# ══════════════════════════════════════════
def title_screen():
    t = 0
    while True:
        clock.tick(FPS_TITLE)
        t += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        # 배경
        draw_sky(screen)
        for s in STARS:
            s.draw(screen, t)
        draw_castle_silhouette(screen)
        screen.blit(ground_surf, (0, 0))

        # 타이틀 패널
        panel_w, panel_h = 680, 320
        panel_x = (WIDTH - panel_w) // 2
        panel_y = 100
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 5, 35, 200))
        pygame.draw.rect(panel, C_GOLD_DIM, (0, 0, panel_w, panel_h), 1, border_radius=12)
        screen.blit(panel, (panel_x, panel_y))

        # 황금 장식선
        glow = abs(math.sin(t * 0.04))
        gc = (int(255 * glow), int(180 * glow), 0)
        pygame.draw.line(screen, gc, (panel_x + 20, panel_y + 12),
                         (panel_x + panel_w - 20, panel_y + 12), 1)
        pygame.draw.line(screen, gc, (panel_x + 20, panel_y + panel_h - 12),
                         (panel_x + panel_w - 20, panel_y + panel_h - 12), 1)

        # 부제목
        tag = font_title_tag.render("~ 이세계 뱀 기사단 ~", True, C_PURPLE)
        screen.blit(tag, (WIDTH//2 - tag.get_width()//2, panel_y + 22))

        # 메인 타이틀 (3줄)
        lines = [
            "평범한 뱀이었던 내가",
            "알고 보니 공주를 구할 기사?",
        ]
        for i, line in enumerate(lines):
            wave = int(3 * math.sin(t * 0.05 + i * 1.2))
            gold_glow = (int(200 + 55 * abs(math.sin(t*0.04 + i*0.5))),
                         int(180 + 35 * abs(math.sin(t*0.04 + i*0.5))), 0)
            txt = font_title_big.render(line, True, gold_glow)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, panel_y + 55 + i * 38 + wave))

        sub = font_title_sub.render("~ 1000점 모아 보스를 물리치고 해피엔딩을 맞이하겠어 ~",
                                    True, (160, 200, 255))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, panel_y + 140))

        # 아이콘 줄
        icons = [("🐍", "용감한 기사"), ("👸", "공주님"), ("🐉", "최종 보스")]
        icon_y = panel_y + 178
        for idx, (icon, label) in enumerate(icons):
            ix = panel_x + 120 + idx * 200
            box = pygame.Surface((130, 60), pygame.SRCALPHA)
            box.fill((30, 15, 70, 180))
            pygame.draw.rect(box, C_PURPLE_DIM, (0, 0, 130, 60), 1, border_radius=8)
            screen.blit(box, (ix, icon_y))
            icon_surf = font_msg_sub.render(icon, True, C_WHITE)
            screen.blit(icon_surf, (ix + 10, icon_y + 8))
            lbl = font_title_tag.render(label, True, C_STAR)
            screen.blit(lbl, (ix + 42, icon_y + 18))

        # 목표 텍스트
        goal = font_title_tag.render("목표 점수: 1000점  |  난이도: Hard", True,
                                     (180, 160, 220))
        screen.blit(goal, (WIDTH//2 - goal.get_width()//2, panel_y + 254))

        # START 버튼 (깜빡)
        if (t // 25) % 2 == 0:
            btn_surf = font_hud.render("▶  SPACE / ENTER 로 모험 시작", True, C_GOLD)
            screen.blit(btn_surf, (WIDTH//2 - btn_surf.get_width()//2, panel_y + 280))

        # 하단 뱀 애니메이션
        sx = (t * 3) % (WIDTH + 80) - 80
        sy = HEIGHT - 30
        for bi in range(5):
            bx = sx - bi * CELL
            if 0 <= bx <= WIDTH:
                col = C_GREEN_HEAD if bi == 0 else C_GREEN_BODY
                pygame.draw.rect(screen, col, (bx, sy, CELL-2, CELL-2), border_radius=4)

        pygame.display.flip()

# ══════════════════════════════════════════
#  게임 오버 / 클리어 화면
# ══════════════════════════════════════════
def result_screen(win, score):
    t = 0
    title_txt = "해피엔딩!" if win else "GAME OVER"
    title_col = C_GOLD if win else C_RED
    while True:
        clock.tick(FPS_TITLE)
        t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        draw_sky(screen)
        for s in STARS:
            s.draw(screen, t)
        draw_castle_silhouette(screen)
        screen.blit(ground_surf, (0, 0))

        if win:
            for _ in range(3):
                spawn_particles(random.randint(100, 700),
                                random.randint(150, 350), C_GOLD, 4)
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        wave = int(5 * math.sin(t * 0.07))
        title = font_msg.render(title_txt, True, title_col)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 180 + wave))

        if win:
            msg = font_msg_sub.render("공주님을 구출했다! 두 사람은 행복하게 살았답니다 ♥", True, C_STAR)
        else:
            msg = font_msg_sub.render("기사님... 다시 도전해보겠습니까?", True, C_STAR)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 260))

        score_txt = font_hud.render(f"최종 점수: {score}", True, C_GOLD)
        screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 310))

        hint = font_title_sub.render("R: 다시 도전   Q: 종료", True, (180, 160, 220))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 360))

        pygame.display.flip()

# ══════════════════════════════════════════
#  유틸
# ══════════════════════════════════════════
def new_food(snake, exclude=None):
    occupied = set(snake)
    if exclude:
        occupied.add(exclude)
    while True:
        pos = (
            random.randrange(0, WIDTH  // CELL) * CELL,
            random.randrange(2, (HEIGHT - 60) // CELL) * CELL,  # HUD/지면 피함
        )
        if pos not in occupied:
            return pos

# ══════════════════════════════════════════
#  메인 게임 루프
# ══════════════════════════════════════════
def main():
    snake     = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    next_dir  = (CELL, 0)
    food      = new_food(snake)
    bonus_food = None
    bonus_timer = 0
    score     = 0
    t         = 0
    launched  = False

    # 배경 서피스 (매 프레임 하늘 다시 안 그리게)
    bg = pygame.Surface((WIDTH, HEIGHT))
    draw_sky(bg)
    for s in STARS:
        s.draw(bg, 0)
    draw_castle_silhouette(bg)

    while True:
        clock.tick(FPS_GAME)
        t += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not launched:
                    launched = True
                if e.key == pygame.K_UP    and direction != (0,  CELL): next_dir = (0, -CELL)
                if e.key == pygame.K_DOWN  and direction != (0, -CELL): next_dir = (0,  CELL)
                if e.key == pygame.K_LEFT  and direction != (CELL,  0): next_dir = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0): next_dir = ( CELL, 0)
                if e.key == pygame.K_w     and direction != (0,  CELL): next_dir = (0, -CELL)
                if e.key == pygame.K_s     and direction != (0, -CELL): next_dir = (0,  CELL)
                if e.key == pygame.K_a     and direction != (CELL,  0): next_dir = (-CELL, 0)
                if e.key == pygame.K_d     and direction != (-CELL, 0): next_dir = ( CELL, 0)

        # ── 배경 ──
        screen.blit(bg, (0, 0))
        # 별 반짝임
        for s in STARS:
            s.draw(screen, t)
        screen.blit(ground_surf, (0, 0))
        draw_game_grid(screen)

        # ── 발사 전 대기 ──
        if not launched:
            draw_food(screen, food, bonus_food, t)
            draw_snake(screen, snake, direction)
            draw_hud(screen, score, len(snake))
            prompt = font_hud_sm.render("SPACE 로 출발!", True, C_GOLD)
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 40))
            pygame.display.flip()
            continue

        direction = next_dir
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # ── 충돌 판정 ──
        dead = (
            head[0] < 0 or head[0] >= WIDTH or
            head[1] < CELL * 2 or head[1] >= HEIGHT - 60 or
            head in snake
        )
        if dead:
            play(SND_MISS)
            if result_screen(False, score):
                main()
            return

        snake.insert(0, head)

        ate = False
        # 일반 먹이
        if head == food:
            play(SND_EAT)
            score += 10
            ate = True
            food = new_food(snake, bonus_food)
            spawn_particles(head[0] + CELL//2, head[1] + CELL//2, C_FOOD)
            # 보너스 아이템 20% 확률 스폰
            if bonus_food is None and random.random() < 0.2:
                bonus_food = new_food(snake, food)
                bonus_timer = 60  # 60틱 후 사라짐
        # 보너스 먹이
        elif bonus_food and head == bonus_food:
            play(SND_EAT)
            score += 30
            ate = True
            spawn_particles(head[0] + CELL//2, head[1] + CELL//2, C_FOOD2, 18)
            bonus_food = None
            bonus_timer = 0

        if not ate:
            snake.pop()

        # 보너스 타이머
        if bonus_food:
            bonus_timer -= 1
            if bonus_timer <= 0:
                bonus_food = None

        # ── 파티클 ──
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        # ── 렌더 ──
        draw_food(screen, food, bonus_food, t)
        draw_snake(screen, snake, direction)
        draw_hud(screen, score, len(snake))

        # ── 클리어 판정 ──
        if score >= TARGET_SCORE:
            play(SND_CLEAR)
            # 마지막 프레임 한번 더 그리기
            pygame.display.flip()
            pygame.time.wait(500)
            if result_screen(True, score):
                main()
            return

        pygame.display.flip()

# ══════════════════════════════════════════
#  엔트리포인트
# ══════════════════════════════════════════
title_screen()
main()