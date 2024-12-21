import serial

class Matrix:

    # The working array that the user modifies through set_matrix
    matrix = [False for i in range(312)]

    def reset(self):
        self.matrix = [False for i in range(312)]

    # X=0-8, Y=0-33, (0, 0) is top left
    def set_matrix(self, x, y, value=True):
        if not (0 <= x <= 8 and 0 <= y <= 33):
            raise Exception(f"Coordinates ({x}, {y}) out of range. X must be 0-8 and Y must be 0-33")

        self.matrix[(y*9)+x] = value


    def draw_line(self, point1, point2):
        # Make point1 always to the left of point2
        if point1[0] > point2[0]:
            point1, point2 = point2, point1

        # If X's are the same, draw vertical line
        if point1[0] == point2[0]:
            for i in range(point1[1], point2[1]+1, -1 if point1[1] > point2[1] else 1):
                self.set_matrix(point1[0], i)
            return

        # If Y's are the same, draw horizontal line
        if point1[1] == point2[1]:
            for i in range(point1[0], point2[0]+1):
                self.set_matrix(i, point1[1])
            return

        print("Sorry, this line drawing algo is janky")
        print("if you want non-straight lines, i recommend doing it yourself w/ numpy or something. this sucks ass lol")
        slope = (point2[1]-point1[1])/(point2[0]-point1[0])

        for i in range(point1[0], point2[0]+1):
            self.set_matrix(i, round(point1[1]+(slope*(i-point1[0]))))


    def draw_rectangle(self, point1, point2, filled=False):
        # Draw horizontal lines
        for y in [point1[1], point2[1]]:
            self.draw_line([point1[0], y], [point2[0], y])

        for x in [point1[0], point2[0]]:
            self.draw_line([x, point1[1]+1], [x, point2[1]-1])

        if filled:
            for y in range(point1[1]+1, point2[1]):
                self.draw_line([point1[0]+1, y], [point2[0]-1, y])


    # Copied from framework example
    def send(self, command_id, parameters, with_response=False):

        with serial.Serial('/dev/ttyACM0', 115200) as s:
            s.write([0x32, 0xAC, command_id] + parameters)

            if with_response:
                res = s.read(32)
                return res

    def send_brightness(self, brightness):
        if not (0 <= brightness <= 255):
            raise Exception(f"Invalid brightness of {brightness}, must be 0-255.")

        self.send(0x00, [brightness])

    def send_matrix(self):

        # DrawBW (0x06) command takes 33 8-bit binary integers, each representing one line
        matrix_encoded = []

        for i in range(0, 312, 8):

            # Slice our matrix into the line of 8 and reverse bc int(x, 2) reads it reversed for some reason
            line = self.matrix[i:i+8][::-1]

            # Copied from https://stackoverflow.com/a/68424066, convert out bool array to int, convert to integer
            line = int("".join(["01"[i] for i in line]), 2)

            matrix_encoded.append(line)

            # Previous one-liner that i changed to make it a tad more readable
            # self.matrix_encoded.append(int("".join(["01"[i] for i in self.matrix[i:i+8]][::-1]), 2))


        self.send(0x06, matrix_encoded)





