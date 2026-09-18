from transformers import pipeline

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

generator = pipeline("text-generation", model=MODEL_NAME, dtype="auto")


def generate_answer(query: str, contexts: list[str]) -> str:
    text = '\n\n'.join(contexts)

    prompt = f"""
Answer the question based on the following contexts.
Say "I don't know" if the answer is not contained in the contexts.

Contexts:{text}
Question: {query}
Answer:
"""
    
    output = generator(prompt, max_new_tokens=100)
    generated_text = output[0]['generated_text']
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):]
    
    return generated_text.strip()


if __name__ == "__main__":
    query = "What is the self-attention mechanism?"
    contexts = [
        "The self-attention mechanism allows a model to weigh the importance of different words in a sentence when encoding it. It computes attention scores for each word with respect to every other word, enabling the model to capture long-range dependencies and contextual relationships effectively."
    ]
    answer = generate_answer(query, contexts)
    print(answer)