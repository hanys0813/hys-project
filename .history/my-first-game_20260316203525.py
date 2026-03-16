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

pygame.quit()