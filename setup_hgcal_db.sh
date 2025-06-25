#!/bin/bash

set -e

echo "=== Updating package list ==="
sudo dnf update -y

echo "=== Installing packages ==="
sudo dnf install -y \
	mariadb-server \
	mariadb \
	git \
	python3 \
	python3-pip \
	httpd

echo "=== Starting MariaDB service ==="
sudo systemctl start mariadb
sudo systemctl enable mariadb

echo "=== Securing MariaDB installation ==="
sudo mysql_secure_installation

echo "=== Cloning Web API ==="
git clone -b install git@github.com:UMN-CMS/HGCAL_QC_WebInterface.git

echo "=== Setting up Python virtual environment ==="
cd HGCAL_QC_WebInterface
python3 -m venv webappenv
source webappenv/bin/activate

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Creating Database Schema ==="
mysql -u root -p < schema.sql

echo "=== Strating Apache HTTP service ==="
sudo systemctl enable httpd
sudo systemctl start httpd

echo "=== Finished ==="
