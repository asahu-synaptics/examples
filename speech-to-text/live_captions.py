#!/usr/bin/env python
"""Live captions from microphone using Moonshine and SileroVAD ONNX models."""

import argparse
import time
import numpy as np

from silero_vad import VADIterator, load_silero_vad
from moonshine import SpeechToText 
from utils.audio_manager import AudioManager

SAMPLING_RATE = 16000
CHUNK_SIZE = 512    
LOOKBACK_CHUNKS = 5
MAX_LINE_LENGTH = 80

MAX_SPEECH_SECS = 15
MIN_REFRESH_SECS = 0.5

def end_recording(speech, do_print=True):
    text = speech_to_text.transcribe(speech)
    if do_print:
        print_captions(text)
    caption_cache.append(text)
    speech *= 0.0

def print_captions(text):
    if len(text) < MAX_LINE_LENGTH:
        for caption in caption_cache[::-1]:
            text = caption + " " + text
            if len(text) > MAX_LINE_LENGTH:
                break
    if len(text) > MAX_LINE_LENGTH:
        text = text[-MAX_LINE_LENGTH:]
    else:
        text = " " * (MAX_LINE_LENGTH - len(text)) + text
    print("\r" + (" " * MAX_LINE_LENGTH) + "\r" + text, end="", flush=True)

def soft_reset(vad_iterator):
    vad_iterator.triggered = False
    vad_iterator.temp_end = 0
    vad_iterator.current_sample = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="live_captions",
        description="Live captioning demo of Moonshine models",
    )
    parser.add_argument(
        "--model_name",
        help="Model to run the demo with",
        default="moonshine/base",
        choices=["moonshine/base", "moonshine/tiny"],
    )
    args = parser.parse_args()
    model_name = args.model_name
    print(f"Loading Moonshine model '{model_name}' (using ONNX runtime) ...")
    
    # Create an instance of the new SpeechToText class.
    speech_to_text = SpeechToText(model_name=model_name, rate=SAMPLING_RATE)

    vad_model = load_silero_vad(onnx=True)
    vad_iterator = VADIterator(
        model=vad_model,
        sampling_rate=SAMPLING_RATE,
        threshold=0.5,
        min_silence_duration_ms=300,
    )

    # Set up the audio stream.
    audio_manager = AudioManager()
    audio_manager.start_record(chunk_size=CHUNK_SIZE)

    caption_cache = []
    lookback_size = LOOKBACK_CHUNKS * CHUNK_SIZE
    speech = np.empty(0, dtype=np.float32)
    recording = False

    print("Press Ctrl+C to quit live captions.\n")
    print_captions("Ready...")

    try:
        for chunk in audio_manager.read(chunk_size=CHUNK_SIZE):
            speech = np.concatenate((speech, chunk))
            if not recording:
                speech = speech[-lookback_size:]
            speech_dict = vad_iterator(chunk)
            if speech_dict:
                if "start" in speech_dict and not recording:
                    recording = True
                    start_time = time.time()
                if "end" in speech_dict and recording:
                    recording = False
                    end_recording(speech)
            elif recording:
                if (len(speech) / SAMPLING_RATE) > MAX_SPEECH_SECS:
                    recording = False
                    end_recording(speech)
                    soft_reset(vad_iterator)
                if (time.time() - start_time) > MIN_REFRESH_SECS:
                    print_captions(speech_to_text.transcribe(speech))
                    start_time = time.time()
    except KeyboardInterrupt:
        audio_manager.stop_record()
        if recording:
            end_recording(speech, do_print=False)
        print("\n")
        print(f"model_name          : {model_name}")
        print(f"MIN_REFRESH_SECS    : {MIN_REFRESH_SECS}s")
        print(f"number inferences   : {speech_to_text.number_inferences}")
        mean_inf_time = speech_to_text.inference_secs / speech_to_text.number_inferences
        print(f"mean inference time : {mean_inf_time:.2f}s")
        realtime_factor = speech_to_text.speech_secs / speech_to_text.inference_secs
        print(f"model realtime factor : {realtime_factor:0.2f}x")
        if caption_cache:
            print(f"Cached captions:\n{' '.join(caption_cache)}")
