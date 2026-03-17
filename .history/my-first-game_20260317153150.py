import pygame
import sys
import random
import math

# 1. 초기화
pygame.init()
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Enemy HP Bar")
clock = pygame.time.Clock()

# 색상
BLACK = (5, 2, 10)
BLOOD_RED = (255, 30, 70)
DEEP_PURPLE = (120, 0, 255)
NEON_CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 100)

# 게임 변수
player_pos = [WIDTH // 2, HEIGHT - 100]
player_hp = 100 # 이건 '탄약/공복' 게이지입니다.
enemies = [] # [x, y, speed, type, angle, current_hp, max_hp]
bullets = []
enemy_bullets = []
souls = []
score = 0
start_time = pygame.time.get_ticks()
last_drain_time = pygame.time.get_ticks()
drain_interval = 10000 
game_over = False

def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("malgungothic", size, True)
    img = font.render(text, True, color)
    screen.blit(img, img.get_rect(center=(x, y)))

def draw_enemy_with_hp(en):
    x, y, etype, angle, hp, m_hp = en[0], en[1], en[3], en[4], en[5], en[6]
    
    # 1. 적 본체 그리기
    color = DEEP_PURPLE
    if m_hp == 3: color = GOLD
    if m_hp >= 6: color = NEON_CYAN
    
    # 회전형 바디
    rect = pygame.Rect(x, y, 40, 40)
    pygame.draw.rect(screen, color, rect, 2 if m_hp > 1 else 0)
    if m_hp > 1:
        pygame.draw.circle(screen, color, (x+20, y+20), 5)

    # 2. 실시간 체력바 (맷집 1인 놈은 안 보여줌)
    if m_hp > 1:
        bar_width = 40
        bar_height = 5
        fill = (hp / m_hp) * bar_width
        pygame.draw.rect(screen, GRAY, (x, y - 10, bar_width, bar_height)) # 배경
        pygame.draw.rect(screen, GREEN, (x, y - 10, fill, bar_height))   # 현재 피

# --- 메인 루프 ---
while True:
    curr = pygame.time.get_ticks()
    sec = (curr - start_time) // 1000

    if not game_over:
        # 1. 공복 시스템 (10초 주기 사망)
        if curr - last_drain_time >= drain_interval:
            player_hp -= 20
            last_drain_time = curr
        if player_hp <= 0: game_over = True

        # 2. 입력 (슬로우 모션 없음)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 2:
                    if score < 500: bullets.append([player_pos[0]+20, player_pos[1], 0])
                    elif score < 1500:
                        bullets.append([player_pos[0]+10, player_pos[1], 0])
                        bullets.append([player_pos[0]+30, player_pos[1], 0])
                    else:
                        bullets.append([player_pos[0]+20, player_pos[1], 0])
                        bullets.append([player_pos[0]+20, player_pos[1], -2])
                        bullets.append([player_pos[0]+20, player_pos[1], 2])
                    player_hp -= 1.5

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 10: player_pos[0] -= 7
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH-50: player_pos[0] += 7
        if keys[pygame.K_UP] and player_pos[1] > 10: player_pos[1] -= 7
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT-50: player_pos[1] += 7

        # 3. 적 생성 (맷집 강화)
        if random.random() < 0.04 + (sec * 0.001):
            etype = 1 if random.random() < 0.3 else 0
            # 맷집 설정: 시간에 따라 더 단단한 놈 등장
            if sec > 60 and random.random() < 0.2: m_hp = 6
            elif sec > 30 and random.random() < 0.4: m_hp = 3
            else: m_hp = 1
            enemies.append([random.randint(40, WIDTH-40), -50, random.uniform(2, 4), etype, 0, m_hp, m_hp])

        # 적 로직
        for en in enemies[:]:
            en[1] += en[2]
            if en[3] == 1 and random.random() < 0.02: # 공격
                angle = math.atan2(player_pos[1]-en[1], player_pos[0]-en[0])
                enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle)*6, math.sin(angle)*6])
            
            # 플레이어 충돌 시 즉사
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).colliderect(pygame.Rect(en[0], en[1], 40, 40)):
                game_over = True
            if en[1] > HEIGHT: enemies.remove(en)

        # 내 탄환 로직 (적 HP 깎기)
        for b in bullets[:]:
            b[0] += b[2]; b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).collidepoint(b[0], b[1]):
                    en[5] -= 1 # HP 감소
                    if b in bullets: bullets.remove(b)
                    if en[5] <= 0:
                        souls.append([en[0]+20, en[1]+20])
                        score += 10 * en[6]
                        enemies.remove(en)

        # 적 탄환 충돌 시 즉사
        for eb in enemy_bullets[:]:
            eb[0] += eb[2]; eb[1] += eb[3]
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).collidepoint(eb[0], eb[1]):
                game_over = True
            elif eb[1] > HEIGHT or eb[0] < 0 or eb[0] > WIDTH: enemy_bullets.remove(eb)

        # 영혼 흡수
        for s in souls[:]:
            dx, dy = player_pos[0]+20-s[0], player_pos[1]+20-s[1]
            dist = (dx**2+dy**2)**0.5
            if dist < 20:
                player_hp = min(100, player_hp + 10); souls.remove(s)
            else:
                s[0] += dx * 0.2; s[1] += dy * 0.2

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_hp, score, game_over = 100, 0, False
                enemies, bullets, souls, enemy_bullets = [], [], [], []
                start_time = last_drain_time = pygame.time.get_ticks()

    # 4. 그리기
    screen.fill(BLACK)
    if not game_over:
        for b in bullets: pygame.draw.circle(screen, WHITE, (int(b[0]), int(b[1])), 4)
        for eb in enemy_bullets: pygame.draw.circle(screen, GOLD, (int(eb[0]), int(eb[1])), 6)
        for s in souls: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 5, 1)
        for en in enemies: draw_enemy_with_hp(en)
        
        # 플레이어 (한 번 맞으면 끝나는 운명)
        pygame.draw.polygon(screen, BLOOD_RED, [[player_pos[0]+20, player_pos[1]], [player_pos[0], player_pos[1]+40], [player_pos[0]+40, player_pos[1]+40]])
        
        # 배고픔 게이지 (탄약)
        pygame.draw.rect(screen, (30, 30, 30), (20, 20, 200, 15))
        pygame.draw.rect(screen, NEON_CYAN, (20, 20, player_hp * 2, 15))
        draw_text(f"SCORE: {score}", 25, WIDTH-100, 35)
    else:
        draw_text("GAME OVER", 60, WIDTH//2, HEIGHT//2-50, BLOOD_RED)
        draw_text(f"SCORE: {score}", 30, WIDTH//2, HEIGHT//2+20)
        draw_text("Press 'R' to Restart", 20, WIDTH//2, HEIGHT//2+80)

    pygame.display.flip()
    clock.tick(60)