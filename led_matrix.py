from serial import Serial

class Matrix:

    def __init__(self, default_brightness: int = 128, serial_port: str = "/dev/ttyACM0"):
        self._matrix = []
        self.reset()
        self._default_brightness = default_brightness
        self._serial_port = Serial(serial_port, 115200)

    @staticmethod
    def check_coords(x: int, y: int) -> None:
        if not (0 <= x <= 8 and 0 <= y <= 33):
            raise ValueError(f"Coordinates ({x}, {y}) out of range. X must be 0-8 and Y must be 0-33")

    @staticmethod
    def check_brightness(brightness: int) -> None:
        if not 0 <= brightness <= 255:
            raise ValueError(f"Brightness {brightness} out of range. Brightness must be 0-255")

    # While 305 is the bottom left, we need 6 extra values
    # for qsend, whose last 8bits start at 304
    def reset(self, brightness: int = 0) -> None:
        self._matrix = [brightness for _ in range(312)]

    def set_brightness(self, brightness: int) -> None:
        self.check_brightness(brightness)

        self._default_brightness = brightness

    def set_matrix(self, x: int, y: int, brightness: int = None) -> None:
        if brightness is None: brightness = self._default_brightness

        self.check_coords(x, y)
        self.check_brightness(brightness)

        self._matrix[(y * 9) + x] = brightness

    def get_matrix(self, x: int, y: int) -> int:
        self.check_coords(x, y)

        return self._matrix[(y * 9) + x]

    def draw_line(self, point1: list[int] | tuple[int, int],
                        point2: list[int] | tuple[int, int],
                        brightness: int = None) -> None:
        if brightness is None: brightness = self._default_brightness

        # Range wrapper that supports betterate(10, 0), going from 10-0
        # Also includes the last number. probably unnecessary, but eh
        def betterate(start: int, to: int) -> list[int]:

            # Reverse if the start is greater.
            reverse = start > to
            if start > to:
                start, to = to, start

            result_list = list(range(start, to + 1))
            if reverse: result_list.reverse()

            return result_list

        # Vertical Line
        if point1[0] == point2[0]:
            points = [[point1[0], i] for i in betterate(point1[1], point2[1])]

        # Horizontal Line
        elif point1[1] == point2[1]:
            points = [[i, point1[1]] for i in betterate(point1[0], point2[0])]

        else:
            raise ValueError(f"Coordinates {point1} {point2} form diagonal line\ndraw_line() only supports horizontal and vertical lines")

        for point in points:
            self.set_matrix(point[0], point[1], brightness)

    def draw_2d(self, image: list[list[int]],
                      x: int = 0, y: int = 0,
                      override: bool = False):

        for y_offset, row in enumerate(image):
            for x_offset, value in enumerate(row):

                if not override and not value:
                    continue

                self.set_matrix(x+x_offset, y+y_offset, value)

    # Adapted from framework example
    def send(self, command_id: int, parameters: list, with_response: bool = False) -> bytes | None:

        self._serial_port.write([0x32, 0xAC, command_id] + parameters)

        if with_response:
            return self._serial_port.read(32)

        return None

    # Column Send, uses StageCol (0x07) and FlushCols (0x08)
    # Sends each of the 9 columns individually, then draws (flushes) them
    def csend(self) -> None:

        columns = [
            [self._matrix[y] for y in range(x, 312, 9)]
            for x in range(9)
        ]

        for i in range(9):
            self.send(0x07, [i, *columns[i]])

        self.send(0x08, [])

    # Quick Send, uses DrawBW (0x06) that takes 39 8-bit integers, each
    # representing 8 LEDs starting from (0, 0) and wrapping around lines
    def qsend(self, brightness: int = None) -> None:
        if brightness is None: brightness = self._default_brightness

        matrix_encoded = [
            sum(int(bool(bit)) << j for j, bit in enumerate(self._matrix[i:i+8]))
            for i in range(0, 312, 8)
        ]

        self.send(0x06, matrix_encoded)
        self.send(0x00, [brightness])
