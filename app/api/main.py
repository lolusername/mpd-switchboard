from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os
from urllib.parse import unquote



app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize Elasticsearch client
es = Elasticsearch(["http://elasticsearch:9200"])

# Get the PDF directory from the environment variable
PDF_DIRECTORY = os.environ.get('PDF_DIRECTORY', '/app/pdf_data')

class SearchQuery(BaseModel):
    query: str
    page: int = 1
    size: int = 50  # Default to 50 results per page

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Search API"}

@app.post("/search")
async def search_pdfs(search_query: SearchQuery):
    try:
        # Calculate offset
        from_idx = (search_query.page - 1) * search_query.size

        result = es.search(
            index="pdf_documents",
            body={
                "query": {
                    "multi_match": {
                        "query": search_query.query,
                        "fields": ["title", "content"],
                        "minimum_should_match": "75%"
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                },
                "min_score": 0.5,
                "from": from_idx,
                "size": search_query.size
            }
        )
        
        total_docs = result['hits']['total']['value']
        hits = result['hits']['hits']
        total_pages = (total_docs + search_query.size - 1) // search_query.size
        
        return {
            "pagination": {
                "current_page": search_query.page,
                "total_pages": total_pages,
                "page_size": search_query.size,
                "total_documents": total_docs,
                "returned_documents": len(hits)
            },
            "results": [{
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "file_name": os.path.basename(hit["_source"]["file_path"]),
                "file_url": hit["_source"]["file_path"],
                "highlights": hit.get("highlight", {}),
                "score": hit["_score"]
            } for hit in hits]
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    if es.ping():
        return {"status": "healthy"}
    else:
        raise HTTPException(status_code=500, detail="Elasticsearch is not responding")

@app.get("/pdf/{file_path:path}")
async def get_pdf(file_path: str):
    # Decode the URL-encoded file path
    decoded_path = unquote(file_path)
    
    # Construct the full path within the PDF_DIRECTORY
    full_path = os.path.join(PDF_DIRECTORY, decoded_path)
    
    if os.path.isfile(full_path) and full_path.lower().endswith('.pdf'):
        return FileResponse(full_path, media_type="application/pdf", filename=os.path.basename(full_path))
    else:
        raise HTTPException(status_code=404, detail=f"PDF file not found: {decoded_path}")

# Update the check_pdf_directory function to show nested structure
@app.get("/check-pdf-directory")
async def check_pdf_directory():
    if os.path.isdir(PDF_DIRECTORY):
        pdf_files = []
        for root, _, files in os.walk(PDF_DIRECTORY):
            for file in files:
                if file.lower().endswith('.pdf'):
                    relative_path = os.path.relpath(os.path.join(root, file), PDF_DIRECTORY)
                    pdf_files.append(relative_path)
        
        return {
            "status": "Directory exists",
            "sample_files": pdf_files[:10],
            "total_pdf_files": len(pdf_files)
        }
    else:
        return {"status": "Directory not found", "path": PDF_DIRECTORY}
