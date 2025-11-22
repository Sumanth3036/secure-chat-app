# How to Set Python Version in Render Dashboard

Since `render.yaml` environment variables are set AFTER Python is installed, you need to manually set the Python version in the Render Dashboard.

## Steps:

1. **Go to your Render Dashboard**: https://dashboard.render.com
2. **Select your service**: `private-chat-backend`
3. **Go to Settings** → **Environment**
4. **Add Environment Variable**:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.10.12`
5. **Save Changes**
6. **Trigger a new deployment** (or wait for auto-deploy)

## Alternative: Recreate the Service

If the above doesn't work, you may need to:

1. Delete the existing service
2. Create a new service from the same repository
3. During creation, in the **Environment** section, add `PYTHON_VERSION=3.10.12` BEFORE clicking "Create Web Service"
4. This ensures Python 3.10.12 is installed from the start

## Why This Happens

Render installs Python BEFORE reading environment variables from `render.yaml`, so the `PYTHON_VERSION` in `envVars` doesn't take effect for the initial Python installation. It must be set in the dashboard or during service creation.





