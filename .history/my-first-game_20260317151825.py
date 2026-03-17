import pygame
import sys
import random

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: Blood & Soul")
clock = pygame.time.Clock()

# 색상 (대마왕 컨셉)
BLACK = (10, 0, 10)
BLOOD_RED = (200, 0, 0)
SOUL_PURPLE = (150, 0, 255)
WHITE = (255, 255, 255)

# 플레이어 설정
player_pos = [WIDTH // 2, HEIGHT - 50]
player_hp = 100
bullets = [] # 내가 쏜 탄환
enemies = [] # 적들
souls = []   # 적이 죽고 남긴 영혼 (자석 효과용)

# 게임 변수
score = 0
enemy_timer = 0

while True:
    # --- 1. 이벤트 처리 & 시간 왜곡 ---
    moving = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # 스페이스바를 누르면 체력을 소모해서 탄환 발사!
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_hp > 5:
                bullets.append([player_pos[0] + 20, player_pos[1]])
                player_hp -= 5 # 발사할 때마다 피가 깎임

    # --- 2. 입력 및 이동 (움직일 때만 시간 정상화) ---
    keys = pygame.key.get_pressed()
    speed = 5
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= speed
        moving = True
    if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - 40:
        player_pos[0] += speed
        moving = True

    # 시간 왜곡: 움직이지 않으면 적들의 속도가 1/5로 줄어듦
    time_scale = 1.0 if moving else 0.2

    # --- 3. 적 생성 및 이동 ---
    enemy_timer += 1
    if enemy_timer > 30: # 적 생성 빈도
        enemies.append([random.randint(0, WIDTH-40), -40])
        enemy_timer = 0

    for en in enemies[:]:
        en[1] += 3 * time_scale # 아래로 내려옴
        if en[1] > HEIGHT: enemies.remove(en)

    # --- 4. 탄환 이동 및 충돌 ---
    for b in bullets[:]:
        b[1] -= 10
        if b[1] < 0: bullets.remove(b)
        
        # 적과 충돌 체크
        for en in enemies[:]:
            if (en[0] < b[0] < en[0]+40) and (en[1] < b[1] < en[1]+40):
                souls.append([en[0]+20, en[1]+20]) # 적이 죽은 자리에 영혼 생성
                enemies.remove(en)
                if b in bullets: bullets.remove(b)
                score += 10

    # --- 5. 영혼 자석 효과 (체력 회복) ---
    for s in souls[:]:
        # 플레이어 쪽으로 빨려 들어옴
        dx = player_pos[0] + 20 - s[0]
        dy = player_pos[1] + 20 - s[1]
        dist = (dx**2 + dy**2)**0.5
        if dist < 10:
            player_hp = min(100, player_hp + 10) # 체력 회복
            souls.remove(s)
        else:
            s[0] += dx * 0.1
            s[1] += dy * 0.1

    # --- 6. 그리기 ---
    screen.fill(BLACK)
    
    # 플레이어 (삼각형)
    pygame.draw.polygon(screen, BLOOD_RED, [[player_pos[0]+20, player_pos[1]], 
                                            [player_pos[0], player_pos[1]+40], 
                                            [player_pos[0]+40, player_pos[1]+40]])
    
    # 탄환 (붉은 선)
    for b in bullets:
        pygame.draw.rect(screen, BLOOD_RED, (b[0], b[1], 4, 15))
        
    # 적 (보라색 사각형)
    for en in enemies:
        pygame.draw.rect(screen, SOUL_PURPLE, (en[0], en[1], 40, 40))
        
    # 영혼 (자석 효과를 받는 작은 원)
    for s in souls:
        pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 5)

    # UI (체력 바)
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 20))
    pygame.draw.rect(screen, BLOOD_RED, (10, 10, player_hp * 2, 20))

    pygame.display.flip()
    clock.tick(60)