# Switchboard

> A comprehensive platform for analyzing government documents through advanced text processing and network analysis.

## Overview

Switchboard helps researchers, journalists, and citizens understand complex document collections obtained through FOIA requests by extracting relationships, identifying key topics, and making documents searchable.

### Key Features

- 📄 Automated document processing and OCR
- 🔍 Advanced search capabilities
- 🔒 Automatic PII redaction
- 📊 Network analysis of communications
- 📈 Topic modeling and clustering
- 🗂 Document organization and tagging

## For Non-Technical Users

This platform helps you:

1. Convert scanned documents into searchable text
2. Find connections between people and organizations
3. Track communication patterns
4. Identify key topics across large document sets
5. Protect privacy by automatically removing sensitive information

## For Developers

### Prerequisites

- Python 3.7+
- Poetry for dependency management
- Make for build automation
- Sufficient storage for document processing

### Installation

1. Clone the repository:

bash

git clone https://github.com/yourusername/switchboard.git
cd switchboard

2. Install dependencies:

bash

make setup

3. Run the preprocessing pipeline:

Check document sizes:

bash

make size-check

Verify OCR requirements:

bash

make ocr-check

Run OCR processing:

bash

make ocr

Test redaction (dry run):

bash

make redact MODE=dry-run

Run actual redaction:

bash

make redact

### Advanced Usage

Run email network analysis:

bash

make email-analysis

## Project Structure

### Pre-Processing Module
- **Document Standardization**
  - Handles various PDF formats and encodings
  - Normalizes text content for consistent processing
  - Supports batch processing with multiprocessing
  - Memory-efficient handling of large documents

- **OCR Processing**
  - Automatic detection of non-searchable PDFs
  - Multi-language OCR support (default: English)
  - In-place or separate output processing
  - Progress tracking and error handling

- **Automated Redaction**
  - Named Entity Recognition (NER) for sensitive data
  - Pattern matching for emails, phone numbers, etc.
  - Dry-run mode for verification
  - Detailed logging of redacted content

- **Size Analysis**
  - PDF size distribution visualization
  - Statistical analysis of document collections
  - Memory usage optimization
  - Batch processing recommendations

### Email Network Analysis
- **Relationship Extraction**
  - Sender/receiver identification
  - CC/BCC analysis
  - Thread reconstruction
  - Temporal pattern analysis

- **Network Visualization**
  - Interactive D3.js network graphs
  - Hierarchical organization views
  - Communication pattern analysis
  - Exportable visualization data

### Advanced Features

#### Topic Modeling
- Uses BERTopic for state-of-the-art topic detection
- Hierarchical topic clustering
- Interactive topic visualization
- Temporal topic evolution tracking

#### Entity Recognition
- Custom NER models for government documents
- Entity relationship mapping
- Confidence scoring
- Entity disambiguation

## Configuration

### Environment Variables

# Required
ELASTICSEARCH_URL=http://localhost:9200
PDF_STORAGE_PATH=/path/to/pdfs

# Optional
DEBUG_MODE=False
BATCH_SIZE=1000
MAX_WORKERS=4
OCR_LANGUAGE=eng

### Configuration Files
- `config/preprocessing.yaml`: Document processing settings
- `config/network.yaml`: Network analysis parameters
- `config/redaction.yaml`: PII detection rules

Example configuration:

preprocessing:
  chunk_size: 5000
  ocr:
    language: eng
    dpi: 300
    force: false
  redaction:
    enabled: true
    patterns:
      - type: email
        regex: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
      - type: phone
        regex: "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b"

## Examples

### Document Processing

# Process a single PDF with default settings
make ocr INPUT_FILE=document.pdf

# Batch process with custom settings
make ocr-batch INPUT_DIR=documents/ BATCH_SIZE=50 WORKERS=8

# Run redaction with custom patterns
make redact INPUT_FILE=document.pdf PATTERNS_FILE=custom_patterns.yaml

### Network Analysis

# Generate basic email network
make email-analysis INPUT_DIR=emails/

# Advanced analysis with temporal patterns
make email-analysis INPUT_DIR=emails/ TEMPORAL=true TIME_WINDOW=7d

# Export network data for visualization
make export-network FORMAT=d3 OUTPUT_FILE=network.json

### Topic Modeling

# Generate topic models
make topics INPUT_DIR=documents/ NUM_TOPICS=20

# Visualize topic evolution
make topic-viz INPUT_DIR=documents/ TIME_FIELD=date

## Security Considerations

### Data Protection
- All documents are processed locally
- Temporary files are securely deleted
- PII is redacted before any network analysis
- Encryption at rest for sensitive data

### Access Control
- Role-based access to different features
- Audit logging of all operations
- Configurable data retention policies
- Secure API authentication

### Compliance
- GDPR-compliant data handling
- FOIA processing guidelines
- Automated PII detection
- Data minimization practices

## System Requirements

### Hardware Recommendations
- **CPU**: 4+ cores recommended for OCR
- **RAM**: Minimum 8GB, 16GB+ recommended
- **Storage**: 
  - 10GB for base installation
  - 2-3x input data size for processing
  - SSD recommended for better performance

### Operating System Support
- **Linux**: Ubuntu 20.04+, CentOS 8+
- **macOS**: 10.15+
- **Windows**: 10+ with WSL2

### Software Dependencies
- **Required**:
  - Tesseract 4.0+
  - Elasticsearch 7.x
  - PostgreSQL 12+
- **Optional**:
  - Redis for caching
  - CUDA for GPU acceleration

## Troubleshooting

### Common Issues

#### OCR Processing
- **Issue**: Low quality text extraction
  - **Solution**: Adjust DPI settings in config
  - **Solution**: Try different OCR languages

- **Issue**: Memory errors during processing
  - **Solution**: Reduce batch size
  - **Solution**: Enable memory mapping

#### Network Analysis
- **Issue**: Slow graph generation
  - **Solution**: Use smaller time windows
  - **Solution**: Enable caching

- **Issue**: Missing connections
  - **Solution**: Check email pattern matching
  - **Solution**: Verify input data format

### Performance Optimization
1. **Document Processing**
   - Use SSD for temporary files
   - Enable multiprocessing
   - Optimize batch sizes

2. **Network Analysis**
   - Use indexed lookups
   - Enable result caching
   - Batch relationship updates

3. **Memory Usage**
   - Configure chunk sizes
   - Use memory mapping
   - Enable garbage collection

## Performance Considerations

### Memory Management
- Batch processing for large document sets
- Configurable chunk sizes for text processing
- Multiprocessing for CPU-intensive tasks
- Memory-mapped file handling for large PDFs

### Scalability
- Elasticsearch for efficient document indexing
- Distributed processing capabilities
- Configurable resource utilization
- Progress tracking and resumable processing

## Development Guidelines

### Adding New Features
1. Use the existing preprocessing pipeline structure
2. Implement proper error handling and logging
3. Add appropriate unit tests
4. Update documentation

### Code Style
- Follow PEP 8 guidelines
- Use type hints for better code clarity
- Document complex functions and classes
- Include usage examples in docstrings

## Architecture

### Data Flow
1. Document Intake → OCR/Text Extraction
2. Preprocessing & Standardization
3. Entity Recognition & Relationship Mapping
4. Topic Modeling & Clustering
5. Interactive Visualization

### Key Technologies
- SpaCy for NLP and entity recognition
- BERTopic for topic modeling
- D3.js for interactive visualizations
- Elasticsearch for document search

## Contributing

We welcome contributions! Key areas:
- Improved entity recognition
- Additional visualization types
- Performance optimizations
- Documentation improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Documentation

Detailed documentation for each module:
- [Pre-Processing Guide](docs/pre-processing.md)
- [Network Analysis Guide](docs/network-analysis.md)
- [Search Configuration](docs/search.md)
- [API Documentation](docs/api.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with support from [Your Organization]
- Uses open-source tools including SpaCy, BERTopic, and more
- Inspired by the need for better FOIA document analysis tools

---

For support, please open an issue or contact [your contact information].
