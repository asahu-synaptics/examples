# Synaptics Astra AI examples

In the following tutorials, we will run NPU-accelerated AI inference on Synaptics Astra using the `SynapRT` Python package.

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

# Speech-to-text

We'll be using Moonshine - an edge AI targetted speech-to-text model with Whisper-like Word Error Rate (WER).

```bash
pip install -r speech-to-text/requirements.txt
```

To transcribe the `jfk.wav`

```bash
python3 speech-to-text/transcribe.py  'samples/jfk.wav'
```

To run live captions with a USB microphones attached (hint: a webcam has a microphone):

```bash
python3 speech-to-text/live_captions.py
```





