#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package list and install dependencies
apt-get update
apt-get install -y wget xz-utils libxrender1 libfontconfig1 libx11-dev libjpeg-dev libxtst6

# Download wkhtmltopdf
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb

# Install wkhtmltopdf
apt-get install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb

# Clean up
rm wkhtmltox_0.12.6-1.bionic_amd64.deb

# Ensure wkhtmltopdf is in a known location
ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
