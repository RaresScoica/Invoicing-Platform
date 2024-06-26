#!/bin/bash
chmod +x /opt/render/project/src//wkhtmltopdf.exe
#!/bin/bash
set -e

# Ensure apt directory structure exists
mkdir -p /var/lib/apt/lists/partial

# Update package lists
apt-get update

# Install wkhtmltopdf and its dependencies
apt-get install -y xvfb libfontconfig wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt