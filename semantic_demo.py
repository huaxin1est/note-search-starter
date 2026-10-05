from pathlib import Path
from fastembed import TextEmbedding
from main import load_paragraphs
import numpy as np

def semantic_search(query, records, vectors, model, top_k=3):
    query_vector = next(model.query_embed(query))
    ranked = []
    for record, vector in zip(records, vectors):
        score = np.dot(query_vector, vector) / (
            np.linalg.norm(query_vector) * np.linalg.norm(vector)
        )
        ranked.append((float(score), record))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:top_k]

if __name__ == "__main__":
    notes_dir = Path(__file__).parent/'notes'
    records = load_paragraphs(notes_dir)
    texts = [record["text"] for record in records]

    model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")
    vectors = list(model.passage_embed(texts))

    print("段落数：", len(records))
    print("向量数：", len(vectors))
    print("每个向量的维度：", len(vectors[0]))

    print(semantic_search("地址修正", records, vectors, model))