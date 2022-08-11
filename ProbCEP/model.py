from __future__ import print_function

import json

from problog.evaluator import SemiringSymbolic
from problog.program import PrologString
from problog import get_evaluatable

from os import path
import sys


# Files that define how EC works
from ProbCEP.precompilation import EventPreCompilation, EventQuery
from ProbCEP.utils import unsorted_groupby, term_to_list, get_values
from input.eventGeneration.event import Event
from preCompilation.PreCompilation import PreCompilationArguments


FRAMEWORK_LIBRARY = {
    'sequence': 'ProbCEP/ProbLogFiles/sequence.pl',
    'eventCalculus': 'ProbCEP/ProbLogFiles/prob_ec_cached.pl'
}


def get_framework_files(frameworks):
    # Wil break if the framework is not the library
    return [
        FRAMEWORK_LIBRARY[f]
        for f in frameworks
    ]


class Model(object):
    def __init__(self, event_definition_files=(), precompile_arguments=None):
        # The base model will be formed from the base ProbLog files that define EC
        # and the files given by the user that should define the rules for the
        # complex event they are trying to detect
        models = [
            self.read_model(m)
            for m in event_definition_files
        ]

        self.model = '\n\n'.join(models)

        if precompile_arguments:
            self.precompilation = EventPreCompilation(precompile_arguments, self.model)
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

        knowledge = get_evaluatable().create_from(model)

        timestamps = [
            term_to_list(term.args[0])
            for term in knowledge.evaluate().keys()
            if term.functor == 'allTimeStamps'
        ]

        return sorted([item for sublist in timestamps for item in sublist])

    def get_values_for(self, existing_timestamps, query_timestamps, tracked_ce, input_events=()):
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

                knowledge = get_evaluatable().create_from(model, semiring=SemiringSymbolic())

                evaluation = knowledge.evaluate()

                res.update(evaluation)

                for k, v in evaluation.items():
                    if v > 0.0:
                        updated_knowledge += '{0}::{1}.\n'.format(v, k).replace('holdsAt', 'holdsAt_')

        return res

    def get_probabilities(self, existing_timestamps, query_timestamps, tracked_ce, input_events=()):
        evaluation = self.get_values_for(
            existing_timestamps, query_timestamps, tracked_ce, input_events=input_events
        )

        return self._evaluation_to_prob(evaluation)

    def get_probabilities_precompile(self, existing_timestamps, query_timestamps, tracked_ce, input_events=()):
        if self.precompilation:
            evaluation, missing_events = self.precompilation.get_values_for(
                query_timestamps, tracked_ce, input_events
            )

            res = self._evaluation_to_prob(evaluation)

            if missing_events:
                input_events += Event.from_evaluation(res)

                res.update(
                    self.get_probabilities(existing_timestamps, query_timestamps, missing_events, input_events)
                )

            return res
        else:
            return self.get_probabilities(existing_timestamps, query_timestamps, tracked_ce, input_events)

    @staticmethod
    def read_model(m):
        if path.exists(m):
            with open(m) as f:
                return f.read()
        else:
            print('\033[93m{} not found\033[0m'.format(m), file=sys.stderr)
            return '\n'


def generate_model(event_definitions, precompile):
    if precompile:
        with open(precompile, 'r') as f:
            json_precompile = json.load(f)

        precomp_args = PreCompilationArguments(
            input_clauses=[Event(**e) for e in json_precompile['input_clauses']],
            queries=[EventQuery(**q) for q in json_precompile['queries']]
        )

        return Model(event_definitions, precomp_args)
    else:
        return Model(event_definitions)


def update_evaluation(evaluation, new_evaluation):
    for event, event_val in new_evaluation.items():
        if event in evaluation:
            for ids, ids_val in event_val.items():
                if ids in evaluation[event]:
                    for timestamp, prob in ids_val.items():
                        evaluation[event][ids][timestamp] = prob
                else:
                    evaluation[event][ids] = ids_val
        else:
            evaluation[event] = event_val

    return evaluation
