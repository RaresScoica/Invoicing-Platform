#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Download precompiled static binary for wkhtmltopdf
wget -O wkhtmltopdf https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.amd64.static.deb

# Make it executable
chmod +x wkhtmltopdf

# Move it to a known location
mv wkhtmltopdf /usr/local/bin/wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
