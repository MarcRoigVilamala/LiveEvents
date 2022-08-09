import threading

from input.endLoop.byButton import create_loop_button
from input.endLoop.byHTTP import create_http_reciever


def create_end_loop_triggers(input_feed, loop_at, button, post_message):
    if loop_at:
        if button:
            thread1 = threading.Thread(target=create_loop_button, args=(input_feed,))
            thread1.start()

        if post_message:
            thread2 = threading.Thread(target=create_http_reciever, args=(input_feed,))
            thread2.start()
