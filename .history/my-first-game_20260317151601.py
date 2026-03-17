import pygame
import sys

# 1. 초기화
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame - Controller")

# 색상 및 속성 정의
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
clock = pygame.time.Clock()

# --- [변수 추가] 원의 시작 위치 ---
circle_x = 400
circle_y = 300
speed = 5  # 한 번에 움직일 거리 (5픽셀)

running = True

# 2. 메인 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- [핵심: 키 입력 확인] ---
    # 현재 눌려 있는 모든 키의 상태를 가져옵니다.
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:   # 왼쪽 화살표
        circle_x -= speed
    if keys[pygame.K_RIGHT]:  # 오른쪽 화살표
        circle_x += speed
    if keys[pygame.K_UP]:     # 위쪽 화살표
        circle_y -= speed
    if keys[pygame.K_DOWN]:   # 아래쪽 화살표
        circle_y += speed

    # 화면 지우기
    screen.fill(WHITE)
    
    # --- [그리기] 고정된 (400, 300) 대신 변수 circle_x, circle_y 사용 ---
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), 50)
    
    # 화면 업데이트
    pygame.display.flip()
    
    # 프레임 제한
    clock.tick(60)

# 3. 종료 처리
pygame.quit()
sys.exit()

