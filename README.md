# Examples
SyNAP demos, test applications and code snippets

## Current Examples
| Example | Description |
|---------|-------------|
| [Real-time Video Inference](video_inference) | Python demos to run real-time video inference via GStreamer on camera, file, or RTSP sources.

***

## Real-time Video Inference
> [!IMPORTANT]
> The firmware version on the SL1680 board must be >=1.0.0

### Running examples
Clone the examples repository and navigate to the `video_inference` folder.
All examples are located in the [`examples`](examples) sub-folder. There are specific examples for each supported input type (camera, file, RTSP) and a more generic example that's compatible with all supported inputs. To run an example:
```sh
python3 -m examples.<example>
```
#### Run options
The examples can also be run with optional input arguments. Here's a few examples:

##### 1. Camera demo with pre-loaded pose model
```sh
python3 -m examples.infer_camera \
-m /usr/share/synap/models/object_detection/body_pose/model/yolov8s-pose/model.synap
```

##### 2. Fullscreen video demo on a specific video file
```sh
python3 -m examples.infer_video \
-i /home/root/video.mp4 \
--fullscreen
```

##### 3. Generic demo with an input source, model and inference parameters
```sh
python3 -m examples.infer \
-i /home/root/video.mp4 \
-m /home/root/model.synap \
--input_codec h264 \
--confidence_threshold 0.85 \
--inference_skip 0
```

The full list of available input options for each demo can be viewed with `python3 -m examples.<example>.py --help`.

### Building demos from examples
The pyz_builder.py script allows you to package examples into self-contained, executable .pyz zip archives, which can be run using python3 <demo>.pyz. For step-by-step packaging instructions, see the [detailed guide on building demos](video_inference/README.md#building-demos-from-examples).

### Customizing and Extending Examples
To learn how to modify and expand these examples for your specific needs, check out the [customization and extension guide](video_inference/README.md#customizing-and-extending-examples).
