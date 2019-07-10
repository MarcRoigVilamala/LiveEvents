from problog import get_evaluatable
from problog.evaluator import SemiringSymbolic
from problog.logic import Constant, Term
from problog.program import PrologString

from PyProbEC.utils import get_values
from eventGeneration.event import Event


class PreCompilation(object):
    def __init__(self, precomp_args, model):
        self.precomp_input = [e.to_problog_with(probability=0.0) for e in precomp_args.input_events]

        model = model + '\n'.join(self.precomp_input)

        all_timepoints = {e.timestamp for e in precomp_args.input_events}
        all_timepoints = all_timepoints.union({q.timepoint for q in precomp_args.queries})

        model += '\nallTimePoints([{}]).'.format(', '.join(map(str, sorted(list(all_timepoints)))))

        self.precompilations = {}
        for query in precomp_args.queries:
            compiled_model = self._compile_model_with(model, query)

            nodes = {
                i: self._get_node_from_str(compiled_model, i.split('::')[1])
                for i in self.precomp_input
            }

            self.precompilations[query.event] = {
                'model': compiled_model,
                'nodes': nodes,
                'base_timepoint': query.timepoint
            }

    @staticmethod
    def _compile_model_with(model, query):
        prolog_string = PrologString(query.create_from_model(model))

        return get_evaluatable(name='ddnnf').create_from(prolog_string, semiring=SemiringSymbolic())

    def get_values_for(self, query_timepoints, expected_events, input_events=()):
        res = {}

        input_events = list(input_events)

        missing_events = set(expected_events) - set(self.precompilations.keys())

        # if missing_events:
        #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #     print(missing_events)
        #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        query_events = set(expected_events) - set(missing_events)

        for timepoint in query_timepoints:
            for event in query_events:
                precompilation = self.precompilations[event]

                timepoint_difference = timepoint - precompilation['base_timepoint']

                knowledge = precompilation['model']

                self._update_knowledge_with(knowledge, input_events, timepoint_difference, precompilation['nodes'])

                evaluation = knowledge.evaluate()

                # Fix the evaluation to have the correct output timestamps
                fixed_evaluation = {}
                for k, v in evaluation.items():
                    new_k = Term(k.functor, k.args[0], Constant(k.args[1].functor + timepoint_difference))

                    fixed_evaluation[new_k] = v

                res.update(fixed_evaluation)

                input_events += [
                    Event(
                        timestamp=t + timepoint_difference,
                        event=event,
                        probability=prob,
                        event_type='holdsAt_'
                    )
                    for event, ids, t, prob in map(get_values, evaluation.items())
                ]

        return res, missing_events

    def _update_knowledge_with(self, knowledge, input_events, timepoint_difference, nodes):
        marked_probabilities = [
            (
                e.to_problog_with(
                    timestamp=e.timestamp - timepoint_difference,
                    probability=0.0
                ),
                e.probability
            )
            for e in input_events
        ]

        for p in self.precomp_input:
            node = nodes[p]

            if node:
                probability = self._find_probability(marked_probabilities, p)

                if probability:
                    knowledge._weights[node] = Constant(probability)
                else:
                    knowledge._weights[node] = Constant(0.0)

    @staticmethod
    def _find_probability(marked_probabilities, precomp_input_event):
        for mark, probability in marked_probabilities:
            if precomp_input_event.replace(' ', '') == mark.replace(' ', ''):
                return probability

        return None

    @staticmethod
    def _get_node_from_str(knowledge, prolog_str):
        for name, node in knowledge._names['named'].items():
            if prolog_str[:-1].replace(' ', '') == str(name):
                return node

        return None


class PreCompilationArguments(object):
    def __init__(self, input_events, queries):
        self.input_events = input_events
        self.queries = queries


class Query(object):
    def __init__(self, event, timepoint):
        self.event = event
        self.timepoint = timepoint

    def create_from_model(self, model):
        return model + '\nquery(holdsAt({event} = true, {timepoint})).'.format(
            event=self.event,
            timepoint=self.timepoint
        )
