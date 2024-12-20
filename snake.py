import led_matrix, time, random
from keyboard import is_pressed

BRIGHTNESS = 128

def non_opposite(direction, key):
    for opposites in [['left', 'right'], ['up', 'down']]:
        if direction in opposites and key in opposites:
            return False

    return True

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

random.seed(time.time())

gameboard = led_matrix.Matrix()
gameboard.send_brightness(BRIGHTNESS)

apple = [random.randint(0, 8), random.randint(0, 33)]
snake = [[4, 16]]
direction = ''
input_queue = []

# Pregame waiting for direction
gameboard.set_matrix(snake[0][0], snake[0][1])
gameboard.set_matrix(apple[0], apple[1])
gameboard.send_matrix()

while direction == '':
    for key in ["up", "down", "left", "right"]:
        if is_pressed(key):
            direction = key


while True:

    dtime = time.time()
    prev = snake[0].copy()


    # If snake on apple, extend snake and move apple
    if snake[0] == apple:

        snake.append(directional_move(snake[-1].copy(), direction, -1))

        while apple in snake:
            apple = [random.randint(0, 8), random.randint(0, 33)]

    # Move snake head in whichever direction
    snake[0] = directional_move(snake[0], direction, 1)

    # Move snake to other side of board if at edge
    if snake[0][1] == -1:   snake[0][1] = 33
    elif snake[0][1] == 34: snake[0][1] = 0

    elif snake[0][0] == -1: snake[0][0] = 8
    elif snake[0][0] == 9:  snake[0][0] = 0

    # If the snake's head is in its body, end the game
    if snake[0] in snake[1:]:

        for i in reversed(range(0, BRIGHTNESS, 4)):
            gameboard.send_brightness(i)

        gameboard.reset()
        gameboard.send_matrix()
        gameboard.send_brightness(128)
        quit()


    # Update the snake's body
    for i in range(1, len(snake)):
        snake[i], prev = prev, snake[i]


    # Draw
    gameboard.reset()
    gameboard.set_matrix(apple[0], apple[1])

    for position in snake:
        gameboard.set_matrix(position[0], position[1])
    gameboard.send_matrix()

    # This is a bit scuffed, but python input on linux is hell and this works so screw you
    while time.time()-dtime < 0.1:
        for key in ["up", "down", "left", "right"]:
            if is_pressed(key) and key != direction and key not in input_queue and non_opposite(direction, key):
                input_queue.append(key)

    if input_queue:
        direction = input_queue[0]
        input_queue.pop(0)
