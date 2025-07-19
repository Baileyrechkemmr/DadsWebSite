# WSL First-Time Setup Guide for Omimi Swords

This guide provides comprehensive instructions for setting up the Omimi Swords project on Windows Subsystem for Linux (WSL). Follow these steps to configure your development environment and populate the local Django database with S3 paths.

## Prerequisites

1. Windows 10 version 2004+ or Windows 11
2. Administrative access to your Windows machine
3. At least 5GB of free disk space
4. Internet connection

## Step 1: Install WSL

### Install WSL 2 with Ubuntu

Open PowerShell as Administrator and run:

```powershell
# Install WSL with Ubuntu (default)
wsl --install

# If you need to specify Ubuntu explicitly
# wsl --install -d Ubuntu
```

Restart your computer when prompted.

After restart, Ubuntu will launch automatically. You'll need to:
1. Create a username and password for your Ubuntu installation
2. Wait for the initial setup to complete

## Step 2: Update Ubuntu

Open Ubuntu from the Start menu and update the system:

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install development essentials
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

## Step 3: Install Python 3 and Required Tools

Install Python and related tools:

```bash
# Install Python 3, pip, venv, and Git
sudo apt install -y python3 python3-pip python3-venv git

# Verify installations
python3 --version
pip3 --version
git --version
```

## Step 4: Clone the Repository

Clone the Omimi Swords repository:

```bash
# Navigate to your preferred directory
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone https://github.com/Baileyrechkemmr/DadsWebSite.git omimi_swords
cd omimi_swords

# Check out the AWS blog backend branch
git checkout aws-blog-backend
```

## Step 5: Create and Activate Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your prompt should change to indicate the virtual environment is active
# (venv) username@hostname:~/projects/omimi_swords$
```

## Step 6: Install Project Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt
```

## Step 7: Set Up Environment Variables

Create a .env file with your AWS credentials:

```bash
# Create .env file
cat > .env << 'EOL'
DEBUG=True
SECRET_KEY=your-secret-key-here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=ominisword-images
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOL

# Edit the file to add your actual credentials
nano .env
```

Replace the placeholder values with your actual AWS credentials and other settings.

## Step 8: Initialize Django Database

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations to set up the database structure
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
# Follow the prompts to create your admin account
```

## Step 9: Populate S3 Paths in the Database

Run the S3 path population script to populate your local database with S3 paths:

```bash
# Run the script
python populate_s3_paths.py
```

This script will:
- Update or create records for Sword_img, Sword_sales, and BlogImages models
- Point image fields to the appropriate S3 paths
- Associate blog images with blog posts
- Display a summary of what was updated

## Step 10: Verify the Setup

```bash
# Start the Django development server
python manage.py runserver 0.0.0.0:8000
```

Open a web browser on Windows and navigate to:
- http://localhost:8000 - To view the website
- http://localhost:8000/admin - To access the admin interface (use the superuser credentials you created)

Verify that:
1. The website loads correctly
2. Images display properly from S3
3. You can log in to the admin interface

## Step 11: Stopping the Server

To stop the Django development server, press `Ctrl+C` in the terminal where it's running.

To deactivate the virtual environment, run:

```bash
deactivate
```

## Common Issues and Troubleshooting

### Port Already in Use

```bash
# If port 8000 is in use, specify a different port
python manage.py runserver 0.0.0.0:8001
```

### Database Migration Errors

```bash
# Reset the database (will delete all data)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python populate_s3_paths.py
```

### S3 Images Not Loading

1. Verify AWS credentials in your .env file
2. Check the S3 bucket name and region
3. Run the check_s3_files.py script:
   ```bash
   python check_s3_files.py
   ```

### WSL Networking Issues

If you encounter networking issues within WSL:

```powershell
# Run in PowerShell as Administrator
wsl --shutdown
netsh winsock reset
Restart-Computer
```

## Working with WSL File System

### Accessing WSL Files from Windows

You can access WSL files in Windows Explorer by navigating to:
```
\\wsl$\Ubuntu\home\your-username\projects\omimi_swords
```

### Accessing Windows Files from WSL

Windows drives are mounted in WSL under `/mnt/`. For example, to access your C: drive:
```bash
cd /mnt/c/Users/your-windows-username/Documents
```

## Keeping Your Environment Updated

```bash
# Pull latest changes
git pull

# Update dependencies if requirements.txt changed
pip install -r requirements.txt

# Apply any new migrations
python manage.py migrate

# If S3 paths need updating
python populate_s3_paths.py
```

## Exiting and Reopening WSL

### Closing WSL

To properly exit WSL, type:
```bash
exit
```

### Reopening WSL and Resuming Development

```bash
# Open Ubuntu from Start menu
# Then navigate to project
cd ~/projects/omimi_swords

# Activate virtual environment
source venv/bin/activate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

## Development Workflow in WSL

1. Pull the latest changes from Git
2. Activate the virtual environment
3. Apply any new migrations
4. Run the development server
5. Make and test changes
6. Commit and push changes (after careful review)

```bash
# Example workflow
cd ~/projects/omimi_swords
source venv/bin/activate
git pull
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# After making changes
git add .
git commit -m "Descriptive commit message"
git push origin aws-blog-backend
```

## Conclusion

You now have a complete development environment for the Omimi Swords project running on WSL. This setup allows you to develop on Windows while taking advantage of Linux's native compatibility with many web development tools.