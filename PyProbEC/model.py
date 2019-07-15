from __future__ import print_function

from problog.evaluator import SemiringSymbolic
from problog.program import PrologString
from problog import get_evaluatable

from os import path
import sys


# Files that define how EC works
from PyProbEC.precompilation import PreCompilation
from PyProbEC.utils import unsorted_groupby, term_to_list, get_values
from eventGeneration.event import Event

PROBLOG_FILES = [
    'PyProbEC/ProbLogFiles/prob_ec_cached.pl',
    'PyProbEC/ProbLogFiles/prob_utils_cached.pl',
]


class Model(object):
    def __init__(self, event_definition_files=(), precompile_arguments=None):
        # The base model will be formed from the base ProbLog files that define EC
        # and the files given by the user that should define the rules for the
        # complex event they are trying to detect
        models = [
            self.read_model(m)
            for m in PROBLOG_FILES + event_definition_files
        ]

        self.model = '\n\n'.join(models)

        if precompile_arguments:
            self.precompilation = PreCompilation(precompile_arguments, self.model)
        else:
            self.precompilation = None

    @staticmethod
    def _evaluation_to_prob(evaluation):
        # event -> ids -> timepoint -> prob
        return {
            event: {
                ids: {
                    timepoint: list(v3)[0][3]
                    for timepoint, v3 in unsorted_groupby(list(v2), key=lambda x: x[2])
                }
                for ids, v2 in unsorted_groupby(list(v1), key=lambda x: str(x[1]))
            }
            for event, v1 in unsorted_groupby(map(get_values, evaluation.items()), lambda x: x[0])
        }

    def get_timepoints(self):
        model = PrologString(self.model + '\n\nquery(allTimePoints(TPs)).')

        knowledge = get_evaluatable().create_from(model)

        timepoints = [
            term_to_list(term.args[0])
            for term in knowledge.evaluate().keys()
            if term.functor == 'allTimePoints'
        ]

        return sorted([item for sublist in timepoints for item in sublist])

    def get_values_for(self, existing_timepoints, query_timepoints, expected_events, input_events=()):
        # As the model we use self.model (basic EC definition + definition of rules by the user) and we add the list
        # of the input events
        string_model = self.model + '\n' + '\n'.join(map(lambda x: x.to_problog(), input_events))

        string_model += '\nallTimePoints([{}]).'.format(', '.join(map(str, existing_timepoints)))

        updated_knowledge = ''

        res = {}

        for timepoint in query_timepoints:
            for event in expected_events:
                query = 'query(holdsAt({event} = true, {timepoint})).\n'.format(event=event, timepoint=timepoint)

                model = PrologString(string_model + '\n' + updated_knowledge + '\n' + query)

                knowledge = get_evaluatable().create_from(model)

                evaluation = knowledge.evaluate()

                res.update(evaluation)

                for k, v in evaluation.items():
                    if v > 0.0:
                        updated_knowledge += '{0}::{1}.\n'.format(v, k).replace('holdsAt', 'holdsAt_')

        return res

    def get_probabilities(self, existing_timepoints, query_timepoints, expected_events, input_events=()):
        evaluation = self.get_values_for(
            existing_timepoints, query_timepoints, expected_events, input_events=input_events
        )

        return self._evaluation_to_prob(evaluation)

    def get_probabilities_precompile(self, existing_timepoints, query_timepoints, expected_events, input_events=()):
        if self.precompilation:
            evaluation, missing_events = self.precompilation.get_values_for(
                query_timepoints, expected_events, input_events
            )

            res = self._evaluation_to_prob(evaluation)

            if missing_events:
                input_events += Event.from_evaluation(res)

                res.update(
                    self.get_probabilities(existing_timepoints, query_timepoints, missing_events, input_events)
                )

            return res
        else:
            return self.get_probabilities(existing_timepoints, query_timepoints, expected_events, input_events)

    @staticmethod
    def read_model(m):
        if path.exists(m):
            with open(m) as f:
                return f.read()
        else:
            print('{} not found'.format(m), file=sys.stderr)
            return '\n'
