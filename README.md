# LiveEvents

This system will attempt to read the video feed from a live camera input (or a pre-recorded video) and perform the necessary steps to automatically detect anomalies on the video.

``python main.py -o anomalyDetection/interesting_objects.txt --precompile anomalyDetection/full_precompile_args.json anomalyDetection/expected_events.txt anomalyDetection/event_defs.pl --graph_x_size 500 --video_name Fighting006_x264 --video --graph``
