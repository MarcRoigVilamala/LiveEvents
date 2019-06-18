class Event(object):
    def __init__(self, timestamp, event, probability):
        self.timestamp = timestamp
        self.event = event
        self.probability = probability

    @staticmethod
    def from_problog(output):
        for event, prob in output.items():
            pass

        return []

    def to_problog(self):
        return '{probability}::happensAt({event}, {timestamp}).'.format(
            probability=self.probability,
            event=self.event,
            timestamp=self.timestamp
        )

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
