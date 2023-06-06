# LiveEvents

This is a system designed to detect complex events from a given input feed. It is designed to allow for the use of multiple types of input data, having been used for audio, text and video.

## Installation

You can download LiveEvents using the following command:

``git clone --recursive https://github.com/MarcRoigVilamala/LiveEvents.git``

Using the `--recursive` modifier ensures that the Cogni-Sketch repository is also downloaded (recommended). It can be omitted if you do not plan on using Cogni-Sketch as an output.

### Python Packages Installation

After cloning the repository into your system, enter the folder using:

``cd LiveEvents``

Then, you can install the required packages using:

``pip install -r requirements.txt``

**Note:** Some additional functionalities may require more packages. However, the packages included in `requirements.txt` are sufficient for running the example demos below.

### Cogni-Sketch Configuration

These steps are only required to allow the use of Cogni-Sketch as a possible output. They can be omitted otherwise.

To configure Cogni-Sketch, enter the folder using:

``cd cogni-sketch``

Then, follow the installation steps for Cogni-Sketch as detailed [here](https://github.com/dais-ita/cogni-sketch#installation). Note that you do not need to clone the Cogni-Sketch repository, as it has already been downloaded by using the `--recursive` argument above.

To allow LiveEvents to inject nodes into the Cogni-Sketch graph, the `checkForProposals` property to true (see [here](https://github.com/dais-ita/cogni-sketch#dynamic-injection-of-graph-changes-via-api) for more details on this functionality). To do this, you need to modify the file `cogni-sketch/public/javascripts/private/core/core_settings.js` on line 61, setting the property to true. It should look like this:

````
...
    // whether live checking for proposals is enabled (via polling in this version)
    "checkForProposals": true, // false,
...
````

#### Setup for AAMAS 2023 Demo

To prepare the Cogni-Sketch enviroment for the AAMAS 2023 demo, some additional steps are required.

You will need to set up the user who will own the canvas on Cogni-Sketch. You can follow the steps to create a user described [here](https://github.com/dais-ita/cogni-sketch#creating-users). The examples below assume that a user named `aamas` exists, so using the same name is recommended. You can choose any password you want. 

Once the `aamas` user has been created, you need to log into the user and create a new project named `liveEvents FP`. This will create a new canvas that LiveEvents will use to post new nodes. This can be done through the hamburger menu on the right of the drop down project selection menu in the Cogni-Sketch interface. 

Finally, you need to import the LiveEvents palette. This will add the node types that LiveEvents uses to generate the graph. This can be done through the hamburger menu on the right of the drop down palette menu in the Cogni-Sketch interface. Select the "Import Palette..." option and paste in the contents of the `cogni-sketch_palettes/liveEventsPalette.json` file. 

**Note:** If you wish to use a different username from `aamas`, use a different project name or change the password for the `admin` user you will need to update those details in the `confs/cogni-sketch/cogniSketchDemoFP_paper.json` file. If the password field is removed from the file the program will ask for the password every time the program is run. The configuration also assumes that Cogni-Sketch is running locally at `http://localhost:5010`. This can also be changed through the configuration file.

## Usage

You can run LiveEvents with the following command while inside the main `LiveEvents` folder:

``python main.py [OPTIONS]``

The easiest way to run the program is to use one of the pre-defined configurations. This can be done using `--conf path/to/file.json`. Some pre-deinfed configurations are provided in the [confs](confs) directory. This includes:

- A demonstration presented at AAMAS 2023 [Visualizing Logic Explanations for Social Media Moderation](https://www.southampton.ac.uk/~eg/AAMAS2023/pdfs/p3056.pdf). This demonstration observes a Reddit thread trying to detect if a community has concerning amounts of hate speech. The system also generates logic explanations for its predictions, making it easy for humans to detect *when* and *why* the system is wrong. 
  - The example shown in [this video](https://youtu.be/rXOWDYeJVMA) can be run using `python main.py --conf confs/cogni-sketch/cogniSketchDemoFP_paper.json`.
  - **Note:** this requires an instance of [Cogni-Sketch](https://github.com/dais-ita/cogni-sketch) to be running. Please ensure that all the configuration for Cogni-Sketch has been done acording to the details described above, or that the `confs/cogni-sketch/cogniSketchDemoFP_paper.json` has been updated accordingly.
- An example that detects concerning situations in an urban setting based on audio input. The examples shown in [this video](https://youtu.be/dllH0VzppPM) can be run using:
  - `--conf confs/audio/worryingSirenDemo_base_case.json` for the original version, where no threat is detected.
  - `--conf confs/audio/worryingSirenDemo.json` for the modified version, where gunshots have been edited into the audio file to generate a concerning situation.
  - `--conf confs/audio/safeEnvDemo.json` an additional version, which modifies the rules to generate an output that is easier to understand. This is done by grouping the "children playing" and "street music" classes into a single "safe environment" class. 

The values defined by the configuration files can be overwritten for the current execution by using the modifiers described in the following section.

## Modifiers

### Event definition

`--tracked_ce` Name of the complex event that needs to be tracked. Use multiple times to track multiple complex events.

`--event_definition`, `--add_to_model` Either of these can be used to add a ProbLog file to the model defining the rules for the complex events. Can be used multiple times to add multiple files.

`--use_framework [sequence|eventCalculus]` Can be used to make use of a framework in the rule definitions. Can be used multiple times to add multiple frameworks.

### Adding input feed types

`--input_feed_type [VideoFeed|LiveAudioFeed|AudioFeed]` can be used to add a feed type.

The feed type can be used to define what type of input feed should be used. This allows to choose between a video file, an audio file or live audio from the microphone. If an audio file is used, `--audio_file path/to/file` must be used to define which audio file should be processed. If a video file is used, `--video_name TEXT` should be used instead to indicate the name of the video file.

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
  --mark_objects                  If used, objects will be marked in the video
  --video_scale FLOAT             Scale of the video
  --video_x_position INTEGER      X position to spawn the video. Only if video
                                  is in use

  --video_y_position INTEGER      Y position to spawn the video. Only if video
                                  is in use
````

#### Connections

The following can be used to send messages to other applications:

````
  --zmq_address TEXT              Specify if you want to send messages through
                                  ZeroMQ

  -p, --zmq_port INTEGER          Port to use for the ZeroMQ connection
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



<!---
````
python main.py rules/worryingSirenDemo/all_events.txt rules/worryingSirenDemo/event_defs.pl AudioFeed --add_to_model rules/worryingSirenDemo/prevTimestamp.pl --add_to_model ProbCEP/ProbLogFiles/prob_ec_cached.pl --add_to_model ProbCEP/ProbLogFiles/sequence.pl --add_event_generator FromAudioNN --audio_file ~/thesis/audios/demo_audio_gunshots.wav --fps 9999 --text --cep_frequency 1 --group_size 1 --group_frequency 1 --precompile rules/worryingSirenDemo/worryingSiren_precompile_args.json --graph
````
>

<!---
````
python main.py anomalyDetection/expected_events.txt anomalyDetection/event_defs.pl VideoFeed --add_event_generator File3DResNet --add_event_generator FileAtLeast --add_event_generator FileOverlapping --add_to_model anomalyDetection/videoPrevTimestamp.pl --add_to_model PyProbEC/ProbLogFiles/prob_ec_cached.pl --add_to_model PyProbEC/ProbLogFiles/sequence.pl -o anomalyDetection/interesting_objects.txt --graph_x_size 500 --fps 99999 --video_name Fighting006_x264 --text --precompile anomalyDetection/full_precompile_args.json
````
>

<!---
``python main.py rules/expected_events.txt rules/event_defs.pl --graph_x_size 500 -o rules/interesting_objects.txt --precompile rules/full_precompile_args.json --text --graph --video --video_name Fighting006_x264 --loop_at 24 --post_message --address 127.0.0.1 -p 5556``
--->
