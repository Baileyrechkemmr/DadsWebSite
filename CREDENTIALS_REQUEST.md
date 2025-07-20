# 🔐 Credentials Request - OMIMI Swords Project

## Required for Development Setup

To run this project locally, you'll need the following credentials from the project maintainer:

### 1. AWS S3 Access (REQUIRED)
```
AWS_ACCESS_KEY_ID=<contact_maintainer>
AWS_SECRET_ACCESS_KEY=<contact_maintainer>
AWS_STORAGE_BUCKET_NAME=ominisword-images
AWS_S3_REGION=us-east-1
```

**Why needed**: All 68+ images are stored in S3. Without these credentials, images won't load.

### 2. Email Configuration (REQUIRED)
```
EMAIL_HOST_USER=<contact_maintainer>
EMAIL_HOST_PASSWORD=<contact_maintainer>
```

**Why needed**: Contact forms (class registration, orders) won't work without SMTP access.

### 3. Django Secret Key (GENERATE NEW)
```
SECRET_KEY=<generate_your_own>
```

**How to generate**:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 📞 How to Request Credentials

1. **Contact the maintainer** via:
   - GitHub issues
   - Email (if known)
   - Team communication channels

2. **Provide your details**:
   - Your name and role
   - Purpose (development, testing, etc.)
   - Duration needed

3. **Security agreement**:
   - Keep credentials secure
   - Don't commit to version control
   - Use only for development
   - Rotate if compromised

## 🛡️ Security Best Practices

- Store credentials only in `.env` file
- Never commit `.env` to git
- Use different credentials for production
- Regularly rotate access keys
- Report any suspected compromise immediately

## 🔄 Alternative Setup (No Credentials)

If you can't get credentials immediately:

1. **Disable S3 temporarily**:
   ```python
   # In settings.py, comment out:
   # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

2. **Use local media**:
   ```python
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
   ```

3. **Skip email features** until configured

---

**Note**: This is a security-conscious approach to credential sharing for collaborative development.
