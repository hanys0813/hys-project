


1. 게임 루프 (Game Loop)
게임의 생존 주기(입력 → 업데이트 → 그리기)를 반복하는 while 문은 main() 함수 안에 위치합니다.

Python
def main():
    # ... 초기 설정 생략 ...
    while True:  # <--- 여기가 메인 게임 루프입니다.
        clock.tick(speed)  # 초당 프레임(FPS)을 제어하여 게임 속도를 유지합니다.
        
        # 1. 이벤트 처리 (입력)
        # 2. 게임 상태 업데이트 (이동, 충돌)
        # 3. 화면 그리기 (렌더링)
이 루프가 한 번 돌 때마다 뱀이 한 칸씩 움직인다고 보시면 됩니다.

2. 플레이어 이동 (Key Input)
키보드 입력 처리는 게임 루프 상단의 이벤트 리스너 부분에서 수행합니다.

Python
for e in pygame.event.get():
    if e.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if e.type == pygame.KEYDOWN:  # 키가 눌렸을 때
        # 현재 방향과 정반대 방향이 아닐 때만 방향 변수를 변경합니다.
        if e.key == pygame.K_UP and direction != (0, CELL):
            direction = (0, -CELL)
        if e.key == pygame.K_DOWN and direction != (0, -CELL):
            direction = (0, CELL)
        # ... 좌우 방향 처리 생략 ...
여기서 결정된 direction 좌표값은 루프 아래쪽에서 뱀의 머리(head) 좌표를 계산할 때 더해집니다.

3. 충돌 감지 (Collision Detection)
이 코드에서는 Pygame의 colliderect() 함수 대신, 좌표 비교(Coordinate Comparison) 방식을 사용하고 있습니다. 뱀과 음식이 모두 CELL(20픽셀) 단위로 딱딱 맞춰 움직이기 때문에 좌표가 일치하는지만 확인하면 됩니다.

① 벽 및 자기 몸과의 충돌 (게임 오버 조건)
Python
# 뱀의 새로운 머리 위치 계산
head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

if (
    head[0] < 0 or head[0] >= WIDTH or   # 좌우 벽 충돌
    head[1] < 0 or head[1] >= HEIGHT or  # 상하 벽 충돌
    head in snake                        # 머리 좌표가 몸통 리스트(snake) 안에 있는지 (자기 몸 충돌)
):
    if game_over_screen(score):
        main()
② 음식과의 충돌 (점수 획득 조건)
Python
if head == food:  # 머리 좌표와 음식 좌표가 정확히 일치하면
    score += 10
    food = new_food(snake)
    # ... (길이 증가 로직: snake.pop()을 실행하지 않음)
요약하자면:
루프: main() 함수 내의 while True:

이동: pygame.event.get() 내부의 if e.type == pygame.KEYDOWN:

충돌: if head[0] < 0... (벽/몸 충돌) 및 if head == food: (음식 충돌)

이렇게 세 부분만 정확히 이해하셔도 전체 코드의 흐름을 다 파악하신 겁니다! 추가로 궁금한 점이 있으신가요?