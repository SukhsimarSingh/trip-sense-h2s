# Firebase Firestore Setup Guide

## Overview

Trip Sense uses **Firebase Firestore** as a cloud database for:
- ✅ Persistent trip storage across devices
- ✅ User-specific trip management
- ✅ Real-time synchronization
- ✅ Secure data access with user isolation
- ✅ Scalable NoSQL database

This guide will help you set up Firestore for cloud-based trip persistence.

## 1. Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project"
3. Name it (e.g., "trip-sense")
4. Disable Google Analytics (optional, but recommended for simplicity)
5. Click "Create project"
6. Wait for project creation to complete

## 2. Enable Firestore Database

1. In Firebase Console, click **"Firestore Database"** in the left sidebar
2. Click **"Create database"**
3. **Database ID**: Leave as **`(default)`** (recommended)
4. **Security Rules**: Select **"Start in production mode"**
5. **Location**: Choose **`europe-west4`** (or your preferred region)
   - For North America: `us-central1` or `us-east1`
   - For Europe: `europe-west4` or `europe-west1`
   - For Asia: `asia-northeast1` or `asia-south1`
6. Click **"Enable"**
7. Wait for database provisioning to complete

**Important Notes:**
- Using the `(default)` database requires no additional configuration
- Choose a location close to your users for optimal performance
- If deploying to Google Cloud Run, choose the same region or nearby
- Firestore location cannot be changed after creation

## 3. Configure Security Rules

Set up Firestore security rules to protect user data:

1. In Firestore Database, click the **"Rules"** tab
2. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own trips
    match /users/{userId}/trips/{tripId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Allow users to read/write their own user document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

3. Click **"Publish"**

These rules ensure:
- Users can only access their own trips
- Authentication is required for all operations
- Data isolation between users

## 4. Get Service Account Key

The service account key allows your backend to access Firestore:

1. Click the **gear icon** (⚙️) → **"Project settings"**
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Confirm by clicking **"Generate key"**
5. Save the JSON file securely (e.g., `firebase-key.json`)
6. **⚠️ Important**: Never commit this file to version control!

**Security Best Practices:**
- Store the key file outside your project directory
- Add `firebase-key.json` to `.gitignore`
- Use environment variables or secret managers in production
- Rotate keys periodically

## 5. Local Development Setup

For local development, set the Firebase credentials:

**Option A: Environment Variable (Recommended)**

Add to your `.env` file:
```env
FIREBASE_CREDENTIALS='{"type": "service_account", "project_id": "...", ...}'
```

**Option B: Direct File Path**

Set the environment variable to point to your key file:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-key.json"
```

**Test Locally:**
```bash
streamlit run streamlit_app.py
```

## 6. Deploy to Cloud Run

**Option A: Using Secret Manager (Recommended for Production)**

```bash
# Create secret in Google Secret Manager
cat path/to/firebase-key.json | gcloud secrets create firebase-credentials --data-file=-

# Grant Cloud Run access to the secret
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --region europe-north1 \
  --set-secrets "FIREBASE_CREDENTIALS=firebase-credentials:latest" \
  --set-env-vars "GEMINI_API_KEY=your-key,GOOGLE_MAPS_API_KEY=your-key,SERPAPI_API_KEY=your-key"
```

**Option B: Using Environment Variables (Quick Start)**

```bash
# Set the credentials as environment variable (one-line)
export FIREBASE_CREDS=$(cat path/to/firebase-key.json | tr -d '\n')

# Deploy with Firebase credentials
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --region europe-north1 \
  --set-env-vars "FIREBASE_CREDENTIALS=$FIREBASE_CREDS,GEMINI_API_KEY=your-key,GOOGLE_MAPS_API_KEY=your-key,SERPAPI_API_KEY=your-key"
```

**Important**: Replace:
- `YOUR_PROJECT_ID` with your Google Cloud project ID
- `your-key` with your actual API keys
- `path/to/firebase-key.json` with the actual path to your key file

## 7. Verify Firestore Integration

### Test Data Storage

1. Run your app locally or access your deployed version
2. Create and save a trip
3. Check Firebase Console → Firestore Database
4. You should see collections:
   - `users/{userId}/trips/{tripId}` - Stored trips
   - Trip documents contain: destination, dates, itinerary, etc.

### Check Logs

**Local Development:**
```bash
# Check local logs
tail -f trip_planner.log
```

**Cloud Run:**
```bash
# View real-time logs
gcloud run services logs tail trip-sense --region europe-north1

# Look for Firebase operations
gcloud run services logs tail trip-sense --region europe-north1 | grep -i "firebase\|firestore"
```

You should see messages like:
- `Trip XXXXXXXX saved to Firebase`
- `Retrieved X trips for user XXXXXXXX`
- `Trip XXXXXXXX deleted from Firebase`

## 8. Monitor Usage

### Firestore Console

Monitor your Firestore usage:
1. Go to Firebase Console → Firestore Database
2. Click **"Usage"** tab
3. View:
   - Document reads/writes/deletes
   - Storage usage
   - Number of collections

### Quotas & Pricing

**Free Tier (Spark Plan):**
- 1 GB storage
- 50,000 document reads/day
- 20,000 document writes/day
- 20,000 document deletes/day

**Paid Tier (Blaze Plan):**
- Pay-as-you-go pricing
- $0.18 per GB storage/month
- $0.06 per 100K document reads
- $0.18 per 100K document writes

Learn more: [Firebase Pricing](https://firebase.google.com/pricing)

## Troubleshooting

### Issue: "Permission denied" errors

**Solution:**
1. Check security rules in Firebase Console
2. Verify authentication is enabled
3. Ensure user is signed in before accessing Firestore

### Issue: "FIREBASE_CREDENTIALS not found"

**Solution:**
1. Verify environment variable is set correctly
2. Check the JSON file is valid (use `cat firebase-key.json | jq`)
3. Ensure file path is correct

### Issue: "Project not found"

**Solution:**
1. Verify project ID in Firebase credentials
2. Ensure Firestore is enabled in Firebase Console
3. Check you're using the correct Firebase project

### Issue: Slow performance

**Solution:**
1. Choose a Firestore location closer to users
2. Implement data caching where appropriate
3. Optimize query patterns (avoid full collection scans)
4. Use composite indexes for complex queries

### Issue: Data not syncing

**Solution:**
1. Check internet connection
2. Verify Firebase credentials are valid
3. Check Cloud Run logs for errors
4. Ensure security rules allow access

## Best Practices

### Data Structure

Trip Sense uses this structure:
```
users/{userId}/
  ├── trips/{tripId}/
  │   ├── trip_name: string
  │   ├── destination: string
  │   ├── start_date: string
  │   ├── end_date: string
  │   ├── itinerary: string
  │   ├── form_data: object
  │   ├── created_at: timestamp
  │   ├── updated_at: timestamp
  │   └── status: string (e.g., "draft", "booked")
```

### Security

1. ✅ Always use authentication
2. ✅ Implement proper security rules
3. ✅ Validate data before writing
4. ✅ Use user-specific paths
5. ✅ Monitor access patterns
6. ✅ Rotate service account keys regularly

### Performance

1. ✅ Batch operations when possible
2. ✅ Use indexes for common queries
3. ✅ Implement pagination for large datasets
4. ✅ Cache frequently accessed data
5. ✅ Monitor quota usage

## Next Steps

- ✅ Enable Firebase Authentication for user management ([setup guide](FIREBASE_AUTH_SETUP.md))
- ✅ Set up backup and recovery procedures
- ✅ Configure monitoring and alerts
- ✅ Review and optimize security rules
- ✅ Plan for scaling as user base grows

## Additional Resources

- **Firebase Documentation**: https://firebase.google.com/docs/firestore
- **Security Rules Guide**: https://firebase.google.com/docs/firestore/security/get-started
- **Best Practices**: https://firebase.google.com/docs/firestore/best-practices
- **Pricing Calculator**: https://firebase.google.com/pricing

---

**Your trips are now safely stored in the cloud!** ☁️🎉

