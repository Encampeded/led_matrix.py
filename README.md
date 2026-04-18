# led_matrix.py
A simple Python library for interfacing with the Framework 16 LED Matrix

## Installation

Install [pyserial](https://pypi.org/project/pyserial/) (and [keyboard](https://pypi.org/project/keyboard/) if you want to try the example games) and copy led_matrix.py to your project folder. Maybe I'll put this on PyPI some day, but that day is not today.

## Usage

```python
from led_matrix import Matrix

# Create a matrix object
matrix = Matrix()

# You can also set the default_brightness (0-255)
# All methods use default_brightness as the default brightness (duh) when unspecified
dimmer_matrix = Matrix(64)
```

Stage LEDs on/off using `set_matrix(x, y)`<br>
The matrix starts at (0, 0) in the top left, and ends at (8, 33) in the bottom right
```python
# Set top left to default_brightness
matrix.set_matrix(0, 0)
# Set LED to the right to max brightness
matrix.set_matrix(1, 0, 255)
```

Change the default_brightness with `set_brightness(brightness)`
```python
matrix.set_brightness(255)
matrix.set_matrix(0, 1) # is now at max brightness
```

Use `qsend()` or `csend()` to display the current array on the matrix
- `csend()` (column send) includes per-led brightness however it is somewhat slow (~200ms)
- `qsend()` (quick send) displays all LEDs at the same brightness, but at significantly quicker speeds (~50ms)
```python
# Display each LED at its specified brightness
matrix.csend()

# Display all LEDs at default_brightness
matrix.qsend()
# ...or at 32 brightness
matrix.qsend(32)
```

Reset all LEDs to the one value using `reset()`
```python
# Turn off all LEDs
matrix.reset()

# Set all LEDs to max brightness
matrix.reset(255)
```

Get the brightness of a given coordinate with `get_matrix()`
```python
matrix.set_matrix(0, 0, 32)
brightness = matrix.get_matrix(0, 0)
print(brightness) # 32
```

### Advanced Features

Use the `Point` named-tuple and its corresponding methods for cleaner code
```python
from led_matrix import Point

top_right = Point(8, 0)

print(f"({top_right.x}, {top_right.y})")
# (8, 0)

matrix.set_point(top_right, 32)

brightness = matrix.get_point(top_right)
print(brightness) # 32

# set_points will set all points in a given iterable
matrix.set_points([
    Point(0, 0),
    Point(1, 1),
    Point(2, 2)
])

# If you object to named-tuples, all methods that take in Points also accept plain tuples, 
# lists, or any other indexable collection of at least (or ideally only) two elements
matrix.set_point((1, 1))
matrix.set_point([7, 2])
```

Draw horizontal or vertical lines with `draw_line()`
```python
matrix.draw_line((0, 0), (0, 33))
matrix.draw_line((0, 9), (5, 9))
```

Draw 2-dimensional arrays with `draw_2d()`
```python
image = [
    [64, 0,  64, 0, 64],
    [64, 64, 64, 0, 64],
    [64, 0,  64, 0, 64]
]

draw_point = Point(2, 3)

matrix.draw_2d(image, draw_point)

# draw_2d automatically ignores zeros. To draw them, even over already-set points, set override to True
blank_image = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

# Erases our HI message
matrix.draw_2d(blank_image, draw_point, override = True)
```

Send patterns or other custom commands using send(command, [parameters])

Command Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
```python
# Display the zigzag pattern, and animate
matrix.send(0x01, [0x04])
matrix.send(0x04, [True])
```

If you have any lingering confusions, I highly encourage reviewing `led_matrix.py` itself. I've tried to keep to code readable and easy to understand.
