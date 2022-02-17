from preCompilation.PreCompilation import InputClause


class Event(InputClause):
    def get_clause_format(self):
        if self.event_type == 'sound':
            return '\n{{probability}}::{event_type}({{timestamp}}, {{identifier}}).'.format(
                event_type=self.event_type
            )

        return '\n{{probability}}::{event_type}({{identifier}}, {{timestamp}}).'.format(
            event_type=self.event_type
        )

    def for_mock_model(self):
        return self.to_problog_with(probability=0.0)

    def __init__(self, timestamp, event, probability=0.0, event_type='happensAt'):
        super().__init__(event, timestamp, probability)
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
                    if event_type == 'sound':
                        timestamp, event = rest.rsplit(', ', 1)
                        event = event[:-2]
                    else:
                        event, timestamp = rest.rsplit(', ', 1)
                        timestamp = timestamp[:-2]

                    probability = float(probability)
                    timestamp = int(timestamp)

                    res.append(
                        Event(timestamp, event, probability, event_type)
                    )

            return res

    def to_nice_string(self):
        return "{:.3}::{}".format(self.probability, self.identifier)

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
