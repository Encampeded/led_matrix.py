from led_matrix import Matrix, Point
from keyboard import is_pressed
from random import shuffle
from time import perf_counter
from collections import deque

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

BRIGHTNESS = 255

TETROMINOS = (
    (
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (0, 0, 0, 0),
        (0, 0, 0, 0)
    ),
    (
        (1, 0, 0),
        (1, 1, 1),
        (0, 0, 0)
    ),
    (
        (0, 0, 1),
        (1, 1, 1),
        (0, 0, 0)
    ),
    (
        (1, 1),
        (1, 1)
    ),
    (
        (0, 1, 1),
        (1, 1, 0),
        (0, 0, 0)
    ),
    (
        (0, 1, 0),
        (1, 1, 1),
        (0, 0, 0)
    ),
    (
        (1, 1, 0),
        (0, 1, 1),
        (0, 0, 0)
    )
)

type Tetromino = tuple[tuple[int, ...], ...]

def next_tetromino() -> Tetromino:
    global tetromino_queue

    if not tetromino_queue:
        new_queue = [i for i, _ in enumerate(TETROMINOS)]
        shuffle(new_queue)
        tetromino_queue.extend(new_queue)

    return TETROMINOS[tetromino_queue.pop()]

def collides(tetromino: Tetromino, position: Point) -> bool:
    """Checks if a tetromino in a given position collides with anything"""
    for y, _ in enumerate(tetromino):
        for x, _ in enumerate(tetromino[y]):

            if not tetromino[y][x]:
                continue

            current_point = Point(position.x+x, position.y+y)

            if not (0 <= current_point.x <= 8 and current_point.y <= 33) or \
                junk[current_point.y][current_point.x]:

                return True

    return False

game = Matrix(BRIGHTNESS)
game.qsend()

input_status: dict[str, bool] = {
    key: False for key in ["up", "down", "left", "right", 'z', 'x']
}

score: int = 0
level: int = 1

tpos: Point = Point(3, 0)
tetromino_queue: deque[int] = deque()
current_tetromino: Tetromino = next_tetromino()
junk: list[list[int]] = [[0 for _ in range(9)] for _ in range(34)]

dtime: float = 0.0

while True:

    # ---------------- UPDATE ---------------- #

    draw = False

    # If time has passed, move tetromino down and check for collisions
    if (perf_counter()-dtime) > (1 / ((0.5*level) + 1)):
        dtime = perf_counter()
        draw = True
        tpos = Point(tpos.x, tpos.y + 1)

        if collides(current_tetromino, tpos):

            # Add current tetromino to junk
            for y, _ in enumerate(current_tetromino):
                for x, _ in enumerate(current_tetromino[y]):

                    if current_tetromino[y][x]:
                        junk[tpos.y-1 + y][tpos.x + x] = 1

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
            tpos = Point(3, 0)
            current_tetromino = next_tetromino()

            # If newly generated tetromino collides, do game over animation and quit
            if collides(current_tetromino, tpos):
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
                if not collides(current_tetromino, Point(tpos.x - 1, tpos.y)):
                    tpos = Point(tpos.x - 1, tpos.y)

            case "right":
                if not collides(current_tetromino, Point(tpos.x+1, tpos.y)):
                    tpos = Point(tpos.x + 1, tpos.y)

            case "down":
                if not collides(current_tetromino, Point(tpos.x, tpos.y+1)):
                    tpos = Point(tpos.x, tpos.y + 1)

                input_status["down"] = False # Jank way to do this but whatever
                dtime = perf_counter()

            case 'x':
                while not collides(current_tetromino, tpos):
                    tpos = Point(tpos.x, tpos.y + 1)
                tpos = Point(tpos.x, tpos.y - 1)
                dtime = 0

            case "up":
                rotated_tetromino = tuple(zip(*current_tetromino[::-1]))
                if not collides(rotated_tetromino, tpos):
                    current_tetromino = rotated_tetromino
            case 'z':
                rotated_tetromino = tuple(zip(*current_tetromino))[::-1]
                if not collides(rotated_tetromino, tpos):
                    current_tetromino = rotated_tetromino

    # ---------------- DRAW ---------------- #

    if not draw:
        continue

    print(f"\033cLevel: {level}\nScore: {score}")

    game.reset()

    # Draw junk and tetromino
    game.draw_2d(junk, (0, 0))
    game.draw_2d(current_tetromino, tpos)

    game.qsend()
