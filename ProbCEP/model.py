from __future__ import print_function

import json

from problog.evaluator import SemiringSymbolic
from problog.program import PrologString
from problog import get_evaluatable

from os import path
import sys


# Files that define how EC works
from ProbCEP.precompilation import EventPreCompilation, EventQuery
from ProbCEP.utils import unsorted_groupby, term_to_list, get_values, get_event_values
from input.eventGeneration.event import Event
from preCompilation.PreCompilation import PreCompilationArguments
import ProbCEP.mykbest


FRAMEWORK_LIBRARY = {
    'sequence': 'ProbCEP/ProbLogFiles/sequence.pl',
    'eventCalculus': 'ProbCEP/ProbLogFiles/prob_ec_cached.pl',
    'instantEventCalculus': 'ProbCEP/ProbLogFiles/instant_prob_ec_cached.pl'
}


def get_framework_files(frameworks):
    # Wil break if the framework is not the library
    return [
        FRAMEWORK_LIBRARY[f]
        for f in frameworks
    ]


class Model(object):
    def __init__(self, event_definition_files=(), precompile_arguments=None, evaluatable_name=None):
        # The base model will be formed from the base ProbLog files that define EC
        # and the files given by the user that should define the rules for the
        # complex event they are trying to detect
        models = [
            self.read_model(m)
            for m in event_definition_files
        ]

        self.model = '\n\n'.join(models)

        self.evaluatable = get_evaluatable(name=evaluatable_name)

        if precompile_arguments:
            self.precompilation = EventPreCompilation(
                precomp_args=precompile_arguments, model=self.model, evaluatable_name=evaluatable_name
            )
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

    def get_values_for(self, existing_timestamps, query_timestamps, tracked_ce, input_events=(), explanation=None):
        # As the model we use self.model (basic EC definition + definition of rules by the user) and we add the list
        # of the input events
        string_model = self.model + '\n' + '\n'.join(map(lambda x: x.to_problog(), input_events))

        string_model += '\nallTimeStamps([{}]).'.format(', '.join(map(str, existing_timestamps)))

        updated_knowledge = ''

        res = {}

        for timestamp in query_timestamps:
            for event in tracked_ce:
                query = 'query(holdsAt({event} = true, {timestamp})).\n'.format(event=event, timestamp=timestamp)

                model = PrologString(string_model + '\n' + updated_knowledge + '\n' + query)

                knowledge = self.evaluatable.create_from(model, label_all=True)

                evaluation = knowledge.evaluate(explain=explanation)

                # If the evaluation value is a tuple, use the average. Otherwise, (if it's a float) keep that
                evaluation = {
                    k: (v[0] + v[1]) / 2 if isinstance(v, tuple) and len(v) == 2 else v
                    for k, v in evaluation.items()
                }

                res.update(evaluation)

                for k, v in evaluation.items():
                    if v > 0.0:
                        updated_knowledge += '{0}::{1}.\n'.format(v, k).replace('holdsAt', 'holdsAt_')

        return res

    def get_probabilities(self, existing_timestamps, query_timestamps, tracked_ce, input_events=(), explanation=None):
        evaluation = self.get_values_for(
            existing_timestamps, query_timestamps, tracked_ce, input_events=input_events, explanation=explanation
        )

        # evaluation = self._evaluation_to_prob(evaluation)
        return evaluation

    def get_probabilities_precompile(self, existing_timestamps, query_timestamps, tracked_ce, input_events=(),
                                     explanation=None):
        if self.precompilation:
            evaluation, missing_events = self.precompilation.get_values_for(
                query_timestamps, tracked_ce, input_events, explanation
            )

            # evaluation = self._evaluation_to_prob(evaluation)

            if missing_events:
                input_events += Event.from_evaluation(evaluation)

                evaluation.update(
                    self.get_probabilities(
                        existing_timestamps, query_timestamps, missing_events, input_events, explanation
                    )
                )

            return evaluation
        else:
            return self.get_probabilities(
                existing_timestamps, query_timestamps, tracked_ce, input_events, explanation
            )

    @staticmethod
    def read_model(m):
        if path.exists(m):
            with open(m) as f:
                return f.read()
        else:
            print('\033[93m{} not found\033[0m'.format(m), file=sys.stderr)
            return '\n'


def generate_model(event_definitions, precompile, evaluatable_name=None):
    if precompile:
        with open(precompile, 'r') as f:
            json_precompile = json.load(f)

        precomp_args = PreCompilationArguments(
            input_clauses=[Event(**e) for e in json_precompile['input_clauses']],
            queries=[EventQuery(**q) for q in json_precompile['queries']]
        )

        return Model(event_definitions, precomp_args, evaluatable_name=evaluatable_name)
    else:
        return Model(event_definitions, evaluatable_name=evaluatable_name)
