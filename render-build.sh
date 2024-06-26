#!/bin/bash
set -e

apt-get update && apt-get install -y wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
