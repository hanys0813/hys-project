import pygame
import random
import math

# 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Neon Particle Sandbox")
clock = pygame.time.Clock()

# 입자 리스트
particles = []

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        
        # 물리 엔진: 초기 속도와 각도
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # 속성
        self.max_life = random.randint(30, 60)
        self.life = self.max_life
        self.initial_size = random.uniform(4, 10)
        self.size = self.initial_size
        
        # 색상 (네온 느낌)
        if color:
            self.color = list(color)
        else:
            self.color = [random.randint(100, 255), random.randint(50, 255), 255]

    def update(self):
        # 이동 및 중력/마찰
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 중력 효과
        self.vx *= 0.98 # 공기 저항
        self.vy *= 0.98
        
        self.life -= 1
        
        # 수명에 따른 크기 축소 (지리는 포인트 1)
        self.size = max(0, (self.life / self.max_life) * self.initial_size)

    def draw(self, surface):
        if self.life > 0:
            # 블룸 효과를 위한 레이어 (지리는 포인트 2)
            # 입자 본체
            alpha = int((self.life / self.max_life) * 255)
            
            # 부드러운 원 그리기 (그라데이션 효과 대신 간단한 다중 원)
            s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha // 4), (self.size * 2, self.size * 2), self.size * 2)
            pygame.draw.circle(s, (*self.color, alpha), (self.size * 2, self.size * 2), self.size)
            surface.blit(s, (int(self.x - self.size * 2), int(self.y - self.size * 2)), special_flags=pygame.BLEND_RGBA_ADD)

def draw_background(surface, time):
    # 역동적인 배경 그라데이션 (지리는 포인트 3)
    for i in range(0, HEIGHT, 4):
        wave = math.sin(i * 0.005 + time) * 20
        c = int(20 + 15 * math.sin(i * 0.01 + time))
        pygame.draw.line(surface, (5, c // 2, c), (0, i), (WIDTH, i), 4)

running = True
time_val = 0

while running:
    # 배경을 검은색으로 밀지 않고 살짝 투명하게 덮으면 잔상 효과(Motion Blur)가 생깁니다.
    # 하지만 여기서는 깔끔한 가산 혼합을 위해 배경을 새로 그립니다.
    draw_background(screen, time_val)
    time_val += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 마우스 입력 처리
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]: # 왼쪽 클릭: 폭발적인 네온 입자
        for _ in range(10):
            particles.append(Particle(*mouse_pos))
            
    if mouse_buttons[2]: # 오른쪽 클릭: 무지개 입자
        hue = (pygame.time.get_ticks() // 5) % 360
        color = pygame.Color(0)
        color.hsva = (hue, 80, 100, 100)
        for _ in range(5):
            particles.append(Particle(*mouse_pos, color=(color.r, color.g, color.b)))

    # 입자 업데이트 및 그리기
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)
        else:
            p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()