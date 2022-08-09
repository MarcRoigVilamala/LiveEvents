import time

from output.liveEventsOutupt import LiveEventsOutput


class Timings(LiveEventsOutput):
    def __init__(self):
        self.start_time = time.time()
        self.finish_initialization = None
        self.end_time = None

    def finish_initialization(self):
        self.finish_initialization = time.time()
        print("Initalization: {}".format(self.finish_initialization - self.start_time))

    def update(self, output_update):
        pass

    def terminate_output(self, evaluation, *args, **kwargs):
        self.end_time = time.time()

        loop_time = self.end_time - self.finish_initialization
        print("Loop time: {}".format(loop_time))
        print("Average time ({} iterations): {}".format(iteration_num, loop_time / iteration_num))
        print("Iterations per second: {}".format(iteration_num / loop_time))
        print("Total time: {}".format(self.end_time - self.start_time))
