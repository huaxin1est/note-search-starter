from fastapi import FastAPI, HTTPException
from main import find_note_files,search_keyword,load_paragraphs
from pathlib import Path
from fastapi.responses import FileResponse
from semantic_demo import semantic_search
from fastembed import TextEmbedding

notes_dir = Path(__file__).parent/'notes'
records = load_paragraphs(notes_dir)
texts = [record["text"] for record in records]

model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")
vectors = list(model.passage_embed(texts))

app = FastAPI()

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/search")
def search(keyword:str):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="关键词不能为空")
    nodes_dir =Path(__file__).parent/'notes'
    paths = find_note_files(nodes_dir,[".txt",".md"])
    matchs = search_keyword(keyword,paths)
    results = []
    for path, number, paragraph in matchs:
        results.append({
            "file": str(path.relative_to(nodes_dir)),
            "paragraph": number,
            "text": paragraph.strip()
        })
    return {"results": results,"keyword":keyword,"count":len(matchs)}  

@app.get("/semantic-search")
def semantic_search_api(query:str):
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400 ,detail="关键词不能为空")
    results = []
    ranked = semantic_search(query,records,vectors,model)
    for score,record in ranked:
        results.append({
        "score": round(score, 3),
        "file": record["file"],
        "paragraph": record["paragraph"],
        "text": record["text"],
        })
    return {"results":results}

@app.get("/hybrid-search")
def hybrid_search_api(query: str):
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400 ,detail="关键词不能为空")
    nodes_dir =Path(__file__).parent/'notes'
    paths = find_note_files(nodes_dir,[".txt",".md"])
    matchs = search_keyword(query,paths)
    results = []
    for path, number, paragraph in matchs[:3]:
        results.append({
            "source": "keyword",
            "file": str(path.relative_to(nodes_dir)),
            "paragraph": number,
            "text": paragraph.strip(),
        })
    seen = {(item["file"], item["paragraph"]) for item in results}

    if len(results) < 3:
        ranked = semantic_search(query, records, vectors, model, top_k=len(records))
        for score, record in ranked:
            key = (record["file"], record["paragraph"])
            if key in seen:
                continue

            results.append({
                "source": "semantic",
                "score": round(score, 3),
                "file": record["file"],
                "paragraph": record["paragraph"],
                "text": record["text"],
            })
            seen.add(key)

            if len(results) == 3:
                break
    return {"query":query,"results":results}
    
