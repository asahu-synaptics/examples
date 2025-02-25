import sys
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class Embeddings:
    def __init__(self):
        self._download_model()
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_threads=4,
                n_ctx=128,
                n_batch=512,
                embedding=True
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)

    def _download_model(self):
        try:
            self.model_path = hf_hub_download(
                repo_id="second-state/All-MiniLM-L6-v2-Embedding-GGUF",
                filename="all-MiniLM-L6-v2-Q8_0.gguf",
            )
            print(f"Model downloaded to: {self.model_path}")
        except Exception as e:
            print(f"Error downloading model: {e}")
            sys.exit(1)

    def generate(self, text):
        try:
            embedding = self.llm.embed(text)
            if embedding is None:
                raise ValueError("No embedding returned")
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py \"text to embed\"")
        sys.exit(1)

    input_text = sys.argv[1]
    generator = Embeddings()
    embedding = generator.generate(input_text)
    print("Generated Embedding:", embedding)
