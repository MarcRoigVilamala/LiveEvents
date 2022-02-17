# LiveEvents

This is a system designed to detect complex events from a given input feed.

Usage:

``python main.py [OPTIONS] EXPECTED_EVENTS EVENT_DEFINITION [VideoFeed|LiveAudioFeed|AudioFeed]``

Where:

`EXPECTED_EVENTS` is the path to a text file where each line specifies the name of one of the complex events we are expecting.

`EVENT_DEFINITION` is the path to a ProbLog file defining the rules for the complex events.

The feed type can be used to define what type of input feed should be used. This allows to choose between a video file, an audio file or live audio from the microphone. If an audio file is used, `--audio_file path/to/file` must be used to define which audio file should be processed. If a video file is used, `--video_name TEXT` should be used instead to indicate the name of the video file.

## Further options

Many more options can be used to add or change behaviours of the system.

### Adding further ProbLog files

Further ProbLog files can be added using the option `--add_to_model path/to/file`. This can be used to add the frameworks provided by the system, as well as any other file.

`--add_to_model PyProbEC/ProbLogFiles/prob_ec_cached.pl` can be used to allow event calculus inspired definitions of complex events.

`--add_to_model PyProbEC/ProbLogFiles/sequence.pl` can be used to add the sequence framework, which allows users to detect patterns from the given input feed.

### Adding event generators

The option `--add_event_generator [File3DResNet|FileAtLeast|FileOverlapping|ObjectDetector|Video|FromAudioNN|FromLiveAudioNN|DemoFromAudioNN]` can be used to add an event generator, which generates simple events from the given input feed. Different types of event generators can be used to generate different types of simple events.

At least one type of event generator is required.

### PreCompilation

`--precompile path/to/file` can be used to load a .json precompilation file. This can significantly increase the maximum speed of the system.

### Outputs

The following options control which outputs are used and their configurations.

`--ce_threshold FLOAT` can be used to define above which threshold of confidence we consider a complex event to be happening. This can be used to configure many of the following outputs.

#### Text

`--text` can be used to output all the values for all expected complex events.

`--clean_text` can be used to output a cleaner version, only showing the expected if their confidence is above the threshold value.

`--timings` can be used to output messages displaying the time efficiency of the approach at different points in the execution.

#### Graph

`--graph` can be used to generate a live graph showing the values of the different complex events.

`--save_graph_to path/to/file` can be used to save the graph as an MP4 file.

`--graph_x_size` can be used to configure the size of the X axis of the graph. If undefined, the system will try to use the appropriate size automatically.

#### Audio

`--audio` can be used to play a live audio as the system is detecting complex events. 

***NOTE:** The correct value for `--fps FLOAT` must be used to keep the audio and event detection in sync. By default, `--fps 1.042` should be used.*

#### Video

`--video` can be used to play a live video as the system is detecting complex events.

The video can be further configured with the following options:

````
  --object_mark                   If used, objects will be marked in the video
  --video_scale FLOAT             Scale of the video
  --video_x_position INTEGER      X position to spawn the video. Only if video
                                  is in use

  --video_y_position INTEGER      Y position to spawn the video. Only if video
                                  is in use
````

#### Connections

The following can be used to send messages to other applications:

````
  --address TEXT                  Specify if you want to send messages through
                                  ZeroMQ

  -p, --port INTEGER              Port to use for the ZeroMQ connection
  --sue_address TEXT              Specify if you want to send a message to SUE
````

### Logic inference configurations

These options allow the user to control how often the logic inference is performed, as well as which inputs it should get.

````
  -w, --max_window INTEGER        Maximum number of frames we want to remember
  --cep_frequency INTEGER         Frequency for calling the CEP code to
                                  generate new complex events

  -g, --group_size INTEGER        Number of frames considered to generate each
                                  simple event

  -f, --group_frequency INTEGER   Frequency with which we generate simple
                                  events
````

### Other options

These are other options that may be used that don't fall into any of the classifications above:

````
  -o, --interesting_objects FILE  File defining the list of objects we care
                                  about from the object detector output

  --fps FLOAT                     Number of frames that are processed every
                                  second. Controls the speed at which the 
                                  program processes the feed

  --loop_at INTEGER               If used, the video will loop at the given
                                  number until a button is pressed

  --button                        Use to create a button to stop the loop
  --post_message                  Use to allow a HTTP POST message to stop the
                                  loop
````

## Execution Examples

````
python main.py anomalyDetection/thesisAudio/expected_events.txt anomalyDetection/thesisAudio/event_defs.pl AudioFeed --add_to_model anomalyDetection/thesisAudio/prevTimestamp.pl --add_to_model PyProbEC/ProbLogFiles/prob_ec_cached.pl --add_to_model PyProbEC/ProbLogFiles/sequence.pl --add_event_generator FromAudioNN --audio_file /home/marc/thesis/audios/demo_audio_base.wav --fps 9999 --text --cep_frequency 1 --group_size 5 --group_frequency 1 --precompile anomalyDetection/thesisAudio/thesisAudio_precompile_args.json
````


````
python main.py anomalyDetection/expected_events.txt anomalyDetection/event_defs.pl VideoFeed --add_event_generator File3DResNet --add_event_generator FileAtLeast --add_event_generator FileOverlapping --add_to_model anomalyDetection/videoPrevTimestamp.pl --add_to_model PyProbEC/ProbLogFiles/prob_ec_cached.pl --add_to_model PyProbEC/ProbLogFiles/sequence.pl -o anomalyDetection/interesting_objects.txt --graph_x_size 500 --fps 99999 --video_name Fighting006_x264 --text --precompile anomalyDetection/full_precompile_args.json
````

<!---
``python main.py anomalyDetection/expected_events.txt anomalyDetection/event_defs.pl --graph_x_size 500 -o anomalyDetection/interesting_objects.txt --precompile anomalyDetection/full_precompile_args.json --text --graph --video --video_name Fighting006_x264 --loop_at 24 --post_message --address 127.0.0.1 -p 5556``
--->
