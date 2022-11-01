import sys

from ProbCEP.explanation_utils import parse_explanation_list
from output.liveEventsOutupt import LiveEventsOutput


class ExplanationTextOutput(LiveEventsOutput):
    def __init__(self, conf):
        if conf['logic'].get('evaluatable') != 'kbest':
            print(
                "Explanations will only work when using 'kbest' as the evaluatable."
                "Use --evaluatable kbest to enable this",
                file=sys.stderr
            )

        self.ce_threshold = conf['events']['ce_threshold']
        # self.ce_threshold = 0.001

        self.explanation_threshold = 0.0

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if output_update.get('new_explanation') and output_update.get('new_parsed_evaluation'):
            explanations_dict = parse_explanation_list(output_update['new_explanation'])

            new_evaluation = output_update['new_parsed_evaluation']

            for complex_event, ce_values in explanations_dict.items():
                for timestamp, values in ce_values.items():
                    ce_prob = new_evaluation[complex_event][timestamp]

                    if ce_prob > self.ce_threshold:
                        print(
                            "{:.8f} :: holdsAt({}=true, {}) :- ".format(ce_prob, complex_event, timestamp)
                        )

                        values = sorted(values, reverse=True)

                        # Print the explanations that contribute more than explanation_threshold
                        i = 0
                        while i < len(values):
                            prob, causes = values[i]

                            if prob > self.explanation_threshold:
                                print("\t{:.8f} :: {}".format(prob, causes))
                                i += 1
                            else:
                                break

                        # Print the accumulation for all other explanations
                        other_probs = 0.0
                        while i < len(values):
                            other_probs += values[i][0]
                            i += 1

                        if other_probs > 0.0:
                            print("\t{:.5f} :: {}".format(other_probs, "Other"))

                        print()

    def terminate_output(self, evaluation, *args, **kwargs):
        pass
