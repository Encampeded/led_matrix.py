# led_matrix.py
A simple Python library for interfacing with the Framework 16 LED Matrix

'''
import led_matrix

matrix = led_matrix.Matrix()

# Set LEDS on/off using set_matrix
# The matrix starts at the top left at (0, 0), and ends at (8, 33)
matrix.set_matrix(0, 0)
matrix.set_matrix(1, 0)

# Turn off an LED by adding False
matrix.set_matrix(0, 0, False)

# Set the brightness 0-255
matrix.send_brightness(32)

matrix.send_matrix()

matrix.reset()

# draw_line() draws a line (duh) between two specified points
# It can draw lines beyond vertical/horizontal, however the algorithm kinda sucks lol. I don't recommend using it
matrix.draw_line([1, 3], [1, 8])
matrix.draw_line([1, 3], [5, 3])

# draw_rectangle draws a rectangle (duh x2)
# First point is top left, with the second being bottom right
matrix.draw_rectangle([2, 15], [7, 25])

matrix.send_matrix()

# Send patterns or other custom commands using send(command, [parameters])
# Command Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
matrix.send_brightness(32)
matrix.send(0x01, [0x04])
matrix.send(0x04, [False])

# If you're curious about additional functionality, I recommend looking at the source, led_matrix.py
# It's really quite simple and I've commented most things that aren't immediately obvious

'''
