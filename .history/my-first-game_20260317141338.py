import pygame
import random
import math

# 초기화
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Unkillable Demon King Aura")
clock = pygame.time.Clock()

particles = []

class DemonAura:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # 위로 솟구치는 속도 (불사대마왕의 기운)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3, -7)
        
        self.max_life = random.randint(40, 70)
        self.life = self.max_life
        self.initial_size = random.uniform(6, 12)
        
        # 흔들림 효과를 위한 변수
        self.offset = random.uniform(0, 100)
        
        # 색상: 검정 ~ 진홍색 ~ 밝은 빨강 (악마적인 느낌)
        if random.random() > 0.3:
            self.color = [random.randint(150, 255), 0, random.randint(0, 50)] # 진홍색
        else:
            self.color = [30, 0, 0] # 심연의 검붉은색

    def update(self):
        # 사인파를 이용한 좌우 흔들림 (지리는 포인트: 기괴한 움직임)
        self.x += self.vx + math.sin(self.life * 0.1 + self.offset) * 2
        self.y += self.vy
        
        # 서서히 느려짐
        self.vy *= 0.97
        
        self.life -= 1
        self.size = (self.life / self.max_life) * self.initial_size

    def draw(self, surface):
        if self.life > 0:
            # 불꽃의 열기 표현을 위한 알파값
            alpha = int((self.life / self.max_life) * 255)
            
            # 메인 오라 (가산 혼합으로 중첩 시 밝아짐)
            glow_size = int(self.size * 3)
            s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # 외곽 번짐 (Darker)
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha // 3), 
                               (glow_size, glow_size), glow_size)
            # 중심부 (Brighter)
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), 
                               (glow_size, glow_size), int(self.size))
            
            surface.blit(s, (int(self.x - glow_size), int(self.y - glow_size)), 
                         special_flags=pygame.BLEND_RGBA_ADD)

def draw_abyss_bg(surface, time):
    # 심연의 배경 (어둡고 무거운 보라/검정 그라데이션)
    for i in range(HEIGHT):
        # 아래쪽이 더 어두운 느낌
        darkness = math.sin(i * 0.002 + time) * 10
        color = (15 + darkness, 0, 20 + darkness)
        pygame.draw.line(surface, color, (0, i), (WIDTH, i))

running = True
time_val = 0

while running:
    # 1. 배경 (잔상을 위해 아주 약간의 투명도를 가진 검은색 덧칠 가능하지만, 여기선 깔끔하게)
    draw_abyss_bg(screen, time_val)
    time_val += 0.02

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. 마우스 위치에서 오라 발생
    m_pos = pygame.mouse.get_pos()
    
    # 가만히 있어도 뿜어져 나오는 기운
    for _ in range(3):
        particles.append(DemonAura(*m_pos))
        
    # 클릭 시 대폭발 (강력한 스킬 사용 느낌)
    if pygame.mouse.get_pressed()[0]:
        for _ in range(15):
            p = DemonAura(*m_pos)
            p.vy *= 2 # 더 빠르게 상승
            particles.append(p)

    # 3. 업데이트 및 그리기
    for p in particles[:]:
        p.update()
        if p.life <= 0 or p.size < 1:
            particles.remove(p)
        else:
            p.draw(screen)

    pygame.display.flip()
    clock.tick(60)
import pygame
import random
import math

# --- 초기 설정 ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# 잔상 효과를 위한 서피스
display_surface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("THE UNKILLABLE DEMON KING - AWAKENED")
clock = pygame.time.Clock()

particles = []
shocks = []
shake_intensity = 0

class Shockwave:
    """공간 왜곡 파동 효과"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 0
        self.max_radius = random.randint(150, 300)
        self.alpha = 255
        self.width = 5

    def update(self):
        self.radius += 10
        self.alpha -= 5
        self.width = max(1, self.width - 0.1)
        return self.alpha > 0

    def draw(self, surface):
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # 진한 진홍색 링
        color = (130, 0, 30, self.alpha)
        pygame.draw.circle(s, color, (self.radius, self.radius), self.radius, int(self.width))
        surface.blit(s, (self.x - self.radius, self.y - self.radius))

class DemonAura:
    def __init__(self, x, y, is_burst=False):
        self.x, self.y = x, y
        # 폭발 시 더 넓게 퍼짐
        speed_mult = 2.5 if is_burst else 1.0
        self.vx = random.uniform(-2, 2) * speed_mult
        self.vy = random.uniform(-4, -10) * speed_mult
        
        self.max_life = random.randint(30, 60)
        self.life = self.max_life
        self.initial_size = random.uniform(8, 18) if is_burst else random.uniform(4, 10)
        
        # 기괴한 움직임을 위한 파라미터
        self.angle = random.uniform(0, math.pi * 2)
        self.spin = random.uniform(-0.2, 0.2)
        
        # 색상: 심연의 보라와 지옥의 빨강 조화
        if random.random() > 0.4:
            self.color = [random.randint(200, 255), 0, random.randint(50, 100)] # Crimson
        else:
            self.color = [random.randint(50, 80), 0, random.randint(120, 200)] # Deep Void Purple

    def update(self):
        # 소용돌이 치는 움직임 추가
        self.angle += self.spin
        self.x += self.vx + math.sin(self.angle) * 3
        self.y += self.vy
        
        self.vy *= 0.96 # 중력 저항 느낌
        self.life -= 1
        self.size = (self.life / self.max_life) * self.initial_size

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            # 입자 본체보다 큰 글로우 효과
            glow_size = int(self.size * 4)
            s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # 레이어드 드로잉 (가장자리-중심-핵)
            # 1. 아우라 외곽
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha // 4), 
                               (glow_size, glow_size), glow_size)
            # 2. 메인 기운
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), 
                               (glow_size, glow_size), int(self.size))
            # 3. 중심부 핵 (흰색에 가까운 붉은색)
            pygame.draw.circle(s, (255, 100, 100, alpha), 
                               (glow_size, glow_size), int(self.size // 2))
            
            surface.blit(s, (int(self.x - glow_size), int(self.y - glow_size)), 
                         special_flags=pygame.BLEND_RGBA_ADD)

def draw_background(surface, time):
    # 배경도 그냥 검정이 아니라 어두운 심연의 흐름을 표현
    for i in range(0, HEIGHT, 10):
        val = math.sin(i * 0.005 + time) * 15
        color = (20 + val, 5, 25 + val)
        pygame.draw.rect(surface, color, (0, i, WIDTH, 10))

# --- 메인 루프 ---
running = True
time_val = 0

while running:
    # 1. 잔상 처리를 위한 배경 드로잉 (매 프레임 0.1 정도의 불투명도로 덮음)
    # 완전 검정이 아닌 아주 어두운 보라색으로 잔상 유지
    display_surface.fill((5, 0, 10))
    draw_background(display_surface, time_val)
    time_val += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    m_pos = pygame.mouse.get_pos()
    m_pressed = pygame.mouse.get_pressed()

    # 2. 기운 생성 (상시)
    for _ in range(2):
        particles.append(DemonAura(m_pos[0], m_pos[1]))

    # 3. 클릭 시 폭발적인 연출
    if m_pressed[0]:
        shake_intensity = 15 # 화면 흔들림 발생
        shocks.append(Shockwave(*m_pos))
        for _ in range(10):
            particles.append(DemonAura(m_pos[0], m_pos[1], is_burst=True))

    # 4. 업데이트 및 그리기 (파동)
    for s in shocks[:]:
        if not s.update():
            shocks.remove(s)
        else:
            s.draw(display_surface)

    # 5. 업데이트 및 그리기 (아우라 입자)
    for p in particles[:]:
        p.update()
        if p.life <= 0 or p.size < 0.5:
            particles.remove(p)
        else:
            p.draw(display_surface)

    # 6. 스크린 쉐이크 적용
    render_offset = [0, 0]
    if shake_intensity > 0:
        render_offset = [random.randint(-shake_intensity, shake_intensity), 
                         random.randint(-shake_intensity, shake_intensity)]
        shake_intensity -= 1

    # 최종 서피스를 메인 화면에 복사
    screen.blit(display_surface, (render_offset[0], render_offset[1]))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
pygame.quit()