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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNetworkAnalyzer:
    def __init__(self):
        # More flexible patterns to capture email headers and relationships
        self.from_pattern = r'(?:From:|From|Sender:).*?(?=To:|Cc:|Subject:|$)'
        self.to_pattern = r'(?:To:|To).*?(?=From:|Cc:|Subject:|$)'
        self.cc_pattern = r'(?:Cc:|Cc|Carbon Copy:).*?(?=From:|To:|Subject:|$)'
        self.email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        self.email_network = {}
        self.email_freq = Counter()
        
        # Initialize spaCy with increased max length
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.max_length = 7000000  # Increase max length to 5M characters
        
        self.entity_mentions = Counter()
        self.entity_connections = {}
        
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
        """Process a single PDF file to extract email relationships and entities"""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
            
        # Extract entities using spaCy
        doc = self.nlp(text)
        
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
    
    def analyze_directory(self, pdf_dir, test_run=False):
        """Analyze all PDFs in directory and subdirectories"""
        logger.info(f"Scanning directory: {pdf_dir}")
        pdf_files = self.find_pdf_files(pdf_dir)
        
        if test_run:
            pdf_files = pdf_files[:500]
            logger.info("TEST RUN: Processing only 500 documents")
        
        total_files = len(pdf_files)
        logger.info(f"Processing {total_files} PDF files")
        
        # Calculate optimal chunk size and number of processes
        chunk_size = max(1, min(100, total_files // (cpu_count() * 4)))
        n_processes = min(cpu_count() * 2, total_files)
        
        # Process PDFs in parallel with optimized settings
        with Pool(processes=n_processes) as pool:
            # Use larger chunks for better efficiency
            results = list(tqdm(
                pool.imap_unordered(
                    self.process_pdf, 
                    pdf_files,
                    chunksize=chunk_size
                ),
                total=total_files,
                desc="Processing PDFs",
                unit="files"
            ))
        
        # Initialize network dictionaries after processing
        self.email_network = defaultdict(lambda: defaultdict(int))
        self.entity_connections = defaultdict(lambda: defaultdict(int))
        
        # Track some statistics
        total_relationships = 0
        total_emails_found = 0
        
        # Analyze email patterns
        for result in results:
            if result:
                total_emails_found += result.get('total_emails', 0)
                
                # Process email relationships
                if result['relationships']:
                    total_relationships += len(result['relationships'])
                    for sender, receiver in result['relationships']:
                        self.email_freq.update([sender, receiver])
                        self.email_network[sender][receiver] += 1
                
                # Process entity mentions and connections
                if result.get('entities'):
                    self.entity_mentions.update(result['entities'])
                
                # Process entity pairs
                if result.get('entity_pairs'):
                    for ent1, ent2 in result['entity_pairs']:
                        self.entity_connections[ent1][ent2] += 1
                        self.entity_connections[ent2][ent1] += 1
        
        logger.info(f"Found {len(self.email_freq)} unique email addresses")
        logger.info(f"Found {total_relationships} email relationships")
        logger.info(f"Found {total_emails_found} total email addresses")
        logger.info(f"Found {len(self.entity_mentions)} unique entities")
        
        return dict(self.email_network), dict(self.email_freq)

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