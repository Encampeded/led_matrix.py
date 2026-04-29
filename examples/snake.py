from led_matrix import Matrix, Point
from keyboard import is_pressed, read_key
from random import randint
from time import perf_counter
from collections import deque

BRIGHTNESS = 64

def directional_move(coords: Point, direction: str, offset: int) -> Point:
    moved_coords = list(coords)

    match direction:
        case 'up':
            moved_coords[1] -= offset
        case 'down':
            moved_coords[1] += offset
        case 'left':
            moved_coords[0] -= offset
        case 'right':
            moved_coords[0] += offset

    # Move snake to other side of board if at edge
    # y-coords
    if moved_coords[1] == -1:   moved_coords[1] = 33
    elif moved_coords[1] == 34: moved_coords[1] = 0

    # x-coords
    elif moved_coords[0] == -1: moved_coords[0] = 8
    elif moved_coords[0] == 9:  moved_coords[0] = 0

    return Point(moved_coords[0], moved_coords[1])

# Checks if a keypress is valid compared to previous direction (not an opposite direction)
def is_valid(direction, key_pressed: str) -> bool:
    for opposites in [['left', 'right'], ['up', 'down']]:
        if direction in opposites and key_pressed in opposites:
            return False

    return True

gameboard: Matrix = Matrix(BRIGHTNESS)

apple: Point = Point(randint(0, 8), randint(0, 33))
snake: deque[Point] = deque()
snake.append(Point(4, 16))

input_queue: deque[str] = deque()
input_status: dict[str, bool] = {
    key: False for key in ["up", "down", "left", "right"]
}

gameboard.set_point(snake[0])
gameboard.set_point(apple)

gameboard.qsend()

# Wait for player input
while not input_queue:
    key = read_key()
    if key not in input_status.keys():
        continue
    input_queue.append(key)

while True:
    dtime = perf_counter()

    # If snake on apple, extend snake and move apple
    if snake[0] == apple:

        snake.append(directional_move(snake[-1], input_queue[0], -1))

        while apple in snake:
            apple = Point(randint(0, 8), randint(0, 33))

    # Move snake in whichever direction
    snake.appendleft(directional_move(snake[0], input_queue[0], 1))
    snake.pop()

    # If the snake's head is in its body, end the game
    if snake.count(snake[0]) > 1:

        for i in reversed(range(0, BRIGHTNESS, 4)):
            gameboard.qsend(i)

        gameboard.reset()
        gameboard.qsend()
        break

    # Draw
    gameboard.reset()

    gameboard.set_point(apple)
    gameboard.set_points(snake)

    gameboard.qsend()

    # This is sucks, but live input on wayland in python seems to just suck
    # Basically, track if a key is pressed or not. If it's newly pressed, then
    # check if the input is valid (not opposite). If it is, add it to the input_queue.
    while perf_counter()-dtime < 0.1:

        for key in ["up", "down", "left", "right"]:
            if is_pressed(key) != input_status[key]:

                input_status[key] = not input_status[key]

                if input_status[key] and is_valid(input_queue[-1], key):
                    input_queue.append(key)

    if len(input_queue) > 1:
        input_queue.popleft()
