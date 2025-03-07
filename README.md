# Switchboard: Email Document Analysis Platform

A specialized platform for analyzing large collections of email documents, built for Data for Black Lives (D4BL). Switchboard makes email archives searchable and analyzable through advanced text processing and a modern web interface.

## Quick Access
- **Production Site**: https://switchboard.miski.studio/
- **Local Development**: http://localhost

## Core Features

### 1. Document Processing & Ingestion
- **Email PDF Processing**
  - Handles large collections of email PDFs
  - Automatic OCR for scanned documents
  - Extracts text content while preserving email structure
  - Processes metadata (From, To, Subject, Date)
  - Supports batch ingestion via S3 or local files

- **OCR Capabilities**
  - Automatic detection of scanned PDFs
  - OCR processing using Tesseract
  - Handles both text and scanned PDFs in the same collection
  - Preserves document structure during OCR
  - Pre-processes images for better OCR accuracy

### 2. Search & Analysis
- **Semantic Search**
  - Full-text search across all documents
  - Relevance-based result ranking
  - Highlighted text matches in context
  - Real-time search as you type

- **Document Management**
  - Pin important documents for quick access
  - Add annotations to documents
  - Track document relevance scores
  - View full document content with formatted email headers

### 3. User Interface
- **Modern Web Interface**
  - Clean, intuitive search interface
  - Document preview with highlights
  - Pinned documents bar for quick access
  - Annotation system for notes and comments

## Technical Architecture

### Components
1. **Backend (Python/FastAPI)**
   - FastAPI for API endpoints
   - Elasticsearch client for search
   - JWT-based authentication
   - Environment-based configuration
   - OCR processing pipeline

2. **Search Engine**
   - Elasticsearch OSS 7.10.2
   - Custom mapping for email documents
   - Optimized for text search
   - Configurable relevance scoring

3. **Frontend (Nuxt 3/Vue.js)**
   - Modern reactive interface
   - Real-time search updates
   - Document state management
   - Mobile-responsive design

4. **Infrastructure**
   - Docker containerization
   - Nginx reverse proxy
   - Let's Encrypt SSL (production)
   - AWS EC2 hosting

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Make
- At least 4GB RAM (8GB recommended for OCR processing)
- Sufficient disk space for document storage

### System Dependencies
All dependencies are handled by Docker, including:
- Tesseract OCR engine
- PDF processing libraries
- Python OCR dependencies
- Image processing tools

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/d4bl/switchboard.git
   cd switchboard/app
   ```

2. Start development environment:
   ```bash
   make rebuild
   ```

3. Access the application:
   - Web Interface: http://localhost
   - API: http://localhost/api
   - API Docs: http://localhost/api/docs

### Production Deployment
1. Configure AWS and domain:
   - Point domain to EC2 instance
   - Configure SSL certificates
   - Set up security groups

2. Deploy:
   ```bash
   make deploy
   ```

3. Verify deployment:
   ```bash
   make check-deployment
   ```

## Document Processing Pipeline

### 1. Data Preparation
- Place email PDFs in data directory
- Organize by collection if needed
- Ensure consistent file naming
- No need to separate scanned and digital PDFs

### 2. Document Processing
- **Text Extraction**
  - Automatic detection of PDF type (scanned vs digital)
  - Direct text extraction for digital PDFs
  - OCR processing for scanned documents
  - Preservation of email structure and formatting

- **OCR Pipeline**
  - Image preprocessing for better quality
  - Tesseract OCR for text extraction
  - Post-processing to maintain email format
  - Quality checks on OCR output

### 3. Ingestion Process
- **Local Ingestion**
  ```bash
  make ingest
  ```
- **S3 Ingestion**
  - Configure AWS credentials
  - Set S3 bucket in configuration
  - Run ingestion command

### 4. Search Index Creation
- Automatic index creation
- Custom mappings for email fields
- Optimized for search performance
- Full-text indexing of OCR'd content

## Configuration

### Development
- `docker-compose.yml` - Development setup
- `nginx/development.conf` - Development server
- `.env.development` - Development variables

### Production
- `docker-compose.production.yml` - Production setup
- `nginx/production.conf` - Production server with SSL
- `.env.production` - Production variables

## Common Tasks

### Managing Documents
1. **Adding New Documents**
   - Add PDFs to data directory
   - Run ingestion process
   - Verify in search interface

2. **Updating Existing Documents**
   - Replace PDFs in data directory
   - Re-run ingestion for updates
   - Check index statistics

### System Maintenance
1. **Checking System Status**
   ```bash
   make check-deployment  # Production
   make check-rebuild    # Development
   ```

2. **Viewing Logs**
   ```bash
   make logs
   ```

3. **Restarting Services**
   ```bash
   make rebuild  # Development
   make deploy   # Production
   ```

## Troubleshooting

### Common Issues
1. **Search Not Working**
   - Check Elasticsearch status
   - Verify index exists
   - Check API connectivity

2. **OCR Issues**
   - Verify Tesseract installation in container
   - Check PDF quality and resolution
   - Monitor OCR processing logs
   - Try reprocessing problematic documents
   - Check container memory limits

3. **Deployment Issues**
   - Verify AWS credentials
   - Check SSL certificates
   - Review nginx logs

4. **Performance Issues**
   - Monitor Elasticsearch memory
   - Check system resources
   - Review request logs
   - Adjust OCR batch size if needed

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test locally with `make rebuild`
5. Submit a pull request

## License
Copyright © 2024 Data for Black Lives

## Acknowledgments
Built by Miski Studio for Data for Black Lives

## AWS Setup & Production Deployment

### 1. AWS Account Setup
1. **Create AWS Account**
   - Sign up for AWS account if you don't have one
   - Enable MFA for root account
   - Create an IAM user with admin access for deployment

2. **Required AWS Services**
   - EC2: For hosting the application
   - Route 53: For domain management (optional)
   - S3: For document storage (optional)
   - IAM: For security management

### 2. EC2 Instance Setup
1. **Launch EC2 Instance**
   ```bash
   # Use these specifications
   Instance Type: t2.medium (minimum)
   Storage: 30GB+ SSD
   OS: Ubuntu Server 22.04 LTS
   ```

2. **Security Group Configuration**
   ```bash
   # Required ports
   SSH (22): Your IP
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   ```

3. **Create Key Pair**
   - Download the .pem file
   - Set correct permissions:
     ```bash
     chmod 400 switchboard-key.pem
     mv switchboard-key.pem ~/.ssh/
     ```

### 3. Domain Configuration
1. **Register Domain** (if not using Route 53)
   - Purchase domain from any registrar
   - Note down nameservers

2. **DNS Configuration**
   - Create A record pointing to EC2 IP:
     ```
     Type: A
     Name: switchboard
     Value: <EC2-IP-Address>
     TTL: 300
     ```
   - Add these records if using email:
     ```
     MX record: for email handling
     TXT record: for SPF verification
     ```

3. **SSL Certificate**
   - SSL is handled automatically by the deployment script using Let's Encrypt
   - Ensure domain is pointing to EC2 IP before deploying

### 4. Environment Setup
1. **Create Production Environment File**
   ```bash
   # .env.production
   NODE_ENV=production
   FRONTEND_PORT=3000
   FRONTEND_HOST=0.0.0.0
   SECRET_KEY=<your-secure-key>
   NUXT_PUBLIC_API_BASE=https://your-domain.com/api
   ELASTICSEARCH_HOST=http://elasticsearch:9200
   ```

2. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your AWS credentials
   AWS_ACCESS_KEY_ID=<your-key>
   AWS_SECRET_ACCESS_KEY=<your-secret>
   AWS_DEFAULT_REGION=us-east-1
   ```

### 5. Initial Deployment
1. **Update Makefile Configuration**
   ```bash
   # Update these variables in Makefile
   EC2_IP := <your-ec2-ip>
   PEM_PATH := ~/.ssh/switchboard-key.pem
   ```

2. **Deploy Application**
   ```bash
   make deploy
   ```

3. **Verify Deployment**
   ```bash
   make check-deployment
   ```

### 6. Elasticsearch Data Migration
1. **Create Snapshot of Local Data**
   ```bash
   # 1. Register snapshot repository in local Elasticsearch
   curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
   {
     "type": "fs",
     "settings": {
       "location": "/usr/share/elasticsearch/snapshots"
     }
   }'

   # 2. Create snapshot
   curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
   ```

2. **Transfer Snapshot to Production**
   ```bash
   # 1. Copy snapshot files to EC2
   rsync -avz -e "ssh -i ~/.ssh/switchboard-key.pem" \
     ./snapshots/ \
     ubuntu@<EC2-IP>:/home/ubuntu/switchboard/app/snapshots/

   # 2. Register snapshot repository in production
   ssh -i ~/.ssh/switchboard-key.pem ubuntu@<EC2-IP> \
     "curl -X PUT 'http://localhost:9200/_snapshot/backup' -H 'Content-Type: application/json' -d'{
       \"type\": \"fs\",
       \"settings\": {
         \"location\": \"/usr/share/elasticsearch/snapshots\"
       }
     }'"

   # 3. Restore snapshot in production
   ssh -i ~/.ssh/switchboard-key.pem ubuntu@<EC2-IP> \
     "curl -X POST 'http://localhost:9200/_snapshot/backup/snapshot_1/_restore?wait_for_completion=true'"
   ```

### 7. Maintenance Tasks
1. **Backup Elasticsearch Data**
   ```bash
   # Create regular snapshots
   make create-snapshot
   ```

2. **Monitor Resources**
   ```bash
   # Check EC2 metrics
   make check-ec2
   
   # View application logs
   make logs
   ```

3. **Update SSL Certificates**
   ```bash
   # Certificates auto-renew, but you can force renewal
   make renew-ssl
   ```

### 8. Troubleshooting Production
1. **Common Issues**
   - **Connection Timeout**
     ```bash
     # Check security groups
     make check-security-group
     ```
   
   - **SSL Certificate Issues**
     ```bash
     # Verify SSL setup
     make check-ssl
     ```
   
   - **Elasticsearch Problems**
     ```bash
     # Check ES health
     make check-es
     ```

2. **Recovery Procedures**
   - **Service Recovery**
     ```bash
     # Restart all services
     make redeploy
     ```
   
   - **Data Recovery**
     ```bash
     # Restore from latest snapshot
     make restore-snapshot
     ```

## Developer Learning Guide

<details>
<summary>🎓 Prerequisites</summary>

- Basic JavaScript/TypeScript
- Basic Python (NumPy, Pandas)
- HTML/CSS fundamentals
- Git basics
</details>

<details>
<summary>🚀 Frontend Development</summary>

### Vue.js & Nuxt Fundamentals 
```bash
# Start with Vue 3 Composition API
npm create vue@latest my-first-vue-app
cd my-first-vue-app
npm install
npm run dev
```

#### Core Concepts
- Vue 3 Composition API
  - `ref()`, `reactive()`, `computed()`
  - Components and props
  - Event handling
  - Lifecycle hooks

#### Practice Projects
1. Todo App
   - Local storage integration
   - CRUD operations
   - State management

2. Search Interface
   - API integration
   - Real-time updates
   - Error handling

### State Management & API Integration
```typescript
// Example of composable for API calls
export function useApi() {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(false)

  async function fetchData(url: string) {
    loading.value = true
    try {
      const response = await fetch(url)
      data.value = await response.json()
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  return { data, error, loading, fetchData }
}
```

### Modern CSS & UI Design (2 weeks)
```bash
# Set up Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
```
</details>

<details>
<summary>⚙️ Backend Development </summary>

### FastAPI Fundamentals (2-3 weeks)
```python
# Basic FastAPI setup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Database & Search (3-4 weeks)
```python
# Elasticsearch setup
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

async def search_documents(query: str):
    result = es.search(
        index="documents",
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]
                }
            }
        }
    )
    return result["hits"]["hits"]
```

### Document Processing (2-3 weeks)
```python
# PDF & OCR Processing
import pypdf
from PIL import Image
import pytesseract

def extract_text(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        return "".join(page.extract_text() for page in reader.pages)

def process_scanned_pdf(pdf_path: str) -> str:
    images = convert_pdf_to_images(pdf_path)
    return "".join(pytesseract.image_to_string(image) for image in images)
```
</details>

<details>
<summary>🛠️ DevOps & Deployment (1-2 months)</summary>

### Docker & Containerization
```dockerfile
# Python API Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### AWS Setup
```bash
# Essential AWS commands
aws configure                    # Set up credentials
aws ec2 describe-instances      # List EC2 instances
aws s3 ls                       # List S3 buckets
aws route53 list-hosted-zones   # List DNS zones
```
</details>

<details>
<summary>🏗️ Practice Projects</summary>

### 1. Simple Search Engine 
- Frontend search interface
- Elasticsearch integration
- Result highlighting
- Basic filtering

### 2. Document Processor 
- PDF text extraction
- OCR implementation
- Document storage
- Progress tracking

### 3. Full Stack App 
- User authentication
- Document management
- Search functionality
- AWS deployment
</details>

<details>
<summary>📚 Learning Resources</summary>

### Documentation
- [Vue.js Guide](https://vuejs.org/guide/introduction.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Elasticsearch Guide](https://www.elastic.co/guide/index.html)

### Video Courses
- Vue Mastery (Vue.js)
- TestDriven.io (FastAPI)
- AWS Certified Developer

</details>

<details>
<summary>💡 Development Tips</summary>

### Start Small
- Build components in isolation
- Use dummy data initially
- Add features incrementally


### Code Organization
```
project/
├── frontend/
│   ├── components/
│   ├── composables/
│   └── pages/
├── backend/
│   ├── api/
│   ├── services/
│   └── models/
└── docker/
```

### Performance Tips
- Implement caching
- Use pagination
- Optimize search queries
- Monitor resource usage
</details>

<details>
<summary>📋 Document Processing Pipeline Overview</summary>

## How Switchboard Processes Your Documents

### 1. Document Collection & Analysis
- **What It Does**:
  - Automatically analyzes each email PDF
  - Determines if it's a regular PDF or scanned document
  - Preserves email headers (From, To, Subject, Date)
  - Maintains original document structure

- **Why It Matters**:
  - No manual sorting needed
  - Handles mixed collections of documents
  - Preserves important metadata
  - Saves hours of manual processing

### 2. Intelligent Text Extraction
- **For Digital PDFs**:
  - Direct text extraction
  - Maintains formatting
  - Preserves links and attachments
  - Fast processing

- **For Scanned Documents**:
  - Advanced OCR (Optical Character Recognition)
  - Image enhancement for better results
  - Handles poor quality scans
  - Supports multiple languages

### 3. Data Enhancement
- **Email Structure Preservation**:
  - Automatically identifies email parts
  - Extracts sender/recipient information
  - Preserves date and time data
  - Maintains conversation threads

- **Content Organization**:
  - Automatic categorization
  - Key information extraction
  - Relationship mapping
  - Topic identification

### 4. Search Optimization
- **What We Index**:
  - Full email content
  - Sender/recipient information
  - Dates and timestamps
  - Attachments and references

- **Search Capabilities**:
  - Natural language search
  - Exact phrase matching
  - Date range filtering
  - Sender/recipient filtering

### 5. Storage & Security
- **Data Protection**:
  - Secure document storage
  - Access control
  - Audit logging
  - Regular backups

- **Compliance Features**:
  - Data encryption
  - Access tracking
  - Retention policies
  - Export capabilities

</details>

<details>
<summary>💡 Benefits for Nonprofits</summary>

## Why Switchboard Makes Sense for Your Organization

### 1. Time & Resource Savings
- **Automated Processing**
  - Reduces manual data entry by 90%
  - Processes thousands of documents automatically
  - Frees up staff for important work
  - Reduces processing errors

- **Quick Implementation**
  - Ready to use in days, not months
  - Minimal training required
  - Works with existing documents
  - Scalable as needs grow

### 2. Enhanced Accessibility
- **Better Document Access**
  - Find any document in seconds
  - Full text search capability
  - Mobile-friendly interface
  - Remote access support

- **Improved Collaboration**
  - Share documents easily
  - Add notes and annotations
  - Track important findings
  - Team-based organization

### 3. Cost Effectiveness
- **Resource Optimization**
  - Reduced storage costs
  - Lower processing overhead
  - Minimal IT requirements
  - Scalable pricing

- **Long-term Benefits**
  - Improved productivity
  - Better data organization
  - Enhanced decision making
  - Sustainable growth

### 4. Real-World Applications
- **Common Use Cases**
  - Historical email archives
  - Document digitization
  - Research projects
  - Compliance requirements

- **Success Stories**
  - [Case study examples can be added here]
  - [Testimonials can be added here]
  - [Impact metrics can be added here]

</details>

<details>
<summary>📊 Implementation & Support</summary>

## Getting Started with Switchboard

### 1. Initial Setup
- Assessment of your needs
- Document inventory
- System configuration
- Team training

### 2. Migration Process
- Staged implementation
- Data validation
- Quality assurance
- Performance tuning

### 3. Ongoing Support
- Technical assistance
- Regular updates
- Performance monitoring
- Training resources

### 4. Success Metrics
- Document processing speed
- Search accuracy
- User adoption
- Time savings

</details>