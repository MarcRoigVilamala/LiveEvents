class Event(object):
    def __init__(self, timestamp, event, probability=0.0, event_type='happensAt'):
        self.timestamp = timestamp
        self.event = event
        self.probability = probability
        self.event_type = event_type

    @staticmethod
    def from_evaluation(evaluation):
        return [
            Event(timestamp=timestamp, event='{} = true'.format(event), probability=prob, event_type='holdsAt_')
            for event, event_values in evaluation.items()
            for ids, ids_values in event_values.items()
            for timestamp, prob in ids_values.items()
            if prob > 0.0
        ]

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as f:
            res = []

            for l in f:
                if '::' in l:
                    probability, rest = l.strip().split('::')
                    event_type, rest = rest.split('(', 1)
                    event, timestamp = rest.rsplit(', ', 1)

                    probability = float(probability)
                    timestamp = int(timestamp[:-2])

                    res.append(
                        Event(timestamp, event, probability, event_type)
                    )

            return res

    def to_prolog(self):
        return self.to_prolog_with()

    def to_prolog_with(self, event_type=None, event=None, timestamp=None):
        if event_type is None:
            event_type = self.event_type
        if event is None:
            event = self.event
        if timestamp is None:
            timestamp = self.timestamp

        return '{event_type}({event}, {timestamp}).'.format(
            event_type=event_type,
            event=event,
            timestamp=timestamp
        )

    def to_problog(self):
        return self.to_problog_with()

    def to_problog_with(self, probability=None, event_type=None, event=None, timestamp=None):
        if probability is None:
            probability = self.probability
        if event_type is None:
            event_type = self.event_type
        if event is None:
            event = self.event
        if timestamp is None:
            timestamp = self.timestamp

        return '{probability}::{event_type}({event}, {timestamp}).'.format(
            probability=probability,
            event_type=event_type,
            event=event,
            timestamp=timestamp
        )

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
