import led_matrix, random
from time import time
from keyboard import is_pressed

BRIGHTNESS = 128

def directional_move(coords, direction, toadd):
    match direction:
        case 'up':
            coords[1] -= toadd
        case 'down':
            coords[1] += toadd
        case 'left':
            coords[0] -= toadd
        case 'right':
            coords[0] += toadd

    return coords

def is_valid(input_queue, key):
    for opposites in [['left', 'right'], ['up', 'down']]:
        if input_queue[-1] in opposites and key in opposites:
            return False

    return True


random.seed(time())

gameboard = led_matrix.Matrix()

gameboard.default_brightness = BRIGHTNESS

apple = [random.randint(0, 8), random.randint(0, 33)]
snake = [[4, 16]]

input_queue = []
input_status = {
    'up': False,
    'down': False,
    'left': False,
    'right': False
}

gameboard.set_matrix(snake[0][0], snake[0][1])
gameboard.set_matrix(apple[0], apple[1])

gameboard.csend()

# Wait for player input
while input_queue == []:
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
    if snake[0][1] == -1:   snake[0][1] = 33
    elif snake[0][1] == 34: snake[0][1] = 0

    elif snake[0][0] == -1: snake[0][0] = 8
    elif snake[0][0] == 9:  snake[0][0] = 0

    # If the snake's head is in its body, end the game
    if snake[0] in snake[1:]:

        for i in reversed(range(0, BRIGHTNESS, 4)):
            gameboard.send(0x00, [i])

        gameboard.reset()
        gameboard.csend()
        gameboard.send(0x00, [BRIGHTNESS])
        quit()

    # Update the snake's body
    for i in range(1, len(snake)):
        snake[i], prev = prev, snake[i]

    # Draw
    gameboard.reset()

    gameboard.set_matrix(apple[0], apple[1])
    for position in snake:
        gameboard.set_matrix(position[0], position[1])

    gameboard.csend()

    # This is pretty scuffed, but unfortunately live input on linux in python seems to be even more scuffed
    # Basically, track if a key if pressed or not. If it's newly pressed, then check if the input is valid
    # If it is, add it to the input_queue.
    while time()-dtime < 0.1:

        for key in ["up", "down", "left", "right"]:
            if is_pressed(key) != input_status[key]:

                input_status[key] = not input_status[key]

                if is_valid(input_queue, key) and input_status[key]:
                    input_queue.append(key)

    if len(input_queue) > 1:
        input_queue.pop(0)
