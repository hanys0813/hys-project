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
OBB_COLOR       = (50,  220,  80)
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
angle       = 0.0
ROT_SLOW    = 30.0
ROT_FAST    = 150.0
z_pressed   = False

# ── 헬퍼 ────────────────────────────────────────────────
def rotate_point(px, py, cx, cy, deg):
    rad = math.radians(deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    dx, dy = px - cx, py - cy
    return (cx + dx * cos_a - dy * sin_a,
            cy + dx * sin_a + dy * cos_a)

def get_obb_vertices(rect, deg):
    cx, cy = rect.centerx, rect.centery
    corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    return [rotate_point(px, py, cx, cy, deg) for px, py in corners]

def project(vertices, axis):
    dots = [v[0] * axis[0] + v[1] * axis[1] for v in vertices]
    return min(dots), max(dots)

def obb_vs_aabb(obb_verts, aabb_rect, deg):
    rad = math.radians(deg)
    ax1 = (math.cos(rad), math.sin(rad))
    ax2 = (-math.sin(rad), math.cos(rad))
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
            return False
    return True

def get_circle(rect):
    return rect.centerx, rect.centery, rect.width // 2

def circle_collide(r1, r2):
    cx1, cy1, rad1 = get_circle(r1)
    cx2, cy2, rad2 = get_circle(r2)
    dist = math.hypot(cx2 - cx1, cy2 - cy1)
    return dist < (rad1 + rad2), dist, rad1 + rad2

# ── 그리기 ──────────────────────────────────────────────
def draw_grid():
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_aabb(rect, color, label=""):
    pygame.draw.rect(screen, color, rect, 2)
    if label:
        lbl = font_small.render(label, True, color)
        screen.blit(lbl, (rect.left, rect.top - 20))

def draw_obb(verts, hit):
    color = OBB_HIT_COLOR if hit else OBB_COLOR
    pygame.draw.polygon(screen, color, [(int(x), int(y)) for x, y in verts], 2)

def draw_circle_bb(rect, hit):
    cx, cy, r = get_circle(rect)
    color = CIRCLE_HIT_COLOR if hit else CIRCLE_COLOR
    pygame.draw.circle(screen, color, (cx, cy), r, 2)

# ✅ 추가된 핵심 함수
def draw_collision_summary(aabb_hit, circle_hit, obb_hit):
    lines = [
        f"Circle: {'HIT' if circle_hit else 'NO'}",
        f"AABB  : {'HIT' if aabb_hit else 'NO'}",
        f"OBB   : {'HIT' if obb_hit else 'NO'}",
    ]

    for i, line in enumerate(lines):
        if i == 0:
            color = CIRCLE_HIT_COLOR if circle_hit else CIRCLE_COLOR
        elif i == 1:
            color = OVERLAP_COLOR if aabb_hit else AABB_COLOR
        else:
            color = OBB_HIT_COLOR if obb_hit else OBB_COLOR

        txt = font_big.render(line, True, color)
        screen.blit(txt, (14, 14 + i * 28))

# 기존 HUD 유지
def draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd):
    lines = [
        f"AABB: {aabb_hit}",
        f"Circle: {circle_hit}",
        f"OBB: {obb_hit}",
    ]
    for i, line in enumerate(lines):
        txt = font_small.render(line, True, TEXT_COLOR)
        screen.blit(txt, (14, 120 + i * 20))

# ── 메인 루프 ────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x -= SPEED
    if keys[pygame.K_RIGHT]: player.x += SPEED
    if keys[pygame.K_UP]:    player.y -= SPEED
    if keys[pygame.K_DOWN]:  player.y += SPEED

    z_pressed = keys[pygame.K_z]
    rot_spd   = ROT_FAST if z_pressed else ROT_SLOW
    angle = (angle + rot_spd * dt) % 360

    # 충돌
    aabb_hit   = player.colliderect(fixed)
    circle_hit, dist, sum_r = circle_collide(player, fixed)
    obb_verts  = get_obb_vertices(fixed, angle)
    obb_hit    = obb_vs_aabb(obb_verts, player, angle)

    # 렌더링
    screen.fill(BG_COLOR)
    draw_grid()

    pygame.draw.rect(screen, RECT_COLOR, player)
    pygame.draw.rect(screen, RECT_COLOR, fixed)

    draw_aabb(player, AABB_COLOR)
    draw_aabb(fixed, AABB_COLOR)

    draw_circle_bb(player, circle_hit)
    draw_circle_bb(fixed, circle_hit)

    draw_obb(obb_verts, obb_hit)

    # ✅ 추가된 부분 (왼쪽 상단)
    draw_collision_summary(aabb_hit, circle_hit, obb_hit)

    # 기존 HUD 유지
    draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd)

    pygame.display.flip()

pygame.quit()
sys.exit()