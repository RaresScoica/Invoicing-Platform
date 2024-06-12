#!/bin/bash
set -e

# Update package lists
apt-get update

# Install wkhtmltopdf and its dependencies
apt-get install -y xvfb libfontconfig wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
