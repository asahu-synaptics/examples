# Sending SyNAP Inference Results over UDP

This is a very simple GStreamer application to send inference results from a Synaptics gstreamer pipeline over UDP.

> [!WARNING]
> The app sends results over UDP as available. No synchronization has been implemented yet.

## Building

1. [Setup and activate the SL1680 toolchain](https://synaptics-astra.github.io/doc/v/1.2.0/yocto.html#how-to-develop-an-application)
2. Clone this repository and navigate to the `gst-udp-app` folder
3. Make the build directory:
```bash
mkdir -p build
cd build
meson setup .. --wipe
```
4. Build `gst-udp`:
```bash
ninja
```
5. Transfer the `gst-udp` executable (located at `build/src/gst-udp`) to the board at `/usr/bin/gst-udp`

## Usage
To run, provide parameters via command line, or a JSON file, or a mix of both:
```sh
gst-udp -a <IP address> -p <port> -i <input source> -m "path/to/model.synap" [-f "/path/to/params.json"]
```
The the following parameters are accepted:
|parameter|type|definition|
|---------|----|----------|
|`ipaddress`|string|IP address of the target device|
|`port`|number|Port to use on the target device|
|`input`|string|The video input source: can be a camera device, file, or RTSP stream|
|`model`|string|Path to a valid .synap model|
|`confidence`|number|The confidence level for detections|
|`skipframes`|number|Number of frames to skip between each inference|
|`postprocmode`|string|Inference mode: must be either "classifier" or "detector"|

<br> `ipaddress` (`-a`) and `port` (`-p`) must be provided via the commandline but the other parameters can be specified via a JSON file:
```sh
gst-udp -a <IP address> -p <port> -f "/path/to/params.json"
```
Here's what a sample `params.json` might look like:
```json
{
    "input": "/dev/video3",
    "model": "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap",
    "confidence": 0.8,
    "skipframes": 1,
    "postprocmode": "detector"
}
```
For more details, including the defaults for some of these parameters, run `gst-udp -h`.

## Utilities
See the [utils](utils) directory for useful scripts to use with `gst-udp`.
