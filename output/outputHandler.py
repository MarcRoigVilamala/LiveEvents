from output.explanationTextOutput import ExplanationTextOutput
from output.newSimpleEventsText import NewSimpleEventsText
from output.text import Text
from output.cleanText import CleanText
from output.timings import Timings
from output.graph import Graph

from input.feed.fromJsonRedditFeed import FromJsonRedditFeed
from input.feed.fromPickleRedditFeed import FromPickleRedditFeed
from input.feed.fromPostRedditFeed import FromPostRedditFeed
from input.feed.audioFeed import AudioFeed

# If your output requires uncommon libraries, use local imports to avoid forcing them for unrelated functions


class OutputHandler(object):
    def __init__(self, input_handler, tracked_ce, conf):
        self.outputs = []

        if conf['output'].get('timings'):
            self.outputs.append(Timings())

        if conf['output'].get('text'):
            self.outputs.append(Text())

        if conf['output'].get('explanation'):
            self.outputs.append(ExplanationTextOutput(conf))

        if conf['output'].get('clean_text'):
            self.outputs.append(CleanText())

        if conf['output'].get('simple_events_text'):
            self.outputs.append(NewSimpleEventsText())

        graph_conf = conf['output'].get('graph')
        if graph_conf and (graph_conf.get('use_graph') or graph_conf.get('save_graph_to')):
            self.outputs.append(
                Graph(
                    graph_conf.get('graph_x_size') or input_handler.input_feed.get_max_length(),
                    tracked_ce,
                    conf['events']['ce_threshold'],
                    graph_conf.get('save_graph_to', False),
                    use_rectangles=False
                )
            )

        video_conf = conf['output'].get('video')
        if video_conf and video_conf.get('play_video'):
            from output.video import Video
            self.outputs.append(
                Video(
                    video_conf.get('video_x_position', 1000),
                    video_conf.get('video_y_position', 200),
                    video_conf.get('video_scale', 1.0),
                    conf['input']['video_name'],
                    video_conf.get('mark_objects', False)
                )
            )

        zmq_conf = conf['output'].get('zmq')
        if zmq_conf:
            from output.connection_output.zmqconnection import ZMQConnection
            self.outputs.append(ZMQConnection(zmq_conf['zmq_address'], zmq_conf['zmq_port']))

        if conf['output'].get('sue_address'):
            from output.sue import SUEConnection
            self.outputs.append(SUEConnection(conf['output']['sue_address']))

        if conf['output'].get('play_audio'):
            from output.audio import Audio
            assert isinstance(input_handler.input_feed, AudioFeed), "The input needs to be AudioFeed to play audio"

            self.outputs.append(Audio(input_handler.input_feed.audio_file))

        if conf['output'].get('cogni_sketch'):
            input_feed = input_handler.input_feed
            if isinstance(input_feed, (FromJsonRedditFeed, FromPickleRedditFeed, FromPostRedditFeed)):
                from output.cogniSketch.cogniSketchRedditOutput import CogniSketchRedditOutput
                self.outputs.append(CogniSketchRedditOutput(conf, tracked_ce, input_handler))
            else:
                raise ValueError("Cogni-Sketch does not support this input feed type: {}".format(type(input_feed)))

    def finish_initialization(self):
        for o in self.outputs:
            o.finish_initialization()

    def update(self, output_update):
        for o in self.outputs:
            o.update(output_update)

    def terminate_outputs(self, evaluation):
        for o in self.outputs:
            o.terminate_output(
                evaluation=evaluation
            )
