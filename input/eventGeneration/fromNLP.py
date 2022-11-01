import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline

from input.eventGeneration.event import Event


os.environ["TOKENIZERS_PARALLELISM"] = "false"


class FromNLP(object):
    def __init__(self, model_name, ignore=()):
        # id2label = {int(k): v for k, v in id2label.items()}

        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.pipe = TextClassificationPipeline(
            model=model, tokenizer=tokenizer, return_all_scores=True, padding='max_length', truncation=True
        )

        self.ignore = set(ignore)

    def get_events(self, enumerated_frames):
        events = [
            Event(
                timestamp=t,
                event=pred['label'].lower().replace(' ', '_'),
                probability=pred['score'],
                event_type='nlp'
            )
            for t, v in enumerated_frames
            for instance in self.pipe(v['body'])
            # self.pipe() returns [[{'label': 'LABEL0', 'score': 0.1}, {'label': 'LABEL1', 'score': 0.9}], ...]
            for pred in instance
            if pred['label'].lower().replace(' ', '_') not in self.ignore
        ]

        return events
