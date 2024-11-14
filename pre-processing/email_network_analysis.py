import re
import pandas as pd
import networkx as nx
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import os
import logging
from pathlib import Path
from datetime import datetime
from pdfminer.high_level import extract_text
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import spacy
import json
from sklearn.manifold import TSNE
from umap import UMAP
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNetworkAnalyzer:
    def __init__(self):
        # Add at the start of __init__
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # More flexible patterns to capture email headers and relationships
        self.from_pattern = r'(?:From:|From|Sender:).*?(?=To:|Cc:|Subject:|$)'
        self.to_pattern = r'(?:To:|To).*?(?=From:|Cc:|Subject:|$)'
        self.cc_pattern = r'(?:Cc:|Cc|Carbon Copy:).*?(?=From:|To:|Subject:|$)'
        self.email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        
        # Initialize network structures with defaultdict
        self.email_network = defaultdict(lambda: defaultdict(int))
        self.email_freq = Counter()
        self.entity_mentions = Counter()
        self.entity_connections = defaultdict(lambda: defaultdict(int))
        
        # Initialize spaCy with increased max length
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.max_length = 7000000  # Increase max length to 5M characters
        
        # Add entity normalization mapping
        self.entity_mapping = {
            'USA': ['USA', 'U.S.', 'US'],
            'DC Government': ['the DC Government', 'DC GOVERNMENT/OU', 'DC Gov', 'DC Government'],
            'Washington DC': ['Washington', 'DC', 'Washington DC'],
            'OCTO': ['OCTO Security Operations Center', 'OCTO SOC', 'OCTO'],
            'NCR': ['NCR', 'National Capital Region'],
        }
        
        # Create reverse mapping for quick lookups
        self.entity_normalize = {}
        for normalized, variants in self.entity_mapping.items():
            for variant in variants:
                self.entity_normalize[variant] = normalized
        
        # Initialize document storage
        self.processed_documents = []
        
        # Initialize topic modeling components
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            umap_model=UMAP(
                n_neighbors=15,
                n_components=2,
                min_dist=0.0,
                metric='cosine'
            )
        )

    def find_pdf_files(self, directory):
        """Recursively find all PDF files in the directory"""
        pdf_files = []
        for root, _, files in os.walk(directory):
            pdf_files.extend([
                os.path.join(root, f) 
                for f in files 
                if f.lower().endswith('.pdf')
            ])
        return pdf_files
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        try:
            text = extract_text(pdf_path)
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""
    
    def normalize_entity(self, entity):
        """Normalize entity names to handle variations"""
        return self.entity_normalize.get(entity, entity)
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file"""
        logger.info(f"Processing: {pdf_path}")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from: {pdf_path}")
            return None
            
        logger.info(f"Extracted {len(text)} characters from {pdf_path}")
        
        # Store text for topic modeling
        self.processed_documents.append({
            'path': str(pdf_path),
            'text': text
        })
        
        try:
            # Extract entities using spaCy
            doc = self.nlp(text)
            logger.info(f"NLP processing complete for {pdf_path}")
            
            # Track entities in this document
            doc_entities = set()
            entity_pairs = []  # Store co-occurring pairs instead of updating connections directly
            
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'GPE']:  # Organizations, People, Locations
                    # Normalize the entity name before adding
                    normalized_entity = self.normalize_entity(ent.text)
                    doc_entities.add(normalized_entity)
            
            # Create pairs of co-occurring entities
            entities_list = list(doc_entities)
            for i in range(len(entities_list)):
                for j in range(i + 1, len(entities_list)):
                    entity_pairs.append((entities_list[i], entities_list[j]))
            
            # Find all emails in the document
            all_emails = re.findall(self.email_pattern, text)
            logger.debug(f"Found {len(all_emails)} total emails in document")
            
            relationships = []
            
            # Try to find structured email headers first
            from_sections = re.finditer(self.from_pattern, text, re.IGNORECASE | re.MULTILINE)
            to_sections = re.finditer(self.to_pattern, text, re.IGNORECASE | re.MULTILINE)
            
            # Process structured sections
            for from_match in from_sections:
                from_text = from_match.group()
                sender_emails = re.findall(self.email_pattern, from_text)
                
                if sender_emails:
                    sender = sender_emails[0]
                    logger.debug(f"Found sender: {sender}")
                    
                    # Look for recipients in nearby To: sections
                    for to_match in to_sections:
                        to_text = to_match.group()
                        receiver_emails = re.findall(self.email_pattern, to_text)
                        
                        for receiver in receiver_emails:
                            if receiver != sender:  # Avoid self-loops
                                relationships.append((sender, receiver))
                                logger.debug(f"Found relationship: {sender} -> {receiver}")
            
            # If no structured relationships found, try to infer from email order
            if not relationships and len(all_emails) >= 2:
                logger.debug("No structured relationships found, inferring from email order")
                # Assume first email is sender and subsequent emails are recipients
                sender = all_emails[0]
                for receiver in all_emails[1:]:
                    if receiver != sender:  # Avoid self-loops
                        relationships.append((sender, receiver))
                        logger.debug(f"Inferred relationship: {sender} -> {receiver}")
            
            if relationships:
                logger.debug(f"Found {len(relationships)} total relationships")
            else:
                logger.debug("No relationships found")
                
            # Return both email and entity data
            return {
                'path': pdf_path,
                'relationships': relationships,
                'total_emails': len(all_emails),
                'entities': list(doc_entities),
                'entity_pairs': entity_pairs  # Add entity pairs to result
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def analyze_directory(self, pdf_dir, test_run=False):
        """Analyze all PDFs in directory"""
        logger.info(f"Scanning directory: {pdf_dir}")
        pdf_files = self.find_pdf_files(pdf_dir)
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        if test_run:
            pdf_files = pdf_files[:50]  # Process 50 files in test mode
            logger.info(f"TEST RUN: Processing {len(pdf_files)} documents")
        
        for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
            try:
                result = self.process_pdf(pdf_path)
                if result:
                    # Store email relationships
                    for sender, receiver in result['relationships']:
                        # Initialize sender if not exists
                        if sender not in self.email_network:
                            self.email_network[sender] = defaultdict(int)
                        
                        # Add connection
                        self.email_network[sender][receiver] += 1
                        
                        # Update frequency counters
                        self.email_freq[sender] += 1
                        self.email_freq[receiver] += 1
                    
                    # Store entity relationships
                    for entity in result['entities']:
                        self.entity_mentions[entity] += 1
                    
                    # Initialize entity connections
                    for entity1, entity2 in result['entity_pairs']:
                        if entity1 not in self.entity_connections:
                            self.entity_connections[entity1] = defaultdict(int)
                        if entity2 not in self.entity_connections:
                            self.entity_connections[entity2] = defaultdict(int)
                        
                        # Add bidirectional connection
                        self.entity_connections[entity1][entity2] += 1
                        self.entity_connections[entity2][entity1] += 1
                    
                    logger.info(f"Successfully processed: {pdf_path}")
                    
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")
                continue
        
        logger.info(f"Processed {len(pdf_files)} documents")
        logger.info(f"Found {len(self.email_freq)} unique email addresses")
        logger.info(f"Detected {sum(len(receivers) for receivers in self.email_network.values())} connections")

    def create_network_visualization(self, min_weight=2):
        """Create summary visualizations and corresponding D3 data"""
        logger.info("Creating network visualizations and D3 data...")
        
        # Create output directory for D3 data
        d3_output_dir = os.path.join('reports', 'email_analysis', 'd3_data')
        os.makedirs(d3_output_dir, exist_ok=True)
        
        # Get domain data
        domains = Counter(email.split('@')[1] for email in self.email_freq.keys())
        top_domains = domains.most_common(10)
        domain_names = [d[0] for d in top_domains]
        domain_counts = [d[1] for d in top_domains]
        
        # 1. Save Bar Chart Data
        bar_chart_data = [
            {"domain": domain, "count": count} 
            for domain, count in top_domains
        ]
        with open(os.path.join(d3_output_dir, 'domain_bar_chart.json'), 'w') as f:
            json.dump(bar_chart_data, f, indent=2)
        
        # 2. Save Email Activity Distribution Data
        connection_counts = [len(receivers) for receivers in self.email_network.values()]
        distribution_data = [
            {"connections": count, "frequency": freq} 
            for count, freq in Counter(connection_counts).items()
        ]
        with open(os.path.join(d3_output_dir, 'connection_distribution.json'), 'w') as f:
            json.dump(distribution_data, f, indent=2)
        
        # 3. Save Domain Network Data
        domain_matrix = np.zeros((10, 10))
        for sender, receivers in self.email_network.items():
            sender_domain = sender.split('@')[1]
            if sender_domain in domain_names:
                for receiver, weight in receivers.items():
                    receiver_domain = receiver.split('@')[1]
                    if receiver_domain in domain_names:
                        i = domain_names.index(sender_domain)
                        j = domain_names.index(receiver_domain)
                        domain_matrix[i][j] += weight
        
        # Create D3 network data
        network_data = {
            "nodes": [
                {"id": domain, "group": 1, "size": count} 
                for domain, count in zip(domain_names, domain_counts)
            ],
            "links": []
        }
        
        if domain_matrix.sum() > 0:
            edge_threshold = min(
                np.percentile(domain_matrix[domain_matrix > 0], .1),
                np.max(domain_matrix) * 0.999
            )
            
            for i in range(len(domain_names)):
                for j in range(i+1, len(domain_names)):
                    weight = domain_matrix[i][j]
                    if weight > edge_threshold:
                        network_data["links"].append({
                            "source": domain_names[i],
                            "target": domain_names[j],
                            "value": float(weight)
                        })
        
        with open(os.path.join(d3_output_dir, 'domain_network.json'), 'w') as f:
            json.dump(network_data, f, indent=2)
        
        # 4. Save Heatmap Data
        heatmap_data = {
            "domains": domain_names,
            "matrix": domain_matrix.tolist()
        }
        with open(os.path.join(d3_output_dir, 'domain_heatmap.json'), 'w') as f:
            json.dump(heatmap_data, f, indent=2)
        
        # 5. Save Entity Network Data
        top_entities = self.entity_mentions.most_common(10)
        entity_network_data = {
            "nodes": [
                {"id": entity, "group": 1, "size": count}
                for entity, count in top_entities
            ],
            "links": []
        }
        
        entity_names = [e[0] for e in top_entities]
        for i, entity1 in enumerate(entity_names):
            for j, entity2 in enumerate(entity_names[i+1:], i+1):
                weight = self.entity_connections[entity1][entity2]
                if weight > 0:
                    entity_network_data["links"].append({
                        "source": entity1,
                        "target": entity2,
                        "value": weight
                    })
        
        with open(os.path.join(d3_output_dir, 'entity_network.json'), 'w') as f:
            json.dump(entity_network_data, f, indent=2)
        
        # Create matplotlib visualization
        fig = plt.figure(figsize=(20, 15))
        gs = fig.add_gridspec(2, 2)
        
        # Add subplots
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Create your visualizations here
        # Example:
        ax1.bar(domain_names, domain_counts)
        ax1.set_title('Top Email Domains')
        
        # Add more visualizations to other subplots...
        
        plt.tight_layout()
        return fig  # Make sure to return the figure object

    def generate_statistics(self):
        """Generate email correspondence statistics"""
        # Extract domains from emails
        domains = Counter(email.split('@')[1] for email in self.email_freq.keys())
        
        # Calculate additional metrics
        total_connections = sum(len(v) for v in self.email_network.values())
        avg_connections = total_connections / len(self.email_freq) if self.email_freq else 0
        
        stats = {
            'total_unique_emails': len(self.email_freq),
            'total_connections': total_connections,
            'avg_connections_per_email': round(avg_connections, 2),
            'top_emailers': pd.DataFrame(
                self.email_freq.most_common(20),
                columns=['Email', 'Frequency']
            ),
            'domain_stats': dict(domains.most_common(20))
        }
        return stats

    def generate_visualization_data(self, output_dir):
        """Generate all visualization data while preserving existing analysis"""
        vis_data_dir = os.path.join(output_dir, 'd3_data')
        os.makedirs(vis_data_dir, exist_ok=True)
        
        logger.info("Creating network visualizations and D3 data...")
        
        # 1. Create network data (NOT the matplotlib figure)
        network_data = {
            "nodes": [],
            "links": []
        }
        
        # Get top domains
        domain_counts = Counter(email.split('@')[1] for email in self.email_freq.keys())
        domain_names = [d[0] for d in domain_counts.most_common(10)]
        
        # Add nodes
        for domain in domain_names:
            network_data["nodes"].append({
                "id": domain,
                "group": 1,
                "size": domain_counts[domain]
            })
        
        # Add links
        for i, domain1 in enumerate(domain_names):
            for j, domain2 in enumerate(domain_names[i+1:], i+1):
                weight = self.domain_matrix[i][j] if hasattr(self, 'domain_matrix') else 0
                if weight > 0:
                    network_data["links"].append({
                        "source": domain1,
                        "target": domain2,
                        "value": float(weight)
                    })
        
        # Save network data
        with open(os.path.join(vis_data_dir, 'domain_network_complete.json'), 'w') as f:
            json.dump(network_data, f, indent=2)
        
        # 2. Generate topic model visualizations
        logger.info("Generating topic model visualizations...")
        documents = [doc['text'] for doc in self.processed_documents]
        embeddings = self.sentence_model.encode(documents, show_progress_bar=True)
        topics, probs = self.topic_model.fit_transform(documents, embeddings)
        
        # Save topic visualizations
        topic_vis = {
            'umap': self._create_umap_visualization(embeddings, topics),
            'tsne': self._create_tsne_visualization(embeddings, topics),
            'similarity': self._create_topic_similarity_network(),
            'info': self.topic_model.get_topic_info().to_dict('records')
        }
        
        for name, data in topic_vis.items():
            with open(os.path.join(vis_data_dir, f'topic_{name}_analysis.json'), 'w') as f:
                json.dump(data, f, indent=2)
        
        logger.info("Visualization data generation complete!")

    def _create_umap_visualization(self, embeddings, topics):
        """Create UMAP visualization data"""
        umap_model = UMAP(n_components=2, metric='cosine')
        umap_embeddings = umap_model.fit_transform(embeddings)
        
        return {
            'points': umap_embeddings.tolist(),
            'topics': topics,
            'labels': self.topic_model.get_topic_info()['Name'].tolist()
        }

    def _create_tsne_visualization(self, embeddings, topics):
        """Create t-SNE visualization data"""
        tsne = TSNE(n_components=2)
        tsne_embeddings = tsne.fit_transform(embeddings)
        
        return {
            'points': tsne_embeddings.tolist(),
            'topics': topics,
            'labels': self.topic_model.get_topic_info()['Name'].tolist()
        }

    def _create_topic_similarity_network(self):
        """Create topic similarity network"""
        # Get topic info
        topic_info = self.topic_model.get_topic_info()
        topics = topic_info.index.tolist()
        
        # Calculate similarities using cosine similarity of topic embeddings
        topic_embeddings = []
        nodes = []
        
        for topic in topics:
            topic_words = self.topic_model.get_topic(topic)
            if isinstance(topic_words, bool):  # Skip if no words returned
                continue
            
            # Get topic representation
            try:
                words = [word for word, _ in topic_words]
                if words:  # Only process if we have words
                    topic_embeddings.append(self.sentence_model.encode(' '.join(words)))
                    nodes.append({
                        'id': str(topic),
                        'label': ' '.join(words[:3]),
                        'size': len(words)
                    })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping topic {topic}: {str(e)}")
                continue
        
        if not topic_embeddings:  # If no valid topics found
            return {'nodes': [], 'links': []}
        
        # Convert to numpy array
        topic_embeddings = np.array(topic_embeddings)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(topic_embeddings)
        
        links = []
        # Create links for similar topics
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                similarity = similarities[i][j]
                if similarity > 0.2:  # Threshold for visualization
                    links.append({
                        'source': nodes[i]['id'],
                        'target': nodes[j]['id'],
                        'value': float(similarity)
                    })
        
        return {'nodes': nodes, 'links': links}