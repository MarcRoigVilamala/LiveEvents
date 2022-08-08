import torch
import pyaudio
import numpy as np


class LiveAudioFeed(object):
    CHUNK = 1024
    WIDTH = 2
    CHANNELS = 2
    RATE = 16000

    def __init__(self):
        self.vggish_model = torch.hub.load('harritaylor/torchvggish', 'vggish')

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.WIDTH),
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK
        )

        self.iteration = 0

    def get_max_length(self):
        return 100

    def __iter__(self):
        all_frames = []

        while True:
            frames = []

            # Record for a second
            for _ in range(0, int(self.RATE / self.CHUNK)):
                data = self.stream.read(self.CHUNK)
                frames.append(data)
                all_frames.append(data)

            np_data = np.frombuffer(b''.join(frames), dtype=np.int16)

            samples = np_data / 32768.0  # Convert to [-1.0, +1.0]

            nn_input = self.vggish_model.forward(samples, self.RATE)

            if len(nn_input.size()) == 1:
                nn_input = nn_input.unsqueeze(0)

            for n in nn_input:
                yield self.iteration, n
                self.iteration += 1
