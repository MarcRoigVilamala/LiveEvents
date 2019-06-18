from eventGeneration.event import Event


def get_events(enumerated_frames):
    return [
        Event(timestamp=i, event='something', probability=0.5)
        for i, frame in enumerated_frames
    ]
