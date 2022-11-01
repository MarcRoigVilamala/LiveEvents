from preCompilation.PreCompilation import InputClause


class Event(InputClause):
    def get_clause_only_format(self):
        if self.timestamp_first:
            clause_format = "{event_type}({{timestamp}}, {{identifier}})"
        else:
            clause_format = "{event_type}({{identifier}}, {{timestamp}})"

        return clause_format.format(
            event_type=self.event_type
        )

    def get_clause_format(self):
        return '\n{{probability}}::{clause}.'.format(
            clause=self.get_clause_only_format()
        )

    def get_clause_only_as_str(self):
        return self.get_clause_only_format().format(
            identifier=self.identifier,
            timestamp=self.timestamp
        )

    @property
    def timestamp_first(self):
        return self.event_type in ['sound', 'nlp']

    def for_mock_model(self):
        return self.to_problog_with(probability=0.0)

    def __init__(self, timestamp, event, probability=0.0, event_type='happensAt'):
        super().__init__(event, timestamp, probability)
        self.event_type = event_type

    @staticmethod
    def from_evaluation(evaluation):
        res = [
            Event(timestamp=int(e.args[1]), event=str(e.args[0]), probability=prob, event_type='holdsAt_')
            for e, prob in evaluation.items()
            if prob > 0.0
        ]

        # res = [
        #     Event(timestamp=timestamp, event='{} = true'.format(event), probability=prob, event_type='holdsAt_')
        #     for event, event_values in evaluation.items()
        #     for ids, ids_values in event_values.items()
        #     for timestamp, prob in ids_values.items()
        #     if prob > 0.0
        # ]

        return res

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

    def to_nice_string(self, prob_precision=3):
        # return "{:.3}::{}".format(self.probability, self.identifier)
        return f"{self.get_clause_only_as_str()}: {self.probability:.{prob_precision}f}"

    def __repr__(self):
        return self.to_problog()

    def __str__(self):
        return self.to_problog()
