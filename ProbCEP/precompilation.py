from problog.logic import Constant, Term
from preCompilation.PreCompilation import PreCompilation, Query
from ProbCEP.utils import get_values
from input.eventGeneration.event import Event


class EventPreCompilation(PreCompilation):
    def __init__(self, precomp_args, model):
        all_timestamps = {e.timestamp for e in precomp_args.input_clauses}
        all_timestamps = all_timestamps.union({q.timestamp for q in precomp_args.queries})

        model += '\nallTimeStamps([{}]).'.format(', '.join(map(str, sorted(list(all_timestamps)))))

        super(EventPreCompilation, self).__init__(precomp_args, model)

    def get_values_for(self, query_timestamps, tracked_ce, input_events=()):
        input_events = list(input_events)

        missing_events = set(tracked_ce) - set(self.precompilations.keys())

        # if missing_events:
        #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #     print(missing_events)
        #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        query_events = set(tracked_ce) - set(missing_events)

        queries = [
            EventQuery(identifier=event, timestamp=timestamp)
            for timestamp in query_timestamps
            for event in query_events
        ]

        res = self.perform_queries(queries, input_events, use_feedback=True)

        return res, missing_events


class EventQuery(Query):
    def generate_feedback(self, evaluation, timestamp_difference):
        return [
            Event(
                timestamp=t + timestamp_difference,
                event=event,
                probability=prob,
                event_type='holdsAt_'
            )
            for event, ids, t, prob in map(get_values, evaluation.items())
        ]

    def update_result_timestamp(self, result, timestamp_difference):
        return Term(result.functor, result.args[0], Constant(result.args[1].functor + timestamp_difference))

    def get_query_format(self):
        return '\nquery(holdsAt({identifier} = true, {timestamp})).'
