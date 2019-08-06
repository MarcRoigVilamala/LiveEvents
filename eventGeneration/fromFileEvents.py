from eventGeneration.event import Event


class FromFileEventGenerator(object):
    def __init__(self, filename):
        self.events = Event.from_file(filename)

    def get_events(self, enumerated_frames):
        timestamps, frames = zip(*enumerated_frames)

        # res = [self.events[int(timestamps[0] / 8)]]
        res = [
            e
            for e in self.events
            if e.timestamp in timestamps
        ]

        return res
