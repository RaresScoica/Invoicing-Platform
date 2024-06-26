#!/bin/bash
set -e

apt-get update
apt-get install -y wget xz-utils libxrender1 libfontconfig1 libx11-dev libjpeg-dev libxtst6
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb || apt-get -f install -y
rm wkhtmltox_0.12.6-1.bionic_amd64.deb
ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
