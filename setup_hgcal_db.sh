#!/bin/bash

set -e

echo "=== Updating package list ==="
sudo dnf update -y

echo "=== Adding MariaDB 10.11 official repo ==="
sudo tee /etc/yum.repos.d/MariaDB.repo > /dev/null <<EOF
[mariadb]
name = MariaDB
baseurl = https://rpm.mariadb.org/10.11/rhel/9/x86_64
gpgkey=https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
enabled=1
EOF

echo "=== Refreshing package list ==="
sudo dnf clean all
sudo dnf makecache


echo "=== Installing packages ==="
sudo dnf install -y \
        MariaDB-server \
        MariaDB-devel \
        git \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        httpd

echo "=== Starting MariaDB service ==="
sudo systemctl start mariadb
sudo systemctl enable mariadb

echo "=== Securing MariaDB installation ==="
echo "=== When prompted, set the root password. You will need this later in the setup. ==="
sudo mariadb-secure-installation

echo "=== Cloning Web API ==="
git clone -b install git@github.com:UMN-CMS/HGCAL_QC_WebInterface.git

echo "=== Setting up Python virtual environment ==="
cd HGCAL_QC_WebInterface
python3 -m venv webappenv
source webappenv/bin/activate

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

read -p "Enter the name for the new MariaDB database: " DB_NAME

echo "=== Creating Database '$DB_NAME' ==="
mariadb -u root -p -e "CREATE DATABASE \`${DB_NAME}\`"
echo "=== Importing schema.sql into '$DB_NAME'"
mariadb -u root -p "$DB_NAME" < schema.sql

echo "=== Starting Apache HTTP service ==="
sudo systemctl enable httpd
sudo systemctl start httpd

echo "=== Finished ==="
