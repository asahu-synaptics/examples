import time
import numpy as np

from silero_vad import VADIterator, load_silero_vad
from moonshine import SpeechToText 
from utils.audio_manager import AudioManager

SAMPLING_RATE = 16000
CHUNK_SIZE = 512    
LOOKBACK_CHUNKS = 9
MAX_LINE_LENGTH = 80
MAX_SPEECH_SECS = 15
MIN_REFRESH_SECS = 0.2

class SpeechToTextPipeline:
    def __init__(self, model, handler):
        self.model = model
        self.handler = handler

        # Set up the speech-to-text and VAD models.
        self.speech_to_text = SpeechToText(model=model, rate=SAMPLING_RATE)
        self.vad_model = load_silero_vad(onnx=True)
        self.vad_iterator = VADIterator(
            model=self.vad_model,
            sampling_rate=SAMPLING_RATE,
            threshold=0.5,
            min_silence_duration_ms=500,
        )

        self.audio_manager = AudioManager()
        self.caption_cache = []
        self.lookback_size = LOOKBACK_CHUNKS * CHUNK_SIZE
        self.speech = np.empty(0, dtype=np.float32)
        self.recording = False

    def print_captions(self, text):
        if len(text) < MAX_LINE_LENGTH:
            for cap in self.caption_cache[::-1]:
                text = cap + " " + text
                if len(text) > MAX_LINE_LENGTH:
                    break
        if len(text) > MAX_LINE_LENGTH:
            text = text[-MAX_LINE_LENGTH:]
        print("\r" + (" " * MAX_LINE_LENGTH) + "\r" + text, end="", flush=True)

    def soft_reset(self):
        self.vad_iterator.triggered = False
        self.vad_iterator.temp_end = 0
        self.vad_iterator.current_sample = 0

    def end_recording(self, do_print=True):
        start_inference = time.time()
        text = self.speech_to_text.transcribe(self.speech)
        inference_time = time.time() - start_inference
        # if do_print:
        #     self.print_captions(text)
        # print("\n")
        self.handler(text, inference_time)
        self.speech *= 0.0

    def run(self):
        self.audio_manager.start_record(chunk_size=CHUNK_SIZE)
        print("Press Ctrl+C to quit live captions.\n")
        # self.print_captions("Ready...")
        start_time = time.time()

        # Flag to mark that end_recording should be called.
        call_end_recording = False

        for chunk in self.audio_manager.read(chunk_size=CHUNK_SIZE):
            # If we flagged end_recording last iteration, do it now.
            if call_end_recording:
                self.end_recording()
                call_end_recording = False

            # Append the current chunk.
            self.speech = np.concatenate((self.speech, chunk))
            if not self.recording:
                self.speech = self.speech[-self.lookback_size:]

            # Process the chunk through VAD.
            speech_dict = self.vad_iterator(chunk)

            if speech_dict:
                if "start" in speech_dict and not self.recording:
                    self.recording = True
                    start_time = time.time()
                if "end" in speech_dict and self.recording:
                    # Flag to call end_recording in the next iteration.
                    call_end_recording = True
                    self.recording = False
            elif self.recording:
                if (len(self.speech) / SAMPLING_RATE) > MAX_SPEECH_SECS:
                    call_end_recording = True
                    self.recording = False
                    self.soft_reset()
                elif (time.time() - start_time) > MIN_REFRESH_SECS:
                    # self.print_captions(self.speech_to_text.transcribe(self.speech))
                    start_time = time.time()


# Example usage:
def handle_results(text, inference_time):
    if text:
        print(f"\033[93mSTT: {text} \033[92m({inference_time*1000:.0f}ms)\033[0m")


pipe = SpeechToTextPipeline(
    model="tiny",
    handler=handle_results,
)

pipe.run()
