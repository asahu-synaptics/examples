# Synaptics Astra SL16xx series AI examples

## Setup Python Environment

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

## Object detection
```bash
python3 -m vision.object_detection 'cam'
```

## Speech-to-text

Moonshine is an edge AI targetted speech-to-text model with Whisper-like Word Error Rate (WER). To transcribe the `jfk.wav`

```bash
python3 -m speech_to_text.moonshine  'samples/jfk.wav'
```

To run live captions with a USB microphones attached (hint: a webcam has a microphone):

```bash
python3 -m speech_to_text.pipeline
```

## Text-to-speech

```bash
python3 -m text_to_speech.piper "synaptics astra example"
```

## Install llama-cpp-python

Install sqlite3
```bash
wget https://synaptics-astra-labs.s3.us-east-1.amazonaws.com/downloads/sqlite3_3.38.5-r0_arm64.deb
wget https://synaptics-astra-labs.s3.us-east-1.amazonaws.com/downloads/python3-sqlite3_3.10.13-r0_arm64.deb
dpkg -i python3-sqlite3_3.10.13-r0_arm64.deb sqlite3_3.38.5-r0_arm64.deb
```
Install `llama-cpp-python`
```
pip install -r llama-cpp-python
```

## Embeddings
```bash
python3 -m embeddings.minilm "synaptics astra example!"
```

## Text Assistant
```bash
python3 -m assistant.text
```

## LLMs

```bash
python3 -m llm.qwen
python3 -m llm.deepseek
```
