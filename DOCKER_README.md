# PDF Chat API - Docker Deployment

This guide will help you deploy the PDF Chat API using Docker and Docker Compose.

## 🐳 Prerequisites

- **Docker** installed on your system
- **Docker Compose** installed
- **OpenAI API Key** for the AI functionality

## 📁 Project Structure

```
NutritionTry/
├── appapi.py              # FastAPI application
├── app.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── deploy.sh             # Deployment script
├── test_api.py           # API test script
├── .env                  # Environment variables (create this)
├── .dockerignore         # Docker ignore file
├── pdf/                  # PDF files folder
│   ├── Chapter 1.pdf     # Your PDF documents
│   └── processed/        # Processed PDFs (auto-created)
└── tmp/                  # Vector database (auto-created)
```

## 🚀 Quick Start

### 1. Set up Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Add PDF Files

Place your PDF files in the `pdf/` folder:

```bash
# Create pdf folder if it doesn't exist
mkdir -p pdf

# Copy your PDF files
cp /path/to/your/documents/*.pdf pdf/
```

### 3. Deploy with Docker

#### Option A: Using the deployment script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

#### Option B: Manual deployment

```bash
# Build the Docker image
docker-compose build

# Start the services
docker-compose up -d

# Check the logs
docker-compose logs -f
```

### 4. Test the API

```bash
# Run the test script
python test_api.py

# Or test manually
curl http://localhost:8001/status
```

## 🌐 Access the API

Once deployed, you can access:

- **API Base URL**: http://localhost:8001
- **Interactive Documentation**: http://localhost:8001/docs
- **Alternative Documentation**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/status

## 📡 API Usage

### Send a Question

```bash
curl -X POST "http://localhost:8001/runs" \
     -F "message=What are the main topics covered in the documents?"
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8001/runs",
    data={"message": "What are the main topics covered in the documents?"}
)

print(response.json())
```

## 🔧 Docker Commands

### Basic Operations

```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f

# Restart the service
docker-compose restart

# Rebuild and restart
docker-compose up --build -d
```

### Container Management

```bash
# List running containers
docker ps

# View container logs
docker logs pdf-chat-api

# Execute commands in container
docker exec -it pdf-chat-api bash

# Remove containers and volumes
docker-compose down -v
```

## 📁 File Management

### Adding New PDFs

1. **Copy new PDFs** to the `pdf/` folder
2. **Restart the service** to process new files:
   ```bash
   docker-compose restart
   ```

### Persistent Storage

- **PDF files**: Mounted from `./pdf/` to `/app/pdf/`
- **Vector database**: Stored in Docker volume `pdf_vector_db`
- **Processed files**: Automatically moved to `pdf/processed/`

## 🔍 Monitoring

### Health Checks

The container includes automatic health checks:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View health check logs
docker inspect pdf-chat-api | grep -A 10 "Health"
```

### Logs

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f pdf-chat-api

# View last 100 lines
docker-compose logs --tail=100 pdf-chat-api
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 8001
lsof -i :8001

# Stop the service and change port in docker-compose.yml
docker-compose down
# Edit docker-compose.yml to use a different port
```

#### 2. Environment Variables Not Loaded

```bash
# Check if .env file exists
ls -la .env

# Verify environment variables
docker-compose config
```

#### 3. PDF Processing Issues

```bash
# Check if PDFs are accessible
docker exec -it pdf-chat-api ls -la /app/pdf/

# View processing logs
docker-compose logs pdf-chat-api | grep -i "pdf"
```

#### 4. Memory Issues

```bash
# Check container resource usage
docker stats pdf-chat-api

# Increase memory limits in docker-compose.yml if needed
```

### Debug Mode

Run the container in debug mode:

```bash
# Stop the service
docker-compose down

# Run in foreground with logs
docker-compose up
```

## 🔒 Security Considerations

1. **API Key**: Never commit your `.env` file to version control
2. **Network**: The API is exposed on localhost only by default
3. **Volumes**: PDF files are mounted read-write for processing
4. **Health Checks**: Regular health monitoring is enabled

## 📈 Scaling

### Multiple Instances

```bash
# Scale to multiple instances
docker-compose up -d --scale pdf-chat-api=3
```

### Production Deployment

For production, consider:

1. **Reverse Proxy**: Use nginx or traefik
2. **SSL/TLS**: Add HTTPS termination
3. **Load Balancing**: Distribute requests across instances
4. **Monitoring**: Add Prometheus/Grafana
5. **Logging**: Centralized logging with ELK stack

## 🧹 Cleanup

### Remove Everything

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove the Docker image
docker rmi nutritiontry_pdf-chat-api

# Clean up any unused resources
docker system prune -f
```

### Keep Data

```bash
# Stop containers but keep volumes
docker-compose down

# Remove containers but keep volumes
docker-compose down --remove-orphans
```

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Ensure PDF files are accessible
4. Check Docker and Docker Compose versions

## 🎉 Success!

Your PDF Chat API is now running in Docker! You can:

- Ask questions about your PDF documents
- Add new PDFs and restart to process them
- Scale the service as needed
- Monitor performance and health

The API is ready for integration with your applications! 🚀 