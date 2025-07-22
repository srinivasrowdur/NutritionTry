#!/bin/bash

# PDF Chat API Google Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID="pa-sandbox-gen-ai-2"  # Replace with your actual Google Cloud project ID
REGION="us-central1"          # Replace with your preferred region
SERVICE_NAME="pdf-chat-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
PORT=8001

echo "🚀 PDF Chat API Google Cloud Run Deployment"
echo "==========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    exit 1
fi

# Load environment variables
source .env

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not found in .env file!"
    exit 1
fi

# Check if PROJECT_ID is set to a real value
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Error: Please update PROJECT_ID in this script with your actual Google Cloud project ID!"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "📋 Configuration:"
echo "   • Project ID: ${PROJECT_ID}"
echo "   • Region: ${REGION}"
echo "   • Service Name: ${SERVICE_NAME}"
echo "   • Image Name: ${IMAGE_NAME}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed!"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please authenticate with Google Cloud..."
    gcloud auth login
fi

# Set the project
echo "🔧 Setting Google Cloud project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Configure Docker to use gcloud as a credential helper
echo "🔧 Configuring Docker authentication..."
gcloud auth configure-docker

# Build and push the Docker image
echo "🔨 Building and pushing Docker image..."
docker build -t ${IMAGE_NAME} .

echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."

# Create a temporary .env.yaml file for Cloud Run
echo "🔧 Creating environment configuration..."
cat > .env.yaml << EOF
OPENAI_API_KEY: "${OPENAI_API_KEY}"
EOF

# Deploy the service
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --port ${PORT} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10 \
    --env-vars-file .env.yaml \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Clean up temporary file
rm .env.yaml

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo ""
echo "🎉 Deployment successful!"
echo "==========================================="
echo "🌐 Service URL: ${SERVICE_URL}"
echo "📖 API Docs: ${SERVICE_URL}/docs"
echo "📋 Alternative Docs: ${SERVICE_URL}/redoc"
echo "🏥 Health Check: ${SERVICE_URL}/health"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
echo "   • Update service: gcloud run services update ${SERVICE_NAME} --region=${REGION}"
echo "   • Delete service: gcloud run services delete ${SERVICE_NAME} --region=${REGION}"
echo ""
echo "📝 Note: The service is configured to allow unauthenticated access."
echo "   For production use, consider removing --allow-unauthenticated"
echo "   and implementing proper authentication." 