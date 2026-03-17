import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 700 # 화면 살짝 키움
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Legend Edition")
clock = pygame.time.Clock()

# 색상 (레전드 형님 전용 컬러)
BLACK = (5, 2, 10)
BLOOD_RED = (255, 30, 70)
DEEP_PURPLE = (120, 0, 255)
NEON_CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# 게임 변수
player_pos = [WIDTH // 2, HEIGHT - 100]
player_hp = 100
bullets = []
enemies = [] # [x, y, speed, type, angle]
enemy_bullets = []
souls = []
score = 0
level = 1
game_over = False

# 시간 관련 변수 (10초 주기)
last_drain_time = pygame.time.get_ticks()
drain_interval = 10000 # 10초

def draw_text(text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("malgungothic", size, True) # 한글 지원 폰트
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def draw_player(x, y, lvl):
    # 몸체
    color = NEON_CYAN if lvl >= 4 else BLOOD_RED
    # 엔진 불꽃 (애니메이션)
    f_h = random.randint(15, 35)
    pygame.draw.polygon(screen, DEEP_PURPLE, [[x+20, y+45+f_h], [x+10, y+40], [x+30, y+40]])
    # 좌우 날개
    pygame.draw.polygon(screen, (50, 50, 50), [[x, y+40], [x-15, y+50], [x, y+20]])
    pygame.draw.polygon(screen, (50, 50, 50), [[x+40, y+40], [x+55, y+50], [x+40, y+20]])
    # 메인 바디
    pygame.draw.polygon(screen, color, [[x+20, y], [x, y+40], [x+40, y+40]])
    # 조종석
    pygame.draw.circle(screen, WHITE, (x+20, y+25), 5)

def draw_enemy(en):
    x, y, etype, angle = en[0], en[1], en[3], en[4]
    if etype == 0: # 회전 톱날 장애물
        for i in range(4):
            a = math.radians(angle + i * 90)
            px = x + 20 + math.cos(a) * 20
            py = y + 20 + math.sin(a) * 20
            pygame.draw.line(screen, DEEP_PURPLE, (x+20, y+20), (px, py), 5)
        pygame.draw.circle(screen, (80, 80, 80), (x+20, y+20), 10)
    else: # 정예 조준병
        pygame.draw.rect(screen, GOLD, (x, y, 40, 40), 2)
        pygame.draw.rect(screen, BLOOD_RED, (x+12, y+12, 16, 16))
        # 안테나 효과
        pygame.draw.line(screen, GOLD, (x+20, y), (x+20, y-10))

# --- 메인 루프 ---
while True:
    current_time = pygame.time.get_ticks()
    
    if not game_over:
        # 1. 10초 주기 피 깎임 (두 틱)
        time_passed = current_time - last_drain_time
        if time_passed >= drain_interval:
            player_hp -= 20 # 두 틱 정도 확 깎음
            last_drain_time = current_time
        
        # 2. 입력 및 시간 왜곡
        moving = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_hp > 2:
                    # 레벨별 탄환 발사
                    bullets.append([player_pos[0]+20, player_pos[1], 0])
                    if level >= 2:
                        bullets.append([player_pos[0]+5, player_pos[1]+10, -1])
                        bullets.append([player_pos[0]+35, player_pos[1]+10, 1])
                    player_hp -= 2

        keys = pygame.key.get_pressed()
        speed = 7
        if keys[pygame.K_LEFT] and player_pos[0] > 20: player_pos[0] -= speed; moving = True
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH-60: player_pos[0] += speed; moving = True
        if keys[pygame.K_UP] and player_pos[1] > 20: player_pos[1] -= speed; moving = True
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT-60: player_pos[1] += speed; moving = True

        time_scale = 1.0 if moving else 0.25

        # 3. 밸런스 기반 적 생성
        # 레벨업 기준 상향 (100 -> 200 -> 500)
        if score >= 500: level = 4
        elif score >= 200: level = 3
        elif score >= 80: level = 2

        if random.random() < (0.04 + level * 0.01) * time_scale:
            etype = 1 if random.random() < 0.2 + (level*0.05) else 0
            enemies.append([random.randint(40, WIDTH-40), -50, random.uniform(2, 5), etype, 0])

        # 적 업데이트
        for en in enemies[:]:
            en[1] += en[2] * time_scale
            en[4] += 5 * time_scale # 회전 애니메이션
            
            if en[3] == 1: # 정예병 사격
                if random.random() < 0.02 * time_scale:
                    angle = math.atan2(player_pos[1] - en[1], player_pos[0] - en[0])
                    enemy_bullets.append([en[0]+20, en[1]+20, math.cos(angle)*6, math.sin(angle)*6])

            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).colliderect(pygame.Rect(en[0], en[1], 40, 40)):
                game_over = True
            if en[1] > HEIGHT: enemies.remove(en)

        # 탄환 및 충돌
        for b in bullets[:]:
            b[0] += b[2]; b[1] -= 12
            if b[1] < 0: bullets.remove(b)
            for en in enemies[:]:
                if pygame.Rect(en[0], en[1], 40, 40).collidepoint(b[0], b[1]):
                    souls.append([en[0]+20, en[1]+20])
                    enemies.remove(en); score += 10
                    if b in bullets: bullets.remove(b)

        # 적 탄환
        for eb in enemy_bullets[:]:
            eb[0] += eb[2] * time_scale; eb[1] += eb[3] * time_scale
            if pygame.Rect(player_pos[0], player_pos[1], 40, 40).collidepoint(eb[0], eb[1]):
                player_hp -= 15; enemy_bullets.remove(eb)
            elif eb[1] > HEIGHT: enemy_bullets.remove(eb)

        # 영혼 흡수 (회복량 너프)
        for s in souls[:]:
            dx, dy = player_pos[0]+20-s[0], player_pos[1]+20-s[1]
            dist = (dx**2+dy**2)**0.5
            if dist < 20:
                player_hp = min(100, player_hp + 7) # 회복량 감소
                souls.remove(s)
            else:
                s[0] += dx * 0.15; s[1] += dy * 0.15

        if player_hp <= 0: game_over = True

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player_hp, score, level, game_over = 100, 0, 1, False
                enemies, bullets, souls, enemy_bullets = [], [], [], []
                last_drain_time = pygame.time.get_ticks()

    # --- 4. 그리기 ---
    screen.fill(BLACK)
    if not game_over:
        for s in souls: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 4)
        for b in bullets: pygame.draw.circle(screen, NEON_CYAN if level >= 4 else BLOOD_RED, (int(b[0]), int(b[1])), 4)
        for eb in enemy_bullets: pygame.draw.circle(screen, GOLD, (int(eb[0]), int(eb[1])), 6)
        for en in enemies: draw_enemy(en)
        
        draw_player(player_pos[0], player_pos[1], level)

        # UI 가독성 업그레이드
        # 피 바
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
        pygame.draw.rect(screen, BLOOD_RED, (20, 20, player_hp * 2, 20))
        # 10초 게이지
        drain_bar = (time_passed / drain_interval) * 200
        pygame.draw.rect(screen, (30, 30, 80), (20, 45, 200, 5))
        pygame.draw.rect(screen, NEON_CYAN, (20, 45, 200 - drain_bar, 5))
        
        draw_text(f"SCORE: {score}", 25, WIDTH-100, 35, GOLD)
        draw_text(f"LV. {level}", 25, 240, 30, NEON_CYAN, False)
    else:
        screen.fill((10, 0, 0))
        draw_text("DEMON DEFEATED", 60, WIDTH//2, HEIGHT//2-50, BLOOD_RED)
        draw_text(f"FINAL SCORE: {score}", 30, WIDTH//2, HEIGHT//2+20)
        draw_text("Press 'R' to Resurrect", 20, WIDTH//2, HEIGHT//2+80, DEEP_PURPLE)

    pygame.display.flip()
    clock.tick(60)