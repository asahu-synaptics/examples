import sys
from llama_cpp import Llama
from utils.models import download


class Embeddings:
    def __init__(self, model_name="mykor"):
        if model_name == "granite":
            self.model_path = download(
                repo_id="bartowski/granite-embedding-107m-multilingual-GGUF",
                filename="granite-embedding-107m-multilingual-Q8_0.gguf",
            )
        else:
            self.model_path = download(
                repo_id="mykor/paraphrase-multilingual-MiniLM-L12-v2.gguf",
                filename="paraphrase-multilingual-MiniLM-L12-118M-v2-Q8_0.gguf",
            )

        self.llm = Llama(
            model_path=self.model_path,
            n_threads=4,
            n_ctx=128,
            n_batch=512,
            embedding=True,
            verbose=False,  # Set verbose to False to keep llm quiet
        )

    def generate(self, text):
        try:
            embedding = self.llm.embed(text)
            if embedding is None:
                raise ValueError("No embedding returned")
            return embedding
        except Exception as e:
            print("Error generating embedding:", e)
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Usage: python script.py "text to embed" [-emb granite]')
        sys.exit(1)

    input_text = sys.argv[1]
    model_name = "mykor"
    if len(sys.argv) == 4 and sys.argv[2] == "-emb":
        model_name = sys.argv[3]
    generator = Embeddings(model_name=model_name)
    embedding = generator.generate(input_text)
    print("Generated Embedding:", embedding)
