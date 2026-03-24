import pygame
import sys
import math

# 초기화
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB + Circle 충돌 감지 데모")

clock = pygame.time.Clock()
FPS = 60
SPEED = 4

# 색상
BG_COLOR       = (30, 30, 40)
BG_CIRCLE_HIT  = (60, 55, 10)   # 원형 충돌 시 배경
RECT_COLOR     = (140, 140, 160)
AABB_COLOR     = (220, 50,  50)
CIRCLE_COLOR   = (80, 140, 240)  # 파란 원
OVERLAP_COLOR  = (255, 200,  0)
CIRCLE_HIT_COLOR = (255, 220, 0) # 원형 충돌 시 색
TEXT_COLOR     = (220, 220, 240)
GRID_COLOR     = (40,  40,  55)

# 폰트
font_small = pygame.font.SysFont("consolas", 16)
font_big   = pygame.font.SysFont("consolas", 22, bold=True)

# ── 오브젝트 정의 ──────────────────────────────────────────
player = pygame.Rect(100, 100, 80, 60)
fixed  = pygame.Rect(0, 0, 120, 90)
fixed.center = (WIDTH // 2, HEIGHT // 2)

def get_circle(rect):
    """오브젝트의 중심 좌표와 반지름(너비 절반) 반환"""
    cx = rect.centerx
    cy = rect.centery
    r  = rect.width // 2
    return cx, cy, r

def circle_collide(r1, r2):
    """두 원의 충돌 감지: 중심 거리 < 반지름 합"""
    cx1, cy1, rad1 = get_circle(r1)
    cx2, cy2, rad2 = get_circle(r2)
    dist = math.hypot(cx2 - cx1, cy2 - cy1)
    return dist < (rad1 + rad2), dist, rad1 + rad2

def draw_grid():
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_aabb(rect, color, label=""):
    pygame.draw.rect(screen, color, rect, 2)
    size = 6
    corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
    for cx, cy in corners:
        pygame.draw.line(screen, color, (cx - size, cy), (cx + size, cy), 2)
        pygame.draw.line(screen, color, (cx, cy - size), (cx, cy + size), 2)
    if label:
        lbl = font_small.render(label, True, color)
        screen.blit(lbl, (rect.left, rect.top - 20))

def draw_circle_bb(rect, hit):
    """원형 Bounding Box 그리기"""
    cx, cy, r = get_circle(rect)
    color = CIRCLE_HIT_COLOR if hit else CIRCLE_COLOR
    # 반투명 채우기
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    alpha = 50 if hit else 30
    pygame.draw.circle(surf, (*color, alpha), (r, r), r)
    screen.blit(surf, (cx - r, cy - r))
    # 테두리
    pygame.draw.circle(screen, color, (cx, cy), r, 2)
    # 중심점
    pygame.draw.circle(screen, color, (cx, cy), 5)
    # 반지름 선
    pygame.draw.line(screen, (*color, 180), (cx, cy), (cx + r, cy), 1)
    # 반지름 수치 표시
    lbl = font_small.render(f"r={r}", True, color)
    screen.blit(lbl, (cx + 4, cy + 4))

def draw_circle_distance_line(r1, r2, hit, dist, sum_r):
    """두 원 중심 사이의 거리 시각화"""
    cx1, cy1, _ = get_circle(r1)
    cx2, cy2, _ = get_circle(r2)
    color = CIRCLE_HIT_COLOR if hit else (140, 160, 220)
    pygame.draw.line(screen, color, (cx1, cy1), (cx2, cy2), 1)
    mid_x = (cx1 + cx2) // 2
    mid_y = (cy1 + cy2) // 2
    lbl = font_small.render(f"d={dist:.1f} / sum_r={sum_r}", True, color)
    screen.blit(lbl, (mid_x - lbl.get_width() // 2, mid_y - 20))

def draw_overlap_highlight(r1, r2):
    ox = max(r1.left, r2.left)
    oy = max(r1.top,  r2.top)
    ow = min(r1.right,  r2.right)  - ox
    oh = min(r1.bottom, r2.bottom) - oy
    if ow > 0 and oh > 0:
        surf = pygame.Surface((ow, oh), pygame.SRCALPHA)
        surf.fill((255, 200, 0, 60))
        screen.blit(surf, (ox, oy))
        pygame.draw.rect(screen, OVERLAP_COLOR, (ox, oy, ow, oh), 2)

def draw_hud(aabb_hit, circle_hit, dist, sum_r):
    lines = [
        "[ ← → ↑ ↓ ]  플레이어 이동",
        f"AABB  충돌: {'YES ◀ 겹침!' if aabb_hit   else 'NO '}",
        f"Circle충돌: {'YES ◀ 겹침!' if circle_hit else 'NO '}   (d={dist:.1f}  합={sum_r})",
    ]
    for i, line in enumerate(lines):
        hit = (i == 1 and aabb_hit) or (i == 2 and circle_hit)
        color = OVERLAP_COLOR if hit else TEXT_COLOR
        surf = font_small.render(line, True, color)
        screen.blit(surf, (14, 14 + i * 22))

    title = font_big.render("AABB + Circle Collision Demo", True, (180, 180, 210))
    screen.blit(title, (WIDTH - title.get_width() - 14, 14))

    p_info = font_small.render(
        f"Player  x:{player.x:4d}  y:{player.y:4d}  w:{player.w}  h:{player.h}",
        True, (160, 200, 160))
    f_info = font_small.render(
        f"Fixed   x:{fixed.x:4d}  y:{fixed.y:4d}  w:{fixed.w}  h:{fixed.h}",
        True, (160, 160, 200))
    screen.blit(p_info, (14, HEIGHT - 52))
    screen.blit(f_info, (14, HEIGHT - 28))

# ── 메인 루프 ──────────────────────────────────────────────
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x -= SPEED
    if keys[pygame.K_RIGHT]: player.x += SPEED
    if keys[pygame.K_UP]:    player.y -= SPEED
    if keys[pygame.K_DOWN]:  player.y += SPEED
    player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # 충돌 감지
    aabb_hit = player.colliderect(fixed)
    circle_hit, dist, sum_r = circle_collide(player, fixed)

    # ── 렌더링 ──
    bg = BG_CIRCLE_HIT if circle_hit else BG_COLOR
    screen.fill(bg)
    draw_grid()

    # 오브젝트 채우기
    pygame.draw.rect(screen, RECT_COLOR, player)
    pygame.draw.rect(screen, RECT_COLOR, fixed)
    pygame.draw.rect(screen, (180, 180, 200), player, 1)
    pygame.draw.rect(screen, (180, 180, 200), fixed,  1)

    # 라벨
    p_lbl = font_small.render("Player (이동)", True, (220, 240, 220))
    f_lbl = font_small.render("Fixed (고정)", True, (220, 220, 240))
    screen.blit(p_lbl, (player.left, player.bottom + 4))
    screen.blit(f_lbl, (fixed.left,  fixed.bottom  + 4))

    # AABB 겹침 하이라이트
    if aabb_hit:
        draw_overlap_highlight(player, fixed)

    # AABB 박스
    aabb_col = OVERLAP_COLOR if aabb_hit else AABB_COLOR
    draw_aabb(player, aabb_col, "AABB-P")
    draw_aabb(fixed,  aabb_col, "AABB-F")

    # 원형 Bounding Box (파란 원, 충돌 시 노란색)
    draw_circle_bb(player, circle_hit)
    draw_circle_bb(fixed,  circle_hit)

    # 두 원 거리 연결선
    draw_circle_distance_line(player, fixed, circle_hit, dist, sum_r)

    draw_hud(aabb_hit, circle_hit, dist, sum_r)
    pygame.display.flip()

pygame.quit()
sys.exit()