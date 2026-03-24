import pygame
import sys

# 초기화
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB 충돌 감지 데모")

clock = pygame.time.Clock()
FPS = 60
SPEED = 4

# 색상
BG_COLOR       = (30, 30, 40)
RECT_COLOR     = (140, 140, 160)
AABB_COLOR     = (220, 50,  50)
OVERLAP_COLOR  = (255, 200,  0)
TEXT_COLOR     = (220, 220, 240)
GRID_COLOR     = (40,  40,  55)

# 폰트
font_small = pygame.font.SysFont("consolas", 16)
font_big   = pygame.font.SysFont("consolas", 22, bold=True)

# ── 오브젝트 정의 ──────────────────────────────────────────
# 이동 가능한 오브젝트 (플레이어)
player = pygame.Rect(100, 100, 80, 60)

# 고정 오브젝트 (화면 중앙)
fixed  = pygame.Rect(0, 0, 120, 90)
fixed.center = (WIDTH // 2, HEIGHT // 2)

def draw_grid():
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_aabb(rect, color, label=""):
    """AABB 테두리 + 코너 마커"""
    pygame.draw.rect(screen, color, rect, 2)
    # 코너 마커
    size = 6
    corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
    for cx, cy in corners:
        pygame.draw.line(screen, color, (cx - size, cy), (cx + size, cy), 2)
        pygame.draw.line(screen, color, (cx, cy - size), (cx, cy + size), 2)
    if label:
        lbl = font_small.render(label, True, color)
        screen.blit(lbl, (rect.left, rect.top - 20))

def draw_overlap_highlight(r1, r2):
    """겹친 영역 반투명 하이라이트"""
    ox = max(r1.left, r2.left)
    oy = max(r1.top,  r2.top)
    ow = min(r1.right,  r2.right)  - ox
    oh = min(r1.bottom, r2.bottom) - oy
    if ow > 0 and oh > 0:
        surf = pygame.Surface((ow, oh), pygame.SRCALPHA)
        surf.fill((255, 200, 0, 60))
        screen.blit(surf, (ox, oy))
        pygame.draw.rect(screen, OVERLAP_COLOR, (ox, oy, ow, oh), 2)

def draw_hud(colliding):
    # 조작 안내
    lines = [
        "[ ← → ↑ ↓ ]  플레이어 이동",
        f"충돌(AABB): {'YES  ← 겹침!' if colliding else 'NO'}",
    ]
    for i, line in enumerate(lines):
        color = OVERLAP_COLOR if (i == 1 and colliding) else TEXT_COLOR
        surf = font_small.render(line, True, color)
        screen.blit(surf, (14, 14 + i * 22))

    # 제목
    title = font_big.render("AABB Collision Demo", True, (180, 180, 210))
    screen.blit(title, (WIDTH - title.get_width() - 14, 14))

    # 좌표 표시
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

    # 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x -= SPEED
    if keys[pygame.K_RIGHT]: player.x += SPEED
    if keys[pygame.K_UP]:    player.y -= SPEED
    if keys[pygame.K_DOWN]:  player.y += SPEED

    # 화면 밖 제한
    player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # AABB 충돌 감지
    colliding = player.colliderect(fixed)

    # ── 렌더링 ──
    screen.fill(BG_COLOR)
    draw_grid()

    # 오브젝트 내부 채우기
    pygame.draw.rect(screen, RECT_COLOR, player)
    pygame.draw.rect(screen, RECT_COLOR, fixed)

    # 오브젝트 테두리
    pygame.draw.rect(screen, (180, 180, 200), player, 1)
    pygame.draw.rect(screen, (180, 180, 200), fixed,  1)

    # 라벨
    p_lbl = font_small.render("Player (이동)", True, (220, 240, 220))
    f_lbl = font_small.render("Fixed (고정)", True, (220, 220, 240))
    screen.blit(p_lbl, (player.left, player.bottom + 4))
    screen.blit(f_lbl, (fixed.left,  fixed.bottom  + 4))

    # 겹침 하이라이트 (충돌 시)
    if colliding:
        draw_overlap_highlight(player, fixed)

    # AABB 박스
    aabb_col = OVERLAP_COLOR if colliding else AABB_COLOR
    draw_aabb(player, aabb_col, "AABB-P")
    draw_aabb(fixed,  aabb_col, "AABB-F")

    draw_hud(colliding)
    pygame.display.flip()

pygame.quit()
sys.exit()