import pandas as pd
from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import logging
import argparse
import os
import csv
from collections import Counter
from pdfminer.high_level import extract_text
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

os.environ["TOKENIZERS_PARALLELISM"] = "false"

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_single_pdf(args):
    """Reusing your existing PDF processing function"""
    full_path, input_folder = args
    try:
        text = extract_text(full_path)
        if text:
            return {'full_path': full_path, 'text': text}
    except Exception as e:
        logging.error(f"Error extracting text from {full_path}: {e}")
    return None

def process_pdfs(input_folder):
    """Reusing your existing PDF processing function"""
    pdf_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append((full_path, input_folder))
    
    pool_size = cpu_count() - 2
    with Pool(processes=pool_size) as pool:
        results = list(tqdm(pool.imap(process_single_pdf, pdf_files), total=len(pdf_files), desc="Processing PDFs"))
    
    data = [result for result in results if result is not None]
    return pd.DataFrame(data)

def preprocess_text(text):
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = text.split()
    
    # Remove stopwords and lemmatize
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def create_bertopic_model():
    logging.info("Creating BERTopic model...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')
    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    
    # Adjust the CountVectorizer parameters
    vectorizer_model = CountVectorizer(stop_words="english", min_df=5, max_df=0.5, ngram_range=(1, 3))
    
    representation_model = MaximalMarginalRelevance(diversity=0.7)
    
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        nr_topics="auto",
        verbose=True
    )
    
    return topic_model

def perform_topic_modeling(docs, model):
    topics, probs = model.fit_transform(docs)
    model.update_topics(docs, n_gram_range=(1, 3))
    
    # Generate improved topic labels using the default method
    new_labels = model.generate_topic_labels(nr_words=5, separator=", ")
    model.set_topic_labels(new_labels)
    
    return topics, probs

def generate_topic_report(model, docs, topics, output_dir):
    topic_info = model.get_topic_info()
    topic_sizes = Counter(topics)
    total_docs = len(docs)
    
    with open(os.path.join(output_dir, "topic_report.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Topic ID", "Name", "Size", "Percentage", "Top Words and Phrases", "Example Documents", "Explanation", "Most Similar Topic"])
        
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            if topic_id == -1:  # Skip outlier topic
                continue
            
            # Top words and phrases
            top_words = model.get_topic(topic_id)
            top_words_str = ", ".join([word for word, _ in top_words[:10]])
            
            # Example documents
            topic_docs = [doc for doc, t in zip(docs, topics) if t == topic_id]
            example_docs = "; ".join([doc[:200] + "..." for doc in topic_docs[:3]])
            
            # Explanation
            explanation = f"This topic appears to be about {row['Name']}. " \
                          f"The documents in this topic are grouped together because they frequently contain " \
                          f"words and phrases like {', '.join([word for word, _ in top_words[:5]])}. " \
                          f"These terms suggest a common theme or subject matter across the documents."
            
            # Topic size and percentage
            size = topic_sizes[topic_id]
            percentage = (size / total_docs) * 100
            
            # Most similar topic
            similar_topics = model.find_topics(row['Name'], top_n=2)
            most_similar = similar_topics[1] if similar_topics[0] == topic_id else similar_topics[0]
            most_similar_topic = f"Topic {most_similar[0]}: {model.get_topic_info().loc[model.get_topic_info()['Topic'] == most_similar[0], 'Name'].values[0]}"
            
            writer.writerow([
                topic_id,
                row['Name'],
                size,
                f"{percentage:.2f}%",
                top_words_str,
                example_docs,
                explanation,
                most_similar_topic
            ])
    
    logging.info(f"Topic report saved as CSV in {output_dir}")

def main(input_dir, output_dir):
    # Process PDFs using your existing infrastructure
    df = process_pdfs(input_dir)
    
    # Preprocess texts
    docs = df['text'].apply(preprocess_text).tolist()
    
    # Create BERTopic model
    model = create_bertopic_model()
    
    # Perform topic modeling
    topics, probs = perform_topic_modeling(docs, model)
    
    # Generate and save topic report
    generate_topic_report(model, docs, topics, output_dir)
    
    logging.info(f"Topic modeling complete. Reports saved in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform advanced topic modeling using BERTopic")
    parser.add_argument("--input_dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output_dir", required=True, help="Directory to save output reports")
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir)
