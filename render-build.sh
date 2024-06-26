#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Download precompiled static binary for wkhtmltopdf
wget -O wkhtmltopdf https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb

# Make it executable
chmod +x wkhtmltopdf

# Install required libraries
apt-get update && apt-get install -y libxrender1 libfontconfig1 libxtst6 libjpeg-dev

# Install wkhtmltopdf
dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb || apt-get -f install -y

# Clean up
rm wkhtmltox_0.12.6-1.bionic_amd64.deb

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
