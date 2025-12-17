# led_matrix.py
A simple Python library for interfacing with the Framework 16 LED Matrix

## Getting started

I don't feel like putting this on PyPy, so:
Install pyserial (and [keyboard](https://pypi.org/project/keyboard/) if you want to try the example games) and put led_matrix.py in your project folder.
``` python
import led_matrix

# Create a matrix object
matrix = led_matrix.Matrix()

# Set the default_brightness attribute (0-255) in the constructor
# All methods use default_brightness as the default brightness (duh) when it's unspecified
matrix = led_matrix.Matrix(64)
```
Set LEDs on/off using set_matrix

The matrix starts at the top left at (0, 0), and ends at (8, 33)
```python
# Set top left to default_brightness
matrix.set_matrix(0, 0)
# Set LED to the right to max brightness
matrix.set_matrix(1, 0, 255)
```

Change the default_brightness with set_brightness.
```python
matrix.set_brightness(255)
matrix.set_matrix(0, 1) # 255
```
Use qsend or csend to display the current array on the matrix.

csend (column send) includes per-led brightness however it is somewhat slow (~200ms)

qsend (quick send) displays all LEDs at the same brightness, but at significantly quicker speeds (~50ms)
```python
# Display each LED at its specified brightness
matrix.csend()

# Display all LEDs at default_brightness
matrix.qsend()
# ...or at 32 brightness
matrix.qsend(32)
```

Reset all LEDs to the one value using reset
```python
# Turn off all LEDs
matrix.reset()

# Set all LEDs to max brightness
matrix.reset(255)
```

get_matrix() shows the brightness of a given coordinate
```python
matrix.set_matrix(0, 0, 128)
brightness = matrix.get_matrix(0, 0)
print(brightness) # 128 
```

Draw horizontal or vertical lines with draw_line
```python
matrix.draw_line([0, 0], [0, 33])
matrix.draw_line([0, 9], [5, 9])

# Make the line fade to point2 by adding a fade length
matrix.draw_line([2, 0], [8, 0], fade=3)

# Or change the brightness of the line from default_brightness
matrix.draw_line([2, 0], [8, 0], brightness=3)
```

Send patterns or other custom commands using send(command, [parameters])

Comand Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
```python
# Display the zigzag pattern, and animate
matrix.send(0x01, [0x04])
matrix.send(0x04, [True])
```
