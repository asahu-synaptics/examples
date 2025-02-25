import os
import sys
import hashlib
from huggingface_hub import hf_hub_download

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output/')

def download_model_files(onnx_file, json_file):
    """Download the model files from Hugging Face Hub."""
    onnx_model_path = hf_hub_download(
        repo_id="rhasspy/piper-voices", 
        filename=onnx_file
    )
    json_model_path = hf_hub_download(
        repo_id="rhasspy/piper-voices", 
        filename=json_file
    )
    return onnx_model_path, json_model_path

def file_checksum(content: str, hash_length: int = 16) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:hash_length]

def text_to_speech(answer, onnx_file="en/en_US/lessac/low/en_US-lessac-low.onnx", json_file="en/en_US/lessac/low/en_US-lessac-low.onnx.json", output_filename=None):
    """
    Convert text to speech and output a WAV file.
    """
    if output_filename is None:
        checksum = file_checksum(answer + onnx_file)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = os.path.join(OUTPUT_DIR, f"speech-output-{checksum}.wav")
    else:
        filename = output_filename

    if os.path.exists(filename):
        print(f"Found cached audio file: {filename}")
        return filename

    VOICE_MODEL_ONNX_FILE, _ = download_model_files(onnx_file, json_file)

    command = (
        f"echo \"{answer}\" | piper --model {VOICE_MODEL_ONNX_FILE} --output_file {filename}"
    )
    os.system(command)

    return filename

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py 'text to convert'")
        sys.exit(1)
    text = sys.argv[1]
    wav_path = text_to_speech(text)
    print(f"Audio written to: {wav_path}")
