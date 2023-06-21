from datetime import datetime

from output.cogniSketch.cogniSketchOutput import CogniSketchOutput


class CogniSketchRedditOutput(CogniSketchOutput):
    def __init__(self, conf, tracked_ce, input_handler):
        super().__init__(conf, tracked_ce, input_handler)

    def prepare_user(self, user, timestamp, force_pending=True, hide=False):
        user_id = "{}user_{}".format(self.uid_start(), user)

        def create_user_json():
            return {
                **self.get_default_obj_json("user", timestamp, hide),
                "uid": user_id,
                "type": "user",
                "mode": "full",
                "data": {
                    "properties": {
                        "username": user
                    },
                    "label": ""
                }
            }

        self.create_with(
            uid=user_id,
            create_json_method=create_user_json,
            force_pending=force_pending
        )

        return user_id

    def prepare_comment(self, comment, timestamp, force_pending=True, hide=False):
        comment_id = "{}comment_{}".format(self.uid_start(), comment['post_id'])

        def create_comment_json():
            return {
                **self.get_default_obj_json("comment", timestamp, hide),
                "uid": comment_id,
                "type": "redditComment",
                "data": {
                    "properties": {
                        "text": comment['body'].replace('\n', '<br>'),
                        "score": str(comment['score']),
                        # "created_at": datetime.fromtimestamp(comment['created_utc']).strftime("%c"),
                        "created_at": datetime.fromtimestamp(comment['created_utc']).strftime("%d/%m/%Y %H:%M"),
                        # "created_at": datetime.fromtimestamp(comment['created_utc']).strftime("%d/%m/%Y"),
                        "subreddit": comment['subreddit'],
                        "total_awards_received": comment['total_awards_received']
                    },
                    "label": ""
                }
            }

        self.create_with(
            uid=comment_id,
            create_json_method=create_comment_json,
            force_pending=force_pending
        )

        return comment_id

    def update(self, output_update):
        if output_update.get('new_evaluation'):
            force_pending = bool(output_update.get('new_complex_events'))

            graph_id = None
            if self.graph:
                graph_id = self.prepare_graph(output_update, force_pending=force_pending)

            self.add_author_comment_and_events(output_update, force_pending=force_pending)

            new_complex_event_ids = self.add_complex_events(output_update, graph_id, force_pending=force_pending)

            self.add_explanations(new_complex_event_ids, output_update, force_pending=force_pending)

            if self.cogni_sketch_conf.get("send_on_update", False):
                if self.send_pending():  # Send pending. If any updates were sent, wait for user input
                    input("Press enter to continue")

    def add_author_comment_and_events(self, output_update, force_pending):
        for timestamp, comment in output_update['relevant_frames']:
            comment_event_ids, some_nlp_shown = self.add_simple_events(force_pending, output_update, timestamp)

            # user_id = self.prepare_user(comment['author'], timestamp, force_pending=force_pending)
            comment_id = self.prepare_comment(comment, timestamp, force_pending=force_pending, hide=not some_nlp_shown)

            # if force_pending:
            #     self.add_link(user_id, comment_id, "posts")

            for nlp_output_id in comment_event_ids:
                self.add_link(comment_id, nlp_output_id, "NLP detects", force_pending=force_pending)
