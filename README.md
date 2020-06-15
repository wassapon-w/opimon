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

Install MongoDB 3.4
```
# wget -qO - https://www.mongodb.org/static/pgp/server-3.4.asc | sudo apt-key add -
# echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
# sudo apt-get update
# sudo apt-get install -y mongodb-org
# sudo service mongod start
```

Install Node.js & Express.js
```
# sudo apt-get install -y npm
# sudo npm install express --save
# sudo npm install mongodb@2.2.33 --save
```

### Running Command

Run simulation of OpenFlow network
```
# sudo mn --custom opimon/Mininet\ Topology/topology.py --topo mytopo --controller=remote,ip=127.0.0.1,port=6753
```

Run simple controller
```
# ryu-manager --ofp-tcp-listen-port 6733 opimon/Controller/controller.py
```

Run monitoring tool
```
# python opimon/Proxy\ Monitor/proxyMonitor.py
```

Run visualization server
```
# nodejs opimon/Visualization/app.js
```

### Reference

[1] Wassapon, W., Uthayopas, P., Chantrapornchai, C., & Ichikawa, K. (2018). Real-Time monitoring and visualization software for OpenFlow network. In International Conference on ICT and Knowledge Engineering (pp. 1–5). IEEE Computer Society. https://doi.org/10.1109/ICTKE.2017.8259622
