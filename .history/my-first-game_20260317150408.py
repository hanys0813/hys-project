import pygame
import sys

# 1. 초기화
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame")

# 색상 정의
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
clock = pygame.time.Clock()

running = True

# 2. 메인 루프 (여기서부터 들여쓰기가 중요함!)
while running:
    # 이 아래 모든 줄은 Tab 키를 한 번씩 눌러서 밀어넣어야 합니다.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 화면을 흰색으로 채우기
    screen.fill(WHITE)
    
    # 파란색 원 그리기 (중심 400, 300 / 반지름 50)
    pygame.draw.circle(screen, BLUE, (400, 300), 50)
    
    # 화면 업데이트
    pygame.display.flip()
    
    # 프레임 제한 (초당 60프레임)
    clock.tick(60)

# 3. 종료 처리
pygame.quit()
sys.exit()