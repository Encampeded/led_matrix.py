import led_matrix

matrix = led_matrix.Matrix()

# Set LEDS on/off using set_matrix
# The matrix starts at the top left at (0, 0), and ends at (8, 33)
matrix.set_matrix(0, 0)
matrix.set_matrix(1, 0)

# Set an LED back off by adding False
matrix.set_matrix(0, 0, False)

# draw_line() draws a line between two specified points
# It *can* draw diagonal lines, however the algorithm kinda sucks. I recommend only using it for horizontal/vertical
matrix.draw_line([1, 3], [1, 8])
matrix.draw_line([3, 4], [7, 4])

# draw_rectangle() draws a rectangle (duh)
# First point is top left, with the second being bottom right
matrix.draw_rectangle([2, 15], [7, 25])

# Add True to make the rectangle filled
matrix.draw_rectangle([1, 27], [7, 32], True)

# Send the current array to the LED matrix
matrix.send_matrix()
matrix.reset()

# Set the brightness of the matrix 0-255
matrix.send_brightness(32)

# Send patterns or other custom commands using send(command, [parameters])
# Command Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
matrix.send_brightness(32)
matrix.send(0x01, [0x04])
matrix.send(0x04, [True])

# If you're curious about additional functionality, I recommend looking at the source, led_matrix.py
# It's really quite simple and I've commented most things that aren't immediately obvious
