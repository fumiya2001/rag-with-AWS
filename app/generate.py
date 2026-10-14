from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
MODEL_NAME = "gpt-4o-mini"  

def generate_answer(query: str, contexts: list[str]) -> str:
    text = '\n\n'.join(contexts)

    prompt = f"""
Answer the question based on the following contexts.
Say "I don't know" if the answer is not contained in the contexts.

Contexts:{text}
Question: {query}
Answer:
"""
    
    output = client.responses.create(model=MODEL_NAME, input=prompt)
    
    return output.output_text.strip()


if __name__ == "__main__":
    query = "What is the self-attention mechanism?"
    contexts = [
        "The self-attention mechanism allows a model to weigh the importance of different words in a sentence when encoding it. It computes attention scores for each word with respect to every other word, enabling the model to capture long-range dependencies and contextual relationships effectively."
    ]
    answer = generate_answer(query, contexts)
    print(answer)