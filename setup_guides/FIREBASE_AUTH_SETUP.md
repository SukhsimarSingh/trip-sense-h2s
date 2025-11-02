# 🔐 Firebase Authentication Setup Guide

## Overview

Your Trip Sense app now uses **Firebase Authentication** for user management with:
- ✅ Email/Password authentication
- ✅ Password reset functionality
- ✅ Email verification
- ✅ Secure user sessions
- ✅ Ready for Google Sign-In (OAuth)

## Step 1: Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `kinetic-pilot-471518-u3`
3. Click **Authentication** in left menu
4. Click **Get started**
5. Enable **Email/Password** provider:
   - Click "Email/Password"
   - Toggle **Enable**
   - Click **Save**

## Step 2: Get Firebase Web API Configuration

Firebase Authentication requires web configuration for client-side auth:

1. In Firebase Console, click ⚙️ (Settings) → **Project settings**
2. Scroll down to **"Your apps"** section
3. If no web app exists:
   - Click the **Web** icon (`</>`) 
   - Register app with nickname: `trip-sense-web`
   - **Don't** check "Set up Firebase Hosting" (not needed)
   - Click **"Register app"**
4. Copy the **firebaseConfig** object shown

It will look like this:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "kinetic-pilot-471518-u3.firebaseapp.com",
  databaseURL: "https://kinetic-pilot-471518-u3.firebaseio.com",
  projectId: "kinetic-pilot-471518-u3",
  storageBucket: "kinetic-pilot-471518-u3.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

## Step 3: Configure Locally

Create the configuration file for local development:

1. Create directory: `.streamlit/` (if it doesn't exist)
2. Create file: `.streamlit/firebase_config.json`
3. Add your Firebase web configuration:

```json
{
  "apiKey": "YOUR_API_KEY",
  "authDomain": "your-project-id.firebaseapp.com",
  "databaseURL": "https://your-project-id.firebaseio.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project-id.appspot.com",
  "messagingSenderId": "YOUR_SENDER_ID",
  "appId": "YOUR_APP_ID"
}
```

**⚠️ Important:**
- Replace ALL placeholder values with your actual Firebase config
- Never commit `firebase_config.json` to version control
- Add `.streamlit/firebase_config.json` to `.gitignore`
- Keep this file secure - it contains authentication keys

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Test Locally

Start your Streamlit app:

```bash
streamlit run streamlit_app.py
```

### What You'll See:

**Landing Page with Authentication:**
- **Sign In** tab - For existing users to log in
- **Sign Up** tab - Create new account with email/password
- **Forgot Password** link - Reset password via email

### Test the Authentication Flow:

1. **Create Test Account:**
   - Go to Sign Up tab
   - Enter email (use a real email for verification)
   - Enter password (minimum 6 characters)
   - Click "Sign Up"
   - Check email for verification link

2. **Verify Email:**
   - Open the verification email from Firebase
   - Click the verification link
   - Return to the app

3. **Sign In:**
   - Go to Sign In tab
   - Enter your credentials
   - Click "Sign In"
   - You should be logged in and see the main app

4. **Test Features:**
   - Create and save a trip
   - Check Firebase Console → Firestore
   - Your trip should be under `users/{your-uid}/trips/`

5. **Test Logout:**
   - Click logout button
   - Verify you're redirected to landing page

## Step 6: Deploy to Cloud Run

### Option A: Using Streamlit Cloud (Recommended for Quick Deployment)

If deploying to Streamlit Cloud, add Firebase config to secrets:

1. Go to your app dashboard on Streamlit Cloud
2. Click **"Settings"** → **"Secrets"**
3. Add the following in TOML format:

```toml
# Firebase Web Configuration
[firebase_web]
apiKey = "YOUR_API_KEY"
authDomain = "your-project-id.firebaseapp.com"
databaseURL = "https://your-project-id.firebaseio.com"
projectId = "your-project-id"
storageBucket = "your-project-id.appspot.com"
messagingSenderId = "YOUR_SENDER_ID"
appId = "YOUR_APP_ID"

# Firebase Service Account (for Firestore)
FIREBASE_CREDENTIALS = '{"type": "service_account", ...}'

# Other API Keys
GEMINI_API_KEY = "your-key"
GOOGLE_MAPS_API_KEY = "your-key"
SERPAPI_API_KEY = "your-key"
```

### Option B: Using Google Cloud Run

**Method 1: Environment Variables (Quick Start)**

```bash
# Convert config to single-line JSON
export FIREBASE_WEB_CONFIG='{"apiKey":"YOUR_KEY","authDomain":"your-project-id.firebaseapp.com","projectId":"your-project-id","storageBucket":"your-project-id.appspot.com","messagingSenderId":"YOUR_SENDER_ID","appId":"YOUR_APP_ID"}'

# Deploy with environment variables
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-env-vars "FIREBASE_WEB_CONFIG=$FIREBASE_WEB_CONFIG,GEMINI_API_KEY=your-key,GOOGLE_MAPS_API_KEY=your-key,SERPAPI_API_KEY=your-key" \
  --set-secrets "FIREBASE_CREDENTIALS=firebase-credentials:latest"
```

**Method 2: Secret Manager (Production Recommended)**

```bash
# Create secret for Firebase web config
echo '{"apiKey":"YOUR_KEY","authDomain":"...","projectId":"..."}' | \
  gcloud secrets create firebase-web-config --data-file=-

# Grant access to Cloud Run
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding firebase-web-config \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secrets
gcloud run deploy trip-sense \
  --image europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/trip-sense-repo/trip-sense \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-secrets="FIREBASE_WEB_CONFIG=firebase-web-config:latest,FIREBASE_CREDENTIALS=firebase-credentials:latest" \
  --set-env-vars="GEMINI_API_KEY=your-key,GOOGLE_MAPS_API_KEY=your-key,SERPAPI_API_KEY=your-key"
```

## Features

### ✨ What Users Can Do

1. **Sign Up** - Create account with email/password
2. **Email Verification** - Receive verification email
3. **Sign In** - Access their trips
4. **Password Reset** - Reset forgotten passwords
5. **Persistent Sessions** - Stay logged in
6. **Logout** - Sign out anytime

### 🔒 Security Features

- Passwords hashed by Firebase (never stored plain text)
- Email verification required
- Secure session tokens
- Password strength requirements (min 6 chars)
- Rate limiting by Firebase
- Built-in security rules

## Step 7: Configure Email Templates (Optional)

Customize the emails Firebase sends:

1. Go to Firebase Console → **Authentication**
2. Click **"Templates"** tab
3. Customize templates for:
   - **Email Verification**: Sent when user signs up
   - **Password Reset**: Sent when user requests password reset
   - **Email Change Verification**: Sent when user changes email

**Tips:**
- Add your app name and branding
- Customize the message text
- Set a custom sender name
- Configure action URL to redirect back to your app

## Step 8: Enable Additional Providers (Optional)

### Google Sign-In

Enable one-click Google authentication:

1. In Firebase Console → **Authentication**
2. Click **"Sign-in method"** tab
3. Click **"Google"** provider
4. Toggle **Enable**
5. Enter **Project support email**
6. Click **Save**

**Additional Setup for Production:**
- Configure OAuth consent screen in Google Cloud Console
- Add authorized domains (your production domain)
- Set up OAuth brand if needed

### Other Providers

Firebase supports many authentication providers:
- **Facebook**: Requires Facebook App ID and Secret
- **Twitter**: Requires Twitter API keys
- **GitHub**: Requires GitHub OAuth App
- **Microsoft**: Azure AD integration
- **Apple**: Sign in with Apple (required for iOS apps)
- **Phone**: SMS-based authentication

See [Firebase Auth Providers](https://firebase.google.com/docs/auth/web/start#next_steps) for setup guides.

## User Management

### View Users

Firebase Console → Authentication → Users tab

### Manage Users

- View all registered users
- Disable/delete users
- Send password reset emails
- Verify email status

### Export Users

```bash
# Using Firebase CLI
firebase auth:export users.json --project kinetic-pilot-471518-u3
```

## Troubleshooting

### Issue: "Invalid API key" or "API key not found"

**Solutions:**
1. Verify `firebase_config.json` exists in `.streamlit/` directory
2. Check the `apiKey` value is correct (starts with "AIza")
3. Ensure the API key is enabled in Firebase Console
4. Verify project settings in Firebase Console
5. Check that Web API key restrictions allow your domain

### Issue: "Email already registered"

**Solutions:**
- User account already exists
- Use "Sign In" tab instead
- Use "Forgot Password" to reset password
- Check Firebase Console → Authentication → Users to verify

### Issue: "WEAK_PASSWORD: Password should be at least 6 characters"

**Solutions:**
- Use minimum 6 characters
- Recommend 8+ characters with mixed case, numbers, symbols
- Update password requirements in your form if needed

### Issue: "Network request failed"

**Solutions:**
1. Check internet connection
2. Verify Firebase project is active (not deleted)
3. Check API quotas in Firebase Console → Usage
4. Ensure Firebase Auth is enabled
5. Check browser console for CORS errors
6. Verify `authDomain` in config matches Firebase project

### Issue: "TOO_MANY_ATTEMPTS_TRY_LATER"

**Solutions:**
- Firebase rate limiting activated
- Wait 15-30 minutes before retry
- This protects against brute force attacks
- Consider implementing CAPTCHA for production

### Issue: Email verification not received

**Solutions:**
1. Check spam/junk folder
2. Verify email address is correct
3. Check Firebase Console → Authentication → Templates
4. Ensure Firebase email sender is not blocked
5. Try resending verification email
6. Check email deliverability settings

### Issue: "CONFIGURATION_NOT_FOUND"

**Solutions:**
1. Verify `firebase_config.json` exists and is valid JSON
2. Check file is in `.streamlit/` directory
3. Restart Streamlit app after adding config
4. Ensure config is loaded properly in code

### Issue: Users can't sign in after deployment

**Solutions:**
1. Add your domain to Authorized domains in Firebase Console
2. Go to Authentication → Settings → Authorized domains
3. Add your Streamlit/Cloud Run domain
4. Wait a few minutes for changes to propagate

### Issue: "Auth state persistence"

**Solutions:**
- Clear browser cookies/cache
- Check localStorage is enabled in browser
- Verify session management code
- Check for session timeout settings

## Cost

Firebase Authentication is **FREE** for:
- Unlimited email/password users
- 10K phone auth verifications/month
- Google Sign-In (unlimited)

## Security Best Practices

### Configuration Security

1. ✅ **Never commit** `.streamlit/firebase_config.json` to version control
2. ✅ Add `firebase_config.json` to `.gitignore`
3. ✅ Use environment variables or Secret Manager in production
4. ✅ Rotate API keys periodically
5. ✅ Restrict API keys by domain/IP when possible

### Authentication Security

1. ✅ **Require email verification** before full access
2. ✅ Implement strong password requirements
3. ✅ Enable multi-factor authentication (optional)
4. ✅ Use HTTPS only (enforced by Firebase)
5. ✅ Set session timeout appropriately
6. ✅ Implement account lockout after failed attempts
7. ✅ Log authentication events for monitoring

### Firestore Security

1. ✅ Implement proper security rules
2. ✅ Validate user authentication before data access
3. ✅ Use user-specific paths: `users/{uid}/trips/{tripId}`
4. ✅ Never trust client-side data
5. ✅ Implement rate limiting

### Monitoring & Alerts

1. ✅ Monitor authentication activity in Firebase Console
2. ✅ Set up alerts for unusual patterns
3. ✅ Review user access logs regularly
4. ✅ Track failed login attempts
5. ✅ Monitor API usage and quotas

### Example Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Helper function to check authentication
    function isSignedIn() {
      return request.auth != null;
    }
    
    // Helper function to check user ownership
    function isOwner(userId) {
      return isSignedIn() && request.auth.uid == userId;
    }
    
    // Helper function to check email verification
    function isVerified() {
      return isSignedIn() && request.auth.token.email_verified == true;
    }
    
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if isOwner(userId) && isVerified();
      
      // Trips subcollection
      match /trips/{tripId} {
        allow read, write: if isOwner(userId) && isVerified();
      }
    }
  }
}
```

## Advanced Features

### Custom Claims

Add custom user roles or permissions:

```python
# Server-side code (not in Streamlit app directly)
from firebase_admin import auth

# Set custom claims
auth.set_custom_user_claims(uid, {
    'role': 'premium',
    'subscription': 'pro'
})

# Access in security rules
// Allow only premium users
allow write: if request.auth.token.role == 'premium';
```

### Multi-Factor Authentication (MFA)

Enable 2FA for enhanced security:

1. Firebase Console → Authentication → Sign-in method
2. Click **"Multi-factor authentication"**
3. Enable **"SMS"** or **"TOTP"**
4. Configure settings
5. Update UI to support MFA enrollment

### Account Linking

Link multiple providers to one account:

```javascript
// Example: Link email to Google account
const provider = new firebase.auth.GoogleAuthProvider();
firebase.auth().currentUser.linkWithPopup(provider);
```

### Analytics Integration

Track authentication events:

1. Enable Google Analytics in Firebase
2. Authentication events auto-logged:
   - `login` - User signs in
   - `sign_up` - User creates account
   - `logout` - User signs out
3. View analytics in Firebase Console

## Monitoring & Debugging

### View User Activity

**Firebase Console:**
1. Go to Authentication → Users
2. View all registered users
3. Check:
   - Email verification status
   - Last sign-in time
   - Provider (email, Google, etc.)
   - UID for debugging

### Debug Authentication Issues

**Enable Debug Logging:**
```python
# In your app code
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Browser Console:**
- Open browser DevTools (F12)
- Check Console tab for Firebase errors
- Network tab shows API requests

**Firebase Logs:**
```bash
# If using Firebase CLI
firebase functions:log
```

## Cost Management

### Free Tier (Spark Plan)

Firebase Authentication is **FREE** with generous limits:
- ✅ **Unlimited** email/password users
- ✅ **50,000** monthly active users (MAU) for phone auth
- ✅ **10,000** phone auth verifications/month
- ✅ **Unlimited** Google Sign-In
- ✅ **Unlimited** other social providers

### Paid Tier (Blaze Plan)

Only charges for phone authentication:
- $0.06 per phone auth verification (after free quota)
- All other auth methods remain free

**Email/Password, Google, Facebook, etc. = FREE forever!**

## Next Steps

- ✅ Enable Firebase Authentication
- ✅ Configure `firebase_config.json`
- ✅ Test sign up/sign in locally
- ✅ Deploy to production (Streamlit Cloud or Cloud Run)
- ✅ Customize email templates
- ✅ Set up monitoring and alerts
- ✅ Review security rules
- 🚀 Optionally enable Google Sign-In or other providers
- 🚀 Consider implementing MFA for premium users
- 🚀 Set up analytics tracking

## Additional Resources

### Documentation
- **Firebase Auth Documentation**: https://firebase.google.com/docs/auth
- **Web Setup Guide**: https://firebase.google.com/docs/auth/web/start
- **Security Best Practices**: https://firebase.google.com/docs/auth/security
- **Email Verification**: https://firebase.google.com/docs/auth/web/manage-users#send_a_user_a_verification_email

### Tools & Console
- **Firebase Console**: https://console.firebase.google.com/
- **Pyrebase4 Documentation**: https://github.com/nhorvath/Pyrebase4
- **Firebase Admin SDK**: https://firebase.google.com/docs/admin/setup

### Support
- **Stack Overflow**: Tag `firebase-authentication`
- **Firebase Community**: https://firebase.google.com/community
- **GitHub Issues**: Report bugs in respective SDKs

---

**🔐 Your app is now secured with Firebase Authentication!** 

Users can create accounts, sign in, and access their personalized trips across all devices!

