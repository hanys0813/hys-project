import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: No Mercy")
clock = pygame.time.Clock()

# 색상
BLACK = (5, 2, 10)
BLOOD_RED = (255, 30, 70)
DEEP_PURPLE = (120, 0, 255)
NEON_CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
SHIELD_BLUE = (0, 191, 255)

# 게임 변수
player_pos = [WIDTH // 2, HEIGHT - 100]
player_hp = 100
bullets = []
enemies = [] # [x, y, speed, type, angle, hp, max_hp]
enemy_bullets = []
souls = []
score = 0
start_time = pygame.time.get_ticks()
last_drain_time = pygame.time.get_ticks()
drain_interval = 10000 
game_over = False

def draw_text(text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("malgungothic", size, True)
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def draw_player(x, y, sc):
    # 점수에 따른 기체 색상 변경
    color = BLOOD_RED
    if sc >= 1500: color = NEON_CYAN
    elif sc >= 500: color = GOLD
    
    # 엔진 불꽃
    f_h = random.randint(15, 35)
    pygame.draw.polygon(screen, DEEP_PURPLE, [[x+20, y+45+f_h], [x+10, y+40], [x+30, y+40]])
    # 본체
    pygame.draw.polygon(screen, (50, 50, 50), [[x, y+40], [x-15, y+50], [x, y+20]])
    pygame.draw.polygon(screen, (50, 50, 50), [[x+40, y+40], [x+55, y+50], [x+40, y+20]])
    pygame.draw.polygon(screen, color, [[x+20, y], [x, y+40], [x+40, y+40]])
    pygame.draw.circle(screen, WHITE, (x+20, y+25), 5)

def draw_enemy(en):
    x, y, etype, angle, ehp, max_hp = en[0], en[1], en[3], en[4], en[5], en[6]
    
    # 체력(방어막) 시각화
    if ehp >= 3:
        pygame.draw.circle(screen, SHIELD_BLUE, (x+20, y+20), 30, 3) # 강력한 3중 방어막
    elif ehp == 2:
        pygame.draw.circle(screen, GOLD, (x+20, y+20), 26, 2) # 2중 방어막
        
    if etype == 0: # 회전 톱날
        for i in range(4):
            a = math.radians(angle + i * 90)
            pygame.draw.line(screen, DEEP_PURPLE, (x+20, y+20), (x+20+math.cos(a)*20, y+20+math.sin(a)*20), 5)
        pygame.draw.circle(screen, (80, 80, 80), (x+20, y+20), 10)
    else: # 공격병
        pygame.draw.rect(screen, BLOOD_RED if ehp == 1 else GOLD, (x, y, 40, 40), 0 if ehp == 1 else 2)
        pygame.draw.circle(screen, WHITE, (x+20, y+20), 5)

# --- 메인 루프 ---
while True:
    current_time = pygame.time.get_ticks()
    elapsed_sec = (current_time - start_time) // 1000

    if not game_over:
        # 1. 10초 주기 피 깎임
        time_passed = current_time - last_drain_time
        if time_passed >= drain_interval:
            player_hp -= 20
            last_drain_time = current_time
        
        # 2. 플레이어 사격 및 입력
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 2:
                    # 사격 화력 진화
                    if score < 500:
                        bullets.append([player_pos[0]+20, player_pos[1], 0])
                    elif score < 1500:
                        bullets.append([player_pos[0]+10, player_pos[1], 0])
                        bullets.append([player_pos[0]+30, player_pos[1], 0])
                    else:
                        bullets.append([player_pos[0]+20, player_pos[1], 0])
                        bullets.append([player_pos[0]+20, player_pos[1], -2])
                        bullets.append([player_pos[0]+20, player_pos[1], 2])
                    player_hp -= 1.5 # 탄약 효율 상향

        keys = pygame.key.get_pressed()
        p_speed = 7
        if keys[pygame.K_LEFT] and player_pos[0] > 20: player_pos[0] -= p_speed
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH-60: player_pos[0] += p_speed
        if keys[pygame.K_UP] and player_pos[1] > 20: player_pos[1] -= p_speed
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT-60: player_pos[1] += p_speed

        # 슬로우 모션 삭제 -> 무조건 1.0 고정
        time_scale = 1.0

        # 3. 적 생성 로직 (시간이 흐를수록 맷집 센 적 등장)
        if random.random() < (0.04 + (elapsed_sec * 0.001)):
            etype = 1 if random.random() < min(0.5, 0.2 + (elapsed_sec * 0.005)) else 0
            # 맷집 결정 (시간에 따라 최대 3회까지)
            hp_roll = random.random()
            if elapsed_sec > 60 and hp_roll < 0.2: ehp = 3
            elif elapsed_sec > 30 and hp_roll < 0.4: ehp = 2
            else: ehp = 1
            enemies.append([random.randint(40, WIDTH-40), -50, random.uniform(2, 4), etype, 0, ehp, ehp])

        # 적 업데이트
        for en in enemies[:]:
            en[1] += en[2] * time_scale
            en[4] += 5 * time_scale # 회전
            
            if en[3] == 1: # 공격형
                shoot_chance = 0.015 if elapsed_sec < 40 else 0.03
                if random.random() < shoot_chance:
                    angle = math.atan2(player_pos[1]-en[1], player_pos[0]-en[0])
                    enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle)*6, math.sin(angle)*6])
                    if elapsed_sec > 45: # 중반 이후 2연발
                        enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle+0.15)*6, math.sin(angle+0.15)*6])

            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).colliderect(pygame.Rect(en[0], en[1], 40, 40)):
                game_over = True
            if en[1] > HEIGHT: enemies.remove(en)

        # 내 탄환 충돌 (HP 깎기)
        for b in bullets[:]:
            b[0] += b[2]; b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).inflate(10, 10).collidepoint(b[0], b[1]):
                    en[5] -= 1 # 적 HP 1 감소
                    if b in bullets: bullets.remove(b)
                    if en[5] <= 0:
                        souls.append([en[0]+20, en[1]+20])
                        enemies.remove(en); score += (10 * en[6]) # 맷집 센 놈은 점수 더 줌

        # 적 탄환 처리
        for eb in enemy_bullets[:]:
            eb[0] += eb[2]; eb[1] += eb[3]
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).collidepoint(eb[0], eb[1]):
                player_hp -= 15; enemy_bullets.remove(eb)
            elif eb[1] > HEIGHT or eb[1] < 0 or eb[0] < 0 or eb[0] > WIDTH: 
                enemy_bullets.remove(eb)

        # 영혼 흡수
        for s in souls[:]:
            dx, dy = player_pos[0]+20-s[0], player_pos[1]+20-s[1]
            dist = (dx**2+dy**2)**0.5
            if dist < 20:
                player_hp = min(100, player_hp + 8); souls.remove(s)
            else:
                s[0] += dx * 0.18; s[1] += dy * 0.18

        if player_hp <= 0: game_over = True

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_hp, score, game_over = 100, 0, False
                enemies, bullets, souls, enemy_bullets = [], [], [], []
                start_time = last_drain_time = pygame.time.get_ticks()

    # --- 4. 그리기 ---
    screen.fill(BLACK)
    if not game_over:
        for s in souls: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 4)
        for b in bullets: pygame.draw.ellipse(screen, WHITE, (b[0]-3, b[1], 6, 15))
        for eb in enemy_bullets: pygame.draw.circle(screen, GOLD, (int(eb[0]), int(eb[1])), 6)
        for en in enemies: draw_enemy(en)
        draw_player(player_pos[0], player_pos[1], score)

        # UI
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
        pygame.draw.rect(screen, BLOOD_RED, (20, 20, max(0, player_hp * 2), 20))
        drain_bar = ((current_time - last_drain_time) / drain_interval) * 200
        pygame.draw.rect(screen, NEON_CYAN, (20, 45, 200 - drain_bar, 5))
        
        draw_text(f"SCORE: {score}", 25, WIDTH-100, 35, GOLD)
        draw_text(f"TIME: {elapsed_sec}s", 25, WIDTH-100, 70, WHITE)
    else:
        draw_text("DEMON DEFEATED", 60, WIDTH//2, HEIGHT//2-50, BLOOD_RED)
        draw_text(f"SCORE: {score} | TIME: {elapsed_sec}s", 30, WIDTH//2, HEIGHT//2+20)
        draw_text("Press 'R' to Resurrect", 20, WIDTH//2, HEIGHT//2+80, DEEP_PURPLE)

    pygame.display.flip()
    clock.tick(60)