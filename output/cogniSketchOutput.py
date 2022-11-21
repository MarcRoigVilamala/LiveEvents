import os
import sys
from getpass import getpass
import requests
from datetime import datetime
from enum import Enum

from ProbCEP.explanation_utils import parse_explanation_list, simplify_explanations, extract_clauses_from
from output.graph import Graph
from output.liveEventsOutupt import LiveEventsOutput


PROBABILITY_TO_WORDS_TABLE = [
    (0.01, "Exceptionally unlikely"),  # 0.0 to 0.01
    (0.1, "Very unlikely"),            # 0.01 to 0.1
    (0.33, "Unlikely"),                # 0.1 to 0.33
    (0.66, "About as likely as not"),  # 0.33 to 0.66
    (0.9, "Likely"),                   # 0.66 to 0.9
    (0.99, "Very unlikely"),           # 0.9 to 0.99
    (1.0, "Virtually certain"),        # 0.99 to 1.0
]

SIMPLE_PROBABILITY_TO_WORDS_TABLE = [
    (0.33, "unlikely"),  # 0.00 to 0.33
    (0.66, "medium"),    # 0.33 to 0.66
    (1.00, "likely")     # 0.66 to 1.00
]


def probability_to_words(prob, using_table=None):
    if using_table is None:
        using_table = PROBABILITY_TO_WORDS_TABLE

    for label_prob, label in using_table:
        if prob < label_prob:
            return label

    raise Exception('Probability {} is too high for given table'.format(prob))


TRANSLATE = {
    "ishate": "Hate Speech",
    "ceBan=true": "Quarantine"
}


class CSObjStage(Enum):
    NOT_CREATED = 0  # The json has not yet been created
    STANDBY = 1  # The json has been created but should not be posted (unless it is required later)
    PENDING = 2  # The json has been created and is pending posting (to be sent when send_pending is called)
    POSTED = 3  # The json has been created and posted to Cogni-Sketch

    @staticmethod
    def will_be_on_canvas(o):
        return o == CSObjStage.PENDING or o == CSObjStage.POSTED


class CogniSketchOutput(LiveEventsOutput):
    def __init__(self, conf, tracked_ce, input_handler):
        self.execution_id = int(datetime.now().timestamp())  # Use the start timestamp as the execution_id

        self.cogni_sketch_conf = conf['output']['cogni_sketch']

        self.proposal_url = '{url}/project/propose/{project}?owner={owner}'.format(
            url=self.cogni_sketch_conf['url'],
            project=self.cogni_sketch_conf['project'],
            owner=self.cogni_sketch_conf['project_owner']
        )

        self.threshold = conf['events']['ce_threshold']

        self.user = self.cogni_sketch_conf['user']
        self.password = self.cogni_sketch_conf.get('password')
        if self.password is None:
            self.password = getpass('Please enter your Cogni-Sketch password: ')

        self.graph = Graph(
            input_handler.input_feed.get_max_length(),
            tracked_ce,
            ce_threshold=self.cogni_sketch_conf.get('graph_threshold', 0.9),
            save_graph_to=None,
            use_rectangles=False,
            mark_threshold=True
        )

        self.cs_objects = {}
        self.cs_links = {}

        self.use_simplified_explanations = self.cogni_sketch_conf.get('use_simplified_explanations', False)

        self.base_x_by_object_type = self.cogni_sketch_conf.get(
            "base_x_by_object_type",
            {
                "user": 225,
                "comment": 225,
                # "event": 0,
                "event": 225,
                "explanation": 0,
                "complex_event": 225,
                "graph": 225
            }
        )
        self.x_by_object_type = dict(self.base_x_by_object_type)
        self.y_by_object_type = self.cogni_sketch_conf.get(
            "y_by_object_type",
            {
                "user": 750,
                "comment": 450,
                "event": 250,
                "explanation": 0,
                "complex_event": -250,
                "graph": -600
            }
        )
        self.x_change_by_object_type = self.cogni_sketch_conf.get(
            "x_change_by_object_type",
            {
                "user": 600,
                "comment": 600,
                "event": 75,
                # "event": 600,
                "explanation": 150,
                "complex_event": 600,
                "graph": 600,
            }
        )
        self.max_instances_per_timestamp = self.cogni_sketch_conf.get(
            "max_instances_per_timestamp",
            {
                "user": 1,
                "comment": 1,
                # "event": 4,
                "event": 1,
                "explanation": 4,
                "complex_event": 1,
                "graph": 1,
            }
        )

        self.max_explanations = self.max_instances_per_timestamp['explanation']
        self.min_explanation_threshold = self.cogni_sketch_conf.get("min_explanation_threshold", 0.0)
        self.hide_threshold = self.cogni_sketch_conf.get("hide_threshold", 0.33)

    @staticmethod
    def get_at_stage(from_dict: dict, stage: CSObjStage):
        res = []

        for v in from_dict.values():
            if v['stage'] == stage:
                res.append(v['json'])

        return res

    def get_cs_objects_at_stage(self, stage: CSObjStage):
        return self.get_at_stage(self.cs_objects, stage)

    def get_cs_objects_uids_at_stage(self, stage: CSObjStage):
        res = []

        for uid, v in self.cs_objects.items():
            if v['stage'] == stage:
                res.append(uid)

        return res

    def get_cs_links_at_stage(self, stage: CSObjStage):
        return self.get_at_stage(self.cs_links, stage)

    @property
    def cs_objects_uids(self):
        return self.cs_objects.keys()

    @property
    def standby_objects(self):
        return self.get_cs_objects_at_stage(CSObjStage.STANDBY)

    @property
    def pending_objects(self):
        return self.get_cs_objects_at_stage(CSObjStage.PENDING)

    @property
    def posted_objects(self):
        return self.get_cs_objects_at_stage(CSObjStage.POSTED)

    @property
    def standby_objects_uids(self):
        return self.get_cs_objects_uids_at_stage(CSObjStage.STANDBY)

    @property
    def pending_objects_uids(self):
        return self.get_cs_objects_uids_at_stage(CSObjStage.PENDING)

    @property
    def posted_objects_uids(self):
        return self.get_cs_objects_uids_at_stage(CSObjStage.POSTED)

    @property
    def pending_links(self):
        return self.get_cs_links_at_stage(CSObjStage.PENDING)

    @property
    def standby_links(self):
        return self.get_cs_links_at_stage(CSObjStage.STANDBY)

    def get_uid_stage(self, uid):
        if uid in self.cs_objects:
            return self.cs_objects[uid]['stage']
        else:
            return CSObjStage.NOT_CREATED

    def set_uid_stage(self, uid, stage: CSObjStage):
        self.cs_objects[uid]['stage'] = stage

    def set_link_stage(self, link_uid, stage: CSObjStage):
        self.cs_links[link_uid]['stage'] = stage

    def uid_start(self):
        return "liveEvents_{}_".format(self.execution_id)  # Use execution_id to create different nodes each execution

    def finish_initialization(self):
        pass

    def get_pos(self, object_type, timestamp):
        self.x_by_object_type.setdefault(object_type, 0)
        self.y_by_object_type.setdefault(object_type, 0)

        x = self.x_by_object_type[object_type]
        y = self.y_by_object_type[object_type]

        change = self.x_change_by_object_type.get(object_type, 100)

        if object_type in self.max_instances_per_timestamp:
            base = self.base_x_by_object_type.get(object_type, 0)
            x = max(
                x,
                base + change * timestamp * self.max_instances_per_timestamp[object_type]
            )

        res = {"x": x, "y": y}

        self.x_by_object_type[object_type] = x + change

        return res

    def get_default_obj_json(self, object_type, timestamp, hide):
        return {
            "mode": "full",
            "expanded": 1,
            "selected": False,
            "showType": False,
            "hide": hide,
            # "hide": False,
            "pos": self.get_pos(object_type, timestamp),
            "linkRefs": [],
            "data": {}
        }

    def prepare_graph(self, output_update, force_pending=True, hide=False):
        latest_timestamp = self.graph.update_graph(output_update["parsed_evaluation"])

        graph_id = "{}graph_{}".format(self.uid_start(), latest_timestamp)

        def create_graph_json():
            project = self.cogni_sketch_conf['project']
            image_filename = 'ce_graph_at_{}.png'.format(latest_timestamp)
            directory_filepath = '{base_path}/{project_owner}/{project}/images'.format(
                base_path=self.cogni_sketch_conf['save_images_to'],
                project_owner=self.cogni_sketch_conf['project_owner'],
                project=project
            )
            graph_filepath = '{directory}/{image_filename}'.format(
                directory=directory_filepath,
                image_filename=image_filename
            )

            if os.path.exists(graph_filepath):
                os.remove(graph_filepath)
            elif not os.path.exists(directory_filepath):
                os.makedirs(directory_filepath)

            self.graph.fig.savefig(graph_filepath)

            graph_cs_path = f'./image/{project}/{image_filename}'

            return {
                **self.get_default_obj_json("graph", latest_timestamp, hide),
                "uid": graph_id,
                "type": "image",
                "mode": "full",
                "data": {
                    "properties": {
                        "filename": {"type": "text", "value": graph_cs_path}
                    }
                }
            }

        self.create_with(
            uid=graph_id,
            create_json_method=create_graph_json,
            force_pending=force_pending
        )

        return graph_id

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
                        "created_at": datetime.fromtimestamp(comment['created_utc']).strftime("%c"),
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

    def prepare_nlp_output(self, event, force_pending=True, hide=False):
        event_id = "{}event_{}_{}".format(self.uid_start(), event.identifier, event.timestamp)

        def create_event_json():
            return {
                **self.get_default_obj_json("event", event.timestamp, hide),
                "uid": event_id,
                "type": "{}SimpleEvent".format(
                    probability_to_words(event.probability, SIMPLE_PROBABILITY_TO_WORDS_TABLE)
                ),
                "data": {
                    "properties": {
                        "probability": event.probability,
                        "wep": probability_to_words(event.probability),
                    },
                    "label": "{}: {:.1f}%".format(
                        TRANSLATE.get(event.identifier, event.identifier),
                        event.probability * 100
                    )
                }
            }

        self.create_with(
            uid=event_id,
            create_json_method=create_event_json,
            force_pending=force_pending
        )

        return event_id

    def prepare_complex_event(self, event, force_pending=True, hide=False):
        event_id = "{}complex_event_{}_{}".format(
            self.uid_start(), str(event.identifier).split('=')[0], event.timestamp
        )

        def create_complex_event_json():
            return {
                **self.get_default_obj_json("complex_event", event.timestamp, hide),
                "uid": event_id,
                "type": "{}ComplexEvent".format(
                    probability_to_words(event.probability, SIMPLE_PROBABILITY_TO_WORDS_TABLE)
                ),
                "data": {
                    "properties": {
                        "probability": event.probability,
                        "wep": probability_to_words(event.probability),
                    },
                    "label": "{}: {:.1f}%".format(
                        TRANSLATE.get(event.identifier, event.identifier),
                        event.probability * 100
                    )
                }
            }

        self.create_with(
            uid=event_id,
            create_json_method=create_complex_event_json,
            force_pending=force_pending
        )

        return event_id

    def prepare_explanation(self, complex_event, timestamp, explanation, force_pending=True, hide=False):
        explanation_id = "{}explanation_{}_{}_{}".format(
            self.uid_start(), complex_event, timestamp, hash(explanation[1])
        )

        def create_explanation_json():
            return {
                **self.get_default_obj_json("explanation", timestamp, hide),
                "uid": explanation_id,
                "type": "{}Explanation".format(
                    probability_to_words(explanation[0], SIMPLE_PROBABILITY_TO_WORDS_TABLE)
                ),
                "data": {
                    "properties": {
                        "probability": explanation[0],
                        "explanation": explanation[1],
                        "wep": probability_to_words(explanation[0]),
                    },
                    "label": "{:.1f}%".format(explanation[0] * 100)
                }
            }

        self.create_with(
            uid=explanation_id,
            create_json_method=create_explanation_json,
            force_pending=force_pending
        )

        return explanation_id

    def prepare_other_explanation(self, complex_event, timestamp, other_explan, force_pending=True, hide=False):
        # other_explan_prob = sum(map(lambda x: x[0], other_explan))

        explanation_id = "{}explanation_{}_{}_{}".format(
            self.uid_start(), complex_event, timestamp, hash(str(other_explan))
        )

        def create_other_explanation_json():
            return {
                **self.get_default_obj_json("explanation", timestamp, hide),
                "uid": explanation_id,
                "type": "unlikelyExplanation",
                "data": {
                    "properties": {
                        "details": other_explan
                    },
                    # "label": str(other_explan_prob)
                    "label": "Other"
                }
            }

        self.create_with(
            uid=explanation_id,
            create_json_method=create_other_explanation_json,
            force_pending=force_pending
        )

        return explanation_id

    def get_explanation_clause(self, clause, force_pending=True):
        if clause.startswith('holdsAt'):
            identifier, timestamp = clause.split('(')[1].split(',')

            timestamp = timestamp[:-1]  # Remove the ")" at the end

            return "{}complex_event_{}_{}".format(self.uid_start(), identifier.split('=')[0], timestamp)
            # return None
        elif clause.startswith('nlp'):
            timestamp, identifier = clause.split('(')[1].split(',')

            identifier = identifier[:-1]  # Remove the ")" at the end

            return "{}event_{}_{}".format(self.uid_start(), identifier, timestamp)
        else:
            raise ValueError('Unknown explanation clause: {}'.format(clause))

    def create_with(self, uid, create_json_method, force_pending=False):
        stage = self.get_uid_stage(uid)

        if stage == CSObjStage.NOT_CREATED:
            self.add_object(  # Create the object if it has not yet been created
                uid,
                create_json_method(),
                force_pending=force_pending
            )
        elif stage == CSObjStage.STANDBY:
            if force_pending:  # If force pending is true, set stage to pending
                self.set_uid_stage(uid, CSObjStage.PENDING)
            # Otherwise, nothing needs to be done, as the json has already been created
        elif stage == CSObjStage.PENDING:
            pass  # The json has already been created and is pending, so nothing needs to be done
        elif stage == CSObjStage.POSTED:
            pass  # The json has already been posted, so nothing needs to be done

    def add_object(self, uid, new_object, force_pending=False):
        self.cs_objects[uid] = {
            "json": new_object,
            "stage": CSObjStage.PENDING if force_pending else CSObjStage.STANDBY
        }

    def add_link(self, source_id, target_id, label="", force_pending=False):
        if source_id not in self.cs_objects_uids:
            print("Link source not found", file=sys.stderr)
        elif target_id not in self.cs_objects_uids:
            print("Link target not found", file=sys.stderr)
        else:
            uid = "link_{}_{}".format(source_id, target_id)

            self.cs_links[uid] = {
                "json": {
                    "uid": uid,
                    "selected": False,
                    "data": {
                        "properties": {},
                        "label": label
                    },
                    "anchorPos": 0.5,
                    "bender": 0,
                    "bidirectional": False,
                    "sourceRef": source_id,
                    "targetRef": target_id
                },
                "stage": CSObjStage.PENDING if force_pending else CSObjStage.STANDBY
            }

    def update(self, output_update):
        if output_update.get('new_evaluation'):
            force_pending = bool(output_update.get('new_complex_events'))

            graph_id = None
            if self.graph:
                graph_id = self.prepare_graph(output_update, force_pending=force_pending)

            self.add_author_comment_and_events(output_update, force_pending=force_pending)

            new_complex_event_ids = self.add_complex_events(output_update, graph_id, force_pending=force_pending)

            self.add_explanations(new_complex_event_ids, output_update, force_pending=force_pending)

            # self.send_pending()

    def add_author_comment_and_events(self, output_update, force_pending):
        for timestamp, comment in output_update['relevant_frames']:
            comment_event_ids, some_nlp_shown = self.add_nlp_outputs(force_pending, output_update, timestamp)

            # user_id = self.prepare_user(comment['author'], timestamp, force_pending=force_pending)
            comment_id = self.prepare_comment(comment, timestamp, force_pending=force_pending, hide=not some_nlp_shown)

            # if force_pending:
            #     self.add_link(user_id, comment_id, "posts")

            for nlp_output_id in comment_event_ids:
                self.add_link(comment_id, nlp_output_id, "NLP detects", force_pending=force_pending)

    def add_nlp_outputs(self, force_pending, output_update, timestamp):
        some_shown = False

        comment_event_ids = []
        for event in output_update['relevant_events']:
            if event.timestamp == timestamp and event.event_type == 'nlp':
                hide = event.probability < self.hide_threshold

                some_shown = some_shown or not hide

                nlp_output_id = self.prepare_nlp_output(
                    event, force_pending=force_pending, hide=hide
                )

                comment_event_ids.append(nlp_output_id)
        return comment_event_ids, some_shown

    def add_complex_events(self, output_update, graph_id, force_pending):
        new_complex_event_ids = []
        for complex_event in output_update['new_events']:
            new_ce_id = self.prepare_complex_event(
                complex_event, force_pending=force_pending, hide=complex_event.probability < self.hide_threshold
            )

            new_complex_event_ids.append(new_ce_id)

            self.add_link(new_ce_id, graph_id, force_pending=force_pending)

        return new_complex_event_ids

    def add_explanations(self, new_complex_event_ids, output_update, force_pending):
        probabilities_by_clause = {}
        for e in output_update['relevant_events']:
            prob, clause = str(e).strip().split("::")
            probabilities_by_clause[clause[:-1].replace(', ', ',')] = float(prob)

        for complex_event, values in parse_explanation_list(output_update['new_explanation']).items():
            for timestamp, explanations in values.items():
                tmp_explanations = explanations

                ce_id = "{}complex_event_{}_{}".format(self.uid_start(), complex_event, timestamp)

                if ce_id in new_complex_event_ids:
                    if self.use_simplified_explanations:
                        explanations = simplify_explanations(
                            explanations,
                            probabilities_by_clause=probabilities_by_clause,
                            max_clauses=8
                        )

                    for current_explan in explanations[:self.max_explanations - 1]:
                        # If the probability of the current explanation is lower than self.min_explanation_threshold,
                        # stop adding explanations as they don't contribute enough to be relevant
                        if current_explan[0] < self.min_explanation_threshold:
                            break

                        explan_id = self.prepare_explanation(
                            complex_event, timestamp, current_explan, force_pending=force_pending,
                            hide=current_explan[0] < self.hide_threshold
                        )

                        self.add_link(explan_id, ce_id, "explains", force_pending=force_pending)

                        for is_negated, clause in extract_clauses_from(current_explan[1]):
                            clause_id = self.get_explanation_clause(clause)

                            self.add_link(clause_id, explan_id, "is part of", force_pending=force_pending)

                    # Get the rest of the explanations that account for more than self.min_explanation_threshold
                    # This is done to ignore explanations that contribute very minimally
                    other_explan = list(
                        filter(
                            lambda x: x[0] > self.min_explanation_threshold,
                            explanations[self.max_explanations - 1:]
                        )
                    )
                    if other_explan:
                        # Get the set of clauses for other explanations. Each element is an is_negated, clause pair
                        other_explan_clauses = set(
                            sum(
                                map(
                                    lambda x: extract_clauses_from(x[1]),
                                    other_explan
                                ),
                                []
                            )
                        )

                        explan_id = self.prepare_other_explanation(
                            complex_event, timestamp, other_explan, force_pending=force_pending, hide=True
                        )

                        self.add_link(explan_id, ce_id, force_pending=force_pending)

                        for is_negated, clause in other_explan_clauses:
                            clause_id = self.get_explanation_clause(clause)

                            self.add_link(clause_id, explan_id, "is part of", force_pending=force_pending)

    def update_pending_links(self):
        # For all the standby links, if both the source and target are going to be in the canvas, set them to pending

        for link in self.standby_links:
            source = self.cs_objects.get(link['sourceRef'])
            if source and CSObjStage.will_be_on_canvas(source['stage']):
                target = self.cs_objects.get(link['targetRef'])
                if target and CSObjStage.will_be_on_canvas(target['stage']):
                    # If both the source and target will be on the canvas after this posting, set the link to pending
                    self.set_link_stage(link['uid'], CSObjStage.PENDING)

    def send_pending(self):
        self.update_pending_links()

        if self.pending_links or self.pending_objects:
            requests.post(
                self.proposal_url,
                json={
                    "objects": self.pending_objects,
                    "links": self.pending_links
                },
                auth=(self.user, self.password)
            )

            for link in self.pending_links:
                self.set_link_stage(link['uid'], CSObjStage.POSTED)

            for cs_uid in self.pending_objects_uids:
                self.set_uid_stage(cs_uid, CSObjStage.POSTED)

    def terminate_output(self, *args, **kwargs):
        self.send_pending()

        # if self.graph:
        #     self.graph.terminate_output(*args, **kwargs)
