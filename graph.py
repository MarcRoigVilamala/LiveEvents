import numpy as np
import matplotlib.pyplot as plt


class Graph(object):
    def __init__(self, graph_x_size, expected_events):
        self.graph_x_size = graph_x_size

        x = np.linspace(0, graph_x_size, graph_x_size)
        y = np.linspace(0, 1, graph_x_size)

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.lines = {}
        for event in expected_events:
            self.lines[event], = self.ax.plot(x, y, label=event)  # Returns a tuple of line objects, thus the comma

        plt.legend()

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

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


