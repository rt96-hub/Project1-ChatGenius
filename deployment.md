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

## Process Management in EC2

### Process Persistence
When running Docker containers in EC2, there are several important considerations for process persistence:

1. **Docker Daemon**:
   - Docker containers will continue running after SSH disconnection by default
   - The Docker daemon runs as a system service and persists across sessions
   - Using `docker-compose up -d` ensures containers run in detached mode

2. **Auto-start on System Reboot**:
   ```bash
   # Enable Docker service to start on boot
   sudo systemctl enable docker

   # Create a startup script (e.g., /etc/systemd/system/docker-compose-app.service):
   sudo nano /etc/systemd/system/docker-compose-app.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Docker Compose Application Service
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/path/to/your/app
   ExecStart=/usr/bin/docker-compose up -d
   ExecStop=/usr/bin/docker-compose down
   TimeoutStartSec=0

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable and start the service:
   ```bash
   sudo systemctl enable docker-compose-app
   sudo systemctl start docker-compose-app
   ```

3. **Process Monitoring**:
   - Use `docker-compose ps` to check container status
   - Monitor container health with:
     ```bash
     docker events --filter 'type=container'
     docker stats
     ```
   - Consider using monitoring tools like Prometheus/Grafana

4. **Handling System Updates**:
   - Set up automatic container restart policies in docker-compose.yml:
     ```yaml
     services:
       frontend:
         restart: unless-stopped
       backend:
         restart: unless-stopped
       db:
         restart: unless-stopped
     ```

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

## Network Access Troubleshooting

### EC2 Access Checklist

1. **Security Group Configuration**:
   - Verify inbound rules in EC2 security group:
     ```
     Type        Port    Source
     ----        ----    ------
     HTTP        80      0.0.0.0/0
     Custom TCP  3000    0.0.0.0/0
     Custom TCP  8000    0.0.0.0/0
     SSH         22      Your IP
     ```
   - Add these rules in EC2 Console: Security Groups → Inbound Rules → Edit

2. **Docker Network Configuration**:
   - Ensure containers are binding to `0.0.0.0` not just `localhost`:
     ```yaml
     # docker-compose.yml
     services:
       frontend:
         # ...
         ports:
           - "0.0.0.0:3000:3000"  # Bind to all interfaces
       backend:
         # ...
         ports:
           - "0.0.0.0:8000:8000"  # Bind to all interfaces
     ```

3. **Firewall Settings**:
   ```bash
   # Check if ports are blocked by firewall
   sudo ufw status

   # If firewall is active, allow ports
   sudo ufw allow 3000
   sudo ufw allow 8000
   ```

4. **Verify Container Status**:
   ```bash
   # Check if containers are running
   docker-compose ps

   # Check container logs for binding issues
   docker-compose logs frontend
   docker-compose logs backend

   # Verify port bindings
   sudo netstat -tulpn | grep -E '3000|8000'
   ```

5. **Common Issues and Solutions**:
   - If you can't access port 3000:
     1. Verify the container is running: `docker-compose ps`
     2. Check container logs: `docker-compose logs frontend`
     3. Ensure Next.js is configured to listen on all interfaces:
        ```js
        // next.config.js
        module.exports = {
          webpackDevMiddleware: config => {
            return {
              ...config,
              watchOptions: {
                poll: 1000,
                aggregateTimeout: 300,
              }
            }
          },
          // Add this section
          server: {
            host: '0.0.0.0',
            port: 3000
          }
        }
        ```
     4. Try accessing using the full URL: `http://[EC2-PUBLIC-IP]:3000`

   - If the page loads but API calls fail:
     1. Check if backend port 8000 is accessible
     2. Verify environment variables are correctly set:
        - NEXT_PUBLIC_API_URL should use EC2 public IP/DNS
        - NEXT_PUBLIC_WS_URL should use EC2 public IP/DNS

// ... rest of existing code ... 