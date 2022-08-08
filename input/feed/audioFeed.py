import torch


class AudioFeed(object):
    def __init__(self, audio_file):
        vggish_model = torch.hub.load('harritaylor/torchvggish', 'vggish')

        self.processed_file = vggish_model.forward(audio_file)

    def get_max_length(self):
        return self.processed_file.shape[0]

    def __iter__(self):
        return enumerate(self.processed_file)
