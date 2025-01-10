# Docker Configuration and Deployment Guide

## Local Development Setup

### Overview
The application consists of three main services:
- Frontend (Next.js application)
- Backend (Python/FastAPI application)
- Database (PostgreSQL)

### Local Docker Configuration
The local development environment is configured in `docker-compose.local.yml` and includes:

1. **Frontend Service**:
   - Builds from `frontend/Dockerfile`
   - Runs on port 3000
   - Uses development environment with hot-reloading
   - Mounts local code directory for real-time changes
   - Environment variables configured for local development
   - Dependencies on backend service

2. **Backend Service**:
   - Builds from `backend/Dockerfile`
   - Runs on port 8000
   - Uses uvicorn with --reload flag for development
   - Mounts local code directory for real-time changes
   - Connects to PostgreSQL database
   - Environment variables for Auth0 and database configuration

3. **Database Service**:
   - Uses PostgreSQL 15
   - Runs on port 5432
   - Persistent data storage using Docker volumes
   - Default credentials (configurable via environment variables)

### Running Locally
1. Copy `.env.example` to `.env.local` and fill in the required variables
2. Run `./local-dev.sh` which will:
   - Stop any running containers
   - Build and start all services with hot-reloading
   - Mount local volumes for development

## Production Deployment (EC2)

### Key Differences from Local Setup
The production configuration (`docker-compose.yml`) differs in several ways:

1. **Volume Mounting**:
   - No source code mounting (uses built containers)
   - Only database volume remains for persistence

2. **Environment Variables**:
   - Uses EC2_PUBLIC_DNS for API and WebSocket URLs
   - Production-specific Auth0 configuration
   - Secure database credentials

3. **Build Configuration**:
   - Frontend builds the Next.js application
   - No hot-reloading or development mode
   - Optimized for production performance

### Deployment Steps for EC2

1. **EC2 Instance Setup**:
   - Launch an EC2 instance with sufficient resources
   - Configure security groups:
     - Port 80/443 for HTTP/HTTPS
     - Port 3000 for frontend
     - Port 8000 for backend
     - Port 5432 for database (restrict to internal access)

2. **Instance Preparation**:
   ```bash
   # Update system
   sudo apt-get update && sudo apt-get upgrade -y

   # Install Docker and Docker Compose
   sudo apt-get install docker.io docker-compose -y

   # Add user to docker group
   sudo usermod -aG docker ${USER}
   ```

3. **Application Deployment**:
   ```bash
   # Clone repository
   git clone [your-repo-url]

   # Create and configure .env file
   cp .env.example .env
   # Edit .env with production values, including:
   # - EC2_PUBLIC_DNS
   # - Auth0 credentials
   # - Database credentials

   # Start services
   docker-compose up -d
   ```

4. **Database Migration**:
   - Run migrations after deployment:
     ```bash
     docker-compose exec backend alembic upgrade head
     ```

### Important Security Considerations

1. **Environment Variables**:
   - Never commit `.env` files with sensitive data
   - Use secure secrets management in production
   - Rotate credentials regularly

2. **Network Security**:
   - Configure EC2 security groups properly
   - Use HTTPS in production
   - Restrict database access to internal network

3. **Monitoring and Maintenance**:
   - Set up logging and monitoring
   - Regular backups of database volume
   - Keep Docker images updated

### Scaling Considerations

1. **Database**:
   - Consider using managed database service (RDS)
   - Implement backup strategy
   - Monitor performance and scale as needed

2. **Application**:
   - Consider using container orchestration (ECS/Kubernetes)
   - Implement load balancing
   - Set up auto-scaling

## Troubleshooting

1. **Common Issues**:
   - Check container logs: `docker-compose logs [service]`
   - Verify environment variables
   - Ensure ports are not in use
   - Check volume permissions

2. **Container Management**:
   ```bash
   # View running containers
   docker-compose ps

   # Restart services
   docker-compose restart [service]

   # View logs
   docker-compose logs -f [service]
   ``` 