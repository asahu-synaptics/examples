import json
import os
import sys
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from embeddings.multilingual import Embeddings

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "qa_47.json")


class Agent:
    def __init__(self, qa_file=DEFAULT_PATH, load_embeddings=True, embedding_model="mykor"):
        self.embeddings = Embeddings(model_name=embedding_model)
        with open(qa_file, "r") as f:
            self.qa_pairs = json.load(f)
        self.question_embeddings = None
        if load_embeddings:
            self.question_embeddings = self.load_embeddings()

    def load_embeddings(self):
        texts = [pair["question"] + " " + pair["answer"] for pair in self.qa_pairs]
        embeddings = []
        for text in tqdm(texts, desc="Computing embeddings"):
            embeddings.append(self.embeddings.generate(text))
        return np.array(embeddings)

    def answer_query(self, query):
        # Use precomputed embeddings if available
        if self.question_embeddings is None:
            raise RuntimeError("Embeddings not loaded. Cannot answer query.")
        query_emb = self.embeddings.generate(query)
        sims = cosine_similarity([query_emb], self.question_embeddings).flatten()
        best_idx = np.argmax(sims)
        return {
            "answer": self.qa_pairs[best_idx]["answer"],
            "similarity": float(sims[best_idx]),
        }

    def evaluate_qa_pairs(self):
        """
        For each Q&A pair, use the question as input and the answer as response,
        compute similarity between the question embedding and the embedding of the
        concatenated question+answer (as used in training).
        Returns a list of dicts: [{"question": ..., "answer": ..., "similarity": ...}, ...]
        """
        results = []
        for idx, pair in enumerate(tqdm(self.qa_pairs, desc="Evaluating QA pairs")):
            question = pair["question"]
            answer = pair["answer"]
            # Embedding for the question as query
            query_emb = self.embeddings.generate(question)
            # Embedding for the (question+answer) as in the dataset
            ref_emb = self.question_embeddings[idx]
            sim = cosine_similarity([query_emb], [ref_emb]).flatten()[0]
            results.append({
                "question": question,
                "answer": answer,
                "similarity": float(sim),
            })
        return results

    def evaluate_questions(self, questions_file):
        """
        For each question in the given questions_file (JSON list of {"question": ...}),
        get the answer from the model and similarity.
        Returns a list of dicts: [{"question": ..., "predicted_answer": ..., "similarity": ...}, ...]
        """
        if self.question_embeddings is None:
            raise RuntimeError("Embeddings not loaded. Cannot evaluate questions.")
        with open(questions_file, "r", encoding="utf-8") as f:
            questions = json.load(f)
        results = []
        for q in tqdm(questions, desc="Evaluating questions"):
            question = q["question"]
            result = self.answer_query(question)
            results.append({
                "question": question,
                "predicted_answer": result["answer"],
                "similarity": f"{result['similarity']:.2f}",
            })
        return results


if __name__ == "__main__":
    # Parse CLI arguments
    args = sys.argv[1:]
    eval_table = False
    eval_ques = False
    qa_file = DEFAULT_PATH
    questions_file = None
    embedding_model = "mykor"

    # Support --qa-file <path> param
    if "--qa-file" in args:
        idx = args.index("--qa-file")
        if len(args) > idx + 1:
            qa_file = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]
        else:
            qa_file = DEFAULT_PATH

    # Support -emb <model> param (mykor or granite)
    if "-emb" in args:
        idx = args.index("-emb")
        if len(args) > idx + 1:
            embedding_model = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]
        else:
            print("Error: -emb flag provided but no model specified.")
            sys.exit(1)

    if "--eval-table" in args:
        eval_table = True
        args = [a for a in args if a != "--eval-table"]
    if "--eval-ques" in args:
        eval_ques = True
        idx = args.index("--eval-ques")
        # If a file is provided after --eval-ques, use it
        if len(args) > idx + 1:
            questions_file = args[idx + 1]
        args = [a for a in args if a != "--eval-ques"]
        if questions_file:
            args.remove(questions_file)
    if len(args) > 0:
        qa_file = args[0]

    agent = None

    if eval_table:
        print(f"Creating embeddings from QA: {qa_file}")
        agent = Agent(qa_file=qa_file, load_embeddings=True, embedding_model=embedding_model)
        results = agent.evaluate_qa_pairs()
        # Add similarity to each original pair and write to JSON
        output_data = []
        for orig, res in zip(agent.qa_pairs, results):
            entry = dict(orig)
            entry["similarity"] = f"{res['similarity']:.2f}"
            output_data.append(entry)
        output_path = os.path.join(os.path.dirname(qa_file), "qa_pairs_jp_with_similarity.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        # Print average similarity
        avg_sim = sum(res['similarity'] for res in results) / len(results)
        print(f"Similarity table written to {output_path}")
        print(f"Average similarity: {avg_sim:.4f}")
        sys.exit(0)

    if eval_ques:
        agent = Agent(qa_file=qa_file, load_embeddings=True, embedding_model=embedding_model)
        if questions_file:
            results = agent.evaluate_questions(questions_file)
            output_path = os.path.join(os.path.dirname(questions_file), "questions_with_predicted_answers.json")
        else:
            # Use all questions from qa_file if it's not a questions file
            with open(qa_file, "r", encoding="utf-8") as f:
                qa_data = json.load(f)
            questions = [{"question": pair["question"]} for pair in qa_data]
            temp_questions_path = os.path.join(os.path.dirname(qa_file), "temp_eval_questions.json")
            with open(temp_questions_path, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            results = agent.evaluate_questions(temp_questions_path)
            output_path = os.path.join(os.path.dirname(qa_file), "qa_questions_with_predicted_answers.json")
            os.remove(temp_questions_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        # Print average similarity
        avg_sim = sum(float(res['similarity']) for res in results) / len(results) if results else 0.0
        print(f"Question evaluation written to {output_path}")
        print(f"Average similarity: {avg_sim:.4f}")
        sys.exit(0)

    YELLOW = "\033[93m"
    RESET = "\033[0m"
    print(YELLOW + "Assistant ready. Type your question (or 'exit' to quit):" + RESET)
    while True:
        query = input(YELLOW + "> " + RESET)
        if query.lower() in ("exit", "quit"):
            break
        result = agent.answer_query(query)
        print(YELLOW + "Answer: " + result["answer"] + RESET)
        print(YELLOW + "Similarity: " + str(result["similarity"]) + RESET)
