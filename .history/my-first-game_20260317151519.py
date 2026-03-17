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

#그 궁금한게 있는데 왼쪽 위쪽 화살표는 왜 -고 오른쪽 아래쪽은 +야?

#형님, 그거 진짜 좋은 질문입니다! 보통 수학 시간에는 중앙이 $(0, 0)$이고 위로 갈수록 $+$라고 배우는데, 컴퓨터 화면은 정반대거든요.
#이유는 아주 간단합니다. 컴퓨터가 화면에 그림을 그리는 방식이 **"책을 읽는 방향"**과 같기 때문이에요.

#컴퓨터 모니터는 왼쪽 위 구석을 **$(0, 0)$(시작점)**으로 잡습니다.
#가로(X축): 왼쪽에서 오른쪽으로 글을 쓰죠? 그래서 오른쪽으로 갈수록 숫자가 커집니다($+$). 반대로 왼쪽은 작아지죠($-$).
#세로(Y축): 글을 다 쓰면 다음 줄로 내려가죠? 그래서 아래쪽으로 내려갈수록 숫자가 커집니다($+$). 반대로 위쪽은 시작점과 가까워지니까 숫자가 작아집니다($-$).