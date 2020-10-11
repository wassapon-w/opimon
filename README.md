# Opimon (OpenFlow Interactive Monitoring)

### Requirements
- Ryu SDN Library
- Node.js & Express.js
- MongoDB
- Mininet & Open vSwitch (Optional)

### Install Command

Recommended OS : Ubuntu Server 20.04

Install Mininet & Open vSwitch
```
# sudo apt-get install -y mininet
```

Install Ryu SDN Library
```
# sudo apt-get install -y python3-pip libffi-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev
# pip3 install ryu pymongo line_profiler
```

Install MongoDB 3.6
```
# wget -qO - https://www.mongodb.org/static/pgp/server-3.6.asc | sudo apt-key add -
# echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
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
# python3 opimon/Proxy\ Monitor/proxyMonitor.py
```

Run visualization server
```
# nodejs opimon/Visualization/app.js
```

### Reference

[1] Wassapon, W., Uthayopas, P., Chantrapornchai, C., & Ichikawa, K. (2018). Real-Time monitoring and visualization software for OpenFlow network. In International Conference on ICT and Knowledge Engineering (pp. 1–5). IEEE Computer Society. https://doi.org/10.1109/ICTKE.2017.8259622
