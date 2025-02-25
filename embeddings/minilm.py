import subprocess
import json
import sys
from huggingface_hub import hf_hub_download
import os

class Embeddings:
    def __init__(self):
        self._download_model()

    def _download_model(self):
        try:
            self.model_path = hf_hub_download(
                repo_id="second-state/All-MiniLM-L6-v2-Embedding-GGUF",
                filename="all-MiniLM-L6-v2-Q8_0.gguf",
            )
            print(f"Model downloaded to: {self.model_path}")
        except Exception as e:
            print(f"Error downloading model: {e}")
            exit(1)

    def generate(self, text):
        try:
            llama_bin_path = os.path.join('llama-embedding')
            command = [
                llama_bin_path,
                '-m', self.model_path,
                '-p', text,
                '--ctx-size', '128',
                '--batch-size', '512',
                '--embd-output-format', 'json',
                '-t', '4'
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                print("Error: Llama-embedding command failed.")
                print("Return code:", result.returncode)
                print("Error output:", result.stderr)
                raise RuntimeError(f"Llama-embedding command failed\n{command}")

            if not result.stdout:
                print("Error: No output from llama-embedding command.")
                raise ValueError("No output from llama-embedding")

            embedding_data = json.loads(result.stdout)
            embedding = embedding_data.get('data', [{}])[0].get('embedding')

            if embedding is None:
                print("Error: Embedding data is missing in the output.")
                raise ValueError("No embedding data found")

            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py \"text to embed\"")
        exit(1)

    input_text = sys.argv[1]
    generator = Embeddings()
    embedding = generator.generate(input_text)
    print("Generated Embedding:", embedding)
