# Synaptics Astra AI examples

In the following tutorials, we will run NPU-accelerated AI inference on Synaptics Astra using the `SynapRT` Python package.

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

# Speech-to-text

We'll be using Moonshine - an edge AI targetted speech-to-text model with Whisper-like Word Error Rate (WER).

```bash
pip install -r speech_to_text/requirements.txt
```

To transcribe the `jfk.wav`

```bash
python3 -m speech_to_text.moonshine  'samples/jfk.wav'
```

To run live captions with a USB microphones attached (hint: a webcam has a microphone):

```bash
python3 -m speech_to_text.pipeline
```

# Text-to-speech

```bash
python3 -m text_to_speech.piper "synaptics astra example"
```


# Embeddings

```
python3 -m embeddings.minilm "synaptics astra example!"
```

## Install llama-embedding
```
http://192.168.50.67/downloads/llama-embedding
chmod u+x llama-embedding 
```

## Voice Assistant

```
python3 -m voice_assistant.main
```
