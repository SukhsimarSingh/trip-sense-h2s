# Trip Sense - Google Cloud Run Deployment Guide

## Overview

This comprehensive guide will help you deploy the complete Trip Sense application to Google Cloud Run, including:
- AI-powered trip planning with Gemini AI
- Firebase Authentication for user management
- Firebase Firestore for cloud storage  
- SerpAPI integration for real-time flight/hotel search
- Payment processing capabilities
- Professional PDF exports

**Deployment Options:**
1. **Google Cloud Run**: Full control, scalable, pay-per-use
2. **Streamlit Cloud**: Quick deployment, easier setup (see additional notes)

## Prerequisites

1. **Google Cloud Account**: Sign up at https://cloud.google.com/
2. **Google Cloud Project**: Create a new project or use an existing one
3. **gcloud CLI**: Install from https://cloud.google.com/sdk/docs/install
4. **Billing Enabled**: Enable billing on your Google Cloud project
5. **API Keys**: Ensure you have the following ready:
   - `GEMINI_API_KEY` - Google Gemini AI API key ([Get it here](https://aistudio.google.com/app/apikey))
   - `GOOGLE_MAPS_API_KEY` - Google Maps Platform API key ([Get it here](https://console.cloud.google.com/apis/credentials))
   - `SERPAPI_API_KEY` - SerpAPI key for flight/hotel search ([Get it here](https://serpapi.com/)) - **Recommended for production**
   
6. **Firebase Setup** (Required): 
   - Firebase project created ([Create one](https://console.firebase.google.com/))
   - Firestore Database enabled (for trip storage)
   - Firebase Authentication enabled (Email/Password provider)
   - Service account JSON key file (for backend access)
   - Firebase web config JSON (for client-side auth)
   - See detailed guides: [Firebase Setup](FIREBASE_SETUP.md) and [Firebase Auth Setup](FIREBASE_AUTH_SETUP.md)

## Deployment Steps

#### Step 1: Install and Configure gcloud CLI

```bash
# Install gcloud CLI (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init

# Set your project ID
gcloud config set project YOUR_PROJECT_ID
```

#### Step 2: Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### Step 3: Create Artifact Registry Repository

Create a Docker repository in europe-north1:

```bash
gcloud artifacts repositories create trip-sense-repo \
  --repository-format=docker \
  --location=europe-north1 \
  --description="Trip Sense container images"
```

#### Step 4: Set Up Secrets (Recommended for Production)

**Option A: Using Secret Manager (Recommended for Production)**

Store your sensitive credentials securely in Google Secret Manager:

```bash
# Create secrets for API keys
# IMPORTANT: Use 'echo -n' to avoid adding trailing newlines!
echo -n "your-actual-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-actual-serpapi-key" | gcloud secrets create serpapi-api-key --data-file=-
echo -n "your-actual-google-maps-key" | gcloud secrets create google-maps-api-key --data-file=-

# Create secret for Firebase service account credentials (backend)
gcloud secrets create firebase-credentials --data-file=path/to/your-firebase-key.json

# Create secret for Firebase web config (client-side auth)
cat > /tmp/firebase-web-config.json << EOF
{
  "apiKey": "YOUR_API_KEY",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project.appspot.com",
  "messagingSenderId": "YOUR_SENDER_ID",
  "appId": "YOUR_APP_ID"
}
EOF
gcloud secrets create firebase-web-config --data-file=/tmp/firebase-web-config.json
rm /tmp/firebase-web-config.json

# Grant Cloud Run access to secrets
# First, get your project number:
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
echo "Your project number: $PROJECT_NUMBER"

# Then grant access to all secrets:
for secret in gemini-api-key serpapi-api-key google-maps-api-key firebase-credentials firebase-web-config
do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done

echo "All secrets created and access granted!"
```

**Note:** 
- The service account format is `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
- Use the **project number** (e.g., `988549865021`), **NOT** the project ID
- This is the default Compute Engine service account
- To manually find your project number: `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`

**Option B: Using Environment Variables (Quick Start)**

You can pass environment variables directly during deployment (less secure but simpler for testing).

#### Step 5: Build the Container Image

```bash
# Build using Cloud Build (recommended - no local Docker required)
gcloud builds submit --tag europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense

# OR build locally with Docker (requires Docker installed)
docker build -t europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense .
docker push europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense
```

#### Step 6: Deploy to Cloud Run

**Option A: Deploy with Secret Manager (Recommended for Production)**

```bash
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,SERPAPI_API_KEY=serpapi-api-key:latest,GOOGLE_MAPS_API_KEY=google-maps-api-key:latest,FIREBASE_CREDENTIALS=firebase-credentials:latest,FIREBASE_WEB_CONFIG=firebase-web-config:latest"
```

**Benefits of Secret Manager:**
- Encrypted at rest and in transit
- Automatic rotation support
- Audit logging of access
- Version control for secrets
- No secrets in environment variables

**Option B: Deploy with Environment Variables (Quick Start / Development)**

```bash
# Prepare Firebase credentials
export FIREBASE_CREDS=$(cat path/to/firebase-key.json | tr -d '\n')
export FIREBASE_WEB=$(cat path/to/firebase-web-config.json | tr -d '\n')

# Deploy
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars="GEMINI_API_KEY=your-gemini-key,SERPAPI_API_KEY=your-serpapi-key,GOOGLE_MAPS_API_KEY=your-google-maps-key,FIREBASE_CREDENTIALS=$FIREBASE_CREDS,FIREBASE_WEB_CONFIG=$FIREBASE_WEB"
```

**Important Configuration:**
- Replace `YOUR_PROJECT_ID` with your Google Cloud project ID
- Replace `your-gemini-key`, `your-serpapi-key`, `your-google-maps-key` with actual API keys
- Ensure Firebase credentials files exist and are valid JSON
- **SerpAPI key is optional** but highly recommended for production (enables real-time booking)

**Security Note:** 
- Environment variables are encrypted at rest by Cloud Run
- For production, **use Secret Manager (Option A)** for better security
- Environment variables are visible in Cloud Run console to project admins

**Region Note:** 
- Using `europe-north1` region for consistency with Artifact Registry
- Choose a region close to your users for optimal performance
- Available regions: `us-central1`, `europe-west1`, `asia-northeast1`, etc.

#### Step 7: Get Your Service URL

After deployment, Cloud Run will provide you with a URL like:
```
https://trip-sense-xxxxxxxxxx-lz.a.run.app
```

(The URL will have a `europe-north1` specific suffix)

## Configuration Options

### Environment Variables (Required)

Your application requires the following credentials:

| Variable | Description | Required | Format |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes | String (starts with "AIza") |
| `GOOGLE_MAPS_API_KEY` | Google Maps Platform API key | Yes | String |
| `SERPAPI_API_KEY` | SerpAPI for real-time booking | Recommended | String |
| `FIREBASE_CREDENTIALS` | Firebase service account JSON | Yes | JSON string or file path |
| `FIREBASE_WEB_CONFIG` | Firebase web app config | Yes | JSON string |

**Notes:**
- **GEMINI_API_KEY**: Powers AI trip planning and itinerary generation
- **GOOGLE_MAPS_API_KEY**: Required for Places, Maps, and Weather APIs
- **SERPAPI_API_KEY**: Enables real-time flight/hotel search (app works without it in demo mode)
- **FIREBASE_CREDENTIALS**: Backend service account for Firestore access
- **FIREBASE_WEB_CONFIG**: Client-side config for Firebase Authentication

**Setting/Updating Environment Variables:**

```bash
# Update environment variables (if using env vars instead of secrets)
gcloud run services update trip-sense \
  --region europe-north1 \
  --update-env-vars "GEMINI_API_KEY=new-key,SERPAPI_API_KEY=new-key,GOOGLE_MAPS_API_KEY=new-key"
```

**Updating Secrets in Secret Manager (Recommended Method):**

```bash
# Update API key secrets
echo -n "new-gemini-key" | gcloud secrets versions add gemini-api-key --data-file=-
echo -n "new-serpapi-key" | gcloud secrets versions add serpapi-api-key --data-file=-
echo -n "new-google-maps-key" | gcloud secrets versions add google-maps-api-key --data-file=-

# Update Firebase service account credentials
gcloud secrets versions add firebase-credentials --data-file=path/to/new-firebase-key.json

# Update Firebase web config
cat > /tmp/new-firebase-web-config.json << EOF
{
  "apiKey": "NEW_API_KEY",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project.appspot.com",
  "messagingSenderId": "YOUR_SENDER_ID",
  "appId": "YOUR_APP_ID"
}
EOF
gcloud secrets versions add firebase-web-config --data-file=/tmp/new-firebase-web-config.json
rm /tmp/new-firebase-web-config.json

# Cloud Run will automatically use the latest secret version
# No need to redeploy unless you're changing other settings
```

**Local Development vs Cloud Run:**

- **Local Development**: API keys are read from `.streamlit/secrets.toml`
- **Cloud Run**: API keys are read from environment variables (more secure)
- The application automatically detects the environment and uses the appropriate method

### Resource Limits

You can adjust memory, CPU, and concurrency:

```bash
--memory 2Gi          # Memory allocation (512Mi, 1Gi, 2Gi, 4Gi, 8Gi)
--cpu 1               # CPU allocation (1, 2, 4)
--concurrency 80      # Max concurrent requests per instance
--max-instances 10    # Maximum number of instances
--min-instances 0     # Minimum instances (0 for scale to zero)
```

### Authentication

To require authentication:

```bash
# Remove --allow-unauthenticated and deploy
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --region europe-north1
```

## Updating Your Deployment

When you make changes to your application:

1. **Rebuild the container image**:
   ```bash
   gcloud builds submit --tag europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense
   ```

2. **Redeploy to Cloud Run**:
   ```bash
   # Redeploy with existing environment variables
   gcloud run deploy trip-sense \
     --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
     --region europe-north1
   
   # Note: This preserves your existing environment variables
   # To update env vars, add: --set-env-vars "KEY=value"
   ```

## Monitoring and Logs

### View Logs
```bash
# Stream logs in real-time
gcloud run services logs tail trip-sense --region europe-north1

# View logs in Cloud Console
# Visit: https://console.cloud.google.com/run
```

### Monitor Performance
```bash
# Get service details
gcloud run services describe trip-sense --region europe-north1

# View metrics in Cloud Console
# Visit: https://console.cloud.google.com/monitoring
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Re-authenticate
   gcloud auth login
   ```

2. **Project Not Set**
   ```bash
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **API Not Enabled**
   ```bash
   # Enable all required APIs
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

4. **Container Build Fails**
   - Check your Dockerfile syntax
   - Ensure all dependencies are in requirements.txt
   - Review build logs: `gcloud builds list`

5. **Service Won't Start**
   - Check logs: `gcloud run services logs read trip-sense --region europe-north1`
   - Verify PORT environment variable is being used
   - Ensure health checks pass

6. **API Key Errors**
   - Verify environment variables are set: `gcloud run services describe trip-sense --region europe-north1 --format="get(spec.template.spec.containers[0].env)"`
   - Ensure API keys are valid and have proper permissions
   - Check that you're using the correct key names: `GEMINI_API_KEY` and `GOOGLE_MAPS_API_KEY`

7. **Permission Errors / File Logging Issues**
   - The application automatically logs to stdout on Cloud Run (file logging is disabled)
   - View logs via Cloud Logging: `gcloud run services logs tail trip-sense --region europe-north1`
   - Cloud Run's ephemeral filesystem doesn't support persistent file writes

8. **Artifact Registry Authentication Issues**
   - Configure Docker authentication: `gcloud auth configure-docker europe-north1-docker.pkg.dev`
   - Ensure you have permissions to push to Artifact Registry
   - Verify the repository exists: `gcloud artifacts repositories list --location=europe-north1`

9. **Firebase Connection Issues**
   - Verify Firebase credentials are set correctly
   - Check Firebase project ID matches your actual project
   - Ensure Firestore is enabled in your Firebase console
   - View logs: `gcloud run services logs tail trip-sense --region europe-north1 | grep -i firebase`
   - Test connection: Check if you can see Firestore operations in Firebase console

10. **SerpAPI Not Working**
   - Verify SERPAPI_API_KEY is set (optional but needed for real-time search)
   - Check your SerpAPI quota at https://serpapi.com/dashboard
   - App will work without SerpAPI but show demo data for flights/hotels
   - View logs: `gcloud run services logs tail trip-sense --region europe-north1 | grep -i serpapi`

11. **Firebase Authentication Not Working**
   - Verify FIREBASE_WEB_CONFIG is set correctly
   - Check Firebase Console → Authentication → Sign-in methods
   - Ensure Email/Password provider is enabled
   - Add your Cloud Run domain to Authorized domains in Firebase Console
   - Test with: `gcloud run services logs tail trip-sense --region europe-north1 | grep -i "auth\|firebase"`

12. **Users Can't Sign In After Deployment**
   - **Solution**: Add Cloud Run domain to Firebase authorized domains
   - Go to Firebase Console → Authentication → Settings → Authorized domains
   - Add your`*.run.app` domain
   - Wait 2-3 minutes for changes to propagate

13. **Trips Not Saving to Firestore**
   - Verify Firestore is enabled in Firebase Console
   - Check Firebase security rules allow authenticated user writes
   - Verify FIREBASE_CREDENTIALS secret is correct
   - Test with: `gcloud run services logs tail trip-sense --region europe-north1 | grep -i "firestore\|saved"`

14. **Cold Start Performance**
   - First request after idle may take 3-5 seconds
   - Use `--min-instances 1` to keep one instance warm (costs more)
   - Optimize by reducing dependencies or using smaller base images
   - Monitor with: `gcloud run services logs tail trip-sense --region europe-north1 | grep -i "cold start"`

### Getting Help

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Support**: https://cloud.google.com/support

## Cost Optimization

Cloud Run uses a pay-per-use pricing model:
- Free tier: 2 million requests/month
- Charges only when handling requests
- Scale to zero when not in use

To minimize costs:
```bash
--min-instances 0     # Scale to zero when idle
--max-instances 3     # Limit maximum instances
--cpu-throttling      # Throttle CPU when not handling requests (default)
```

## Custom Domain

To use a custom domain:

1. Verify domain ownership in Cloud Console
2. Map your domain:
   ```bash
   gcloud run domain-mappings create \
     --service trip-sense \
     --domain your-domain.com \
     --region europe-north1
   ```

## Security Best Practices

### Current Security Features

**Secrets Excluded from Docker Image**
- `.streamlit/secrets.toml` is excluded via `.dockerignore`
- API keys are never baked into the container image
- Keys are only stored in Cloud Run's encrypted environment

**Environment Variables Encrypted**
- Cloud Run encrypts environment variables at rest
- Transmitted securely over encrypted channels
- Only accessible to your service instances

**HTTPS Enabled by Default**
- All Cloud Run services use HTTPS automatically
- Custom SSL certificates managed by Google

### Advanced Security Options

1. **Use Secret Manager** (Recommended for Production):
   ```bash
   # Create secrets in Secret Manager
   echo -n "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
   echo -n "your-serpapi-key" | gcloud secrets create serpapi-api-key --data-file=-
   gcloud secrets create firebase-credentials --data-file=path/to/firebase-key.json
   
   # Deploy with secrets from Secret Manager
   gcloud run deploy trip-sense \
     --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
     --region europe-north1 \
     --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,SERPAPI_API_KEY=serpapi-api-key:latest,FIREBASE_CREDENTIALS=firebase-credentials:latest" \
     --set-env-vars="FIREBASE_PROJECT_ID=your-firebase-project-id"
   ```

2. **Restrict Access with IAM**:
   ```bash
   # Require authentication (remove --allow-unauthenticated)
   gcloud run deploy trip-sense \
     --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
     --region europe-north1
   
   # Grant specific users access
   gcloud run services add-iam-policy-binding trip-sense \
     --region europe-north1 \
     --member="user:your-email@example.com" \
     --role="roles/run.invoker"
   ```

3. **Enable Binary Authorization** (Optional):
   ```bash
   # Require signed container images
   gcloud run deploy trip-sense \
     --binary-authorization=default \
     --region europe-north1
   ```

## Important Notes

### Logging

- **Cloud Run**: Logs are written to stdout and automatically captured by Cloud Logging
- **Local Development**: Logs are written to `trip_planner.log` file
- The application detects the environment automatically (via `K_SERVICE` env var)

### Secrets Management

- **Never commit** sensitive files to version control:
  - `.streamlit/secrets.toml` - Streamlit secrets
  - `.streamlit/auth_config.yaml` - Authentication credentials (**Contains hashed passwords!**)
  - `.env` - Environment variables
  - `firebase-key.json` - Firebase credentials
  - Any `*-firebase-adminsdk-*.json` files
  - API key files
- **Docker build** excludes all secrets via `.dockerignore`
- **Production** uses Google Secret Manager or environment variables
- **Local Development** uses `.streamlit/secrets.toml` (gitignored)
- **Firebase** credentials are base64-encoded or stored in Secret Manager for Cloud Run

### Authentication Configuration (Important!)

The `.streamlit/auth_config.yaml` file contains authentication credentials:

**⚠️ Security Warning:**
- This file contains **hashed passwords** and **cookie keys**
- **NEVER** commit the actual `auth_config.yaml` to version control
- A template file is provided: `.streamlit/auth_config.yaml.example`

**Setup Instructions:**

1. **Copy the template:**
   ```bash
   cp .streamlit/auth_config.yaml.example .streamlit/auth_config.yaml
   ```

2. **Generate secure password hashes:**
   ```python
   import bcrypt
   password = "your-secure-password"
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   print(hashed.decode())
   ```

3. **Update auth_config.yaml:**
   - Change the `cookie.key` to a random string
   - Replace password hashes with your generated ones
   - Update user details (email, name)

4. **Verify it's gitignored:**
   ```bash
   git status  # Should NOT show auth_config.yaml
   ```

**Note:** The app currently uses guest mode (no authentication required). The `auth_config.yaml` file is included for future authentication features but is not actively used in the current deployment.

### Resource Usage

- Default configuration: 2GB RAM, 1 CPU
- Streamlit apps may need more memory for concurrent users
- Monitor performance and adjust `--memory` flag as needed

## Quick Reference Commands

```bash
# View service details
gcloud run services describe trip-sense --region europe-north1

# View logs in real-time
gcloud run services logs tail trip-sense --region europe-north1

# List all revisions
gcloud run revisions list --service trip-sense --region europe-north1

# Rollback to previous revision
gcloud run services update-traffic trip-sense --to-revisions REVISION_NAME=100 --region europe-north1

# Update environment variables
gcloud run services update trip-sense --update-env-vars "KEY=value" --region europe-north1

# Delete service
gcloud run services delete trip-sense --region europe-north1

# View Artifact Registry images
gcloud artifacts docker images list europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo

# Delete old images from Artifact Registry
gcloud artifacts docker images delete europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense:TAG
```

## Quick Deploy Script (Optional)

Create a `deploy.sh` script for faster redeployment:

```bash
#!/bin/bash
# deploy.sh - Quick deployment script for Trip Sense

PROJECT_ID="your-project-id"
REGION="europe-north1"
SERVICE_NAME="trip-sense"
IMAGE="europe-north1-docker.pkg.dev/$PROJECT_ID/trip-sense-repo/trip-sense"

echo "Deploying Trip Sense to Cloud Run..."

# Build and push
echo "Building container image..."
gcloud builds submit --tag $IMAGE

# Deploy with secrets
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,SERPAPI_API_KEY=serpapi-api-key:latest,FIREBASE_CREDENTIALS=firebase-credentials:latest" \
  --set-env-vars="FIREBASE_PROJECT_ID=your-firebase-project-id"

echo "Deployment complete!"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Alternative: Streamlit Cloud Deployment

### Quick Deployment to Streamlit Cloud

Streamlit Cloud offers a simpler deployment option with automatic HTTPS and a user-friendly interface:

#### Step 1: Prepare Your Repository

1. Ensure your code is on GitHub, GitLab, or Bitbucket
2. Add all setup guides and configuration files
3. Verify `requirements.txt` includes all dependencies
4. Commit and push changes

#### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub/GitLab/Bitbucket account
3. Click **"New app"**
4. Select your repository, branch, and main file (`streamlit_app.py`)

#### Step 3: Configure Secrets

Add secrets in TOML format in the Streamlit Cloud dashboard:

```toml
# API Keys
GEMINI_API_KEY = "your-gemini-key"
GOOGLE_MAPS_API_KEY = "your-google-maps-key"
SERPAPI_API_KEY = "your-serpapi-key"

# Firebase Service Account (for Firestore)
FIREBASE_CREDENTIALS = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
'''

# Firebase Web Config (for Authentication)
[firebase_web]
apiKey = "your-api-key"
authDomain = "your-project.firebaseapp.com"
projectId = "your-project-id"
storageBucket = "your-project.appspot.com"
messagingSenderId = "your-sender-id"
appId = "your-app-id"
```

#### Step 4: Add Authorized Domain

1. Copy your Streamlit Cloud URL (e.g., `your-app.streamlit.app`)
2. Go to Firebase Console → Authentication → Settings → Authorized domains
3. Add your Streamlit Cloud domain
4. Wait a few minutes for propagation

#### Step 5: Deploy

Click **"Deploy"** and wait for the build to complete!

### Streamlit Cloud vs Google Cloud Run

| Feature | Streamlit Cloud | Google Cloud Run |
|---------|-----------------|------------------|
| **Setup** | Very easy | Moderate complexity |
| **Cost** | Free tier available | Pay-per-use |
| **Custom domain** | Limited (paid plans) | Full support |
| **Resource control** | Limited | Full control |
| **Scaling** | Automatic | Configurable |
| **Best for** | Prototypes, demos | Production apps |

## Next Steps

### Essential Setup

- Deploy your application with all API keys configured
- Test authentication (sign up, sign in, logout)
- Test trip planning and AI generation
- Test real-time booking (flights and hotels)
- Test trip storage and retrieval from Firestore
- Test PDF export functionality
- Verify cross-device access (cloud sync)

### Security & Production Readiness

- Migrate to Secret Manager for production (if using Cloud Run)
- Set up Firebase security rules (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))
- Enable email verification for new users
- Add custom domain (optional)
- Set up monitoring and alerts
- Configure backup strategies for Firestore

### Optimization & Monitoring

- Review and optimize costs
- Monitor SerpAPI usage and quotas
- Set up Firebase Analytics (optional)
- Implement caching for API responses
- Monitor Cloud Run/Streamlit Cloud logs
- Set up error tracking (e.g., Sentry)

### User Experience

- Customize Firebase email templates
- Add terms of service and privacy policy
- Implement user feedback mechanism
- Add analytics tracking
- Create user documentation
- Set up support channels

---

**Need Help?** 
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Streamlit on Cloud Run: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Firebase Documentation: https://firebase.google.com/docs
- SerpAPI Documentation: https://serpapi.com/docs
- Support: https://cloud.google.com/support

