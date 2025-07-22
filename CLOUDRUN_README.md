# Google Cloud Run Deployment Guide

This guide will help you deploy your PDF Chat API to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud Project**: Create a new project or use an existing one
3. **Google Cloud CLI**: Install the gcloud CLI tool
4. **Docker**: Ensure Docker is installed and running locally

## Setup Instructions

### 1. Install Google Cloud CLI

**macOS (using Homebrew):**
```bash
brew install google-cloud-sdk
```

**macOS (manual installation):**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Other platforms:** Visit [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install)

### 2. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Set up your project

```bash
# List your projects
gcloud projects list

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID
```

### 4. Enable required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 5. Configure Docker authentication

```bash
gcloud auth configure-docker
```

## Deployment

### Quick Deployment

1. **Update the deployment script:**
   Edit `deploy-cloudrun.sh` and replace `your-project-id` with your actual Google Cloud project ID.

2. **Ensure your .env file exists:**
   ```bash
   echo "OPENAI_API_KEY=your_actual_openai_api_key" > .env
   ```

3. **Run the deployment script:**
   ```bash
   ./deploy-cloudrun.sh
   ```

### Manual Deployment

If you prefer to deploy manually, follow these steps:

1. **Build and tag the Docker image:**
   ```bash
   PROJECT_ID="your-project-id"
   SERVICE_NAME="pdf-chat-api"
   IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
   
   docker build -t ${IMAGE_NAME} .
   ```

2. **Push the image to Google Container Registry:**
   ```bash
   docker push ${IMAGE_NAME}
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy ${SERVICE_NAME} \
       --image ${IMAGE_NAME} \
       --platform managed \
       --region us-central1 \
       --port 8001 \
       --allow-unauthenticated \
       --memory 2Gi \
       --cpu 2 \
       --timeout 300 \
       --concurrency 80 \
       --max-instances 10 \
       --set-env-vars "OPENAI_API_KEY=your_actual_openai_api_key,PYTHONUNBUFFERED=1"
   ```

## Configuration Options

### Environment Variables

The following environment variables can be configured:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PYTHONUNBUFFERED`: Set to 1 for better logging (recommended)

### Cloud Run Settings

The deployment uses these recommended settings:

- **Memory**: 2GB (suitable for PDF processing)
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds (5 minutes)
- **Concurrency**: 80 requests per instance
- **Max Instances**: 10 (to control costs)

### Regions

Available regions for deployment:
- `us-central1` (Iowa) - Default
- `us-east1` (South Carolina)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

To change the region, update the `REGION` variable in the deployment script.

## Post-Deployment

### Accessing Your Service

After successful deployment, you'll get a service URL like:
```
https://pdf-chat-api-xxxxx-uc.a.run.app
```

### Available Endpoints

- **Root**: `GET /` - Service information
- **Health Check**: `GET /health` - Service health status
- **PDF List**: `GET /pdfs` - List available PDF documents
- **API Documentation**: `GET /docs` - Interactive API docs
- **Chat**: `POST /chat` - Main chat endpoint (PDF content only)

### Monitoring and Logs

```bash
# View service logs
gcloud run services logs read pdf-chat-api --region=us-central1

# View real-time logs
gcloud run services logs tail pdf-chat-api --region=us-central1
```

### Updating the Service

To update your service with new code:

```bash
# Rebuild and push the image
docker build -t gcr.io/YOUR_PROJECT_ID/pdf-chat-api .
docker push gcr.io/YOUR_PROJECT_ID/pdf-chat-api

# Update the service
gcloud run services update pdf-chat-api --region=us-central1
```

## Cost Optimization

### Free Tier
Google Cloud Run offers a generous free tier:
- 2 million requests per month
- 360,000 vCPU-seconds
- 180,000 GiB-seconds of memory

### Cost Control
- Set `--max-instances` to limit scaling
- Use `--cpu-throttling` for cost savings
- Monitor usage in Google Cloud Console

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

2. **Permission Errors**
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="user:YOUR_EMAIL" \
       --role="roles/run.admin"
   ```

3. **Service Not Starting**
   - Check logs: `gcloud run services logs read pdf-chat-api --region=us-central1`
   - Verify environment variables are set correctly
   - Ensure the Docker image builds successfully

4. **Memory Issues**
   - Increase memory allocation: `--memory 4Gi`
   - Check if PDF files are too large

### Getting Help

- **Google Cloud Documentation**: [Cloud Run Docs](https://cloud.google.com/run/docs)
- **Google Cloud Support**: Available in Google Cloud Console
- **Community**: [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-run)

## Knowledge Base Constraints

The PDF Chat Agent has been configured with strict knowledge base constraints to ensure it only responds to questions about the uploaded PDF content:

### How It Works

1. **PDF-Only Responses**: The agent will only answer questions that are directly related to the content of the uploaded PDF documents
2. **Rejection of Off-Topic Questions**: Questions about general knowledge, current events, or topics not covered in the PDFs will be politely rejected
3. **Clear Feedback**: When a question is outside the scope, the agent provides clear guidance to ask about PDF content instead

### Example Behavior

**✅ PDF-Related Questions (Will be answered):**
- "What are the main topics in the documents?"
- "What does the Tetra Pak document cover?"
- "Summarize the key points from the PDFs"

**❌ General Questions (Will be rejected):**
- "What is the capital of France?"
- "How do I install Python?"
- "What's the weather like today?"

### Benefits

- **Focused Responses**: Ensures users get relevant information from the PDF content
- **Prevents Hallucination**: Reduces the risk of the agent making up information
- **Clear Boundaries**: Users understand exactly what the agent can and cannot help with

## Security Considerations

### Production Deployment

For production use, consider:

1. **Authentication**: Remove `--allow-unauthenticated` and implement proper auth
2. **HTTPS**: Cloud Run provides HTTPS by default
3. **Environment Variables**: Use Google Secret Manager for sensitive data
4. **Network Security**: Configure VPC connector if needed

### Using Secret Manager

```bash
# Create a secret
echo -n "your_openai_api_key" | gcloud secrets create openai-api-key --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy pdf-chat-api \
    --image gcr.io/YOUR_PROJECT_ID/pdf-chat-api \
    --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

## Cleanup

To remove the deployed service:

```bash
gcloud run services delete pdf-chat-api --region=us-central1
```

To remove the Docker image:

```bash
gcloud container images delete gcr.io/YOUR_PROJECT_ID/pdf-chat-api
``` 