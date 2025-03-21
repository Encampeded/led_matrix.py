import serial

class Matrix:

    def __init__(self, default_brightness: int = 128) -> None:
        self.matrix = [0 for i in range(312)]
        self.default_brightness = default_brightness

    def reset(self, brightness: int = 0) -> None:
        self.brightness = [value for i in range(312)]

    def set_matrix(self, x: int, y: int, brightness: int = None) -> None:

        if brightness is None: brightness = self.default_brightness

        if not (0 <= x <= 8 and 0 <= y <= 33):
            raise ValueError(f"Coordinates ({x}, {y}) out of range. X must be 0-8 and Y must be 0-33")
        if not 0 <= brightness <= 255:
            raise ValueError(f"Brightness {brightness} out of range. Brightness must be 0-255")

        self.matrix[(y * 9) + x] = brightness


    def draw_line(self, point1: list[int], point2: list[int], fade: int = 0, brightness: int = None) -> None:
        if brightness is None: brightness = self.default_brightness

        # Range wrapper that supports betterate(10, 0), going from 10-0
        # Also actually includes the last number, probably unnecessary, but
        # screw you
        def betterate(start: int, to: int) -> list[int]:

            reverse: bool = start > to  # Reverse if the start is greater.
            if start > to:
                start, to = to, start

            result_list = list(range(start, to + 1))
            if reverse:
                result_list.reverse()

            return result_list

        points = []

        # Vertical Line
        if point1[0] == point2[0]:
            for i in betterate(point1[1], point2[1]):
                points.append([point1[0], i])

        # Horizontal Line
        elif point1[1] == point2[1]:
            for i in betterate(point1[0], point2[0]):
                points.append([i, point1[1]])

        # Maybe I'll implement this at some point. idk
        else: raise ValueError(f"Coordinates {point1} {point2} form diagonal line\ndraw_line() only supports horizontal and vertical lines")

        if fade > len(points):
            raise ValueError(f"Fade length {fade} longer than line length {len(points)}")

        for point in (points[:-fade] if fade else points):
            self.set_matrix(point[0], point[1], brightness)

        if fade:
            bdiff = int(brightness / (fade + 1))
            for b, i in enumerate(range(len(points) - fade, len(points))):

                self.set_matrix(points[i][0], points[i][1],
                                int(brightness - ((b + 1) * bdiff)))


    # Copied from framework example
    def send(self, command_id: int, parameters: list[str],
             with_response: bool = False) -> bytes | None:

        with serial.Serial('/dev/ttyACM0', 115200) as s:
            s.write([0x32, 0xAC, command_id] + parameters)

            if with_response:
                res = s.read(32)
                return res

        return None


    # Column Send, uses StageCol (0x07) and FlushCols (0x08)
    # Sends each of the 9 columns individually, then draws (flushes) them
    def csend(self) -> None:

        columns = []
        for x in range(9):
            column = []
            for y in range(x, 312, 9):
                column.append(self.matrix[y])
            columns.append(column)

        for i in range(9):
            self.send(0x07, [i, *columns[i]])

        self.send(0x08, [])


    # Quick Send, uses DrawBW (0x06) that takes 33 8-bit integers, each
    # representing 8 LEDs starting from (0, 0)
    def qsend(self, brightness: int = None) -> None:
        if brightness is None: brightness = self.default_brightness

        matrix_encoded = []

        for i in range(0, 312, 8):

            # Slice our matrix into the line of 8 and reverse bc int(x, 2)
            # reads it reversed for some reason
            line = [bool(i) for i in self.matrix[i:i + 8][::-1]]

            # Copied from https://stackoverflow.com/a/68424066, convert our
            # bool array to int 0/1, convert to integer using binary
            line = int("".join(["01"[i] for i in line]), 2)

            matrix_encoded.append(line)

        self.send(0x06, matrix_encoded)
        self.send(0x00, [brightness])
