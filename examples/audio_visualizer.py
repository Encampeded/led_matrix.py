import argparse
import math
import numpy as np
import numpy.typing as npt
import sounddevice as sd
import led_matrix
from collections import namedtuple

"""
Code adapted from:
https://python-sounddevice.readthedocs.io/en/0.5.3/examples.html#real-time-text-mode-spectrogram

Fair warning, I might completely refactor this at some point.
Also, I have no idea what I'm doing when it comes to raw audio.
If any of y'all think you could improve this, go for it.
"""

Range = namedtuple("Range", ["low", "high"])

class MatrixVisualizer:

    def __init__(self, device: str | int, gain: int, range: Range, style: int, brightness: int, block_size: int):

        # Audio stuff
        self.device: str | int = device
        self.samplerate = sd.query_devices(self.device, "input")["default_samplerate"]
        self.gain: int = gain
        self.range: Range = range
        self.stream: sd.InputStream | None = None

        # Display
        self.matrix: led_matrix.Matrix = led_matrix.Matrix(brightness)
        self.brightness: int = brightness
        self.block_size: int = block_size

        # Style
        self.style: int
        self.columns: int
        self.height: int
        self.visualizer: list[int]
        self.weight_distribution: npt.NDArray[np.float64]
        self.delta_f: float
        self.fft_size: int
        self.low_bin: int

        self.update_style(style)

    def update_style(self, style: int):
        self.style = style

        if 1 <= style <= 3:
            self.columns = 9
            self.height = 16


        elif style <= 5:
            self.columns = 34
            self.height = 8

        else:
            raise ValueError("Unknown style " + str(style))

        self.visualizer = [0] * self.columns
        self.weight_distribution = np.linspace(0.8, 2, num=self.columns)

        self.delta_f = (self.range.high - self.range.low) / (self.columns - 1)
        self.fft_size = math.ceil(self.samplerate / self.delta_f)
        self.low_bin = math.floor(self.range.low / self.delta_f)

    def gain_increment(self):
        self.gain += 2
        print(f"gain = {self.gain} (Incremented by 2)")

    def gain_decrement(self):
        self.gain -= 2
        print(f"gain = {self.gain} (Decremented by 2)")

    def decrement_visualizer(self):
        self.visualizer = [max(0, h-1) for h in self.visualizer]

    def update_visualizer(self, indata):
        self.decrement_visualizer()

        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=self.fft_size))
        magnitude *= self.gain / self.fft_size

        magnitudes_raw = magnitude[self.low_bin:self.low_bin + self.columns]
        magnitudes_raw *= self.weight_distribution

        magnitudes: list[int] = [
            int(round((np.clip(x, 0, 1) * self.height)))
            for i, x in enumerate(magnitudes_raw)
        ]

        self.visualizer = [
            max(h, self.visualizer[i]) for i, h in enumerate(magnitudes)
        ]

    def update_matrix(self):
        self.matrix.reset()

        # IF ADDING ANOTHER STYLE:
        #   - Set self.columns and self.height in update_style
        #   - Then add a case here
        match self.style:

            # Default, middle both ways
            case 1:
                for x, c in enumerate(self.visualizer):
                    self.matrix.draw_line((x, 17), (x, 17+c))
                    self.matrix.draw_line((x, 17), (x, 17-c))

            case 2:
                for x, c in enumerate(self.visualizer):
                    self.matrix.draw_line((x, 33), (x, 33-c))

            case 3:
                for x, c in enumerate(self.visualizer):
                    self.matrix.draw_line((x, 0), (x, c))

            case 4:
                for y, l in enumerate(self.visualizer):
                    self.matrix.draw_line((0, y), (l, y))

            case 5:
                for y, l in enumerate(self.visualizer):
                    self.matrix.draw_line((8, y), (8-l, y))

            case _:
                raise NotImplementedError(f"Style {self.style} missing!")

        self.matrix.qsend()

    def callback(self, indata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
        if any(indata):
            self.update_visualizer(indata)
        else:
            self.decrement_visualizer()

        self.update_matrix()

    def start_visualizer(self) -> sd.InputStream:
        if self.stream is not None:
            raise RuntimeError("Stream already exists!")

        self.stream = sd.InputStream(device=self.device, channels=1, callback=self.callback,
                                     blocksize=int(self.samplerate * self.block_size / 1000),
                                     samplerate=self.samplerate)

        self.stream.start()

        return self.stream

    def stop_visualizer(self):
        if self.stream is None:
            return

        self.stream.close()
        self.stream = None

    def __enter__(self):
        return self.start_visualizer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_visualizer()

if __name__ == "__main__":

    usage = "Enter q to quit, +/- to increase/decrease gain"

    parser = argparse.ArgumentParser(
        description= "Show an audio visualizer on the FW16 LED Matrix\n\n" + usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-l", "--list-devices",
                        action="store_true",
                        help="show list of audio devices and exit")

    parser.add_argument("-d", "--device",
                        type=lambda x : int(x) if x.isdigit() else x,
                        default="Audio Expansion Card",
                        help="input device (numeric ID or substring, see --list-devices) (default \"%(default)s\")3")

    parser.add_argument("-g", "--gain",
                        type=float, default=10,
                        help="initial gain factor (default %(default)s)")

    parser.add_argument("-r", "--range",
                        type=float, nargs=2,
                        metavar=("LOW", "HIGH"), default=[200, 2000],
                        help="frequency range (default %(default)s Hz)")

    parser.add_argument("-s", "--style",
                        type=int, default=1,
                        help="visualizer style (1-5, default %(default)s)")

    parser.add_argument("-b", "--brightness",
                        type=int, default=32,
                        help="brightness of LEDs (default %(default)s)")

    parser.add_argument("-m", "--ms-block",
                        type=float, metavar="DURATION", default=70,
                        help="block size in ms (default %(default)sms); the # of ms between updates")

    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    if not 0 <= args.brightness <= 255:
        parser.error("Brightness must be 0-255")

    hz_low, hz_high = args.range
    if hz_high <= hz_low:
        parser.error("HIGH must be greater than LOW")

    # device: str | int, gain: int, range: Range, style: int, brightness: int, speed: int
    visualizer = MatrixVisualizer(
        device = args.device,
        gain = args.gain,
        range = Range(hz_low, hz_high),
        style = args.style,
        brightness = args.brightness,
        block_size = args.ms_block
    )

    with visualizer:
        print("\x1b[31;40m", usage, "\x1b[0m", sep="")
        while True:
            response = input().lower().strip()

            if len(response) > 1:
                # Red escape code cool beans
                print("\x1b[31;40m", usage, "\x1b[0m", sep="")

            match response:
                case 'q':
                    break

                case '+':
                    visualizer.gain_increment()

                case '-':
                    visualizer.gain_decrement()

                case _:
                    print("\x1b[31;40m", usage.center(30, "#"), "\x1b[0m", sep="")
