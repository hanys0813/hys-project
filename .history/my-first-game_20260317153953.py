import pygame
import sys
import random
import math

pygame.init()
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEMON REAPER: No Mercy")
clock = pygame.time.Clock()

# 색상
BLACK       = (5, 2, 10)
BLOOD_RED   = (255, 30, 70)
DARK_RED    = (160, 10, 30)
DEEP_PURPLE = (120, 0, 255)
NEON_CYAN   = (0, 255, 255)
GOLD        = (255, 215, 0)
WHITE       = (255, 255, 255)
SHIELD_BLUE = (0, 191, 255)
ORANGE      = (255, 140, 0)
GREEN_NEON  = (0, 255, 100)
PINK        = (255, 60, 200)
GRAY_DARK   = (40, 40, 55)
TEAL        = (0, 200, 180)

# ──────────────────────────────────────────────
# 적 정의 테이블
# type_id : (name, base_hp, shape, color, speed_range, score_val, shoot_type)
# shoot_type: 0=없음, 1=직진, 2=삼방향, 3=원형
ENEMY_DEFS = {
    0: ("톱날",      1, "saw",      DEEP_PURPLE, (2.5, 4.0), 10,  0),
    1: ("돌격병",    1, "soldier",  BLOOD_RED,   (2.0, 3.5), 12,  1),
    2: ("중장갑",    3, "tank",     (80,80,80),  (1.0, 2.0), 40,  1),
    3: ("보스눈알",  5, "eyeball",  GOLD,        (0.8, 1.5), 80,  2),
    4: ("수류탄",    2, "grenade",  ORANGE,      (1.5, 3.0), 25,  0),  # 파괴시 폭발
    5: ("유령",      2, "ghost",    (160,0,255,180),(1.8,3.0),30, 3),
    6: ("스텔스",    1, "stealth",  (30,30,50),  (3.5, 5.5), 20,  1),  # 반투명, 빠름
}

# ──────────────────────────────────────────────
# 파티클
particles = []   # [x, y, vx, vy, life, max_life, color, size]

def spawn_particles(x, y, color, count=12, speed=4, size=3):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd   = random.uniform(1, speed)
        life  = random.randint(20, 45)
        particles.append([x, y, math.cos(angle)*spd, math.sin(angle)*spd,
                          life, life, color, random.randint(1, size)])

def update_draw_particles():
    for p in particles[:]:
        p[0] += p[2]; p[1] += p[3]
        p[3] += 0.12  # 중력
        p[4] -= 1
        alpha = p[4] / p[5]
        c = p[6]
        col = (int(c[0]*alpha), int(c[1]*alpha), int(c[2]*alpha))
        pygame.draw.circle(screen, col, (int(p[0]), int(p[1])), p[7])
        if p[4] <= 0: particles.remove(p)

# ──────────────────────────────────────────────
# 배경 별
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
          random.uniform(0.3, 1.5), random.randint(1, 2)] for _ in range(120)]

def draw_stars():
    for s in stars:
        s[1] += s[2]
        if s[1] > HEIGHT: s[1] = 0; s[0] = random.randint(0, WIDTH)
        bright = random.randint(150, 255)
        pygame.draw.circle(screen, (bright, bright, bright), (int(s[0]), int(s[1])), s[3])

# ──────────────────────────────────────────────
# 화면흔들림
shake_timer = 0
shake_mag   = 0

def trigger_shake(mag=6, dur=8):
    global shake_timer, shake_mag
    shake_timer = dur; shake_mag = mag

def get_shake_offset():
    if shake_timer > 0:
        return (random.randint(-shake_mag, shake_mag),
                random.randint(-shake_mag, shake_mag))
    return (0, 0)

# ──────────────────────────────────────────────
def draw_text(text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("malgungothic", size, True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf, rect)

# ──────────────────────────────────────────────
def draw_player(x, y, sc, inv_timer):
    # 색상 티어
    color = BLOOD_RED
    if sc >= 1500:   color = NEON_CYAN
    elif sc >= 500:  color = GOLD

    # 무적 깜빡임
    if inv_timer > 0 and (inv_timer // 4) % 2 == 0:
        return

    # 엔진 불꽃 (2개)
    for ox in [8, 28]:
        fh = random.randint(12, 28)
        pygame.draw.polygon(screen, DEEP_PURPLE,
            [[x+ox+4, y+45+fh], [x+ox, y+38], [x+ox+8, y+38]])

    # 날개
    pygame.draw.polygon(screen, GRAY_DARK, [[x,y+40],[x-18,y+52],[x,y+18]])
    pygame.draw.polygon(screen, GRAY_DARK, [[x+40,y+40],[x+58,y+52],[x+40,y+18]])
    # 동체
    pygame.draw.polygon(screen, color, [[x+20,y],[x,y+40],[x+40,y+40]])
    # 조종석
    pygame.draw.circle(screen, WHITE, (x+20, y+24), 6)
    pygame.draw.circle(screen, (100,200,255), (x+20, y+24), 4)

# ──────────────────────────────────────────────
def draw_hp_bar(x, y, hp, max_hp, width=44, height=6):
    """적 머리 위 HP 바"""
    if max_hp <= 1:
        return  # hp 1짜리는 바 안 그림 (작아서 의미 없음)
    ratio = max(0, hp / max_hp)
    bar_x = x - 2
    bar_y = y - 12
    # 배경
    pygame.draw.rect(screen, (40, 10, 10), (bar_x, bar_y, width, height))
    # HP
    if ratio > 0.6:   bar_color = GREEN_NEON
    elif ratio > 0.3: bar_color = GOLD
    else:             bar_color = BLOOD_RED
    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(width * ratio), height))
    # 테두리
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, width, height), 1)

# ──────────────────────────────────────────────
def draw_enemy(en):
    x, y   = int(en[0]), int(en[1])
    etype  = en[3]   # type_id
    angle  = en[4]
    hp     = en[5]
    max_hp = en[6]
    alpha_val = en[7] if len(en) > 7 else 255  # 스텔스용

    cx, cy = x + 20, y + 20
    name, _, shape, base_color, _, _, _ = ENEMY_DEFS[etype]

    # ── 방어막 링 (hp > 1)
    if hp >= 3:
        r = 32 + math.sin(pygame.time.get_ticks()*0.005)*3
        pygame.draw.circle(screen, SHIELD_BLUE, (cx, cy), int(r), 2)
    elif hp == 2:
        r = 28 + math.sin(pygame.time.get_ticks()*0.006)*2
        pygame.draw.circle(screen, GOLD, (cx, cy), int(r), 2)

    # ── 형태별 그리기
    if shape == "saw":        _draw_saw(screen, cx, cy, angle, base_color, hp)
    elif shape == "soldier":  _draw_soldier(screen, cx, cy, angle, base_color, hp)
    elif shape == "tank":     _draw_tank(screen, cx, cy, angle, base_color, hp)
    elif shape == "eyeball":  _draw_eyeball(screen, cx, cy, angle, base_color, hp)
    elif shape == "grenade":  _draw_grenade(screen, cx, cy, angle, base_color, hp)
    elif shape == "ghost":    _draw_ghost(screen, cx, cy, angle, base_color, hp)
    elif shape == "stealth":  _draw_stealth(screen, cx, cy, angle, base_color, hp)

    # ── HP 바
    draw_hp_bar(x, y, hp, max_hp)

def _draw_saw(surf, cx, cy, angle, color, hp):
    # 회전 톱날 – 4개 날 + 중심 원
    for i in range(6):
        a = math.radians(angle + i * 60)
        ex = cx + math.cos(a) * 22
        ey = cy + math.sin(a) * 22
        pygame.draw.polygon(surf, color, [
            (cx + math.cos(a-0.3)*8, cy + math.sin(a-0.3)*8),
            (ex, ey),
            (cx + math.cos(a+0.3)*8, cy + math.sin(a+0.3)*8)
        ])
    pygame.draw.circle(surf, (90,90,90), (cx,cy), 9)
    pygame.draw.circle(surf, WHITE, (cx,cy), 4)

def _draw_soldier(surf, cx, cy, angle, color, hp):
    # 마름모 몸통
    pts = [(cx, cy-20),(cx+16,cy),(cx,cy+20),(cx-16,cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, WHITE, pts, 1)
    # 눈
    ex = cx + math.cos(math.radians(angle))*6
    ey = cy + math.sin(math.radians(angle))*6
    pygame.draw.circle(surf, NEON_CYAN, (int(ex),int(ey)), 4)

def _draw_tank(surf, cx, cy, angle, color, hp):
    # 큰 육각형 + 포신
    pts = []
    for i in range(6):
        a = math.radians(i*60 + angle*0.3)
        pts.append((cx + math.cos(a)*22, cy + math.sin(a)*22))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, GOLD, pts, 2)
    # 포신
    gun_a = math.radians(angle)
    pygame.draw.line(surf, GOLD, (cx,cy),
        (cx + math.cos(gun_a)*28, cy + math.sin(gun_a)*28), 5)
    pygame.draw.circle(surf, (50,50,50), (cx,cy), 8)

def _draw_eyeball(surf, cx, cy, angle, color, hp):
    # 큰 흰자
    pygame.draw.circle(surf, WHITE, (cx,cy), 22)
    # 홍채
    ir = 14 + math.sin(pygame.time.get_ticks()*0.003)*2
    pygame.draw.circle(surf, color, (cx,cy), int(ir))
    # 동공
    px = cx + math.cos(math.radians(angle*2))*5
    py = cy + math.sin(math.radians(angle*2))*5
    pygame.draw.circle(surf, BLACK, (int(px),int(py)), 7)
    # 혈관
    for i in range(4):
        a = math.radians(i*90 + angle*0.5)
        pygame.draw.line(surf, BLOOD_RED,
            (cx + math.cos(a)*10, cy + math.sin(a)*10),
            (cx + math.cos(a)*20, cy + math.sin(a)*20), 1)

def _draw_grenade(surf, cx, cy, angle, color, hp):
    # 타원 + 신관
    pygame.draw.ellipse(surf, color, (cx-12, cy-18, 24, 36))
    pygame.draw.ellipse(surf, WHITE, (cx-12, cy-18, 24, 36), 2)
    # 신관
    pygame.draw.line(surf, GOLD, (cx,cy-18),(cx+4,cy-26), 3)
    # 줄무늬
    pygame.draw.line(surf, DARK_RED, (cx-12,cy),(cx+12,cy), 2)
    # 깜빡이는 불꽃
    if (pygame.time.get_ticks()//200) % 2 == 0:
        pygame.draw.circle(surf, WHITE, (cx+4, cy-27), 3)

def _draw_ghost(surf, cx, cy, angle, color, hp):
    # 반투명 느낌 (밝기 변화)
    pulse = int(128 + math.sin(pygame.time.get_ticks()*0.004)*80)
    gc = (min(255, color[0]+pulse//4), min(255, color[1]), min(255, color[2]+pulse//2))
    # 몸통 – 물방울
    pts = [(cx,cy-22),(cx+18,cy+2),(cx+10,cy+20),(cx-10,cy+20),(cx-18,cy+2)]
    pygame.draw.polygon(surf, gc, pts)
    pygame.draw.polygon(surf, WHITE, pts, 1)
    # 눈 2개
    for ex_off in [-6, 6]:
        pygame.draw.circle(surf, WHITE, (cx+ex_off, cy-4), 5)
        pygame.draw.circle(surf, BLACK, (cx+ex_off, cy-4), 3)

def _draw_stealth(surf, cx, cy, angle, color, hp):
    # 매우 얇은 삼각형 + 글로우
    blink = int(60 + math.sin(pygame.time.get_ticks()*0.008)*40)
    gc = (blink, blink, blink+30)
    pts = [(cx, cy-22),(cx+20,cy+18),(cx-20,cy+18)]
    pygame.draw.polygon(surf, gc, pts)
    pygame.draw.polygon(surf, NEON_CYAN, pts, 1)
    pygame.draw.circle(surf, NEON_CYAN, (cx,cy), 4)

# ──────────────────────────────────────────────
# 게임 상태
player_pos    = [WIDTH//2 - 20, HEIGHT - 110]
player_hp     = 100.0
inv_timer     = 0     # 무적 프레임
bullets       = []    # [x, y, vx, vy]
enemies       = []    # [x, y, speed, type_id, angle, hp, max_hp]
enemy_bullets = []    # [x, y, vx, vy, color]
souls         = []
explosions    = []    # [x, y, radius, max_r, life]
score         = 0
start_time    = pygame.time.get_ticks()
last_drain    = pygame.time.get_ticks()
DRAIN_INTERVAL= 10000
game_over     = False
shoot_cooldown= 0
combo         = 0
combo_timer   = 0

def reset_game():
    global player_pos, player_hp, inv_timer, bullets, enemies, enemy_bullets
    global souls, explosions, particles, score, start_time, last_drain
    global game_over, shoot_cooldown, combo, combo_timer, shake_timer
    player_pos    = [WIDTH//2 - 20, HEIGHT - 110]
    player_hp     = 100.0
    inv_timer     = 0
    bullets       = []
    enemies       = []
    enemy_bullets = []
    souls         = []
    explosions    = []
    particles.clear()
    score         = 0
    start_time    = pygame.time.get_ticks()
    last_drain    = pygame.time.get_ticks()
    game_over     = False
    shoot_cooldown= 0
    combo         = 0
    combo_timer   = 0
    shake_timer   = 0

# ──────────────────────────────────────────────
# 시간에 따른 적 타입 가중치 테이블
def pick_enemy_type(elapsed_sec):
    weights = {0:40, 1:40}
    if elapsed_sec > 15: weights[4] = 15
    if elapsed_sec > 25: weights[6] = 15
    if elapsed_sec > 35: weights[2] = 20
    if elapsed_sec > 50: weights[5] = 20
    if elapsed_sec > 70: weights[3] = 10
    total = sum(weights.values())
    r = random.random() * total
    cum = 0
    for k, w in weights.items():
        cum += w
        if r < cum: return k
    return 1

def pick_enemy_hp(etype, elapsed_sec):
    _, base_hp, *_ = ENEMY_DEFS[etype]
    if base_hp >= 3:   # 탱크/보스 → 고정
        return base_hp
    # 일반 적도 시간 지날수록 더 맷집
    roll = random.random()
    if elapsed_sec > 60 and roll < 0.25:   return base_hp + 2
    elif elapsed_sec > 35 and roll < 0.40: return base_hp + 1
    return base_hp

# ──────────────────────────────────────────────
while True:
    current_time = pygame.time.get_ticks()
    elapsed_sec  = (current_time - start_time) // 1000
    if shake_timer > 0: shake_timer -= 1
    ox, oy = get_shake_offset()

    # ── 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        # ── 피 깎임
        if current_time - last_drain >= DRAIN_INTERVAL:
            player_hp -= 20; last_drain = current_time

        # ── 사격
        keys = pygame.key.get_pressed()
        if shoot_cooldown > 0: shoot_cooldown -= 1

        if keys[pygame.K_SPACE] and shoot_cooldown == 0 and player_hp > 2:
            player_hp -= 1.2
            shoot_cooldown = 8  # 연사 속도 고정
            bx, by = player_pos[0]+20, player_pos[1]
            if score < 500:
                bullets.append([bx, by, 0, -14])
            elif score < 1500:
                bullets.append([bx-12, by, -1, -13])
                bullets.append([bx+12, by,  1, -13])
            else:
                bullets.append([bx,    by,  0, -14])
                bullets.append([bx-14, by, -2, -13])
                bullets.append([bx+14, by,  2, -13])

        # ── 플레이어 이동
        p_speed = 7
        if keys[pygame.K_LEFT]  and player_pos[0] > 10:        player_pos[0] -= p_speed
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH-50:  player_pos[0] += p_speed
        if keys[pygame.K_UP]    and player_pos[1] > 10:        player_pos[1] -= p_speed
        if keys[pygame.K_DOWN]  and player_pos[1] < HEIGHT-60: player_pos[1] += p_speed

        if inv_timer > 0: inv_timer -= 1

        # ── 적 생성
        spawn_rate = 0.03 + elapsed_sec * 0.0008
        if random.random() < min(spawn_rate, 0.10):
            etype = pick_enemy_type(elapsed_sec)
            _, base_hp, shape, _, speed_range, _, _ = ENEMY_DEFS[etype]
            ehp   = pick_enemy_hp(etype, elapsed_sec)
            spd   = random.uniform(*speed_range)
            enemies.append([random.randint(40, WIDTH-40), -55,
                            spd, etype, 0, ehp, ehp])

        # ── 적 업데이트
        p_rect = pygame.Rect(player_pos[0]+4, player_pos[1]+4, 32, 36)
        for en in enemies[:]:
            en[1] += en[2]
            en[4] += 4

            etype = en[3]
            _, _, _, _, _, _, shoot_type = ENEMY_DEFS[etype]

            # 사격
            shoot_chance = 0.012 + elapsed_sec * 0.0003
            if shoot_type == 1 and random.random() < shoot_chance:
                ang = math.atan2(player_pos[1]-en[1], player_pos[0]-en[0])
                spd = 5.5
                col = BLOOD_RED if etype != 6 else NEON_CYAN
                enemy_bullets.append([en[0]+20, en[1]+20,
                                       math.cos(ang)*spd, math.sin(ang)*spd, col])

            elif shoot_type == 2 and random.random() < shoot_chance * 0.7:
                ang = math.atan2(player_pos[1]-en[1], player_pos[0]-en[0])
                for da in [-0.3, 0, 0.3]:
                    enemy_bullets.append([en[0]+20, en[1]+20,
                        math.cos(ang+da)*5, math.sin(ang+da)*5, GOLD])

            elif shoot_type == 3 and random.random() < 0.008:
                for i in range(8):
                    a = math.radians(i*45 + en[4])
                    enemy_bullets.append([en[0]+20, en[1]+20,
                        math.cos(a)*4, math.sin(a)*4, PINK])

            # 충돌 – 플레이어
            if inv_timer == 0 and pygame.Rect(en[0], en[1], 40, 40).colliderect(p_rect):
                player_hp -= 25; inv_timer = 60
                trigger_shake(8, 10)
                spawn_particles(player_pos[0]+20, player_pos[1]+20, BLOOD_RED, 16, 5)
                if player_hp <= 0:
                    game_over = True

            if en[1] > HEIGHT: enemies.remove(en)

        # ── 내 탄환
        for b in bullets[:]:
            b[0] += b[2]; b[1] += b[3]
            if b[1] < -10 or b[0] < 0 or b[0] > WIDTH:
                bullets.remove(b); continue
            hit = False
            for en in enemies[:]:
                if not hit and pygame.Rect(en[0]-4, en[1]-4, 48, 48).collidepoint(b[0], b[1]):
                    en[5] -= 1
                    hit = True
                    spawn_particles(b[0], b[1], WHITE, 6, 3)
                    # 피격 파티클 (적 색)
                    _, _, _, ecolor, *_ = ENEMY_DEFS[en[3]]
                    spawn_particles(b[0], b[1], ecolor, 5, 2)
                    if b in bullets: bullets.remove(b)
                    if en[5] <= 0:
                        _, _, _, ecolor, _, score_val, _ = ENEMY_DEFS[en[3]]
                        spawn_particles(en[0]+20, en[1]+20, ecolor, 20, 6)
                        trigger_shake(5, 6)
                        # 수류탄 폭발
                        if en[3] == 4:
                            explosions.append([en[0]+20, en[1]+20, 0, 70, 20])
                            trigger_shake(10, 14)
                        souls.append([en[0]+20, en[1]+20])
                        enemies.remove(en)
                        score += score_val
                        # 콤보
                        combo += 1; combo_timer = 90
            # 폭발 충돌
            for exp in explosions:
                dx = b[0]-exp[0]; dy = b[1]-exp[1]
                if (dx*dx+dy*dy)**0.5 < exp[2] and b in bullets:
                    bullets.remove(b); break

        # ── 적 탄환
        for eb in enemy_bullets[:]:
            eb[0] += eb[2]; eb[1] += eb[3]
            if not (0 < eb[0] < WIDTH and -10 < eb[1] < HEIGHT+10):
                enemy_bullets.remove(eb); continue
            if inv_timer == 0 and p_rect.collidepoint(eb[0], eb[1]):
                player_hp -= 12; inv_timer = 30
                trigger_shake(4, 6)
                spawn_particles(player_pos[0]+20, player_pos[1]+20, BLOOD_RED, 10, 4)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                if player_hp <= 0: game_over = True

        # ── 폭발 업데이트
        for exp in explosions[:]:
            exp[2] = min(exp[2] + 4, exp[3])
            exp[4] -= 1
            if exp[4] <= 0: explosions.remove(exp)
            # 범위 내 적 데미지
            for en in enemies[:]:
                dx = en[0]+20 - exp[0]; dy = en[1]+20 - exp[1]
                if (dx*dx+dy*dy)**0.5 < exp[2]:
                    en[5] -= 0.05  # 지속 데미지
                    if en[5] <= 0:
                        _, _, _, ecolor, _, sv, _ = ENEMY_DEFS[en[3]]
                        spawn_particles(en[0]+20,en[1]+20,ecolor,15,5)
                        enemies.remove(en)
                        score += sv

        # ── 영혼 흡수
        for s in souls[:]:
            dx = player_pos[0]+20-s[0]; dy = player_pos[1]+20-s[1]
            dist = (dx*dx+dy*dy)**0.5
            if dist < 22:
                player_hp = min(100, player_hp + 9)
                spawn_particles(int(s[0]), int(s[1]), NEON_CYAN, 8, 3)
                souls.remove(s)
            else:
                s[0] += dx * 0.15; s[1] += dy * 0.15

        # ── 콤보 타이머
        if combo_timer > 0: combo_timer -= 1
        else: combo = 0

        if player_hp <= 0: game_over = True

    # ─────────────────────────────────────────
    # 그리기
    screen.fill(BLACK)

    # 화면 흔들림 적용
    screen.blit(screen, (ox, oy))

    draw_stars()

    if not game_over:
        # 영혼
        for s in souls:
            pulse = int(150 + math.sin(pygame.time.get_ticks()*0.006)*80)
            pygame.draw.circle(screen, (pulse,255,pulse), (int(s[0]),int(s[1])), 5)
            pygame.draw.circle(screen, WHITE, (int(s[0]),int(s[1])), 2)

        # 탄환
        for b in bullets:
            pygame.draw.ellipse(screen, WHITE, (b[0]-3, b[1]-7, 6, 14))
            pygame.draw.ellipse(screen, NEON_CYAN, (b[0]-2, b[1]-5, 4, 10))

        # 적 탄환
        for eb in enemy_bullets:
            col = eb[4]
            pygame.draw.circle(screen, col, (int(eb[0]),int(eb[1])), 6)
            pygame.draw.circle(screen, WHITE, (int(eb[0]),int(eb[1])), 3)

        # 폭발
        for exp in explosions:
            alpha = exp[4] / 20.0
            r = int(exp[2])
            col = (int(255*alpha), int(160*alpha), 0)
            pygame.draw.circle(screen, col, (int(exp[0]),int(exp[1])), r, 3)
            pygame.draw.circle(screen, WHITE, (int(exp[0]),int(exp[1])), max(1,r//2), 2)

        # 적
        for en in enemies:
            draw_enemy(en)

        # 파티클
        update_draw_particles()

        # 플레이어
        draw_player(player_pos[0], player_pos[1], score, inv_timer)

        # ── UI
        # HP 바
        pygame.draw.rect(screen, (50,10,10), (20, 20, 200, 18))
        hp_ratio = max(0, player_hp / 100)
        hp_color = GREEN_NEON if hp_ratio > 0.5 else GOLD if hp_ratio > 0.25 else BLOOD_RED
        pygame.draw.rect(screen, hp_color, (20, 20, int(200*hp_ratio), 18))
        pygame.draw.rect(screen, WHITE, (20, 20, 200, 18), 1)
        draw_text("HP", 14, 56, 29, WHITE)

        # 드레인 바
        drain_ratio = (current_time - last_drain) / DRAIN_INTERVAL
        pygame.draw.rect(screen, (10,40,50), (20, 44, 200, 6))
        pygame.draw.rect(screen, NEON_CYAN, (20, 44, int(200*(1-drain_ratio)), 6))

        # 점수 / 시간
        draw_text(f"SCORE: {score}", 24, WIDTH-110, 30, GOLD)
        draw_text(f"TIME: {elapsed_sec}s", 20, WIDTH-110, 60, WHITE)

        # 콤보
        if combo >= 3:
            col = NEON_CYAN if combo < 7 else BLOOD_RED
            draw_text(f"COMBO ×{combo}!", 28, WIDTH//2, 60, col)

    else:
        update_draw_particles()
        draw_text("DEMON DEFEATED", 64, WIDTH//2 + ox, HEIGHT//2-60 + oy, BLOOD_RED)
        draw_text(f"SCORE : {score}", 34, WIDTH//2 + ox, HEIGHT//2+10 + oy, GOLD)
        draw_text(f"TIME  : {elapsed_sec}s", 26, WIDTH//2 + ox, HEIGHT//2+50 + oy, WHITE)
        draw_text("[ R ]  부활", 22, WIDTH//2 + ox, HEIGHT//2+100 + oy, DEEP_PURPLE)

    pygame.display.flip()
    clock.tick(60)