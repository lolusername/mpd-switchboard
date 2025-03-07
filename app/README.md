# Switchboard

A document search platform for D4BL that makes email PDFs searchable and analyzable.

## What It Does
- Processes email PDF documents
- Makes text searchable with semantic search capabilities
- Provides a modern web interface to search and explore documents
- Highlights relevant text snippets in search results
- Allows pinning and annotating important documents

## Tech Stack
- Python 3.12 (FastAPI backend)
- Elasticsearch OSS 7.10.2 (search engine)
- Nuxt 3 (Vue.js frontend)
- Nginx (reverse proxy)
- Docker & Docker Compose

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Make

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/d4bl/switchboard.git
   cd switchboard/app
   ```

2. Start the development environment:
   ```bash
   make rebuild
   ```
   This will:
   - Build all Docker containers
   - Start the services in development mode
   - Set up Elasticsearch with proper settings

3. Access the application:
   - Web UI: http://localhost
   - API: http://localhost/api
   - API Documentation: http://localhost/api/docs

### Development Workflow
- Frontend code is in `frontend/`
- Backend code is in `api/`
- Nginx configurations in `nginx/`
  - `development.conf` - Local development
  - `production.conf` - Production deployment

### Common Development Commands
```bash
# Start all services
make rebuild

# View logs
make logs

# Stop all services
make down

# Check service status
make check-rebuild
```

## Production Deployment

### Prerequisites
- AWS EC2 instance
- Domain name pointing to EC2 (currently using switchboard.miski.studio)
- SSL certificates (handled by Let's Encrypt)

### Deployment Steps
1. Ensure your AWS credentials are configured

2. Deploy to production:
   ```bash
   make deploy
   ```
   This will:
   - Clean up the EC2 instance
   - Copy application files
   - Set up SSL certificates
   - Build and start services in production mode

3. Verify deployment:
   ```bash
   make check-deployment
   ```

### Production Configuration
- Uses `docker-compose.production.yml`
- SSL certificates managed by Let's Encrypt
- Environment variables in `.env.production`
- Production-specific Nginx config in `nginx/production.conf`

## Architecture

### Components
- **Frontend**: Nuxt 3 application with modern UI
- **Backend**: FastAPI serving the API
- **Search**: Elasticsearch OSS for document indexing and search
- **Nginx**: Reverse proxy handling SSL and routing

### API Endpoints
- `POST /api/search` - Search documents
- `GET /api/health` - Service health check
- `GET /api/routes` - List available routes
- `GET /api/index-stats` - Elasticsearch index statistics

## Troubleshooting

### Common Issues
1. **Elasticsearch fails to start**
   - Check system limits: `sysctl -w vm.max_map_count=262144`
   - Verify Docker memory settings

2. **SSL certificate issues**
   - Run `make check-deployment` to verify certificate status
   - Check Nginx logs for certificate errors

3. **API connection issues**
   - Verify Elasticsearch is running and healthy
   - Check API logs with `make logs`

### Useful Commands
```bash
# Check deployment status
make check-deployment

# View service logs
make logs

# Restart EC2 instance
make force-restart-instance

# Debug SSH connection
make debug-ssh
```

## Security
- HTTPS enforced in production
- API endpoints properly secured
- Regular security updates
- Environment-specific configurations
- Proper CORS settings

## Contributing
1. Create a feature branch
2. Make changes
3. Test locally with `make rebuild`
4. Submit a pull request

## License
Copyright © 2024 Data for Black Lives