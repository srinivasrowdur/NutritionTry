#!/bin/bash

# PDF Chat API Google Cloud Build Deployment Script
# This script uses Cloud Build for a more streamlined deployment

set -e

# Configuration
PROJECT_ID="pa-sandbox-gen-ai-2"  # Replace with your actual Google Cloud project ID
REGION="us-central1"          # Replace with your preferred region
SERVICE_NAME="pdf-chat-api"

echo "🚀 PDF Chat API Google Cloud Build Deployment"
echo "============================================="

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
gcloud services enable artifactregistry.googleapis.com

# Grant Cloud Build the necessary permissions
echo "🔧 Setting up Cloud Build permissions..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create Artifact Registry repository
echo "🔧 Creating Artifact Registry repository..."
gcloud artifacts repositories create ${SERVICE_NAME}-repo \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for ${SERVICE_NAME}" \
    --quiet || echo "Repository already exists"

# Create a cloudbuild.yaml file
echo "🔧 Creating Cloud Build configuration..."
cat > cloudbuild.yaml << EOF
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${REGION}-docker.pkg.dev/\$PROJECT_ID/${SERVICE_NAME}-repo/${SERVICE_NAME}', '.']
  
  # Push the container image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${REGION}-docker.pkg.dev/\$PROJECT_ID/${SERVICE_NAME}-repo/${SERVICE_NAME}']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${SERVICE_NAME}'
      - '--image'
      - '${REGION}-docker.pkg.dev/\$PROJECT_ID/${SERVICE_NAME}-repo/${SERVICE_NAME}'
      - '--region'
      - '${REGION}'
      - '--platform'
      - 'managed'
      - '--port'
      - '8001'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--timeout'
      - '300'
      - '--concurrency'
      - '80'
      - '--max-instances'
      - '10'
      - '--set-env-vars'
      - 'OPENAI_API_KEY=${OPENAI_API_KEY},PYTHONUNBUFFERED=1'

images:
  - '${REGION}-docker.pkg.dev/\$PROJECT_ID/${SERVICE_NAME}-repo/${SERVICE_NAME}'
EOF

# Submit the build
echo "🚀 Submitting build to Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

# Clean up the cloudbuild.yaml file
rm cloudbuild.yaml

# Get the service URL
echo "⏳ Waiting for deployment to complete..."
sleep 30
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo ""
echo "🎉 Deployment successful!"
echo "============================================="
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