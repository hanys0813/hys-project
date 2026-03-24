import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Way Collision Detection Demo")

clock = pygame.time.Clock()
FPS = 60
SPEED = 4

# 색상 설정
BG_COLOR       = (20, 20, 25)
CIRCLE_COLOR   = (80, 140, 240)  # 파란색
AABB_COLOR     = (220, 50, 50)   # 빨간색
OBB_COLOR      = (50, 220, 80)   # 초록색
TEXT_COLOR     = (255, 255, 255)
GRID_COLOR     = (40, 40, 50)

font_small = pygame.font.SysFont("malgungothic", 16)
font_bold  = pygame.font.SysFont("malgungothic", 25, bold=True)

# 오브젝트 설정
player = pygame.Rect(100, 100, 80, 60)
fixed  = pygame.Rect(0, 0, 120, 90)
fixed.center = (WIDTH // 2, HEIGHT // 2)

angle = 0.0
ROT_SPEED = 60.0

# ── 충돌 로직 함수들 ──────────────────────────────────────────

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
    axes = [(math.cos(rad), math.sin(rad)), (-math.sin(rad), math.cos(rad)), (1, 0), (0, 1)]
    aabb_verts = [(aabb_rect.left, aabb_rect.top), (aabb_rect.right, aabb_rect.top),
                  (aabb_rect.right, aabb_rect.bottom), (aabb_rect.left, aabb_rect.bottom)]
    for axis in axes:
        min1, max1 = project(obb_verts, axis)
        min2, max2 = project(aabb_verts, axis)
        if max1 < min2 or max2 < min1: return False
    return True

def circle_collide(r1, r2):
    c1, c2 = pygame.Vector2(r1.center), pygame.Vector2(r2.center)
    rad1, rad2 = r1.width // 2, r2.width // 2
    return c1.distance_to(c2) < (rad1 + rad2)

# ── 그리기 함수들 ───────────────────────────────────────────

def draw_collision_status(circle_hit, aabb_hit, obb_hit):
    # 1. 화면 왼쪽 상단 HUD
    status_y = 20
    labels = [
        (f"Circle Collision: {'YES' if circle_hit else 'NO'}", CIRCLE_COLOR if circle_hit else (100,100,100)),
        (f"AABB Collision:   {'YES' if aabb_hit else 'NO'}", AABB_COLOR if aabb_hit else (100,100,100)),
        (f"OBB Collision:    {'YES' if obb_hit else 'NO'}", OBB_COLOR if obb_hit else (100,100,100))
    ]
    for i, (text, color) in enumerate(labels):
        img = font_small.render(text, True, color)
        screen.blit(img, (20, status_y + i * 25))

    # 2. 화면 상단 중앙 큰 텍스트 알림
    center_x = WIDTH // 2
    if circle_hit:
        msg = font_bold.render("Circle: HIT", True, CIRCLE_COLOR)
        screen.blit(msg, (center_x - 250, 20))
    if aabb_hit:
        msg = font_bold.render("AABB: HIT", True, AABB_COLOR)
        screen.blit(msg, (center_x - 60, 20))
    if obb_hit:
        msg = font_bold.render("OBB: HIT", True, OBB_COLOR)
        screen.blit(msg, (center_x + 130, 20))

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

    angle = (angle + ROT_SPEED * dt) % 360

    # 충돌 판정
    circle_hit = circle_collide(player, fixed)
    aabb_hit   = player.colliderect(fixed)
    obb_verts  = get_obb_vertices(fixed, angle)
    obb_hit    = obb_vs_aabb(obb_verts, player, angle)

    # 렌더링
    screen.fill(BG_COLOR)
    
    # 그리드
    for i in range(0, WIDTH, 40): pygame.draw.line(screen, GRID_COLOR, (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40): pygame.draw.line(screen, GRID_COLOR, (0, i), (WIDTH, i))

    # 1. 원형 시각화 (파랑)
    pygame.draw.circle(screen, CIRCLE_COLOR, player.center, player.width // 2, 2)
    pygame.draw.circle(screen, CIRCLE_COLOR, fixed.center, fixed.width // 2, 2)

    # 2. AABB 시각화 (빨강)
    pygame.draw.rect(screen, AABB_COLOR, player, 2)
    pygame.draw.rect(screen, AABB_COLOR, fixed, 1) # 고정 박스의 원래 AABB

    # 3. OBB 시각화 (초록)
    pygame.draw.polygon(screen, OBB_COLOR, obb_verts, 2)

    # 플레이어 본체
    pygame.draw.rect(screen, (200, 200, 200), player, 1)

    # 상태 표시
    draw_collision_status(circle_hit, aabb_hit, obb_hit)

    pygame.display.flip()

pygame.quit()