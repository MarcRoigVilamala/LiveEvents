# LiveEvents

This system will attempt to read the video feed from a live camera input (or a pre-recorded video) and perform the necessary steps to automatically detect anomalies on the video.

``python main.py anomalyDetection/expected_events.txt anomalyDetection/event_defs.pl --graph_x_size 500 -o anomalyDetection/interesting_objects.txt --precompile anomalyDetection/full_precompile_args.json --text --graph --video --video_name Fighting006_x264 --loop_at 24 --post_message --address 127.0.0.1 -p 5556``
