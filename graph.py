import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.animation import FFMpegFileWriter


class Graph(object):
    def __init__(self, graph_x_size, expected_events, ce_threshold, save_graph_to=None, use_rectangles=True):
        self.graph_x_size = graph_x_size
        self.ce_threshold = ce_threshold
        self.use_rectangles = use_rectangles

        x = [0, graph_x_size]
        y = [0, 1]

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()

        self.fig = plt.figure(figsize=(16, 9))
        self.ax = self.fig.add_subplot(1, 1, 1)

        # Keeps track of which line and color is used for each complex event, to allow updating the lines and creating
        # rectangles of the same color (if the option is active)
        self.lines = {}
        self.colors = {}
        for event in expected_events:
            self.lines[event], = self.ax.plot(x, y, label=event)  # Returns a tuple of line objects, thus the comma

            self.colors[event] = self.lines[event].get_color()

        self.previous_x_data_length = 0

        self.last_rectangle = {}

        plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3)
        plt.xlabel('Time (s)')
        plt.ylabel('Confidence')

        if save_graph_to:
            self.graph_writer = FFMpegFileWriter(fps=1)
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

    def update(self, evaluation):
        # We can get the x_data from just one of the lines since they should all be the same
        x_data = sorted(evaluation[list(self.lines.keys())[0]]['()'].keys())

        # Find which range we want to show based on the data we have
        max_data = x_data[-1]
        right = max(max_data, self.graph_x_size)
        left = right - self.graph_x_size

        # Increase the range by 10% on each side to make it less cramped
        left -= self.graph_x_size / 10
        right += self.graph_x_size / 10

        self.ax.set_xlim(left, right)

        for event, line in self.lines.items():
            y_data = [evaluation[event]['()'][k] for k in x_data]

            line.set_xdata(x_data)
            line.set_ydata(y_data)

            if self.use_rectangles:
                for i in range(self.previous_x_data_length, len(x_data)):
                    if y_data[i] > self.ce_threshold:
                        self.mark_rectangle_until(event, x_data, i)

        self.previous_x_data_length = len(x_data)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        if self.graph_writer:
            # for _ in range(8):
            self.graph_writer.grab_frame()

    def close(self):
        if self.graph_writer:
            self.graph_writer.finish()
