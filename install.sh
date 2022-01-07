#!/bin/sh
# Install script for Opimon and dependencies.

# Check Permission
test $(id -u) -ne 0 && echo "This script must be run as root" && exit 0

# Installing
echo "Installing Mininet and Open vSwitch"
apt-get install -y mininet

echo "Installing Ryu SDN Library"
apt-get install -y python3 python3-pip libffi-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev
pip3 install ryu pymongo line_profiler

echo "Installing MongoDB"
wget -qO - https://www.mongodb.org/static/pgp/server-3.6.asc | apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/3.6 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.6.list
apt-get update
apt-get install -y mongodb-org
service mongod start

echo "Node.js & Express.js"
apt-get install -y npm
npm install express --save
npm install mongodb@2.2.33 --save