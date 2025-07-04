# Assistant Text QA Evaluation - Usage Guide

This guide explains how to use `text.py` for evaluating question-answer pairs and question retrieval using multilingual embeddings.

## 1. Basic Usage

Run interactively (default model, default QA file):

```sh
python3 -m assistant.text
```

You can then type your question and get the most relevant answer.

---

## 2. Evaluate QA Pairs (`--eval-table`)

Compute similarity scores for all Q&A pairs in a JSON file.

**Default (uses default QA file and model):**
```sh
python3 -m assistant.text --eval-table
```

**Specify a QA file:**
```sh
python3 -m assistant.text --eval-table --qa-file path/to/qa_file.json
```

**Specify embedding model (`mykor` or `granite`):**
```sh
python3 -m assistant.text --eval-table --qa-file path/to/qa_file.json -emb granite
```

- Output: `qa_pairs_jp_with_similarity.json` (in the same directory as your QA file)
- Prints the average similarity score.

---

## 3. Evaluate Questions (`--eval-ques`)

Answer a list of questions using the QA dataset as the knowledge base.

**Use all questions from the QA file:**
```sh
python3 -m assistant.text --eval-ques --qa-file path/to/qa_file.json
```

**Use a separate questions file (JSON list of {"question": ...}):**
```sh
python3 -m assistant.text --eval-ques path/to/questions.json --qa-file path/to/qa_file.json
```

**Specify embedding model:**
```sh
python3 -m assistant.text --eval-ques path/to/questions.json --qa-file path/to/qa_file.json -emb granite
```

- Output: `questions_with_predicted_answers.json` (or `qa_questions_with_predicted_answers.json` if using all questions from the QA file)
- Prints the average similarity score.

---

## 4. Embedding Model Options

- `mykor` (default): Uses the MiniLM-based multilingual embedding model.
- `granite`: Uses the Granite multilingual embedding model.

Specify with `-emb`:
```sh
python3 -m assistant.text --eval-table -emb granite
```

---

## 5. Arguments Summary

- `--eval-table` : Evaluate all QA pairs for similarity.
- `--eval-ques [questions.json]` : Evaluate questions (optionally specify a questions file).
- `--qa-file path/to/qa_file.json` : Specify the QA dataset file.
- `-emb [mykor|granite]` : Choose the embedding model.

---

## 6. Example Commands

**Evaluate QA pairs with granite model:**
```sh
python3 -m assistant.text --eval-table --qa-file assistant/data/qa_47.json -emb granite
```

**Evaluate questions from a file with default model:**
```sh
python3 -m assistant.text --eval-ques assistant/data/questions.json --qa-file assistant/data/qa_47.json
```

**Interactive mode with granite model:**
```sh
python3 -m assistant.text -emb granite
```

---

## 7. Notes

- The first time you use a model, it will be downloaded automatically from Hugging Face.
- Output files are saved in the same directory as the input QA or questions file.
- For custom question evaluation, provide a JSON file with a list of objects: `[{"question": "..."}, ...]`
