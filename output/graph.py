import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.animation import FFMpegFileWriter

from output.liveEventsOutupt import LiveEventsOutput


class Graph(LiveEventsOutput):
    def __init__(self, graph_x_size, tracked_ce, ce_threshold, save_graph_to=None, use_rectangles=True,
                 mark_threshold=False, legend_fontsize='medium', supress_drawing=False):
        self.graph_x_size = graph_x_size
        self.ce_threshold = ce_threshold
        self.use_rectangles = use_rectangles

        x = [0, graph_x_size]
        y = [0, 1]

        # You probably won't need this if you're embedding things in a tkinter plot...
        if supress_drawing:
            plt.ioff()
        else:
            plt.ion()

        self.fig = plt.figure(figsize=(16, 9))
        self.ax = self.fig.add_subplot(1, 1, 1)

        # self.fig.set_size_inches(16, 4.5, True)

        # Keeps track of which line and color is used for each complex event, to allow updating the lines and creating
        # rectangles of the same color (if the option is active)
        self.lines = {}
        self.colors = {}
        for event in tracked_ce:
            self.lines[event], = self.ax.plot(
                x, y, label=event, linewidth=3
            )  # Returns a tuple of line objects, thus the comma

            self.colors[event] = self.lines[event].get_color()

        if mark_threshold:
            plt.axhline(y=ce_threshold, color='r', linestyle='dashed')

        self.previous_x_data_length = {}

        self.last_rectangle = {}

        plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=legend_fontsize)
        plt.xlabel('Time (s)')
        plt.ylabel('Confidence')

        self.save_graph_to = save_graph_to
        if save_graph_to:
            self.graph_writer = FFMpegFileWriter(fps=1 / 0.96)  # VGGish splits audio into sections of 0.96s
            # self.graph_writer.setup(self.fig, save_graph_to, 100)
            self.graph_writer.setup(self.fig, save_graph_to)
        else:
            self.graph_writer = None

    def add_rectangle(self, event, x1, x2):
        return self.ax.add_patch(patches.Rectangle((x1, -1), x2 - x1, 3, color=self.colors[event], alpha=0.3))

    def mark_rectangle_until(self, event, x_data, i):
        if i > 0:
            last_rectangle = self.last_rectangle.get(event)
            if last_rectangle and last_rectangle.get_x() + last_rectangle.get_width() == x_data[i - 1]:
                last_rectangle.set_width(
                    last_rectangle.get_width() + (x_data[i] - x_data[i - 1])
                )
            else:
                self.last_rectangle[event] = self.add_rectangle(event, x_data[i - 1], x_data[i])

    def update_graph(self, evaluation):
        max_data = 0  # Will keep track of the highest value in the x-axis
        for event, line in self.lines.items():
            x_data, y_data = zip(*sorted(evaluation[event].items()))

            max_data = max(max(x_data), max_data)

            line.set_xdata(x_data)
            line.set_ydata(y_data)

            if self.use_rectangles:
                for i in range(self.previous_x_data_length.get(event, 0), len(x_data)):
                    if y_data[i] > self.ce_threshold:
                        self.mark_rectangle_until(event, x_data, i)

            self.previous_x_data_length[event] = len(x_data)

        # Find which range we want to show based on the data we have
        right = max(max_data, self.graph_x_size)
        left = right - self.graph_x_size

        # Increase the range by 10% on each side to make it less cramped
        left -= self.graph_x_size / 10
        right += self.graph_x_size / 10

        self.ax.set_xlim(left, right)

        return max_data

    def update(self, output_update):
        if 'new_parsed_evaluation' in output_update:
            self.update_graph(output_update['parsed_evaluation'])

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            if self.graph_writer:
                # for _ in range(8):
                self.graph_writer.grab_frame()

    def close(self):
        if self.graph_writer:
            self.graph_writer.finish()

    def finish_initialization(self):
        pass

    def terminate_output(self, *args, **kwargs):
        input('Press enter to finish')
        self.close()
