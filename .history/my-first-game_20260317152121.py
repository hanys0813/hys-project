import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Death Match")
clock = pygame.time.Clock()

# 색상
BLACK = (5, 0, 10)
BLOOD_RED = (255, 0, 50)
SHADOW_PURPLE = (100, 0, 200)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# 게임 상태 변수
player_pos = [WIDTH // 2, HEIGHT - 70]
player_hp = 100
bullets = []        # 플레이어 탄환
enemies = []        # 적 (x, y, speed, type) - type 0:일반, 1:공격형
enemy_bullets = []  # 적이 쏜 탄환
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
            
            # 발사 (체력 소모)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 5:
                    bullets.append([player_pos[0] + 20, player_pos[1]])
                    player_hp -= 5
                # 탄약을 다 썼을 때 사망 판정은 아래 로직에서 처리

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

        # 2. 적 생성 (일반 적 vs 공격하는 적)
        if random.random() < 0.05 * time_scale:
            etype = 1 if random.random() < 0.3 else 0 # 30% 확률로 공격형 등장
            enemies.append([random.randint(0, WIDTH-40), -50, random.uniform(2, 4), etype, 0])

        # 3. 로직 업데이트
        # 적 이동 및 공격
        for en in enemies[:]:
            en[1] += en[2] * time_scale
            
            # 공격형 적(type 1)의 사격 로직
            if en[3] == 1:
                en[4] += 1 # 공격 쿨타임 카운트
                if en[4] > 80: # 일정 시간마다 발사
                    # 플레이어 방향으로 조준탄 계산
                    angle = math.atan2(player_pos[1] - en[1], player_pos[0] - en[0])
                    enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle)*5, math.sin(angle)*5])
                    en[4] = 0

            # 충돌 판정
            p_rect = pygame.Rect(player_pos[0], player_pos[1], 40, 40)
            e_rect = pygame.Rect(en[0], en[1], 40, 40)
            if p_rect.colliderect(e_rect):
                game_over = True
            if en[1] > HEIGHT: enemies.remove(en)

        # 적 탄환 이동 및 충돌
        for eb in enemy_bullets[:]:
            eb[0] += eb[2] * time_scale
            eb[1] += eb[3] * time_scale
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).collidepoint(eb[0], eb[1]):
                player_hp -= 15 # 적 탄환에 맞으면 데미지
                enemy_bullets.remove(eb)
            elif eb[1] > HEIGHT or eb[0] < 0 or eb[0] > WIDTH:
                enemy_bullets.remove(eb)

        # 내 탄환 이동 및 적 처치
        for b in bullets[:]:
            b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).collidepoint(b[0], b[1]):
                    souls.append([en[0]+20, en[1]+20])
                    enemies.remove(en)
                    if b in bullets: bullets.remove(b)
                    score += 15 if en[3] == 1 else 10

        # 영혼 흡수 (자석)
        for s in souls[:]:
            dx = player_pos[0] + 20 - s[0]
            dy = player_pos[1] + 20 - s[1]
            dist = (dx**2 + dy**2)**0.5
            if dist < 15:
                player_hp = min(100, player_hp + 10)
                souls.remove(s)
            else:
                s[0] += dx * 0.15
                s[1] += dy * 0.15

        # 체력 소진 체크 (탄약 다 써도 사망)
        if player_hp <= 0:
            game_over = True

    else:
        # 게임 오버 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_hp, score, game_over = 100, 0, False
                enemies, bullets, souls, enemy_bullets = [], [], [], []

    # --- 4. 그리기 ---
    screen.fill(BLACK)
    
    if not game_over:
        # 적 탄환 (노란색 파동)
        for eb in enemy_bullets:
            pygame.draw.circle(screen, GOLD, (int(eb[0]), int(eb[1])), 6)

        # 영혼/내 탄환 그리기 (이전과 동일)
        for s in souls: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 4)
        for b in bullets: pygame.draw.ellipse(screen, BLOOD_RED, (b[0]-2, b[1], 6, 20))

        # 적 (일반 vs 정예병)
        for en in enemies:
            color = GOLD if en[3] == 1 else SHADOW_PURPLE
            pygame.draw.rect(screen, color, (en[0], en[1], 40, 40), 3)
            if en[3] == 1: # 정예병은 안에 빨간 눈 표시
                pygame.draw.circle(screen, BLOOD_RED, (en[0]+20, en[1]+20), 5)

        # 플레이어 및 UI (이전과 동일)
        pygame.draw.polygon(screen, BLOOD_RED, [[player_pos[0]+20, player_pos[1]], [player_pos[0], player_pos[1]+40], [player_pos[0]+40, player_pos[1]+40]])
        pygame.draw.rect(screen, (30, 30, 30), (20, 20, 200, 15))
        pygame.draw.rect(screen, BLOOD_RED, (20, 20, max(0, player_hp * 2), 15))
        draw_text(f"SOULS: {score}", 25, WIDTH - 80, 30)
    else:
        screen.fill((20, 0, 0))
        draw_text("DEMON DEFEATED", 60, WIDTH//2, HEIGHT//2 - 50, BLOOD_RED)
        draw_text(f"FINAL SOULS: {score}", 30, WIDTH//2, HEIGHT//2 + 20)
        draw_text("Press 'R' to Resurrect", 20, WIDTH//2, HEIGHT//2 + 80, SHADOW_PURPLE)

    pygame.display.flip()
    clock.tick(60)