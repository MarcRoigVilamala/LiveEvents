from output.text import Text
from output.cleanText import CleanText
from output.timings import Timings
from output.graph import Graph
# If your output requires uncommon libraries, use local imports to avoid forcing them for unrelated functions


class OutputHandler(object):
    def __init__(self, input_handler, tracked_ce, conf):
        self.outputs = []

        if conf['output'].get('timings'):
            self.outputs.append(Timings())

        if conf['output'].get('text'):
            self.outputs.append(Text())

        if conf['output'].get('clean_text'):
            self.outputs.append(CleanText())

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
            self.outputs.append(Audio(conf['input']['audio_file']))

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
