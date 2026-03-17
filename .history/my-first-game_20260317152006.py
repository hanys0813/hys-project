import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Awakened")
clock = pygame.time.Clock()

# 색상 (진홍색과 심연의 보라)
BLACK = (5, 0, 10)
BLOOD_RED = (255, 0, 50)
SHADOW_PURPLE = (100, 0, 200)
WHITE = (255, 255, 255)

# 게임 상태 변수
player_pos = [WIDTH // 2, HEIGHT - 70]
player_hp = 100
bullets = []
enemies = []
souls = []
score = 0
game_over = False

def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("arial", size, True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# --- 메인 루프 ---
while True:
    if not game_over:
        # 1. 입력 및 시간 왜곡
        moving = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 발사: 스페이스바를 누를 때 피 5 소모
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 5:
                    bullets.append([player_pos[0] + 20, player_pos[1]])
                    player_hp -= 5

        keys = pygame.key.get_pressed()
        speed = 6
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= speed
            moving = True
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - 40:
            player_pos[0] += speed
            moving = True
        if keys[pygame.K_UP] and player_pos[1] > 0:
            player_pos[1] -= speed
            moving = True
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT - 40:
            player_pos[1] += speed
            moving = True

        time_scale = 1.0 if moving else 0.2

        # 2. 적 생성 (장애물)
        if random.random() < 0.05 * time_scale:
            enemies.append([random.randint(0, WIDTH-40), -50, random.uniform(2, 5)])

        # 3. 로직 업데이트
        # 적 이동 및 플레이어 충돌
        for en in enemies[:]:
            en[1] += en[2] * time_scale
            # 플레이어와 적 충돌 판정 (Rect 기반)
            p_rect = pygame.Rect(player_pos[0], player_pos[1], 40, 40)
            e_rect = pygame.Rect(en[0], en[1], 40, 40)
            if p_rect.colliderect(e_rect):
                game_over = True # 부딪히면 즉사
            
            if en[1] > HEIGHT: enemies.remove(en)

        # 탄환 이동 및 적 처치
        for b in bullets[:]:
            b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).collidepoint(b[0], b[1]):
                    souls.append([en[0]+20, en[1]+20])
                    enemies.remove(en)
                    if b in bullets: bullets.remove(b)
                    score += 10

        # 영혼 흡수 (자석)
        for s in souls[:]:
            dx = player_pos[0] + 20 - s[0]
            dy = player_pos[1] + 20 - s[1]
            dist = (dx**2 + dy**2)**0.5
            if dist < 15:
                player_hp = min(100, player_hp + 8)
                souls.remove(s)
            else:
                s[0] += dx * 0.15
                s[1] += dy * 0.15

        # 체력 소진 체크
        if player_hp <= 0:
            game_over = True

    else:
        # 게임 오버 시 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # 재시작 초기화
                player_hp, score, game_over = 100, 0, False
                enemies, bullets, souls = [], [], []

    # --- 4. 지리게 그리기 ---
    screen.fill(BLACK)
    
    if not game_over:
        # 영혼 (빛나는 효과)
        for s in souls:
            pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 4)
            pygame.draw.circle(screen, SHADOW_PURPLE, (int(s[0]), int(s[1])), 8, 1)

        # 탄환 (검기 형태)
        for b in bullets:
            pygame.draw.ellipse(screen, BLOOD_RED, (b[0]-2, b[1], 6, 20))

        # 적 (기괴한 코어 형태)
        for en in enemies:
            time_f = pygame.time.get_ticks() * 0.01
            pulse = math.sin(time_f) * 5
            pygame.draw.rect(screen, SHADOW_PURPLE, (en[0]-pulse/2, en[1]-pulse/2, 40+pulse, 40+pulse), 3)
            pygame.draw.rect(screen, (50, 0, 50), (en[0]+10, en[1]+10, 20, 20))

        # 플레이어 (대마왕 로켓 - 아우라 포함)
        p_x, p_y = player_pos
        pygame.draw.polygon(screen, BLOOD_RED, [[p_x+20, p_y], [p_x, p_y+40], [p_x+40, p_y+40]])
        # 엔진 불꽃 (아우라)
        flame_h = random.randint(10, 30)
        pygame.draw.polygon(screen, SHADOW_PURPLE, [[p_x+10, p_y+40], [p_x+30, p_y+40], [p_x+20, p_y+40+flame_h]])

        # UI
        pygame.draw.rect(screen, (30, 30, 30), (20, 20, 200, 15))
        pygame.draw.rect(screen, BLOOD_RED, (20, 20, player_hp * 2, 15))
        draw_text(f"SOULS: {score}", 25, WIDTH - 80, 30)
    else:
        # 게임 오버 화면
        screen.fill((20, 0, 0))
        draw_text("DEMON DEFEATED", 60, WIDTH//2, HEIGHT//2 - 50, BLOOD_RED)
        draw_text(f"FINAL SOULS: {score}", 30, WIDTH//2, HEIGHT//2 + 20)
        draw_text("Press 'R' to Resurrect", 20, WIDTH//2, HEIGHT//2 + 80, SHADOW_PURPLE)

    pygame.display.flip()
    clock.tick(60)