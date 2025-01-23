from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch, helpers
from pydantic import BaseModel
import os
from urllib.parse import unquote
from typing import List
import time
from fastapi.security import OAuth2PasswordRequestForm
import auth
from datetime import timedelta

# Create the FastAPI app
app = FastAPI()

# Standard CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
        "http://localhost:80",
        "http://52.23.77.209",
        "http://52.23.77.209:3000",
        "http://52.23.77.209:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Initialize Elasticsearch client with better error handling and retry logic
es = None  # Initialize es as None first

def init_elasticsearch():
    global es
    for i in range(3):  # Retry 3 times
        try:
            es = Elasticsearch(
                ["http://elasticsearch:9200"],
                retry_on_timeout=True,
                max_retries=3,
                request_timeout=30
            )
            
            # Test connection
            if not es.ping():
                raise Exception("Cannot ping Elasticsearch")
                
            # Wait for yellow status
            health = es.cluster.health(wait_for_status='yellow', timeout='30s')
            print(f"Elasticsearch health: {health['status']}")
            
            # Create index if it doesn't exist
            if not es.indices.exists(index="pdf_documents"):
                mapping = {
                    "mappings": {
                        "properties": {
                            "title": { "type": "text" },
                            "content": { "type": "text" },
                            "file_path": { "type": "keyword" },
                            "uploaded_at": { "type": "date" }
                        }
                    },
                    "settings": {
                        "number_of_replicas": 0
                    }
                }
                es.indices.create(index="pdf_documents", body=mapping)
                print("Created pdf_documents index")
            return True
            
        except Exception as e:
            print(f"Elasticsearch initialization attempt {i+1} failed: {str(e)}")
            if i == 2:  # Last attempt
                print("Failed to initialize Elasticsearch after 3 attempts")
                return False
            time.sleep(5)  # Wait 5 seconds before retrying
    return False

@app.on_event("startup")
async def startup_event():
    if not init_elasticsearch():
        print("WARNING: Application starting without Elasticsearch connection")

# Get the PDF directory from the environment variable
PDF_DIRECTORY = os.environ.get('PDF_DIRECTORY', '/app/pdf_data')

class SearchQuery(BaseModel):
    query: str
    page: int = 1
    size: int = 50  # We'll keep this but ignore it from the request

class BulkIndexRequest(BaseModel):
    documents: List[dict]

class BulkDocuments(BaseModel):
    documents: List[dict]

# This is a simple user store - in production, use a database
users_db = {
    "admin": {
        "username": "admin",
        "password": auth.get_password_hash("admin123")  # Change this!
    }
}

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Search API"}

@app.get("/api")
async def list_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": route.methods,
            "name": route.name
        })
    return {"routes": routes}

@app.post("/search")
async def search_pdfs(search_query: SearchQuery):
    if not es:
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch connection not available"
        )
    
    try:
        # Check cluster health first
        health = es.cluster.health()
        if health['status'] == 'red':
            raise HTTPException(
                status_code=503,
                detail="Elasticsearch cluster is unhealthy"
            )
        
        # Check if index exists
        if not es.indices.exists(index="pdf_documents"):
            return {
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                    "total_documents": 0,
                    "returned_documents": 0
                },
                "results": []
            }
            
        page_size = 50
        current_page = max(1, search_query.page)
        
        try:
            # First get total count with same query as search
            count_result = es.count(
                index="pdf_documents",
                body={
                    "query": {
                        "multi_match": {
                            "query": search_query.query,
                            "fields": ["content^2", "title"],
                            "operator": "or",
                            "minimum_should_match": "50%"
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
                                "fragment_size": 150
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
        except Exception as es_error:
            print(f"Elasticsearch query error: {str(es_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Search query error: {str(es_error)}"
            )
            
    except Exception as e:
        print(f"Search error details: {str(e)}")
        if "no such index" in str(e).lower():
            return {
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                    "total_documents": 0,
                    "returned_documents": 0
                },
                "results": []
            }
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    if not es:
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch is not initialized"
        )
    try:
        health = es.cluster.health()
        return {
            "status": "healthy",
            "elasticsearch": health['status']
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Elasticsearch health check failed: {str(e)}"
        )

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

@app.post("/api/documents/_bulk")
async def bulk_index(request: Request):
    try:
        docs = await request.json()
        print(f"Received bulk request with {len(docs)} documents")
        
        actions = [{"_index": "pdf_documents", "_source": doc} for doc in docs]
        success, failed = helpers.bulk(es, actions, stats_only=True)
        
        print(f"Bulk indexed {success} documents, {failed} failed")
        return {
            "status": "success",
            "indexed": success,
            "failed": failed
        }
    except Exception as e:
        print(f"Bulk index error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Optional: Add route listing for debugging
@app.get("/api/routes")
async def list_routes():
    return {
        "routes": [
            {"path": route.path, "methods": route.methods}
            for route in app.routes
        ]
    }

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not auth.verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route example
@app.get("/protected")
async def protected_route(current_user: str = Depends(auth.get_current_user)):
    return {"message": "You are authenticated", "user": current_user}
