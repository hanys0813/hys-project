import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB + Circle + OBB 충돌 감지 통합 데모")

clock = pygame.time.Clock()
FPS = 60
SPEED = 4

# ── 색상 설정 (기존 유지 및 강조 색상 추가) ──────────────────────
BG_COLOR         = (30, 30, 40)
BG_CIRCLE_HIT    = (35, 35, 50)
RECT_COLOR       = (140, 140, 160)
AABB_COLOR       = (220, 50,  50)  # 빨간색
CIRCLE_COLOR     = (80, 140, 240)  # 파란색
OBB_COLOR        = (50,  220,  80) # 초록색
OVERLAP_COLOR    = (255, 200,  0)
TEXT_COLOR       = (220, 220, 240)
GRID_COLOR       = (40,  40,  55)

font_small = pygame.font.SysFont("consolas", 16)
font_big   = pygame.font.SysFont("consolas", 22, bold=True)
font_status = pygame.font.SysFont("consolas", 26, bold=True) # 상단 전광판용

# ── 오브젝트 및 상태 ──────────────────────────────────────────
player = pygame.Rect(100, 100, 80, 60)
fixed  = pygame.Rect(0, 0, 120, 90)
fixed.center = (WIDTH // 2, HEIGHT // 2)

angle       = 0.0
ROT_SLOW    = 30.0
ROT_FAST    = 150.0
z_pressed   = False

# ── 헬퍼 함수들 (기존 로직 유지) ─────────────────────────────────
def rotate_point(px, py, cx, cy, deg):
    rad = math.radians(deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    dx, dy = px - cx, py - cy
    return (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)

def get_obb_vertices(rect, deg):
    cx, cy = rect.centerx, rect.centery
    corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    return [rotate_point(px, py, cx, cy, deg) for px, py in corners]

def project(vertices, axis):
    dots = [v[0] * axis[0] + v[1] * axis[1] for v in vertices]
    return min(dots), max(dots)

def obb_vs_aabb(obb_verts, aabb_rect, deg):
    rad = math.radians(deg)
    ax1, ax2 = (math.cos(rad), math.sin(rad)), (-math.sin(rad), math.cos(rad))
    ax3, ax4 = (1.0, 0.0), (0.0, 1.0)
    aabb_verts = [(aabb_rect.left, aabb_rect.top), (aabb_rect.right, aabb_rect.top),
                  (aabb_rect.right, aabb_rect.bottom), (aabb_rect.left, aabb_rect.bottom)]
    for axis in (ax1, ax2, ax3, ax4):
        min1, max1 = project(obb_verts,  axis)
        min2, max2 = project(aabb_verts, axis)
        if max1 < min2 or max2 < min1: return False
    return True

def get_circle(rect):
    return rect.centerx, rect.centery, rect.width // 2

def circle_collide(r1, r2):
    cx1, cy1, rad1 = get_circle(r1)
    cx2, cy2, rad2 = get_circle(r2)
    dist = math.hypot(cx2 - cx1, cy2 - cy1)
    return dist < (rad1 + rad2), dist, rad1 + rad2

# ── 그리기 함수들 (기존 스타일 유지) ──────────────────────────────
def draw_grid():
    for x in range(0, WIDTH, 40): pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40): pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_aabb(rect, color, label=""):
    pygame.draw.rect(screen, color, rect, 2)
    if label:
        lbl = font_small.render(label, True, color)
        screen.blit(lbl, (rect.left, rect.top - 20))

def draw_obb(verts, hit):
    color = OBB_COLOR if not hit else (255, 255, 255) # 충돌 시 흰색 테두리 강조
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    int_verts = [(int(x), int(y)) for x, y in verts]
    pygame.draw.polygon(surf, (*OBB_COLOR, 50 if hit else 20), int_verts)
    screen.blit(surf, (0, 0))
    pygame.draw.polygon(screen, OBB_COLOR, int_verts, 2)

def draw_circle_bb(rect, hit):
    cx, cy, r = get_circle(rect)
    color = CIRCLE_COLOR
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, 60 if hit else 30), (r, r), r)
    screen.blit(surf, (cx - r, cy - r))
    pygame.draw.circle(screen, color, (cx, cy), r, 2)

def draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd):
    # 1. 화면 중앙 상단: "HIT" 메시지 동시 표시 (추가된 기능)
    status_y = 60
    if circle_hit:
        msg = font_status.render("Circle: HIT", True, CIRCLE_COLOR)
        screen.blit(msg, (WIDTH//2 - 250, status_y))
    if aabb_hit:
        msg = font_status.render("AABB: HIT", True, AABB_COLOR)
        screen.blit(msg, (WIDTH//2 - 70, status_y))
    if obb_hit:
        msg = font_status.render("OBB: HIT", True, OBB_COLOR)
        screen.blit(msg, (WIDTH//2 + 110, status_y))

    # 2. 왼쪽 상단: 상세 정보 HUD (기존 유지 및 통합)
    z_str = "빠름 ◀ Z 누름" if z_pressed else "느림  (Z: 빠르게)"
    lines = [
        f"AABB   충돌 : {'YES' if aabb_hit   else 'NO '}",
        f"Circle 충돌 : {'YES' if circle_hit else 'NO '}",
        f"OBB    충돌 : {'YES' if obb_hit    else 'NO '}",
        f"--------------------------",
        f"회전 속도   : {rot_spd:.0f}°/s ({z_str})",
        f"Circle dist : {dist:.1f} / sum_r: {sum_r}",
    ]
    for i, line in enumerate(lines):
        color = TEXT_COLOR
        if i == 0 and aabb_hit: color = AABB_COLOR
        if i == 1 and circle_hit: color = CIRCLE_COLOR
        if i == 2 and obb_hit: color = OBB_COLOR
        surf = font_small.render(line, True, color)
        screen.blit(surf, (14, 14 + i * 22))

    # 하단 정보 (기존 유지)
    p_info = font_small.render(f"Player  x:{player.x:4d} y:{player.y:4d}", True, (160, 200, 160))
    f_info = font_small.render(f"Fixed   angle:{angle:6.1f}°", True, (160, 160, 200))
    screen.blit(p_info, (14, HEIGHT - 52))
    screen.blit(f_info, (14, HEIGHT - 28))

# ── 메인 루프 ──────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x -= SPEED
    if keys[pygame.K_RIGHT]: player.x += SPEED
    if keys[pygame.K_UP]:    player.y -= SPEED
    if keys[pygame.K_DOWN]:  player.y += SPEED
    player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    z_pressed = keys[pygame.K_z]
    rot_spd = ROT_FAST if z_pressed else ROT_SLOW
    angle = (angle + rot_spd * dt) % 360

    # 충돌 판정
    aabb_hit   = player.colliderect(fixed)
    circle_hit, dist, sum_r = circle_collide(player, fixed)
    obb_verts  = get_obb_vertices(fixed, angle)
    obb_hit    = obb_vs_aabb(obb_verts, player, angle)

    # 렌더링
    screen.fill(BG_COLOR)
    draw_grid()

    # 객체 그리기
    # 고정 객체 (회전)
    surf = pygame.Surface((fixed.width, fixed.height), pygame.SRCALPHA)
    surf.fill((*RECT_COLOR, 180))
    rotated = pygame.transform.rotate(surf, -angle)
    rr = rotated.get_rect(center=fixed.center)
    screen.blit(rotated, rr.topleft)

    # 플레이어 객체
    pygame.draw.rect(screen, (100, 100, 120), player)
    pygame.draw.rect(screen, (200, 200, 220), player, 1)

    # 충돌 시각화 레이어
    draw_circle_bb(player, circle_hit)
    draw_circle_bb(fixed,  circle_hit)
    draw_aabb(player, AABB_COLOR if aabb_hit else (100, 100, 100), "AABB-P")
    draw_obb(obb_verts, obb_hit)

    # HUD 및 상단 전광판 표시
    draw_hud(aabb_hit, circle_hit, obb_hit, dist, sum_r, rot_spd)

    pygame.display.flip()

pygame.quit()