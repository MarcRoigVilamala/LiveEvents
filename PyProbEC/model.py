from __future__ import print_function

from problog.evaluator import SemiringSymbolic
from problog.program import PrologString
from problog import get_evaluatable

from os import path
import sys


# Files that define how EC works
from PyProbEC.precompilation import EventPreCompilation
from PyProbEC.utils import unsorted_groupby, term_to_list, get_values
from eventGeneration.event import Event

PROBLOG_FILES = [
    'PyProbEC/ProbLogFiles/prob_ec_cached.pl',
]


class Model(object):
    def __init__(self, event_definition_files=(), precompile_arguments=None, semiring=None):
        # The base model will be formed from the base ProbLog files that define EC
        # and the files given by the user that should define the rules for the
        # complex event they are trying to detect
        models = [
            self.read_model(m)
            for m in PROBLOG_FILES + event_definition_files
        ]

        self.model = '\n\n'.join(models)

        self.semiring = semiring

        if precompile_arguments:
            self.precompilation = EventPreCompilation(precompile_arguments, self.model, semiring)
        else:
            self.precompilation = None

    @staticmethod
    def _evaluation_to_prob(evaluation):
        # event -> ids -> timestamp -> prob
        return {
            event: {
                ids: {
                    timestamp: list(v3)[0][3]
                    for timestamp, v3 in unsorted_groupby(list(v2), key=lambda x: x[2])
                }
                for ids, v2 in unsorted_groupby(list(v1), key=lambda x: str(x[1]))
            }
            for event, v1 in unsorted_groupby(map(get_values, evaluation.items()), lambda x: x[0])
        }

    def get_timestamps(self):
        model = PrologString(self.model + '\n\nquery(allTimeStamps(TPs)).')

        knowledge = get_evaluatable(semiring=self.semiring).create_from(model, semiring=self.semiring)

        timestamps = [
            term_to_list(term.args[0])
            for term in knowledge.evaluate(semiring=self.semiring).keys()
            if term.functor == 'allTimeStamps'
        ]

        return sorted([item for sublist in timestamps for item in sublist])

    def get_values_for(self, existing_timestamps, query_timestamps, expected_events, input_events=()):
        # As the model we use self.model (basic EC definition + definition of rules by the user) and we add the list
        # of the input events
        string_model = self.model + '\n' + '\n'.join(map(lambda x: x.to_problog(), input_events))

        string_model += '\nallTimeStamps([{}]).'.format(', '.join(map(str, existing_timestamps)))

        updated_knowledge = ''

        res = {}

        for timestamp in query_timestamps:
            for event in expected_events:
                query = 'query(holdsAt({event} = true, {timestamp})).\n'.format(event=event, timestamp=timestamp)

                model = PrologString(string_model + '\n' + updated_knowledge + '\n' + query)

                knowledge = get_evaluatable(
                    name='ddnnf', semiring=self.semiring
                ).create_from(
                    model, semiring=self.semiring
                )

                evaluation = knowledge.evaluate(semiring=self.semiring)

                res.update(evaluation)

                for k, v in evaluation.items():
                    if v > 0.0:
                        updated_knowledge += '{0}::{1}.\n'.format(v, k).replace('holdsAt', 'holdsAt_')

        return res

    def get_probabilities(self, existing_timestamps, query_timestamps, expected_events, input_events=()):
        evaluation = self.get_values_for(
            existing_timestamps, query_timestamps, expected_events, input_events=input_events
        )

        return self._evaluation_to_prob(evaluation)

    def get_probabilities_precompile(self, existing_timestamps, query_timestamps, expected_events, input_events=()):
        if self.precompilation:
            evaluation, missing_events = self.precompilation.get_values_for(
                query_timestamps, expected_events, input_events
            )

            res = self._evaluation_to_prob(evaluation)

            if missing_events:
                input_events += Event.from_evaluation(res)

                res.update(
                    self.get_probabilities(existing_timestamps, query_timestamps, missing_events, input_events)
                )

            return res
        else:
            return self.get_probabilities(existing_timestamps, query_timestamps, expected_events, input_events)

    @staticmethod
    def read_model(m):
        if path.exists(m):
            with open(m) as f:
                return f.read()
        else:
            print('{} not found'.format(m), file=sys.stderr)
            return '\n'
