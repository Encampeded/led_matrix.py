"""
Snake Game Implementation Using an LED Matrix.

This program implements a simple Snake game using an LED matrix. It controls
the snake's movement, handles user inputs via keyboard, detects collisions, and
updates the display using the led_matrix module.

Features:

- Control the snake using arrow keys.
- Apples spawn randomly on the matrix.
- Snake grows when it eats an apple.
- The game ends if the snake collides with itself.
- The snake wraps around the edges of the matrix.
"""
import sys  # To quit
import random
from time import time
from keyboard import is_pressed
import led_matrix

BRIGHTNESS = 128


def directional_move(coords: list[list[int]], direction: str,
                     offset: int) -> list[list[int]]:
    """
    This function changes the coordinates based on the direction and offset
    provided.

    Args:
        coords (list[list[int]]): The coordinates of the snake.
        direction (str): The direction to move in.
        offset (int): The amount to move in said direction.

    Returns:
        (list[list[int]]): The updated coordinates of the snake.
    """
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


def is_valid(current_input_queue: list[str], key_pressed: str) -> bool:
    """
    Check if the pressed key is a valid movement based on the last input in the
    queue. The function ensures that the new key does not form an invalid
    opposite movement (e.g., left followed by right or up followed by down).

    Args:
        current_input_queue (list): A list representing the current movement
                                    inputs.
        key (str): The new movement input to validate.

    Returns:
        bool: True if the key is a valid movement, False otherwise.
    """
    for opposites in [['left', 'right'], ['up', 'down']]:
        if current_input_queue[-1] in opposites and key_pressed in opposites:
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
    if snake[0][1] == -1:  # y-coords
        snake[0][1] = 33
    elif snake[0][1] == 34:
        snake[0][1] = 0

    elif snake[0][0] == -1:  # x-coords
        snake[0][0] = 8
    elif snake[0][0] == 9:
        snake[0][0] = 0

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

    # This is pretty scuffed, but unfortunately live input on linux in python
    # seems to be even more scuffed.
    # Basically, track if a key if pressed or not. If it's newly pressed, then
    # check if the input is valid.
    # If it is, add it to the input_queue.
    while time()-dtime < 0.1:

        for key in ["up", "down", "left", "right"]:
            if is_pressed(key) != input_status[key]:

                input_status[key] = not input_status[key]

                if is_valid(input_queue, key) and input_status[key]:
                    input_queue.append(key)

    if len(input_queue) > 1:
        input_queue.pop(0)
