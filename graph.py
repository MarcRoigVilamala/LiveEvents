import matplotlib.pyplot as plt
from matplotlib import patches


class Graph(object):
    def __init__(self, graph_x_size, expected_events):
        self.graph_x_size = graph_x_size

        x = [0, graph_x_size]
        y = [0, 1]

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.lines = {}
        self.colors = {}
        for event in expected_events:
            self.lines[event], = self.ax.plot(x, y, label=event)  # Returns a tuple of line objects, thus the comma

            self.colors[event] = self.lines[event].get_color()

        self.previous_x_data_length = 0

        self.last_rectangle = {}

        plt.legend()

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

            for i in range(self.previous_x_data_length, len(x_data)):
                if y_data[i] > 0.01:
                    self.mark_rectangle_until(event, x_data, i)

        self.previous_x_data_length = len(x_data)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
