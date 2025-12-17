import led_matrix
from keyboard import is_pressed
from random import shuffle
from time import perf_counter

# ---------------- README ---------------- #
#
#                 Controls
# Left/Right: Move left/right
# Down: Soft Drop
# Up: Rotate Clockwise
# Z: Rotate Counter-Clockwise
# X: Hard Drop
#
# You can change the brightness with the
# BRIGHTNESS variable below. 0-255
#
# If you're on Linux, you'll need to run
# python as sudo so it can get input.
#
# Also, fair warning, the code is somewhat
# messy. Sorry (but idc lol it works)
#
# ---------------------------------------- #

BRIGHTNESS = 64

TETROMINOS = [
    [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [1, 1],
        [1, 1]
    ],
    [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ],
    [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ]
]

def next_tetromino():

    global tetromino_queue

    if not tetromino_queue:
        tetromino_queue = list(range(len(TETROMINOS)))
        shuffle(tetromino_queue)

    return TETROMINOS[tetromino_queue.pop()]


def collides(tetromino: list[list[int]], position: list[int]) -> bool:
    """Checks if a tetromino in a given position collides with anything"""
    for y in range(len(tetromino)):
        for x in range(len(tetromino[y])):

            if not tetromino[y][x]:
                continue

            coords = [position[0]+x, position[1]+y]

            if not (0 <= coords[0] <= 8 and coords[1] <= 33) or \
                junk[coords[1]][coords[0]]:

                return True

    return False

game = led_matrix.Matrix(BRIGHTNESS)
game.qsend()

input_status: dict[str, bool] = {
    key: False for key in ["up", "down", "left", "right", 'z', 'x']
}

score = 0
level = 1

tpos = [3, 0]
tetromino_queue = []
tetromino = next_tetromino()
junk = [[0 for i in range(9)] for i in range(34)]

dtime = 0

while True:

    # ---------------- UPDATE ---------------- #

    draw = False

    # If time has passed, move tetromino down and check for collisions
    if (perf_counter()-dtime) > (1 / ((0.5*level) + 1)):
        dtime = perf_counter()
        draw = True
        tpos[1] += 1

        if collides(tetromino, tpos):

            # Add current tetromino to junk
            for y, _ in enumerate(tetromino):
                for x, _ in enumerate(tetromino[y]):

                    if tetromino[y][x]:
                        junk[tpos[1]-1 + y][tpos[0] + x] = 1

            # Check for new rows
            cleared_rows = [ i for i, row in enumerate(junk) if set(row) == {1} ]

            if cleared_rows:
                score += pow(2, len(cleared_rows)-1)*100
                level = int(score/1000)+1
                print(int(score/1000)+1)

                # Flash cleared rows
                for _ in range(12):
                    for y in cleared_rows:
                        game.draw_line([0, y], [8, y], brightness = not game.get_matrix(0, y))
                    game.qsend()

                for i in reversed(cleared_rows):
                    junk.pop(i)
                for _ in cleared_rows:
                    junk.insert(0, [0 for i in range(9)])

            # Generate new tetromino
            tpos = [3, 0]
            tetromino = next_tetromino()

            # If newly generated tetromino collides, do game over animation and quit
            if collides(tetromino, tpos):
                for y in range(34):
                    game.draw_line([0, y], [8, y], brightness = 0)
                    game.qsend()
                break


    # Handles input/tetromino movement
    for key in input_status.keys():

        if is_pressed(key) == input_status[key]:
            continue

        input_status[key] = not input_status[key]

        if not input_status[key]:
            continue

        draw = True

        match key:
            case "left":
                if not collides(tetromino, [tpos[0]-1, tpos[1]]):
                    tpos[0] -= 1

            case "right":
                if not collides(tetromino, [tpos[0]+1, tpos[1]]):
                    tpos[0] += 1

            case "down":
                if not collides(tetromino, [tpos[0], tpos[1]+1]):
                    tpos[1] += 1

                input_status["down"] = False # Jank way to do this but whatever
                dtime = perf_counter()

            case 'x':
                while not collides(tetromino, tpos):
                    tpos[1] += 1
                tpos[1] -= 1
                dtime = 0

            case "up":
                rotated_tetromino = list(zip(*tetromino[::-1]))
                if not collides(rotated_tetromino, tpos):
                    tetromino = rotated_tetromino
            case 'z':
                rotated_tetromino = list(zip(*tetromino))[::-1]
                if not collides(rotated_tetromino, tpos):
                    tetromino = rotated_tetromino

    # ---------------- DRAW ---------------- #

    if not draw:
        continue
    print(f"\033cLevel: {level}\nScore: {score}")

    game.reset()

    # Draw junk and tetromino
    game.draw_2d(junk)
    game.draw_2d(tetromino, tpos[0], tpos[1], False)

    game.qsend()
