import led_matrix
import random
import sys
from time import time
from keyboard import is_pressed

BRIGHTNESS = 128

def directional_move(coords: list[int], direction: str, offset: int) -> list[int]:

    match direction:
        case 'up':
            coords[1] -= offset
        case 'down':
            coords[1] += offset
        case 'left':
            coords[0] -= offset
        case 'right':
            coords[0] += offset

    return coords

# Checks if a keypress is valid compared to previous direction (not opposite)
def is_valid(direction, key_pressed: str) -> bool:
    for opposites in [['left', 'right'], ['up', 'down']]:
        if direction in opposites and key_pressed in opposites:
            return False

    return True


random.seed(time())

gameboard: led_matrix.Matrix = led_matrix.Matrix(BRIGHTNESS)

apple: list[int] = [random.randint(0, 8), random.randint(0, 33)]
snake: list[list[int]] = [[4, 16]]

input_queue: list[str] = []
input_status: dict[str, bool] = {
    'up': False,
    'down': False,
    'left': False,
    'right': False
}

gameboard.set_matrix(snake[0][0], snake[0][1])
gameboard.set_matrix(apple[0], apple[1])

gameboard.qsend()

# Wait for player input
while not input_queue:
    for key in ["up", "down", "left", "right"]:
        if is_pressed(key):
            input_queue.append(key)

while True:

    dtime = time()
    prev = snake[0].copy()

    # If snake on apple, extend snake and move apple
    if snake[0] == apple:

        snake.append(directional_move(snake[-1].copy(), input_queue[0], -1))

        while apple in snake:
            apple = [random.randint(0, 8), random.randint(0, 33)]

    # Move snake head in whichever direction
    snake[0] = directional_move(snake[0], input_queue[0], 1)

    # Move snake to other side of board if at edge
    # y-coords
    if snake[0][1] == -1:   snake[0][1] = 33
    elif snake[0][1] == 34: snake[0][1] = 0

    # x-coords
    elif snake[0][0] == -1: snake[0][0] = 8
    elif snake[0][0] == 9:  snake[0][0] = 0

    # If the snake's head is in its body, end the game
    if snake[0] in snake[1:]:

        for i in reversed(range(0, BRIGHTNESS, 4)):
            gameboard.qsend(i)

        gameboard.reset()
        gameboard.qsend()
        sys.exit(0)

    # Update the snake's body
    for i in range(1, len(snake)):
        snake[i], prev = prev, snake[i]

    # Draw
    gameboard.reset()

    gameboard.set_matrix(apple[0], apple[1])
    for position in snake:
        gameboard.set_matrix(position[0], position[1])

    gameboard.qsend()

    # This is sucks, but live input on wayland in python seems to just suck
    # Basically, track if a key if pressed or not. If it's newly pressed, then
    # check if the input is valid (not opposite). If it is, add it to the input_queue.
    while time()-dtime < 0.1:

        for key in ["up", "down", "left", "right"]:
            if is_pressed(key) != input_status[key]:

                input_status[key] = not input_status[key]

                if is_valid(input_queue[-1], key) and input_status[key]:
                    input_queue.append(key)

    if len(input_queue) > 1:
        input_queue.pop(0)
