import sys
import threading
from pydub import AudioSegment
from pydub.playback import play

from output.liveEventsOutupt import LiveEventsOutput


class Audio(LiveEventsOutput):
    def __init__(self, audio_file):
        if AudioSegment is None:
            print("Audio could not be played because the pydub library could not be found", file=sys.stderr)
        else:
            audio = AudioSegment.from_file(audio_file)

            audio_thread = threading.Thread(target=play, args=(audio,))
            audio_thread.start()

    def finish_initialization(self):
        pass

    def update(self, output_update):
        pass

    def terminate_output(self, *args, **kwargs):
        pass
