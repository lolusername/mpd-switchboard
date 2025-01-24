import pandas as pd
import networkx as nx
import spacy
from collections import Counter
from pyvis.network import Network
import argparse
import os
from tqdm import tqdm
import pickle
from pathlib import Path
from multiprocessing import Pool, cpu_count
from pdfminer.high_level import extract_text

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 10000000

def find_pdf_files(directory):
    """Recursively find all PDF files in the directory"""
    return list(Path(directory).rglob("*.pdf"))

def extract_pdf_text(pdf_path):
    """Extract text from a PDF file"""
    try:
        text = extract_text(pdf_path)
        return text.strip() if text else ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def process_document(doc):
    """Process a single document with spaCy"""
    entities = []
    relations = []
    
    for token in doc:
        if token.dep_ in ('nsubj', 'dobj') and token.head.pos_ == 'VERB':
            subject = token.text
            verb = token.head.text
            object = [w for w in token.head.children if w.dep_ == 'dobj']
            object = object[0].text if object else ''
            if object:
                relations.append((subject, verb, object))
    
    for ent in doc.ents:
        entities.append(ent.text)
    
    words = [token.lemma_.lower() for token in doc 
             if not token.is_stop and token.is_alpha and len(token.text) > 2]
    
    return words, entities, relations

def process_pdf_batch(pdf_paths):
    """Process a batch of PDFs with optimized performance"""
    word_freq = Counter()
    entity_freq = Counter()
    relations_counter = Counter()
    
    # Extract text from all PDFs in batch first
    texts = []
    for pdf_path in pdf_paths:
        text = extract_pdf_text(pdf_path)
        if text:
            texts.append(text)
    
    # Process all texts in batch using spaCy's pipe
    for doc in nlp.pipe(texts, batch_size=len(texts)):
        words, entities, relations = process_document(doc)
        word_freq.update(words)
        entity_freq.update(entities)
        relations_counter.update(relations)
    
    return word_freq, entity_freq, relations_counter

def create_word_cooccurrence_network(word_freq, n_words=100):
    """Create word co-occurrence network from word frequencies"""
    top_words = set([word for word, _ in word_freq.most_common(n_words)])
    G = nx.Graph()
    
    for word, freq in word_freq.items():
        if word in top_words:
            G.add_node(word, size=freq)
    
    return G

def create_knowledge_graph(entity_freq, relations_counter, n_entities=50):
    """Create knowledge graph from entities and relations"""
    top_entities = set([ent for ent, _ in entity_freq.most_common(n_entities)])
    G = nx.Graph()
    
    for (subj, verb, obj), freq in relations_counter.items():
        if subj in top_entities and obj in top_entities:
            G.add_node(subj, size=entity_freq[subj])
            G.add_node(obj, size=entity_freq[obj])
            G.add_edge(subj, obj, label=verb, weight=freq)
    
    return G

def visualize_network(G, title, output_file):
    """Create and save an interactive network visualization"""
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    
    for node, attrs in G.nodes(data=True):
        net.add_node(node, size=attrs.get('size', 10), title=node)
    
    for u, v, attrs in G.edges(data=True):
        net.add_edge(u, v, value=attrs.get('weight', 1), title=attrs.get('label', ''))

    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])
    net.save_graph(output_file)

def save_intermediate_results(counters, output_dir, batch_num):
    """Save intermediate results to disk"""
    os.makedirs(os.path.join(output_dir, 'intermediate'), exist_ok=True)
    word_freq, entity_freq, relations_counter = counters
    
    with open(os.path.join(output_dir, 'intermediate', f'word_freq_{batch_num}.pkl'), 'wb') as f:
        pickle.dump(word_freq, f)
    with open(os.path.join(output_dir, 'intermediate', f'entity_freq_{batch_num}.pkl'), 'wb') as f:
        pickle.dump(entity_freq, f)
    with open(os.path.join(output_dir, 'intermediate', f'relations_{batch_num}.pkl'), 'wb') as f:
        pickle.dump(relations_counter, f)

def main(input_dir, output_dir, batch_size=50):
    # Find all PDF files
    pdf_files = find_pdf_files(input_dir)
    print(f"Found {len(pdf_files)} PDF files")
    
    # Optimize batch size based on available RAM and CPU cores
    available_ram = 128  # GB
    estimated_ram_per_pdf = 0.5  # GB (conservative estimate)
    max_pdfs_by_ram = int((available_ram * 0.7) / estimated_ram_per_pdf)  # Using 70% of available RAM
    
    optimal_batch_size = min(
        max_pdfs_by_ram,
        batch_size * max(1, cpu_count()),  # Ensure at least 1 process
        100  # Hard cap for safety
    )
    
    print(f"Processing with batch size: {optimal_batch_size}")
    
    # Create batches
    batches = [pdf_files[i:i + optimal_batch_size] 
              for i in range(0, len(pdf_files), optimal_batch_size)]
    
    # Process batches in parallel
    with Pool(processes=max(1, cpu_count() - 1)) as pool:  # Ensure at least 1 process
        results = []
        for batch_results in tqdm(pool.imap(process_pdf_batch, batches),
                                total=len(batches),
                                desc="Processing PDF batches"):
            results.append(batch_results)
            
            # Combine results immediately to free memory
            batch_word_freq, batch_entity_freq, batch_relations = batch_results
            
            # Save intermediate results
            save_intermediate_results(
                (batch_word_freq, batch_entity_freq, batch_relations),
                output_dir,
                len(results) - 1
            )
    
    # Combine all intermediate results
    print("Combining intermediate results...")
    final_word_freq = Counter()
    final_entity_freq = Counter()
    final_relations = Counter()
    
    intermediate_dir = os.path.join(output_dir, 'intermediate')
    for filename in os.listdir(intermediate_dir):
        with open(os.path.join(intermediate_dir, filename), 'rb') as f:
            if filename.startswith('word_freq'):
                final_word_freq.update(pickle.load(f))
            elif filename.startswith('entity_freq'):
                final_entity_freq.update(pickle.load(f))
            elif filename.startswith('relations'):
                final_relations.update(pickle.load(f))
    
    # Create and save networks
    print("Creating networks...")
    word_network = create_word_cooccurrence_network(final_word_freq)
    knowledge_graph = create_knowledge_graph(final_entity_freq, final_relations)
    
    print("Saving visualizations...")
    visualize_network(word_network, "Word Co-occurrence Network", 
                     os.path.join(output_dir, "word_network.html"))
    visualize_network(knowledge_graph, "Knowledge Graph", 
                     os.path.join(output_dir, "knowledge_graph.html"))
    
    # Clean up intermediate files
    print("Cleaning up...")
    for filename in os.listdir(intermediate_dir):
        os.remove(os.path.join(intermediate_dir, filename))
    os.rmdir(intermediate_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate network visualizations from PDF documents")
    parser.add_argument("--input_dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output_dir", required=True, help="Directory to save output visualizations")
    parser.add_argument("--batch_size", type=int, default=5, 
                       help="Number of PDFs to process in each batch")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.batch_size)