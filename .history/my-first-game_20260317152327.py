import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Evolution")
clock = pygame.time.Clock()

# 색상
BLACK = (5, 0, 10)
BLOOD_RED = (255, 0, 50)
SHADOW_PURPLE = (100, 0, 200)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)

# 게임 상태 변수
player_pos = [WIDTH // 2, HEIGHT - 70]
player_hp = 100.0  # 정밀한 계산을 위해 실수형으로 변경
bullets = []
enemies = []
enemy_bullets = []
souls = []
score = 0
level = 1
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
            
            # 발사 (레벨에 따른 탄환 생성)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 3:
                    if level == 1:
                        bullets.append([player_pos[0] + 20, player_pos[1], 0])
                    elif level == 2:
                        bullets.append([player_pos[0] + 5, player_pos[1], 0])
                        bullets.append([player_pos[0] + 35, player_pos[1], 0])
                    elif level >= 3:
                        bullets.append([player_pos[0] + 20, player_pos[1], 0])
                        bullets.append([player_pos[0] + 20, player_pos[1], -2]) # 왼쪽 대각선
                        bullets.append([player_pos[0] + 20, player_pos[1], 2])  # 오른쪽 대각선
                    player_hp -= 3

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

        # --- [추가] 실시간 피 깎임 (공복 시스템) ---
        # 매 프레임마다 조금씩 감소 (초당 약 2~3 정도 감소)
        player_hp -= 0.05 * time_scale

        # 2. 레벨 업 시스템
        if score >= 600: level = 4
        elif score >= 300: level = 3
        elif score >= 100: level = 2

        # 3. 적 생성 및 이동 로직 (기존과 동일하되 점수별 난이도 상승)
        spawn_rate = 0.05 + (level * 0.01)
        if random.random() < spawn_rate * time_scale:
            etype = 1 if random.random() < 0.2 + (level * 0.05) else 0
            enemies.append([random.randint(0, WIDTH-40), -50, random.uniform(2, 4), etype, 0])

        # 적 로직 업데이트
        for en in enemies[:]:
            en[1] += en[2] * time_scale
            if en[3] == 1: # 공격형
                en[4] += 1
                if en[4] > 100 / time_scale:
                    angle = math.atan2(player_pos[1] - en[1], player_pos[0] - en[0])
                    enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle)*5, math.sin(angle)*5])
                    en[4] = 0
            # 충돌
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).colliderect(pygame.Rect(en[0], en[1], 40, 40)):
                game_over = True
            if en[1] > HEIGHT: enemies.remove(en)

        # 내 탄환 이동 (대각선 발사 포함)
        for b in bullets[:]:
            b[0] += b[2] # 대각선 이동값
            b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).collidepoint(b[0], b[1]):
                    souls.append([en[0]+20, en[1]+20])
                    enemies.remove(en)
                    if b in bullets: bullets.remove(b)
                    score += 20 if en[3] == 1 else 10

        # 적 탄환 충돌
        for eb in enemy_bullets[:]:
            eb[0] += eb[2] * time_scale
            eb[1] += eb[3] * time_scale
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).collidepoint(eb[0], eb[1]):
                player_hp -= 15
                enemy_bullets.remove(eb)
            elif eb[1] > HEIGHT or eb[0] < 0 or eb[0] > WIDTH:
                enemy_bullets.remove(eb)

        # 영혼 흡수 및 회복
        for s in souls[:]:
            dx = player_pos[0] + 20 - s[0]
            dy = player_pos[1] + 20 - s[1]
            dist = (dx**2 + dy**2)**0.5
            if dist < 20:
                player_hp = min(100, player_hp + 12)
                souls.remove(s)
            else:
                s[0] += dx * 0.2
                s[1] += dy * 0.2

        if player_hp <= 0:
            game_over = True

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_hp, score, level, game_over = 100, 0, 1, False
                enemies, bullets, souls, enemy_bullets = [], [], [], []

    # --- 4. 그리기 ---
    screen.fill(BLACK)
    
    if not game_over:
        # 탄환 궤적 효과
        for b in bullets:
            color = CYAN if level == 4 else BLOOD_RED
            pygame.draw.ellipse(screen, color, (b[0]-3, b[1], 8, 25))

        for en in enemies:
            color = GOLD if en[3] == 1 else SHADOW_PURPLE
            pygame.draw.rect(screen, color, (en[0], en[1], 40, 40), 3)
        
        for eb in enemy_bullets: pygame.draw.circle(screen, GOLD, (int(eb[0]), int(eb[1])), 6)
        for s in souls: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 5)

        # 플레이어 진화 단계 표시
        p_color = BLOOD_RED if level < 4 else CYAN
        pygame.draw.polygon(screen, p_color, [[player_pos[0]+20, player_pos[1]], [player_pos[0], player_pos[1]+40], [player_pos[0]+40, player_pos[1]+40]])
        
        # UI
        pygame.draw.rect(screen, (30, 30, 30), (20, 20, 200, 15))
        pygame.draw.rect(screen, BLOOD_RED, (20, 20, max(0, player_hp * 2), 15))
        draw_text(f"SOULS: {score}", 25, WIDTH - 80, 30)
        draw_text(f"LV. {level}", 25, 40, 60, GOLD)
    else:
        screen.fill((20, 0, 0))
        draw_text("DEMON DEFEATED", 60, WIDTH//2, HEIGHT//2 - 50, BLOOD_RED)
        draw_text(f"FINAL SOULS: {score}", 30, WIDTH//2, HEIGHT//2 + 20)
        draw_text("Press 'R' to Resurrect", 20, WIDTH//2, HEIGHT//2 + 80, SHADOW_PURPLE)

    pygame.display.flip()
    clock.tick(60)