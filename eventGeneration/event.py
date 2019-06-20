class Event(object):
    def __init__(self, timestamp, event, probability, type='happensAt'):
        self.timestamp = timestamp
        self.event = event
        self.probability = probability
        self.type = type

    @staticmethod
    def from_evaluation(evaluation):
        return [
            Event(timestamp=timestamp, event='{} = true'.format(event), probability=prob, type='holdsAt_')
            for event, event_values in evaluation.items()
            for ids, ids_values in event_values.items()
            for timestamp, prob in ids_values.items()
            if prob > 0.0
        ]

    def to_problog(self):
        return '{probability}::{type}({event}, {timestamp}).'.format(
            probability=self.probability,
            type=self.type,
            event=self.event,
            timestamp=self.timestamp
        )

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
