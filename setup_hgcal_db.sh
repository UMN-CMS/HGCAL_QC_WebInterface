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
        httpd \
	mod_ssl

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

echo "=== Creating httpd config files ==="
sudo tee /etc/httpd/conf.d/factorydb.conf > /dev/null <<EOF
Alias "/Factory/static" /home/$(whoami)/HGCAL_QC_WebInterface/static
<Directory "/home/$(whoami)/HGCAL_QC_WebInterface/static">
    AllowOverride None
    Require all granted
</Directory>

ScriptAlias /Factory/ /home/$(whoami)/HGCAL_QC_WebInterface/cgi-bin/
<Directory "/home/$(whoami)/HGCAL_QC_WebInterface/cgi-bin/">
    AllowOverride None
    Options +ExecCGI
    Require all granted
</Directory>
EOF
sudo tee /etc/httpd/conf.d/ssl.conf > /dev/null <<EOF
LoadModule ssl_module modules/mod_ssl.so

Listen 443
#<VirtualHost *:443>
# Add domain name and SSL Certificate File here
#    ServerName yourdomain.com
#    SSLEngine on
#    SSLCertificateFile /etc/path/to/cert.pem
#    SSLCertificateKeyFile /etc/path/to/privkey.pem
#</VirtualHost>
EOF

echo "=== Allowing access through firewall on ports 80 (HTTP) and 443 (HTTPS) ==="
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

echo "=== Allowing Apache access to $(whoami)'s home directory ==="
sudo setsebool -P httpd_enable_homedirs 1
sudo chcon -R -t httpd_sys_script_exec_t ~/HGCAL_QC_WebInterface/cgi-bin/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/HGCAL_QC_WebInterface/static/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/HGCAL_QC_WebInterface/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/
sudo chcon -t httpd_sys_content_t /home/

sudo systemctl restart httpd

echo "=== Finished ==="
