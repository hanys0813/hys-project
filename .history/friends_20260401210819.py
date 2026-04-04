import pygame
import random
import sys
import math

# --- 초기화 ---
pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "nanumgothic", "dotum", "apple ghtic", "arial"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

# --- 설정 및 색상 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
RED, GREEN, BLUE = (255, 50, 50), (50, 255, 80), (50, 150, 255)
YELLOW, GOLD, PURPLE, ORANGE = (255, 255, 0), (255, 215, 0), (160, 32, 240), (255, 140, 0)
SKY_BLUE, ICE_BLUE = (135, 206, 235), (200, 240, 255)
DAY_BG, NIGHT_BG = (45, 55, 75), (15, 10, 25)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("보스 처치 속성 각성 (밸런스 조정판)")
clock = pygame.time.Clock()
font_sm = get_korean_font(20)
font_md = get_korean_font(30)
font_lg = get_korean_font(60)

# --- 유틸리티 ---
def check_collision(pos, radius, rect):
    closest_x = max(rect.left, min(pos[0], rect.right))
    closest_y = max(rect.top, min(pos[1], rect.bottom))
    return ((pos[0] - closest_x)**2 + (pos[1] - closest_y)**2) < (radius**2)

class Enemy:
    def __init__(self, level, boss_killed):
        side = random.randint(0, 3)
        if side == 0: self.rect = pygame.Rect(random.randint(0, WIDTH), -40, 28, 28)
        elif side == 1: self.rect = pygame.Rect(random.randint(0, WIDTH), HEIGHT+40, 28, 28)
        elif side == 2: self.rect = pygame.Rect(-40, random.randint(0, HEIGHT), 28, 28)
        else: self.rect = pygame.Rect(WIDTH+40, random.randint(0, HEIGHT), 28, 28)
        
        self.type = random.choices(["basic", "ranger", "dasher"], weights=[75, 15, 10])[0]
        # 체력 증가량 소폭 하향
        self.hp = 30 + level * 15 + (boss_killed * 100) 
        self.speed = random.uniform(2.0, 3.0) + (boss_killed * 0.3)
        self.timer = 0
        self.slow_timer = 0 

    def update(self, p_pos, e_bullets):
        current_speed = self.speed * 0.4 if self.slow_timer > 0 else self.speed
        if self.slow_timer > 0: self.slow_timer -= 1

        dx, dy = p_pos[0] - self.rect.centerx, p_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        
        if self.type == "basic":
            self.rect.x += (dx / dist) * current_speed
            self.rect.y += (dy / dist) * current_speed
        elif self.type == "ranger":
            if dist > 250:
                self.rect.x += (dx / dist) * current_speed
                self.rect.y += (dy / dist) * current_speed
            elif dist < 150:
                self.rect.x -= (dx / dist) * current_speed
                self.rect.y -= (dy / dist) * current_speed
            self.timer += 1
            if self.timer > 100: # 발사 간격 소폭 증가 (너프)
                e_bullets.append({"pos": list(self.rect.center), "vel": [(dx/dist)*5, (dy/dist)*5]})
                self.timer = 0
        elif self.type == "dasher":
            self.timer += 1
            if self.timer < 60:
                self.rect.x += (dx / dist) * (current_speed * 0.6)
                self.rect.y += (dy / dist) * (current_speed * 0.6)
                self.dash_vec = [(dx/dist)*10, (dy/dist)*10]
            elif self.timer < 85:
                self.rect.x += self.dash_vec[0]
                self.rect.y += self.dash_vec[1]
            else: self.timer = 0

class Boss:
    def __init__(self, count):
        self.is_final = (count >= 3)
        size = 180 if self.is_final else 130
        self.rect = pygame.Rect(WIDTH//2 - size//2, -200, size, size)
        self.max_hp = 5000 * (4.0 ** count) if not self.is_final else 600000
        self.hp = self.max_hp
        self.entry = False
        self.timer, self.ang = 0, 0

    def update(self, p_pos, e_bullets):
        if not self.entry:
            self.rect.y += 3
            if self.rect.y >= 90: self.entry = True
            return
        self.rect.x += math.sin(pygame.time.get_ticks()*0.005) * 6
        self.timer += 1
        div = 6 if self.is_final else 12
        if self.timer % div == 0:
            count = 20 if self.is_final else 12
            for i in range(count):
                rad = math.radians(i * (360/count) + self.ang)
                e_bullets.append({"pos": list(self.rect.center), "vel": [math.cos(rad)*7, math.sin(rad)*7]})
            self.ang += 15

def draw_center(txt, y, font, color):
    s = font.render(txt, True, color)
    screen.blit(s, (WIDTH//2 - s.get_width()//2, y))

def main():
    while True:
        if not run_game(): break

def run_game():
    p_pos = [WIDTH//2, HEIGHT//2]
    p_radius, lives, level, exp, exp_next = 18, 3, 1, 0, 150
    dmg, atk_spd = 90, 1.0 # 기본 공격력 상향
    pierce_count = 1
    
    element = "None" 
    boss_killed, cycle_timer, invinc = 0, 0, 0
    is_night, victory = False, False
    
    is_rolling, roll_timer, roll_cd, roll_ghosts = False, 0, 0, []
    enemies, bullets, e_bullets, effects = [], [], [], []
    boss = None
    shoot_tick = 0

    def show_boss_reward():
        nonlocal dmg, atk_spd, pierce_count, element
        waiting = True
        while waiting:
            screen.fill(BLACK)
            pygame.draw.rect(screen, GOLD, (50, 50, WIDTH-100, HEIGHT-100), 5)
            draw_center("◈ 보스 처치: 속성 각성 ◈", 100, font_lg, GOLD)
            draw_center("스타일의 변화를 선택하세요", 190, font_sm, WHITE)
            
            draw_center("1. 화염의 숨결 [공격력 0.8배 / 광역 폭발]", 280, font_md, ORANGE)
            draw_center("2. 전술적 가속 [공격력 0.6배 / 연사력 +250% / 관통+1]", 340, font_md, YELLOW)
            draw_center("3. 절대 영도 [공격력 1.4배 / 적 둔화 / 무한 관통]", 400, font_md, ICE_BLUE)
            
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_1: 
                        element = "Fire"; dmg *= 0.8; waiting = False
                    if ev.key == pygame.K_2: 
                        element = "Lightning"; dmg *= 0.6; atk_spd += 2.5; pierce_count += 1; waiting = False
                    if ev.key == pygame.K_3: 
                        element = "Ice"; dmg *= 1.4; pierce_count = 99; waiting = False
                    if ev.key == pygame.K_q: pygame.quit(); sys.exit()

    running = True
    while running:
        clock.tick(FPS)
        cycle_timer += 1
        screen.fill(NIGHT_BG if is_night else DAY_BG)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); sys.exit()
                if e.key == pygame.K_r: return True

        # --- 낮/밤 전환 ---
        if cycle_timer > 1800:
            is_night = not is_night
            cycle_timer = 0
            if is_night: boss = Boss(boss_killed)
            else: boss = None; e_bullets.clear()

        # --- [스폰율 너프 핵심 로직] ---
        if not is_night:
            # 기본 확률 대폭 하향 (0.06 -> 0.04), 보스당 증가분 하향 (0.1 -> 0.06)
            spawn_chance = min(0.35, 0.04 + (boss_killed * 0.06))
            if random.random() < spawn_chance:
                # 무조건 여러 마리 나오던 것을 확률로 변경
                spawn_count = 1 + (boss_killed if random.random() > 0.4 else 0)
                for _ in range(int(spawn_count)):
                    enemies.append(Enemy(level, boss_killed))

        # --- 플레이어 이동 ---
        keys = pygame.key.get_pressed()
        move_dir = [keys[pygame.K_RIGHT]-keys[pygame.K_LEFT], keys[pygame.K_DOWN]-keys[pygame.K_UP]]
        if keys[pygame.K_LSHIFT] and not is_rolling and roll_cd <= 0 and any(move_dir):
            is_rolling, roll_timer, roll_cd, invinc = True, 15, 40, 15
            roll_dir = move_dir
        if is_rolling:
            p_pos[0] += roll_dir[0] * 12
            p_pos[1] += roll_dir[1] * 12
            roll_timer -= 1
            if cycle_timer % 2 == 0: roll_ghosts.append([list(p_pos), 20])
            if roll_timer <= 0: is_rolling = False
        else:
            p_pos[0] += move_dir[0] * 5.5
            p_pos[1] += move_dir[1] * 5.5
            if roll_cd > 0: roll_cd -= 1
        p_pos[0] = max(p_radius, min(WIDTH-p_radius, p_pos[0]))
        p_pos[1] = max(p_radius, min(HEIGHT-p_radius, p_pos[1]))

        # --- 전투 ---
        if shoot_tick > 0: shoot_tick -= 1
        if (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and shoot_tick <= 0:
            targets = enemies + ([boss] if boss else [])
            if targets:
                target = min(targets, key=lambda t: math.hypot(p_pos[0]-t.rect.centerx, p_pos[1]-t.rect.centery))
                dx, dy = target.rect.centerx-p_pos[0], target.rect.centery-p_pos[1]
                dist = math.hypot(dx, dy) or 1
                bullets.append({"pos": list(p_pos), "vel": [(dx/dist)*16, (dy/dist)*16], "p": pierce_count, "hit_list": []})
                shoot_tick = max(2, int(18 / atk_spd))

        for eff in effects[:]:
            eff['life'] -= 1
            if eff['life'] <= 0: effects.remove(eff)

        for b in bullets[:]:
            b["pos"][0] += b["vel"][0]; b["pos"][1] += b["vel"][1]
            if b["pos"][0] < -50 or b["pos"][0] > WIDTH+50 or b["pos"][1] < -50 or b["pos"][1] > HEIGHT+50:
                bullets.remove(b); continue
            
            for target in (enemies + ([boss] if boss else [])):
                if target.rect.collidepoint(b["pos"]) and target not in b["hit_list"]:
                    target.hp -= dmg
                    b["p"] -= 1
                    b["hit_list"].append(target)
                    
                    if element == "Fire":
                        effects.append({'pos': list(b["pos"]), 'radius': 75, 'life': 10, 'color': ORANGE})
                        for en in enemies:
                            if math.hypot(en.rect.centerx - b["pos"][0], en.rect.centery - b["pos"][1]) < 75:
                                en.hp -= dmg * 0.7
                    elif element == "Ice":
                        if hasattr(target, 'slow_timer'): target.slow_timer = 150
                    
                    if target.hp <= 0:
                        if target == boss:
                            boss_killed += 1
                            victory = boss.is_final
                            if victory: running = False
                            else:
                                # 보스 처치 시 화면 청소
                                boss, is_night, cycle_timer = None, False, 0
                                enemies.clear(); bullets.clear(); e_bullets.clear()
                                show_boss_reward()
                        else:
                            if target in enemies: enemies.remove(target); exp += (80 + boss_killed * 60)
                    
                    if b["p"] < 0: 
                        if b in bullets: bullets.remove(b)
                        break

        for en in enemies[:]:
            en.update(p_pos, e_bullets)
            if check_collision(p_pos, p_radius, en.rect) and invinc <= 0:
                lives -= 1; invinc = 60; enemies.remove(en)
        if boss:
            boss.update(p_pos, e_bullets)
            if check_collision(p_pos, p_radius, boss.rect) and invinc <= 0:
                lives -= 1; invinc = 70
        for eb in e_bullets[:]:
            eb["pos"][0] += eb["vel"][0]; eb["pos"][1] += eb["vel"][1]
            if math.hypot(p_pos[0]-eb["pos"][0], p_pos[1]-eb["pos"][1]) < p_radius + 6:
                if invinc <= 0: lives -= 1; invinc = 70
                e_bullets.remove(eb)

        if exp >= exp_next:
            level += 1; exp, exp_next = 0, int(exp_next * 1.4)
            screen.fill(BLACK)
            draw_center(f"--- LEVEL UP ({level}) ---", 150, font_lg, YELLOW)
            draw_center("1. 공격력 (+90)  2. 연사력 (+35%)  3. 체력 회복", 350, font_md, WHITE)
            pygame.display.flip()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_1: dmg += 90; waiting = False
                        if ev.key == pygame.K_2: atk_spd += 0.35; waiting = False
                        if ev.key == pygame.K_3: lives = min(5, lives+1); waiting = False
                        if ev.key == pygame.K_q: pygame.quit(); sys.exit()

        if invinc > 0: invinc -= 1
        if lives <= 0: running = False

        # --- 렌더링 ---
        for eff in effects:
            pygame.draw.circle(screen, eff['color'], (int(eff['pos'][0]), int(eff['pos'][1])), eff['radius'], 2)
        for g in roll_ghosts[:]:
            pygame.draw.circle(screen, (100, 150, 255), (int(g[0][0]), int(g[0][1])), p_radius, 1)
            g[1] -= 2
            if g[1] <= 0: roll_ghosts.remove(g)
        
        p_color = YELLOW if element == "Lightning" else (ORANGE if element == "Fire" else (ICE_BLUE if element == "Ice" else WHITE))
        if invinc % 10 < 5: pygame.draw.circle(screen, p_color, (int(p_pos[0]), int(p_pos[1])), p_radius)
        
        for en in enemies:
            ec = RED if en.type=="basic" else (GREEN if en.type=="ranger" else ORANGE)
            if en.slow_timer > 0: ec = ICE_BLUE
            pygame.draw.rect(screen, ec, en.rect)
        for b in bullets:
            pygame.draw.circle(screen, p_color, (int(b["pos"][0]), int(b["pos"][1])), 5)
        for eb in e_bullets: pygame.draw.circle(screen, RED, (int(eb["pos"][0]), int(eb["pos"][1])), 6)
        if boss:
            pygame.draw.rect(screen, PURPLE, boss.rect)
            pygame.draw.rect(screen, RED, (WIDTH//2-150, 20, (max(0, boss.hp)/boss.max_hp)*300, 15))

        # UI
        status = f"속성: {element} | 보스: {boss_killed}/3 | 레벨: {level}"
        screen.blit(font_sm.render(status, True, GOLD), (20, 20))
        screen.blit(font_sm.render(f"체력: " + "♥" * lives, True, RED), (20, 50))
        pygame.draw.rect(screen, GREEN, (0, HEIGHT-10, (exp/exp_next)*WIDTH, 10))
        pygame.display.flip()

    screen.fill(BLACK)
    draw_center("승리!" if victory else "패배", HEIGHT//2-50, font_lg, GOLD if victory else RED)
    draw_center("Q: 종료 | R: 재시작", HEIGHT//2 + 50, font_md, WHITE)
    pygame.display.flip()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q: pygame.quit(); sys.exit()
                if ev.key == pygame.K_r: return True

if __name__ == "__main__":
    main()