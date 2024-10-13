from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel

app = FastAPI()

# Initialize Elasticsearch client
es = Elasticsearch(["http://elasticsearch:9200"])

class SearchQuery(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Search API"}

@app.post("/search")
async def search_pdfs(search_query: SearchQuery):
    try:
        result = es.search(
            index="pdf_documents",
            body={
                "query": {
                    "multi_match": {
                        "query": search_query.query,
                        "fields": ["title", "content"]
                    }
                }
            }
        )
        hits = result['hits']['hits']
        return [{"title": hit["_source"]["title"], "content": hit["_source"]["content"], "file_url": hit["_source"]["file_url"][:200]} for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    if es.ping():
        return {"status": "healthy"}
    else:
        raise HTTPException(status_code=500, detail="Elasticsearch is not responding")
