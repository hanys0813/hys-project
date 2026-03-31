import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB + Circle + OBB 충돌 감지 데모")

clock = pygame.time.Clock()
FPS = 60
SPEED = 4

BG_COLOR        = (30, 30, 40)
BG_CIRCLE_HIT   = (60, 55, 10)
RECT_COLOR      = (140, 140, 160)
AABB_COLOR      = (220, 50,  50)
CIRCLE_COLOR    = (80, 140, 240)
OVERLAP_COLOR   = (255, 200,  0)
CIRCLE_HIT_COLOR= (255, 220,  0)
OBB_COLOR       = (50,  220,  80)   # 초록 OBB
OBB_HIT_COLOR   = (255, 200,  0)
TEXT_COLOR      = (220, 220, 240)
GRID_COLOR      = (40,  40,  55)

font_small = pygame.font.SysFont("consolas", 16)
font_big   = pygame.font.SysFont("consolas", 22, bold=True)

# ── 오브젝트 ──────────────────────────────────────────────
player = pygame.Rect(100, 100, 80, 60)
fixed  = pygame.Rect(0, 0, 120, 90)
fixed.center = (WIDTH // 2, HEIGHT // 2)

# 회전 상태
angle       = 0.0      # 현재 각도 (도)
ROT_SLOW    = 30.0     # 기본 속도 (도/초)
ROT_FAST    = 150.0    # Z 누를 때 속도
z_pressed   = False

# ── 헬퍼: 점 회전 ─────────────────────────────────────────
def rotate_point(px, py, cx, cy, deg):
    rad = math.radians(deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    dx, dy = px - cx, py - cy
    return (cx + dx * cos_a - dy * sin_a,
            cy + dx * sin_a + dy * cos_a)

# ── OBB 꼭짓점 계산 ───────────────────────────────────────
def get_obb_vertices(rect, deg):
    """rect의 4꼭짓점을 중심 기준으로 deg만큼 회전한 좌표 반환"""
    cx, cy = rect.centerx, rect.centery
    corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    return [rotate_point(px, py, cx, cy, deg) for px, py in corners]

# ── OBB vs AABB(player) 충돌 — SAT ───────────────────────
def project(vertices, axis):
    dots = [v[0] * axis[0] + v[1] * axis[1] for v in vertices]
    return min(dots), max(dots)

def obb_vs_aabb(obb_verts, aabb_rect, deg):
    """SAT: OBB 축 2개 + AABB 축 2개 = 총 4축 분리 테스트"""
    rad = math.radians(deg)
    # OBB 로컬 축
    ax1 = (math.cos(rad), math.sin(rad))
    ax2 = (-math.sin(rad), math.cos(rad))
    # AABB 축
    ax3 = (1.0, 0.0)
    ax4 = (0.0, 1.0)

    aabb_verts = [
        (aabb_rect.left,  aabb_rect.top),
        (aabb_rect.right, aabb_rect.top),
        (aabb_rect.right, aabb_rect.bottom),
        (aabb_rect.left,  aabb_rect.bottom),
    ]

    for axis in (ax1, ax2, ax3, ax4):
        min1, max1 = project(obb_verts,  axis)
        min2, max2 = project(aabb_verts, axis)
        if max1 < min2 or max2 < min1:
            return False    # 분리 축 발견 → 충돌 없음
    return True             # 모든 축에서 겹침 → 충돌

# ── Circle 충돌 ───────────────────────────────────────────
def get_circle(rect):
    return rect.centerx, rect.centery, rect.width // 2

def circle_collide(r1, r2):
    cx1, cy1, rad1 = get_circle(r1)
    cx2, cy2, rad2 = get_circle(r2)
    dist = math.hypot(cx2 - cx1, cy2 - cy1)
    return dist < (rad1 + rad2), dist, rad1 + rad2

# ── 그리기 함수들 ─────────────────────────────────────────
def draw_grid():
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_aabb(rect, color, label=""):
    pygame.draw.rect(screen, color, rect, 2)
    size = 6
    for cx, cy in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
        pygame.draw.line(screen, color, (cx - size, cy), (cx + size, cy), 2)
        pygame.draw.line(screen, color, (cx, cy - size), (cx, cy + size), 2)
    if label:
        lbl = font_small.render(label, True, color)
        screen.blit(lbl, (rect.left, rect.top - 20))

def draw_obb(verts, hit):
    """초록 OBB (4꼭짓점 폴리곤)"""
    color = OBB_HIT_COLOR if hit else OBB_COLOR
    # 반투명 채우기
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    int_verts = [(int(x), int(y)) for x, y in verts]
    pygame.draw.polygon(surf, (*color, 40), int_verts)
    screen.blit(surf, (0, 0))
    # 테두리
    pygame.draw.polygon(screen, color, int_verts, 2)
    # 꼭짓점 마커
    for x, y in int_verts:
        pygame.draw.circle(screen, color, (x, y), 4)
    # 라벨
    cx = sum(v[0] for v in verts) / 4
    cy = sum(v[1] for v in verts) / 4
    lbl = font_small.render("OBB", True, color)
    screen.blit(lbl, (int(cx) - lbl.get_width() // 2,
                      int(cy) - lbl.get_height() // 2))

def draw_circle_bb(rect, hit):
    cx, cy, r = get_circle(rect)
    color = CIRCLE_HIT_COLOR if hit else CIRCLE_COLOR
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    alpha = 50 if hit else 30
    pygame.draw.circle(surf, (*color, alpha), (r, r), r)
    screen.blit(surf, (cx - r, cy - r))
    pygame.draw.circle(screen, color, (cx, cy), r, 2)
    pygame.draw.circle(screen, color, (cx, cy), 5)
    pygame.draw.line(screen, (*color, 180), (cx, cy), (cx + r, cy), 1)
    lbl = font_small.render(f"r={r}", True, color)
    screen.blit(lbl, (cx + 4, cy + 4))

def draw_circle_distance_line(r1, r2, hit, dist, sum_r):
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

def draw_rotated_rect(rect, deg, color):
    """회전한 고정 오브젝트 시각화 (Surface 회전)"""
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    surf.fill((*RECT_COLOR, 220))
    pygame.draw.rect(surf, (180, 180, 200), surf.get_rect(), 1)
    rotated = pygame.transform.rotate(surf, -deg)
    rr = rotated.get_rect(center=rect.center)
    screen.blit(rotated, rr.topleft)

def draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd):
    z_str = "빠름 ◀ Z 누름" if z_pressed else "느림  (Z: 빠르게)"
    lines = [
        "[ ← → ↑ ↓ ]  플레이어 이동  |  [ Z ] 회전 가속",
        f"회전 속도   : {rot_spd:.0f}°/s  ({z_str})",
        f"AABB  충돌  : {'YES ◀ 겹침!' if aabb_hit   else 'NO '}",
        f"Circle충돌  : {'YES ◀ 겹침!' if circle_hit else 'NO '}   (d={dist:.1f}  합={sum_r})",
        f"OBB   충돌  : {'YES ◀ 겹침!' if obb_hit    else 'NO '}",
    ]
    for i, line in enumerate(lines):
        hit = ((i == 2 and aabb_hit) or
               (i == 3 and circle_hit) or
               (i == 4 and obb_hit))
        color = OVERLAP_COLOR if hit else TEXT_COLOR
        surf = font_small.render(line, True, color)
        screen.blit(surf, (14, 14 + i * 22))

    title = font_big.render("AABB + Circle + OBB Collision Demo", True, (180, 180, 210))
    screen.blit(title, (WIDTH - title.get_width() - 14, 14))

    p_info = font_small.render(
        f"Player  x:{player.x:4d}  y:{player.y:4d}  w:{player.w}  h:{player.h}",
        True, (160, 200, 160))
    f_info = font_small.render(
        f"Fixed   cx:{fixed.centerx}  cy:{fixed.centery}  angle:{angle:6.1f}°",
        True, (160, 160, 200))
    screen.blit(p_info, (14, HEIGHT - 52))
    screen.blit(f_info, (14, HEIGHT - 28))

# ── 메인 루프 ──────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # 초 단위 델타타임

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

    z_pressed = keys[pygame.K_z]
    rot_spd   = ROT_FAST if z_pressed else ROT_SLOW
    angle = (angle + rot_spd * dt) % 360

    # 충돌 감지
    aabb_hit   = player.colliderect(fixed)
    circle_hit, dist, sum_r = circle_collide(player, fixed)
    obb_verts  = get_obb_vertices(fixed, angle)
    obb_hit    = obb_vs_aabb(obb_verts, player, angle)

    # ── 렌더링 ──
    bg = BG_CIRCLE_HIT if circle_hit else BG_COLOR
    screen.fill(bg)
    draw_grid()

    # 플레이어 (회전 없음)
    pygame.draw.rect(screen, RECT_COLOR, player)
    pygame.draw.rect(screen, (180, 180, 200), player, 1)
    p_lbl = font_small.render("Player (이동)", True, (220, 240, 220))
    screen.blit(p_lbl, (player.left, player.bottom + 4))

    # 고정 오브젝트 — 회전된 Surface로 그리기
    draw_rotated_rect(fixed, angle, RECT_COLOR)
    f_lbl = font_small.render("Fixed (회전)", True, (220, 220, 240))
    screen.blit(f_lbl, (fixed.left, fixed.bottom + 4))

    # AABB 겹침 하이라이트
    if aabb_hit:
        draw_overlap_highlight(player, fixed)

    # AABB 박스
    aabb_col = OVERLAP_COLOR if aabb_hit else AABB_COLOR
    draw_aabb(player, aabb_col, "AABB-P")
    draw_aabb(fixed,  aabb_col, "AABB-F")

    # 원형 BB
    draw_circle_bb(player, circle_hit)
    draw_circle_bb(fixed,  circle_hit)
    draw_circle_distance_line(player, fixed, circle_hit, dist, sum_r)

    # ★ OBB (초록) — 회전된 꼭짓점 기반
    draw_obb(obb_verts, obb_hit)

    draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd)
    pygame.display.flip()

    

pygame.quit()
sys.exit()