# pygame_image_practice.py
# 이미지 불러오기 / 크기조절 / 위치 / 회전 실습

import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("이미지 실습")
clock = pygame.time.Clock()

# ──────────────────────────────────────────
# ① 이미지 불러오기
# ──────────────────────────────────────────
try:
    original = pygame.image.load("player.png").convert_alpha()
except FileNotFoundError:
    # player.png 없으면 임시 surface 생성
    original = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.polygon(original, (80, 200, 120),
                        [(40, 0), (80, 80), (0, 80)])

# ──────────────────────────────────────────
# ② 크기 조절  ← 숫자를 바꿔보세요!
# ──────────────────────────────────────────
# image = pygame.transform.scale(original, (120, 120))  # 고정 크기
# image = pygame.transform.scale_by(original, 2.0)      # 배율 (2배)
image = original                                         # 원본 그대로

# ──────────────────────────────────────────
# ③ Rect 위치 설정  ← anchor를 바꿔보세요!
# ──────────────────────────────────────────
rect = image.get_rect()
rect.center    = (WIDTH // 2, HEIGHT // 2)   # 화면 중앙
# rect.topleft   = (50, 50)
# rect.midbottom = (WIDTH // 2, HEIGHT - 20)
# rect.topright  = (WIDTH - 10, 10)

# ──────────────────────────────────────────
# ④ 회전  ← 각도를 바꿔보세요! (반시계 방향 +)
# ──────────────────────────────────────────
# image = pygame.transform.rotate(image, 45)
# image = pygame.transform.rotate(image, 90)
# image = pygame.transform.rotate(image, 180)

# ※ 회전하면 Rect 크기가 바뀌므로 center를 다시 고정
# rect = image.get_rect(center=rect.center)

BG     = (30, 30, 40)
CYAN   = (0, 220, 200)
GRAY   = (80, 80, 100)
WHITE  = (255, 255, 255)

try:
    font = pygame.font.SysFont("malgungothic", 18)
except Exception:
    font = pygame.font.SysFont(None, 20)


def draw_cross(surf, cx, cy, color, size=12):
    pygame.draw.line(surf, color, (cx - size, cy), (cx + size, cy), 2)
    pygame.draw.line(surf, color, (cx, cy - size), (cx, cy + size), 2)


angle = 0
running = True
while running:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    screen.fill(BG)

    # ── 보조 격자 ──
    for x in range(0, WIDTH, 80):
        pygame.draw.line(screen, (40, 40, 55), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (40, 40, 55), (0, y), (WIDTH, y))

    # ── 이미지 그리기 ──
    screen.blit(image, rect)

    # ── Rect 테두리 표시 ──
    pygame.draw.rect(screen, CYAN, rect, 1)

    # ── anchor 점 표시 ──
    draw_cross(screen, rect.centerx, rect.centery, CYAN)

    # ── 좌표 정보 HUD ──
    lines = [
        f"image size : {image.get_size()}",
        f"rect.topleft  : {rect.topleft}",
        f"rect.center   : {rect.center}",
        f"rect.midbottom: {rect.midbottom}",
    ]
    for i, txt in enumerate(lines):
        surf = font.render(txt, True, WHITE)
        screen.blit(surf, (12, 12 + i * 22))

    hint = font.render("ESC: 종료", True, GRAY)
    screen.blit(hint, (12, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()