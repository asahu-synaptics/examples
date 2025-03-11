"""Piper Text-to-Speech model using Piper command line tool."""

import os
import sys
import hashlib
from utils.models import download

class TextToSpeech:
    def __init__(self, onnx_file="en/en_US/lessac/low/en_US-lessac-low.onnx",
                       json_file="en/en_US/lessac/low/en_US-lessac-low.onnx.json",
                       output_dir="output"):
        self.onnx_file = download(repo_id="rhasspy/piper-voices", filename=onnx_file)
        self.json_file = download(repo_id="rhasspy/piper-voices", filename=json_file)
        self.output_dir = os.path.join(os.path.dirname(__file__), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def file_checksum(content: str, hash_length: int = 16) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:hash_length]

    def synthesize(self, text: str, output_filename: str = None) -> str:
        if output_filename is None:
            chk = self.file_checksum(text + self.onnx_file)
            output_filename = os.path.join(self.output_dir, f"speech-output-{chk}.wav")
        
        if os.path.exists(output_filename):
            return output_filename

        cmd = f'echo "{text}" | piper --model {self.onnx_file} --output_file {output_filename}'
        os.system(cmd)
        return output_filename

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py 'text to convert'")
        sys.exit(1)
    
    text = sys.argv[1]
    tts = TextToSpeech()
    wav_path = tts.synthesize(text)
    print(f"Audio written to: {wav_path}")

if __name__ == "__main__":
    main()
