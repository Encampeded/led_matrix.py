# led_matrix.py
A simple Python library for interfacing with the Framework 16 LED Matrix

## Usage

I don't feel like putting this on PyPy, so just download led_matrix.py and put it in your project folder.
``` python
import led_matrix

# Create a matrix object
matrix = led_matrix.Matrix()

# You can set the default_brightness attribute in the constructor
# All methods use default_brightness as the default if brightness is unspecified
matrix = led_matrix.Matrix(64)
```
Set LEDs on/off using set_matrix(x, y, brightness)

The matrix starts at the top left at (0, 0), and ends at (8, 33)
```python
matrix.set_matrix(0, 0)      # 64
matrix.set_matrix(2, 0, 255) # 255

matrix.default_brightness = 255
matrix.set_matrix(0, 3)      # 255
```
Use qsend() or csend() to display the current array on the matrix

csend() includes per-led brightness however it is somewhat slow (~200ms)

qsend(brightness) displays each led at the same brightness but at significantly quicker speeds (~50ms)
```python
# Display each LED at its specified brightness
matrix.csend()

# Display all LEDs at default_brightness
matrix.qsend()  
matrix.q
```

reset() resets all LEDs to the one value

```python
# Turn off all LEDs
matrix.reset()

# Set all LEDs to max brightness
matrix.reset(255)
```

Draw horizontal or vertical lines with draw_line(point1, point2, fade, brightness)
```python
matrix.draw_line([0, 0], [0, 33])
matrix.draw_line([0, 9], [5, 9])

# Make the line fade to point2 by adding a fade length
matrix.draw_line([2, 0], [8, 0], 3)
```

Send patterns or other custom commands using send(command, [parameters])

Comand Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
```python
# Display the zigzag pattern, and animate
matrix.send(0x01, [0x04])
matrix.send(0x04, [True])
```
