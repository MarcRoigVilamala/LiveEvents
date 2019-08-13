from preCompilation.PreCompilation import InputClause


class Event(InputClause):
    def get_clause_format(self):
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
                    event, timestamp = rest.rsplit(', ', 1)

                    probability = float(probability)
                    timestamp = int(timestamp[:-2])

                    res.append(
                        Event(timestamp, event, probability, event_type)
                    )

            return res

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
