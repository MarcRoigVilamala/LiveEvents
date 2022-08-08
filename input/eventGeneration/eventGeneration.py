import itertools


class EventGenerator(object):
    def __init__(self, event_generators):
        self.event_generators = event_generators

    def get_events(self, enumerated_frames):
        return list(
            itertools.chain.from_iterable(
                [
                    event_gen.get_events(enumerated_frames)
                    for event_gen in self.event_generators
                ]
            )
        )
