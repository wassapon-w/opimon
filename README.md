# Opimon (OpenFlow Interactive Monitoring)

### Requirements
- Ryu SDN Library
- Node.js & Express.js
- MongoDB
- Mininet & Open vSwitch (Optional)

### Install Command

Recommended OS : Ubuntu Server 16.04

Install Mininet & Open vSwitch
```
# sudo apt-get install -y mininet
```

Install Ryu SDN Library
```
# git clone https://github.com/boom10899/ryuInstallHelper.git
# cd ryuInstallHelper
# sudo bash ryuInstallHelper.sh
# cd ~/ryu
# sudo pip install -r tools/pip-requires
# sudo apt-get install -y python-lzma
# sudo python -m pip install pymongo
```

Install MongoDB
```
# sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
# echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
# sudo apt-get update
# sudo apt-get install -y mongodb-org
# sudo service mongod start
```

Install Node.js & Express.js
```
# sudo apt-get install -y npm
# sudo npm install express --save
# sudo npm install mongodb --save
```

### Running Command

Run simulation of OpenFlow network
```
# sudo mn --custom ryuPacketMonitor/Mininet\ Topology/topology.py --topo mytopo --controller=remote,ip=127.0.0.1,port=6753
```

Run simple controller
```
# ryu-manager --ofp-tcp-listen-port 6733 ryuPacketMonitor/Controller/controller.py
```

Run monitoring tool
```
# python packetMonitor/Proxy\ Monitor/proxyMonitor.py
```

Run visualization server
```
# nodejs packetMonitor/Visualization/app.js
```
