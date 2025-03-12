# led_matrix.py
A simple Python library for interfacing with the Framework 16 LED Matrix

## Usage

I don't feel like putting this on PyPy, so just download led_matrix.py and put it in your project folder.
``` python
import led_matrix

matrix = led_matrix.Matrix()
```
Set LEDs on/off using set_matrix(x, y, brightness)

The matrix starts at the top left at (0, 0), and ends at (8, 33)
```python
matrix.set_matrix(0, 0, 255)

# Brightness is 0-255, and defaults to default_brightness 128 if unspecified

matrix.set_matrix(2, 0)   # 128
matrix.default_brightness = 255
matrix.set_matrix(0, 3)   # 255
```
Use qsend() or csend() to display the current array on the matrix

csend() includes per-led brightness however it is somewhat slow (~200ms).

qsend() displays each led at the same  brightness but at significantly quicker speeds (~50ms)
```python
matrix.csend()
matrix.qsend()
```

reset() sets all LEDs to the same value (default 0)

```python
# Set all LEDs to max brightness
matrix.reset(255)
# Turn off all LEDs
matrix.reset()
```
Send patterns or other custom commands using send(command, [parameters])

Comand Reference: https://github.com/FrameworkComputer/inputmodule-rs/blob/main/commands.md
```python
# Display the zigzag pattern, and animate
matrix.send(0x01, [0x04])
matrix.send(0x04, [True])
```
