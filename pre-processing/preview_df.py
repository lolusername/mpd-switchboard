import pandas as pd
import pickle
import argparse

def load_and_preview_df(file_path):
    # Load the DataFrame from the pickle file
    with open(file_path, 'rb') as f:
        df = pickle.load(f)
    
    print("DataFrame loaded successfully.")
    
    # Basic info about the DataFrame
    print("\nDataFrame Info:")
    print(df.info())
    
    # Preview the first few rows
    print("\nFirst few rows of the DataFrame:")
    print(df.head())
    
    # Basic statistics of the DataFrame
    print("\nBasic statistics of the DataFrame:")
    print(df.describe(include='all'))
    
    # Column names
    print("\nColumn names:")
    print(df.columns)
    
    # Number of unique values in each column
    print("\nNumber of unique values in each column:")
    print(df.nunique())
    
    # Check for missing values
    print("\nMissing values in each column:")
    print(df.isnull().sum())
    
    # Sample of text content (if 'text' column exists)
    if 'text' in df.columns:
        print("\nSample of text content:")
        print(df['text'].sample(1).values[0][:500] + "...")  # Print first 500 characters of a random text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and preview DataFrame from pickle file")
    parser.add_argument("file_path", help="Path to the pickle file containing the DataFrame")
    args = parser.parse_args()
    
    load_and_preview_df(args.file_path)