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
git clone https://hgcaltestgui:gldt-_nACNMrPNxyAuX4uz5Ae@gitlab.cern.ch/hgcal-integration/hgcal-label-info.git

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

read -p "Enter the name for the new MariaDB database: " DB_NAME
read -p "Enter desired name of the Read user: " READ_USER
read -p "Create a password for the Read user: " READ_PASS
read -p "Enter desired name of the Insert user: " INSERTER
read -p "Create a password for the Insert user: " INSERT_PASS

sed -i "s/user=''/user='$READ_USER'/g" ./cgi-bin/exampleDB/connect.py
sed -i "s/user =''/user='$INSERTER'/g" ./cgi-bin/exampleDB/connect.py
sed -i "s/password=''/password='$READ_PASS'/g" ./cgi-bin/exampleDB/connect.py
sed -i "s/password =''/password='$INSERT_PASS'/g" ./cgi-bin/exampleDB/connect.py
sed -i "s/name = ''/name = '$DB_NAME'/g" ./cgi-bin/exampleDB/connect.py

read -p "Create an password to access admin functionalities from the webpage: " ADMIN_PASS
echo
hash=$(python3 -c "import hashlib, sys; print(hashlib.sha256(sys.stdin.read().encode()).hexdigest())" <<< "$ADMIN_PASS")

sed -i "s/ == '':/ == '$hash':/g" ./cgi-bin/exampleDB/connect.py
sed -i "s:path/to:home/$(whoami):g" ./cgi-bin/exampleDB/cgi_runner.sh

echo "=== Creating Database '$DB_NAME' ==="
mariadb -u root -p -e "CREATE DATABASE \`${DB_NAME}\`"
echo "=== Importing schema.sql into '$DB_NAME' ==="
mariadb -u root -p "$DB_NAME" < schema.sql
echo "=== Adding users to Database ==="
export DB_NAME
export READ_USER
export READ_PASS
export INSERTER
export INSERT_PASS
envsubst < users.sql > tmp.sql
mariadb -u root -p < tmp.sql
rm tmp.sql

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

echo "=== Allowing Apache access to traverse $(whoami)'s home directory ==="
sudo chmod o+x /home/
sudo chmod o+x /home/$(whoami)/
sudo chmod o+x /home/$(whoami)/HGCAL_QC_WebInterface/

echo "=== Changing SELinux Permissions ==="
sudo setsebool -P httpd_enable_homedirs 1
sudo setsebool -P httpd_can_network_connect_db 1
sudo setsebool -P httpd_can_network_connect 1
sudo chcon -R -t httpd_sys_script_exec_t ~/HGCAL_QC_WebInterface/cgi-bin/
sudo chcon -R -t httpd_sys_script_exec_t ~/HGCAL_QC_WebInterface/hgcal-label-info/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/HGCAL_QC_WebInterface/static/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/HGCAL_QC_WebInterface/
sudo chcon -t httpd_sys_content_t /home/$(whoami)/
sudo chcon -t httpd_sys_content_t /home/
sudo chcon -R -t httpd_sys_script_exec_t /home/admin/HGCAL_QC_WebInterface/webappenv
cat <<EOF > apache_mysql_socket.te
module apache_mysql_socket 1.0;

require {
    type httpd_sys_script_t;
    type mysqld_var_run_t;
    class unix_stream_socket connectto;
}

allow httpd_sys_script_t mysqld_var_run_t:unix_stream_socket connectto;
EOF
checkmodule -M -m -o apache_mysql_socket.mod apache_mysql_socket.te
semodule_package -o apache_mysql_socket.pp -m apache_mysql_socket.mod
sudo semodule -i apache_mysql_socket.pp
sudo restorecon -v /var/lib/mysql/mysql.sock 
curl -k http://localhost/Factory/exampleDB/home_page.p
sudo ausearch -c 'python3' --raw | audit2allow -M my-python-sql
sudo semodule -i my-python-sql.pp

sudo systemctl restart httpd

echo "=== Finished ==="
