import serial, time

class Matrix:

    matrix = [0 for i in range(312)]
    default_brightness = 128

    def reset(self, value = 0):
        self.matrix = [value for i in range(312)]

    def set_matrix(self, x, y, brightness=default_brightness):

        if not (0 <= x <= 8 and 0 <= y <= 33):
            raise Exception(f"Coordinates ({x}, {y}) out of range. X must be 0-8 and Y must be 0-33")
        if not (0 <= brightness <= 255):
            raise Exception(f"Brightness {brightness} out of range. Brightness must be 0-255")

        self.matrix[(y*9)+x] = brightness

    # Copied from framework example
    def send(self, command_id, parameters, with_response=False):

        with serial.Serial('/dev/ttyACM0', 115200) as s:
            s.write([0x32, 0xAC, command_id] + parameters)

            if with_response:
                res = s.read(32)
                return res

    # Column Send, uses StageCol (0x07) and FlushCols (0x08)
    # Sends each of the 9 columns individually, then draws them
    def csend(self):

        columns = []
        for x in range(9):
            column = []
            for y in range(x, 312, 9):
                column.append(self.matrix[y])
            columns.append(column)

        for i in range(9):
            self.send(0x07, [i, *columns[i]])

        self.send(0x08, [])

    # Quick Send, uses DrawBW (0x06) that takes 33 8-bit integers, each representing 8 LEDs starting from (0, 0)
    def qsend(self, brightness=default_brightness):

        matrix_encoded = []

        for i in range(0, 312, 8):

            # Slice our matrix into the line of 8 and reverse bc int(x, 2) reads it reversed for some reason
            line = [bool(i) for i in self.matrix[i:i+8][::-1]]

            # Copied from https://stackoverflow.com/a/68424066, convert our bool array to int 0/1, convert to integer using binary
            line = int("".join(["01"[i] for i in line]), 2)

            matrix_encoded.append(line)

        self.send(0x00, [brightness])
        self.send(0x06, matrix_encoded)

