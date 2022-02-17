import torch
import torch.nn as nn

from eventGeneration.event import Event


class SoundVGGish(nn.Module):
    def __init__(self, n_classes=10):
        super(SoundVGGish, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(in_features=128, out_features=100),
            nn.ReLU(),
            nn.Linear(in_features=100, out_features=80),
            nn.ReLU(),
            nn.Linear(in_features=80, out_features=50),
            nn.ReLU(),
            nn.Linear(in_features=50, out_features=25),
            nn.ReLU(),
            nn.Linear(in_features=25, out_features=n_classes),

            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.net(x)


class FromAudioNN(object):
    def __init__(self, classes, network):
        self.classes = classes

        self.network = network

    def get_events_from(self, audio_tensor):
        return self.network(audio_tensor.unsqueeze(0)).squeeze()

    def get_events(self, enumerated_frames):
        events = [
            Event(
                timestamp=t,
                event=c,
                probability=o,
                event_type='sound'
            )
            for t, v in enumerated_frames
            for c, o in zip(self.classes, self.get_events_from(v))
        ]

        return events


class DemoFromAudioNN(object):
    def __init__(self, sequence, network=None, classes=None):
        self.sequence = sequence

        if classes:
            self.classes = classes
        else:
            self.classes = ['boom', 'siren', 'silence', 'gun_shot', 'shatter', 'screaming']

        if network:
            self.network = network
        else:
            self.network = SoundVGGish(n_classes=len(self.classes))
            self.network.load_state_dict(torch.load('neuralNetworkWeights/sounds.pt'))

    def get_events(self, enumerated_frames):
        timestamps, frames = zip(*enumerated_frames)

        inputs = filter(lambda x: x[0] in timestamps, self.sequence)

        events = [
            Event(
                timestamp=t,
                event=c,
                probability=o,
                event_type='sound'
            )
            for t, v in inputs
            for c, o in zip(self.classes, self.network(torch.load(v).unsqueeze(0)).squeeze())
        ]

        return events
