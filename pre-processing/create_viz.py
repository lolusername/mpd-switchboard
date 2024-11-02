import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import logging
import json
from collections import Counter
from multiprocessing import Pool, cpu_count
from itertools import combinations
from tqdm import tqdm
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_processed_docs():
    """Load the processed documents from JSON"""
    try:
        json_path = './reports/processed_docs.json'
        logger.info(f"Attempting to load JSON from: {json_path}")
        
        if not os.path.exists(json_path):
            logger.error(f"File not found: {json_path}")
            return []
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Raw data from JSON file:")
            logger.info(json.dumps(data[:1], indent=2))  # Print first document
            logger.info(f"Total documents loaded: {len(data)}")
            return data
            
    except Exception as e:
        logger.error(f"Error loading processed docs: {str(e)}")
        return []

def create_graph_from_docs(docs):
    """Create a new graph from processed documents"""
    logger.info(f"Processing all {len(docs)} documents...")
    
    # First pass: count entity frequencies
    entity_freq = Counter()
    for doc in tqdm(docs, desc="Counting entities"):
        for entity, _ in doc.get('entities', []):
            entity_freq[entity] += 1
    
    # Get top 15 entities
    top_entities = set(k for k, _ in entity_freq.most_common(55))
    logger.info(f"Selected top {len(top_entities)} entities")
    
    # Create graph with only top entities
    G = nx.Graph()
    
    # Second pass: add edges between top entities that appear in same document
    for doc in tqdm(docs, desc="Building entity relations"):
        doc_entities = set(entity for entity, _ in doc.get('entities', []))
        doc_top_entities = doc_entities & top_entities  # Intersection with top entities
        
        # Add edges between all pairs of top entities in this document
        for entity1, entity2 in combinations(doc_top_entities, 2):
            if not G.has_edge(entity1, entity2):
                G.add_edge(entity1, entity2, weight=1)
            else:
                G[entity1][entity2]['weight'] += 1
    
    logger.info(f"Created graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
    return G, entity_freq

def visualize_keyword_cooccurrence_graph(docs, output_dir):
    """Visualize the keyword co-occurrence graph."""
    logger.info("Processing keywords...")
    
    # Count all keywords with better filtering
    keyword_freq = Counter()
    for doc in tqdm(docs, desc="Counting keywords"):
        keywords = doc.get('keywords', [])
        if isinstance(keywords, str):
            keywords = keywords.split()
        
        # Filter out empty strings and very short keywords
        valid_keywords = [k.strip() for k in keywords if k and k.strip() and len(k.strip()) > 2]
        keyword_freq.update(valid_keywords)
    
    # Remove any remaining empty strings
    if '' in keyword_freq:
        del keyword_freq['']
    
    if not keyword_freq:
        logger.error("No valid keywords found after filtering!")
        return
        
    logger.info(f"Total unique keywords found: {len(keyword_freq)}")
    logger.info("Top 15 keywords with frequencies:")
    for kw, freq in keyword_freq.most_common(15):
        logger.info(f"{kw}: {freq}")
    
    # Get top 15 keywords
    top_keywords = dict(keyword_freq.most_common(15))
    
    # Build co-occurrence network
    keyword_graph = nx.Graph()
    
    # Add nodes first
    for kw, freq in top_keywords.items():
        keyword_graph.add_node(kw, frequency=freq)
    
    # Add edges between keywords that appear in same document
    for doc in tqdm(docs, desc="Building keyword network"):
        keywords = set(doc.get('keywords', []))
        if isinstance(keywords, str):
            keywords = set(keywords.split())
        
        # Clean keywords
        keywords = {k.strip() for k in keywords if k and k.strip() and len(k.strip()) > 2}
        
        # Find intersections with top keywords
        doc_top_keywords = keywords & set(top_keywords.keys())
        
        # Add edges between all pairs
        for kw1, kw2 in combinations(doc_top_keywords, 2):
            if not keyword_graph.has_edge(kw1, kw2):
                keyword_graph.add_edge(kw1, kw2, weight=1)
            else:
                keyword_graph[kw1][kw2]['weight'] += 1
    
    # Check if we have any edges
    if len(keyword_graph.edges()) == 0:
        logger.error("No connections found between keywords!")
        # Let's try to understand why
        logger.info("Keywords found in graph: " + str(list(keyword_graph.nodes())))
        sample_docs_with_keywords = []
        for doc in docs[:1000]:  # Check first 1000 docs
            kws = set(k.strip() for k in doc.get('keywords', []) if k and k.strip())
            if kws:
                sample_docs_with_keywords.append(list(kws))
            if len(sample_docs_with_keywords) >= 5:
                break
        logger.info("Sample of document keywords: " + str(sample_docs_with_keywords))
        return
    
    logger.info(f"Created graph with {len(keyword_graph.nodes())} nodes and {len(keyword_graph.edges())} edges")
    
    # Visualization
    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(keyword_graph, k=2, iterations=50)
    
    # Draw edges
    edge_weights = [keyword_graph[u][v]['weight'] for u, v in keyword_graph.edges()]
    max_weight = max(edge_weights)
    edge_widths = [0.5 + 3 * (w / max_weight) for w in edge_weights]
    nx.draw_networkx_edges(keyword_graph, pos, 
                          width=edge_widths,
                          alpha=0.3)
    
    # Draw nodes
    node_sizes = [top_keywords[node] * 50 for node in keyword_graph.nodes()]
    nx.draw_networkx_nodes(keyword_graph, pos,
                          node_size=node_sizes,
                          node_color='lightblue')
    
    # Draw labels
    nx.draw_networkx_labels(keyword_graph, pos, font_size=10)
    
    plt.title("Top 15 Keywords Co-occurrence Network")
    plt.savefig(os.path.join(output_dir, 'keyword_cooccurrence_graph.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save keyword analysis
    with open(os.path.join(output_dir, 'keyword_analysis.csv'), 'w', encoding='utf-8') as f:
        f.write("Keyword,Frequency,Top Co-occurrences\n")
        for keyword, freq in top_keywords.items():
            if keyword in keyword_graph:
                co_occurrences = []
                for neighbor in keyword_graph.neighbors(keyword):
                    weight = keyword_graph[keyword][neighbor]['weight']
                    co_occurrences.append((neighbor, weight))
                top_co = '; '.join([f"{k}({w})" for k, w in 
                                  sorted(co_occurrences, key=lambda x: x[1], 
                                  reverse=True)[:5]])
                f.write(f"{keyword},{freq},{top_co}\n")

def visualize_document_similarity_graph(docs, output_dir):
    """Visualize the document similarity graph."""
    plt.figure(figsize=(20, 20))
    
    # Create similarity graph
    similarity_graph = nx.Graph()
    
    # Prepare document texts
    texts = [" ".join(doc['keywords']) for doc in docs]
    
    if texts:
        vectorizer = TfidfVectorizer(max_features=1000)
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Add edges for similar documents
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    if similarity_matrix[i, j] > 0.3:
                        similarity_graph.add_edge(docs[i]['path'], docs[j]['path'], 
                                               weight=similarity_matrix[i, j])
            
            pos = nx.spring_layout(similarity_graph, k=2, iterations=50)
            nx.draw(similarity_graph, pos,
                   with_labels=True,
                   node_size=100,
                   font_size=8,
                   edge_color='gray',
                   alpha=0.7)
            
            plt.title("Document Similarity Graph")
            plt.savefig(os.path.join(output_dir, 'document_similarity_graph.png'), 
                       dpi=300, bbox_inches='tight')
        except Exception as e:
            logger.error(f"Error creating similarity graph: {str(e)}")
    plt.close()

def main():
    output_dir = './reports/visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        logger.info("Loading processed documents...")
        docs = load_processed_docs()
        
        if not docs:
            logger.error("No documents loaded")
            return
        
        logger.info(f"Loaded {len(docs)} documents")
        
        # Print first document as example
        if docs:
            logger.info("Sample of first document:")
            logger.info(json.dumps(docs[0], indent=2))
        
        logger.info("Creating graph from documents...")
        G, entity_freq = create_graph_from_docs(docs)
        
        if len(G.nodes()) == 0:
            logger.error("No entities found in the documents!")
            return
            
        logger.info("Creating keyword co-occurrence graph...")
        visualize_keyword_cooccurrence_graph(docs, output_dir)
        
        logger.info("Creating document similarity graph...")
        visualize_document_similarity_graph(docs, output_dir)
        
        logger.info(f"All visualizations have been saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error in visualization process: {str(e)}")
        raise

if __name__ == "__main__":
    main()