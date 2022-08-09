import tkinter as tk


def create_loop_button(video_input):
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    def com():
        video_input.stop_loop()
        # root.destroy()

    button = tk.Button(
        frame,
        text="Start Event",
        command=com
    )
    button.pack(side=tk.LEFT)

    root.mainloop()
