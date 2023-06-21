import os
import sys
from getpass import getpass
import requests
from datetime import datetime
from enum import Enum

from ProbCEP.explanation_utils import parse_explanation_list, simplify_explanations, extract_clauses_from
from input.eventGeneration.event import Event
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
        if prob <= label_prob:
            return label

    raise Exception('Probability {} is too high for given table'.format(prob))


TRANSLATE = {
    "ishate": "Hate Speech",
    "ceQuarantine=true": "Quarantine"
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
            self.password = getpass('Please enter the password for user "{}" in Cogni-Sketch: '.format(self.user))

        self.graph = Graph(
            input_handler.input_feed.get_max_length(),
            tracked_ce,
            ce_threshold=self.cogni_sketch_conf.get('graph_threshold', 0.9),
            save_graph_to=None,
            use_rectangles=False,
            mark_threshold=self.cogni_sketch_conf.get('mark_threshold', True),
            legend_fontsize=35,
            supress_drawing=True
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
        self.x_padding_by_object_type = self.cogni_sketch_conf.get("x_padding_by_object_type", {})
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

        self.max_explanations_per_ce = self.max_instances_per_timestamp['explanation'] // len(tracked_ce)
        self.min_explanation_threshold = self.cogni_sketch_conf.get("min_explanation_threshold", 0.0)
        self.hide_threshold = self.cogni_sketch_conf.get("hide_threshold", 0.33)

        self.tracked_simple_events = self.cogni_sketch_conf.get("tracked_simple_events", None)

        self.probability_to_words_table = self.cogni_sketch_conf.get(
            "probability_to_words_table", SIMPLE_PROBABILITY_TO_WORDS_TABLE
        )

        if "title" in self.cogni_sketch_conf:
            self.prepare_title(self.cogni_sketch_conf["title"])

        if "starting_image" in self.cogni_sketch_conf:
            self.prepare_image(self.cogni_sketch_conf["starting_image"])

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

        base = self.base_x_by_object_type.get(object_type, 0)

        change = self.x_change_by_object_type.get(object_type, 100)
        change_by_instances = change * timestamp * self.max_instances_per_timestamp.get(object_type, 0)

        padding = self.x_padding_by_object_type.get(object_type, 0)

        x = max(
            x,
            base + change_by_instances + padding * timestamp
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

    def prepare_title(self, title, timestamp=0, force_pending=True, hide=False):
        title_id = "{}title_{}".format(self.uid_start(), hash(title))

        def create_title_json():
            return {
                **self.get_default_obj_json("title", timestamp, hide),
                "uid": title_id,
                "type": "header",
                "data": {
                    "properties": {},
                    "label": title
                }
            }

        self.create_with(
            uid=title_id,
            create_json_method=create_title_json,
            force_pending=force_pending
        )

        return title_id

    def prepare_image(self, image_cs_path, timestamp=0, force_pending=True, hide=False):
        image_id = "{}image_{}".format(self.uid_start(), hash(image_cs_path))

        def create_image_json():
            return {
                **self.get_default_obj_json("image", timestamp, hide),
                "uid": image_id,
                "type": "image",
                "mode": "full",
                "data": {
                    "properties": {
                        "filename": {"type": "text", "value": image_cs_path}
                    }
                }
            }

        self.create_with(
            uid=image_id,
            create_json_method=create_image_json,
            force_pending=force_pending
        )

        return image_id

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

    def prepare_simple_event(self, event, force_pending=True, hide=False):
        event_id = "{}event_{}_{}".format(self.uid_start(), event.identifier, event.timestamp)

        def create_event_json():
            return {
                **self.get_default_obj_json("event", event.timestamp, hide),
                "uid": event_id,
                "type": "{}SimpleEvent".format(
                    probability_to_words(event.probability, self.probability_to_words_table)
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
                    probability_to_words(event.probability, self.probability_to_words_table)
                ),
                "data": {
                    "properties": {
                        "probability": event.probability,
                        "wep": probability_to_words(event.probability),
                    },
                    "label": "{}: {:.1f}%".format(
                        TRANSLATE.get(event.identifier, event.identifier.split("=")[0]),
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
                    probability_to_words(explanation[0], self.probability_to_words_table)
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

    def get_explanation_clause(self, clause):
        timestamp, event, event_type = Event.extract_values_from_clause(clause)

        if event_type.startswith('holdsAt'):
            return "{}complex_event_{}_{}".format(self.uid_start(), event.split('=')[0], timestamp)
        else:
            return "{}event_{}_{}".format(self.uid_start(), event, timestamp)

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

            # Apply bend depending on the angle of the link
            source_pos = self.cs_objects[source_id]['json']['pos']
            target_pos = self.cs_objects[target_id]['json']['pos']

            x_diff = target_pos['x'] - source_pos['x']
            y_diff = target_pos['y'] - source_pos['y']

            if y_diff == 0.0:
                bender = 0.0
            else:
                bender = -x_diff * 0.2 / y_diff

            self.cs_links[uid] = {
                "json": {
                    "uid": uid,
                    "selected": False,
                    "data": {
                        "properties": {},
                        "label": label
                    },
                    "anchorPos": 0.4,
                    "bender": bender,
                    "bidirectional": False,
                    "sourceRef": source_id,
                    "targetRef": target_id
                },
                "stage": CSObjStage.PENDING if force_pending else CSObjStage.STANDBY
            }

    def update(self, output_update):
        raise NotImplementedError("The update() method needs to be overwritten for every type of output")

    def add_simple_events(self, force_pending, output_update, timestamp):
        some_shown = False

        simple_event_ids = []
        for event in output_update['relevant_events']:
            if event.timestamp == timestamp and self.is_simple_event(event) and self.is_tracked_simple_event(event):
                hide = event.probability < self.hide_threshold

                some_shown = some_shown or not hide

                simple_event_id = self.prepare_simple_event(
                    event, force_pending=force_pending, hide=hide
                )

                simple_event_ids.append(simple_event_id)
        return simple_event_ids, some_shown

    def is_simple_event(self, event):
        return event.event_type != 'holdsAt_'

    def is_tracked_simple_event(self, event):
        if self.tracked_simple_events is None:
            return True

        return event.identifier in self.tracked_simple_events

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

                    shown_explanations, other_explanations = self.choose_shown_explanations(explanations)

                    n_explanations_added = self.add_shown_explanations(
                        ce_id, complex_event, shown_explanations, timestamp, force_pending
                    )

                    if other_explanations:
                        self.add_other_explanations(
                            ce_id, complex_event, other_explanations, timestamp, force_pending
                        )
                        n_explanations_added += 1

                    # If we have added fewer explanations than max_explanations_per_ce, call get_pos for the difference
                    # of times. This ensures that the explanations for each complex event always appear in the same
                    # position relative to their complex events (ideally centered below it).
                    # TODO: Implement a fix that allows for control of this without having to call get_pos directly. It
                    #  should work the same as having fewer simple events for one timestamp. Current code relies on
                    #  timestamps so it doesn't work when there are explanations for multiple complex events.
                    for i in range(n_explanations_added, self.max_explanations_per_ce):
                        self.get_pos("explanation", timestamp)

    def add_other_explanations(self, ce_id, complex_event, other_explanations, timestamp, force_pending):
        # Get the set of clauses for other explanations. Each element is an is_negated, clause pair
        other_explan_clauses = set(
            sum(
                map(
                    lambda x: extract_clauses_from(x[1]),
                    other_explanations
                ),
                []
            )
        )

        explan_id = self.prepare_other_explanation(
            complex_event, timestamp, other_explanations, force_pending=force_pending, hide=True
        )

        self.add_link(explan_id, ce_id, force_pending=force_pending)
        for is_negated, clause in other_explan_clauses:
            clause_id = self.get_explanation_clause(clause)

            self.add_link(clause_id, explan_id, "is part of", force_pending=force_pending)

    def add_shown_explanations(self, ce_id, complex_event, shown_explanations, timestamp, force_pending):
        n_explanations_added = 0
        for current_explan in shown_explanations:
            # If the probability of the current explanation is lower than self.min_explanation_threshold,
            # stop adding explanations as they don't contribute enough to be relevant
            if current_explan[0] < self.min_explanation_threshold:
                break

            explan_id = self.prepare_explanation(
                complex_event, timestamp, current_explan, force_pending=force_pending,
                hide=current_explan[0] < self.hide_threshold
            )
            n_explanations_added += 1

            self.add_link(explan_id, ce_id, "explains", force_pending=force_pending)

            for is_negated, clause in extract_clauses_from(current_explan[1]):
                clause_id = self.get_explanation_clause(clause)

                if CSObjStage.will_be_on_canvas(self.get_uid_stage(clause_id)):
                    self.add_link(clause_id, explan_id, "is part of", force_pending=force_pending)
                else:
                    # TODO: Decide what to do if one of the explanation clauses is not on the canvas
                    pass
        return n_explanations_added

    def choose_shown_explanations(self, explanations):
        shown_explanations = explanations[:self.max_explanations_per_ce - 1]
        other_explanations = explanations[self.max_explanations_per_ce - 1:]

        # Get the rest of the explanations that account for more than self.min_explanation_threshold
        # This is done to ignore explanations that contribute very minimally
        other_explanations = list(
            filter(
                lambda x: x[0] > self.min_explanation_threshold,
                other_explanations
            )
        )

        if len(other_explanations) == 1:
            # If there is only 1 additional explanation, show it directly
            shown_explanations += other_explanations
            other_explanations = []

        return shown_explanations, other_explanations

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
            for link in self.pending_links:
                if not CSObjStage.will_be_on_canvas(self.get_uid_stage(link['targetRef'])):
                    print("Missing targetRef: {}".format(link))
                if not CSObjStage.will_be_on_canvas(self.get_uid_stage(link['sourceRef'])):
                    print("Missing sourceRef: {}".format(link))

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

            return True

        return False

    def terminate_output(self, *args, **kwargs):
        self.send_pending()

        # if self.graph:
        #     self.graph.terminate_output(*args, **kwargs)
