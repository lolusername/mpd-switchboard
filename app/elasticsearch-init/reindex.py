import os
import time
import requests
from elasticsearch import Elasticsearch, helpers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reindex_data():
    # Connect to source Elasticsearch
    source_es = Elasticsearch([os.environ.get('ES_SOURCE', 'http://localhost:9200')])
    target_url = os.environ.get('ES_TARGET', 'http://localhost:8000')
    
    logger.info(f"Source ES: {os.environ.get('ES_SOURCE')}")
    logger.info(f"Target API: {target_url}")

    # Get all indices
    indices = source_es.indices.get_alias().keys()
    logger.info(f"Found indices: {list(indices)}")
    
    for index in indices:
        logger.info(f"Reindexing {index}...")
        
        # Get documents from source
        docs = helpers.scan(source_es, index=index, query={"query": {"match_all": {}}})
        batch = []
        
        for doc in docs:
            batch.append(doc['_source'])
            
            # Send in batches of 100
            if len(batch) >= 100:
                try:
                    response = requests.post(
                        f"{target_url}/api/documents/_bulk",
                        json=batch
                    )
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Successfully indexed {result['indexed']} documents")
                    else:
                        logger.error(f"Error indexing batch: {response.text}")
                except Exception as e:
                    logger.error(f"Error sending batch: {e}")
                batch = []
        
        # Send remaining documents
        if batch:
            try:
                response = requests.post(
                    f"{target_url}/api/documents/_bulk",
                    json=batch
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully indexed final {result['indexed']} documents")
                else:
                    logger.error(f"Error indexing final batch: {response.text}")
            except Exception as e:
                logger.error(f"Error sending final batch: {e}")

if __name__ == "__main__":
    reindex_data() 