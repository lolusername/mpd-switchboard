import os
import json
import logging
import argparse
import pandas as pd
from pathlib import Path
from email_network_analysis import EmailNetworkAnalyzer
import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_output_directory(base_dir):
    """Create output directory if it doesn't exist"""
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def generate_report(pdf_dir, output_dir, test_run=False):
    """Generate comprehensive email analysis report"""
    analyzer = EmailNetworkAnalyzer()
    
    # Analyze PDFs
    analyzer.analyze_directory(pdf_dir, test_run=test_run)
    
    # Create and save visualizations
    try:
        fig = analyzer.create_network_visualization()
        if fig:  # Only save if figure was created
            fig.savefig(os.path.join(output_dir, "email_analysis.png"), dpi=300, bbox_inches='tight')
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Could not create matplotlib visualization: {str(e)}")
    
    # Generate and save statistics
    stats = analyzer.generate_statistics()
    
    # Save detailed CSV and JSON files
    stats['top_emailers'].to_csv(os.path.join(output_dir, 'top_emailers.csv'), index=False)
    
    with open(os.path.join(output_dir, 'email_statistics.json'), 'w') as f:
        json.dump({
            'summary': {
                'total_unique_emails': stats['total_unique_emails'],
                'total_connections': stats['total_connections'],
                'avg_connections': stats['avg_connections_per_email']
            },
            'domain_stats': stats['domain_stats']
        }, f, indent=2)
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Analyze email networks from PDF documents.")
    parser.add_argument('--pdf_dir', required=True, help='Directory containing PDF files')
    parser.add_argument('--output_dir', default='./reports/email_analysis', 
                       help='Base directory for output files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--test-run', action='store_true', 
                       help='Process only 500 documents for testing')

    args = parser.parse_args()

    # Set logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, 
                       format='%(asctime)s - %(levelname)s - %(message)s')

    # Create output directory
    output_dir = create_output_directory(args.output_dir)
    logger.info(f"Output directory created at: {output_dir}")
    
    # Generate report
    try:
        stats = generate_report(args.pdf_dir, output_dir, test_run=args.test_run)
        logger.info(f"Analysis complete. Results saved to {output_dir}")
        logger.info(f"Found {stats['total_unique_emails']} unique email addresses")
        logger.info(f"Detected {stats['total_connections']} connections")
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

if __name__ == "__main__":
    main()