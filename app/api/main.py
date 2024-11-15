from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os
from urllib.parse import unquote

# Create the FastAPI app
app = FastAPI()

# Custom middleware to ensure CORS headers are always sent
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Error handling middleware
@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"Error caught in middleware: {str(e)}")
        return JSONResponse(
            status_code=500,  # Return 200 even for errors to avoid CORS issues
            content={"error": str(e)}
        )

# Standard CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Elasticsearch client
es = Elasticsearch(["http://elasticsearch:9200"])

# Get the PDF directory from the environment variable
PDF_DIRECTORY = os.environ.get('PDF_DIRECTORY', '/app/pdf_data')

class SearchQuery(BaseModel):
    query: str
    page: int = 1
    size: int = 50  # We'll keep this but ignore it from the request

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Search API"}

@app.post("/search")
async def search_pdfs(search_query: SearchQuery):
    try:
        page_size = 50
        current_page = max(1, search_query.page)
        
        # First get total count with same query as search
        count_result = es.count(
            index="pdf_documents",
            body={
                "query": {
                    "multi_match": {
                        "query": search_query.query,
                        "fields": ["content"],
                        "operator": "or",
                        "minimum_should_match": "75%"
                    }
                }
            }
        )
        
        total_docs = count_result['count']
        print(f"Total matching documents: {total_docs}")
        
        if total_docs == 0:
            return {
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": page_size,
                    "total_documents": 0,
                    "returned_documents": 0
                },
                "results": []
            }
        
        # Calculate total pages based on actual matching documents
        total_pages = (total_docs + page_size - 1) // page_size
        
        # Ensure current page is within bounds
        current_page = min(max(1, current_page), total_pages)
        
        # Calculate from_idx based on actual available documents
        from_idx = (current_page - 1) * page_size
        
        # Calculate actual size for this page
        remaining_docs = total_docs - from_idx
        current_page_size = min(page_size, remaining_docs)
        
        print(f"Debug - Page: {current_page}, From: {from_idx}, Size: {current_page_size}, Total: {total_docs}")
        
        # Search with fixed size
        result = es.search(
            index="pdf_documents",
            body={
                "query": {
                    "multi_match": {
                        "query": search_query.query,
                        "fields": ["title", "content"],
                        "operator": "or",
                        "minimum_should_match": "75%"
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {"number_of_fragments": 0},
                        "content": {
                            "number_of_fragments": 3, 
                            "fragment_size": 150,
                            "max_analyzed_offset": 1000000
                        }
                    }
                },
                "from": from_idx,
                "size": current_page_size,
                "track_total_hits": True
            }
        )
        
        hits = result['hits']['hits']
        
        # Add debug logging
        print(f"Page: {current_page}, From: {from_idx}, Size: {current_page_size}, Hits: {len(hits)}")
        
        return {
            "pagination": {
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": current_page_size,
                "total_documents": total_docs,
                "returned_documents": len(hits)
            },
            "results": [{
                "title": hit["_source"].get("title", ""),
                "content": hit["_source"].get("content", ""),
                "file_name": os.path.basename(hit["_source"].get("file_path", "")),
                "file_url": hit["_source"].get("file_path", ""),
                "highlights": hit.get("highlight", {}),
                "score": hit["_score"]
            } for hit in hits]
        }
    except Exception as e:
        print(f"Search error details: {str(e)}")  # More detailed error logging
        raise  # Re-raise the exception to see the actual error

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

@app.get("/index-stats")
async def get_index_stats():
    try:
        stats = es.indices.stats(index="pdf_documents")
        count = es.count(index="pdf_documents")
        return {
            "total_docs": count["count"],
            "index_stats": stats["_all"]["total"],
            "exists": es.indices.exists(index="pdf_documents")
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {"error": str(e)}
