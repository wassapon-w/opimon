var express = require('express');
var path =  require("path");
var fs = require('fs');
var app = express();

var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
// var url = 'mongodb://sd-lemon.naist.jp:9999/opimon';
// var url = 'mongodb://localhost:27017/opimon';
var url = 'mongodb://opimon:KFJaJSdVHbRFU3e0DOEcsmobGz5Nd8krM7sUIi17nmCwYm39eGK1ap5uomgB6EYNoVvkD9VQ79wrn1XAGop5cg==@opimon.documents.azure.com:10250/opimon?ssl=true';
var counter = 0;
var startTime = 0;

app.get('/', function(req, res){
    res.setHeader('Content-Type', 'text/html');
    res.sendFile(path.join(__dirname, './public', 'index.html'));
});

app.get('/visualize.js', function(req, res){
    res.sendFile(path.join(__dirname, './public/js', 'visualize.js'));
});

app.get('/settings.json', function(req, res){
    res.sendFile(path.join(__dirname, './public', 'settings.json'));
});

app.get('/ku.png', function(req, res){
    res.sendFile(path.join(__dirname, './public/img', 'KU.png'));
});

app.get('/naist.png', function(req, res){
    res.sendFile(path.join(__dirname, './public/img', 'NAIST.png'));
});

app.get('/flowmods', function (req, res) {
  getFlowMods();

  function getFlowMods() {
  	var flowModsDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('flow_mods').find( { timestamp: { $gte: new Date(Date.now() - 10 * 1000), $lt: new Date(Date.now()) } } );
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				// console.dir(doc);
  				flowModsDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request FlowMod from webpage");
  				db.close();

          var flowTable = {};
          var switchFlowTable = [];

          for(var i = 0; i < flowModsDatabase.length; i++) {
            if(flowTable[flowModsDatabase[i]["switch"]] != undefined) {
              if(flowModsDatabase[i]["message"]["actions"][0] != undefined) {
                var flow = {};
                flow["switch_id"] = flowModsDatabase[i]["switch"];
                flow["match"] = flowModsDatabase[i]["message"]["match"];
                flow["actions"] = flowModsDatabase[i]["message"]["actions"];
                flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
                flow["idle_timeout"] = flowModsDatabase[i]["message"]["idle_timeout"];
                flow["timestamp"] = flowModsDatabase[i]["timestamp"];
                flowTable[flowModsDatabase[i]["switch"]].push(flow);
              }
            }
            else {
              flowTable[flowModsDatabase[i]["switch"]] = [];
              switchFlowTable.push(flowModsDatabase[i]["switch"]);

              if(flowModsDatabase[i]["message"]["actions"][0] != undefined) {
                var flow = {};
                flow["switch_id"] = flowModsDatabase[i]["switch"];
                flow["match"] = flowModsDatabase[i]["message"]["match"];
                flow["actions"] = flowModsDatabase[i]["message"]["actions"];
                flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
                flow["idle_timeout"] = flowModsDatabase[i]["message"]["idle_timeout"];
                flow["timestamp"] = flowModsDatabase[i]["timestamp"];
                flowTable[flowModsDatabase[i]["switch"]].push(flow);
              }
            }
          }

          flowTable["switchFlowTable"] = switchFlowTable.sort(function(a,b) { return a - b; });

          res.json(flowTable);
  			}
  		});
  	});
  }
});

app.get('/topology', function (req, res) {
  getTopology();

  function getTopology() {
  	var topologyDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('topology').find( { timestamp: { $gte: new Date(Date.now() - 10 * 1000), $lt: new Date(Date.now()) } } );
      // var cursor = db.collection('topology').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				// console.dir(doc);
  				topologyDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Topology from webpage");
  				db.close();

          var topology = {};
          topology["node"] = [];
          topology["link"] = [];

          var checkSwitch = {};

          var nodeCounter = 0;
          for(var i = 0; i < topologyDatabase.length; i++) {
            var isNew = true;
            for(var j = 0; j < topology["node"].length; j++) {
              if(topology["node"][j]["id"] == topologyDatabase[i]["switch_dst"]) {
                for(var k = 0; k < topology["node"][j]["connect_to"].length; k++) {
                  if(topology["node"][j]["connect_to"][k] == topologyDatabase[i]["switch_src"]) {
                    isNew = false;
                    break;
                  }
                }
                if(isNew) {
                  topology["node"][j]["connect_to"].push(topologyDatabase[i]["switch_src"] + '');

                  if(checkSwitch[topologyDatabase[i]["switch_src"] + ''] != 1) {
                    var node = {};
                    node["id"] = topologyDatabase[i]["switch_src"] + '';
                    node["group"] = 1;
                    node["connect_to"] = [];
                    topology["node"].push(node);
                    checkSwitch[topologyDatabase[i]["switch_src"] + ''] = 1;
                  }

                  topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] + '';
                  topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] + '';
                  topologyDatabase[i]["value"] = 1;
                  topology["link"].push(topologyDatabase[i]);
                  isNew = false;
                  break;
                }
              }
            }

            if(isNew) {
              nodeCounter++;
              var node = {};
              node["id"] = topologyDatabase[i]["switch_dst"] + '';
              node["group"] = 1;
              node["connect_to"] = [];
              node["connect_to"].push(topologyDatabase[i]["switch_src"] + '');
              topology["node"].push(node);
              checkSwitch[topologyDatabase[i]["switch_dst"] + ''] = 1;

              if(checkSwitch[topologyDatabase[i]["switch_src"] + ''] != 1) {
                var node = {};
                node["id"] = topologyDatabase[i]["switch_src"] + '';
                node["group"] = 1;
                node["connect_to"] = [];
                topology["node"].push(node);
                checkSwitch[topologyDatabase[i]["switch_src"] + ''] = 1;
              }

              topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] + '';
              topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] + '';
              topologyDatabase[i]["value"] = 1;
              topology["link"].push(topologyDatabase[i]);
            }
          }

          topology["nodeCounter"] = nodeCounter;

          res.json(topology);
  			}
  		});
  	});
  }
});

app.get('/switch', function (req, res) {
  getSwitchPort();

  function getSwitchPort() {
  	var switchDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('switch_port').find( { timestamp: { $gte: new Date(Date.now() - 10 * 1000), $lt: new Date(Date.now()) } } );
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				switchDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Switch Port from webpage");
  				db.close();

          var switchPort = {};
          var portChecker = {};

          for(var i = 0; i < switchDatabase.length; i++) {
            if(switchPort[switchDatabase[i]["switch_id"]] != undefined) {
              if(portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] != 1) {
                var port = {};
                port["port_no"] = switchDatabase[i]["port_no"];
                port["hw_addr"] = switchDatabase[i]["hw_addr"];
                switchPort[switchDatabase[i]["switch_id"]]["ports"].push(port);

                portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] = 1;
              }
            }
            else {
              switchPort[switchDatabase[i]["switch_id"]] = {};
              switchPort[switchDatabase[i]["switch_id"]]["switch_id"] = switchDatabase[i]["switch_id"];
              switchPort[switchDatabase[i]["switch_id"]]["ports"] = [];

              var port = {};
              port["port_no"] = switchDatabase[i]["port_no"];
              port["hw_addr"] = switchDatabase[i]["hw_addr"];
              switchPort[switchDatabase[i]["switch_id"]]["ports"].push(port);

              portChecker[switchDatabase[i]["switch_id"]] = {}
              portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] = 1;
            }
          }

          for(var eachSwitch in switchPort) {
              switchPort[eachSwitch]["ports"].sort(function(a,b) {return (a.port_no > b.port_no) ? 1 : ((b.port_no > a.port_no) ? -1 : 0);} );
          }

          res.json(switchPort);
  			}
  		});
  	});
  }
});

app.get('/flowmodsdata', function (req, res) {
  getFlowMods();

  function getFlowMods() {
  	var flowModsDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('flow_mods').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				flowModsDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request FlowMod (Full) from webpage");
  				db.close();

          res.json(flowModsDatabase);
  			}
  		});
  	});
  }
});

app.get('/topologydata', function (req, res) {
  getTopology();

  function getTopology() {
  	var topologyDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('topology').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				topologyDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Topology (Full) from webpage");
  				db.close();

          res.json(topologyDatabase);
  			}
  		});
  	});
  }
});

app.get('/switchdata', function (req, res) {
  getSwitchPort();

  function getSwitchPort() {
  	var switchDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('switch_port').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				switchDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Switch Port (Full) from webpage");
  				db.close();

          res.json(switchDatabase);
  			}
  		});
  	});
  }
});

app.get('/dataquery', function (req, res, next) {
  // console.log(req.query["timeSecond"]);
  // res.json({'status': 200, 'msg': 'success'});
  var queryData = {};
  var queryTime = new Date(parseInt(req.query["timeSecond"]));
  var fromTime = new Date(parseInt(req.query["timeSecond"]) - 60 * 1000);
  var toTime = new Date(parseInt(req.query["timeSecond"]) + 30 * 1000);
  queryTopology();

  function queryTopology() {
  	var topologyDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('topology').find( { timestamp: { $gte: fromTime, $lt: toTime } } );
      // var cursor = db.collection('topology').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				// console.log(doc);
  				topologyDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Topology from webpage");
  				db.close();

          var topology = {};
          topology["node"] = [];
          topology["link"] = [];

          var checkSwitch = {};

          var nodeCounter = 0;
          for(var i = 0; i < topologyDatabase.length; i++) {
            var isNew = true;
            for(var j = 0; j < topology["node"].length; j++) {
              if(topology["node"][j]["id"] == topologyDatabase[i]["switch_dst"]) {
                for(var k = 0; k < topology["node"][j]["connect_to"].length; k++) {
                  if(topology["node"][j]["connect_to"][k] == topologyDatabase[i]["switch_src"]) {
                    isNew = false;
                    break;
                  }
                }
                if(isNew) {
                  topology["node"][j]["connect_to"].push(topologyDatabase[i]["switch_src"] + '');

                  if(checkSwitch[topologyDatabase[i]["switch_src"] + ''] != 1) {
                    var node = {};
                    node["id"] = topologyDatabase[i]["switch_src"] + '';
                    node["group"] = 1;
                    node["connect_to"] = [];
                    topology["node"].push(node);
                    checkSwitch[topologyDatabase[i]["switch_src"] + ''] = 1;
                  }

                  topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] + '';
                  topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] + '';
                  topologyDatabase[i]["value"] = 1;
                  topology["link"].push(topologyDatabase[i]);
                  isNew = false;
                  break;
                }
              }
            }

            if(isNew) {
              nodeCounter++;
              var node = {};
              node["id"] = topologyDatabase[i]["switch_dst"] + '';
              node["group"] = 1;
              node["connect_to"] = [];
              node["connect_to"].push(topologyDatabase[i]["switch_src"] + '');
              topology["node"].push(node);
              checkSwitch[topologyDatabase[i]["switch_dst"] + ''] = 1;

              if(checkSwitch[topologyDatabase[i]["switch_src"] + ''] != 1) {
                var node = {};
                node["id"] = topologyDatabase[i]["switch_src"] + '';
                node["group"] = 1;
                node["connect_to"] = [];
                topology["node"].push(node);
                checkSwitch[topologyDatabase[i]["switch_src"] + ''] = 1;
              }

              topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] + '';
              topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] + '';
              topologyDatabase[i]["value"] = 1;
              topology["link"].push(topologyDatabase[i]);
            }
          }

          topology["nodeCounter"] = nodeCounter;

          queryData["topology"] = topology;

          querySwitchPort()
  			}
  		});
  	});
  }

  function querySwitchPort() {
  	var switchDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('switch_port').find( { timestamp: { $gte: fromTime, $lt: toTime } } );
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				switchDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Switch Port from webpage");
  				db.close();

          var switchPort = {};
          var portChecker = {};

          for(var i = 0; i < switchDatabase.length; i++) {
            if(switchPort[switchDatabase[i]["switch_id"]] != undefined) {
              if(portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] != 1) {
                var port = {};
                port["port_no"] = switchDatabase[i]["port_no"];
                port["hw_addr"] = switchDatabase[i]["hw_addr"];
                switchPort[switchDatabase[i]["switch_id"]]["ports"].push(port);

                portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] = 1;
              }
            }
            else {
              switchPort[switchDatabase[i]["switch_id"]] = {};
              switchPort[switchDatabase[i]["switch_id"]]["switch_id"] = switchDatabase[i]["switch_id"];
              switchPort[switchDatabase[i]["switch_id"]]["ports"] = [];

              var port = {};
              port["port_no"] = switchDatabase[i]["port_no"];
              port["hw_addr"] = switchDatabase[i]["hw_addr"];
              switchPort[switchDatabase[i]["switch_id"]]["ports"].push(port);

              portChecker[switchDatabase[i]["switch_id"]] = {}
              portChecker[switchDatabase[i]["switch_id"]][switchDatabase[i]["port_no"]] = 1;
            }
          }

          for(var eachSwitch in switchPort) {
              switchPort[eachSwitch]["ports"].sort(function(a,b) {return (a.port_no > b.port_no) ? 1 : ((b.port_no > a.port_no) ? -1 : 0);} );
          }

          queryData["switch"] = switchPort;

          queryFlowMods();
  			}
  		});
  	});
  }

  function queryFlowMods() {
  	var flowModsDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('flow_mods').find( { timestamp: { $gte: fromTime, $lt: toTime } } );
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				// console.dir(doc);
  				flowModsDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request FlowMod from webpage");
  				db.close();

          var flowTable = {};
          var switchFlowTable = [];

          for(var i = 0; i < flowModsDatabase.length; i++) {
            if(flowTable[flowModsDatabase[i]["switch"]] != undefined) {
              if(flowModsDatabase[i]["message"]["actions"][0] != undefined) {
                var flow = {};
                flow["switch_id"] = flowModsDatabase[i]["switch"];
                flow["match"] = flowModsDatabase[i]["message"]["match"];
                flow["actions"] = flowModsDatabase[i]["message"]["actions"];
                flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
                flow["idle_timeout"] = flowModsDatabase[i]["message"]["idle_timeout"];
                flow["timestamp"] = flowModsDatabase[i]["timestamp"];
                flowTable[flowModsDatabase[i]["switch"]].push(flow);
              }
            }
            else {
              flowTable[flowModsDatabase[i]["switch"]] = [];
              switchFlowTable.push(flowModsDatabase[i]["switch"]);

              if(flowModsDatabase[i]["message"]["actions"][0] != undefined) {
                var flow = {};
                flow["switch_id"] = flowModsDatabase[i]["switch"];
                flow["match"] = flowModsDatabase[i]["message"]["match"];
                flow["actions"] = flowModsDatabase[i]["message"]["actions"];
                flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
                flow["idle_timeout"] = flowModsDatabase[i]["message"]["idle_timeout"];
                flow["timestamp"] = flowModsDatabase[i]["timestamp"];
                flowTable[flowModsDatabase[i]["switch"]].push(flow);
              }
            }
          }

          flowTable["switchFlowTable"] = switchFlowTable.sort(function(a,b) { return a - b; });

          queryData["flowTable"] = flowTable;

          queryPortStat();
  			}
  		});
  	});
  }

  function queryPortStat() {
  	var portDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('port_stats').find( { timestamp: { $gte: fromTime, $lt: toTime } } );
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				portDatabase.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request Port Stats from webpage");
  				db.close();

          var portDetail = {};

          for(var i = 0; i < portDatabase.length; i++) {
            if(portDetail[portDatabase[i]["switch"]] == undefined) {
                portDetail[portDatabase[i]["switch"]] = {}
            }

            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]] = {}
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_packets"] = portDatabase[i]["rx_packets"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["tx_packets"] = portDatabase[i]["tx_packets"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_bytes"] = portDatabase[i]["rx_bytes"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["tx_bytes"] = portDatabase[i]["tx_bytes"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_dropped"] = portDatabase[i]["rx_dropped"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["tx_dropped"] = portDatabase[i]["tx_dropped"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_errors"] = portDatabase[i]["rx_errors"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["tx_errors"] = portDatabase[i]["tx_errors"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_frame_err"] = portDatabase[i]["rx_frame_err"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_over_err"] = portDatabase[i]["rx_over_err"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["rx_crc_err"] = portDatabase[i]["rx_crc_err"]
            portDetail[portDatabase[i]["switch"]][portDatabase[i]["port_no"]]["collisions"] = portDatabase[i]["collisions"]
          }

          queryData["ports"] = portDetail;

          res.json(queryData);
  			}
  		});
  	});
  }
});

app.get('/gettime', function (req, res) {
  getMinTime();

  function getMinTime() {
  	var minTime = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('topology').find().sort({"timestamp":1}).limit(1);
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
          // console.dir(doc);
  				minTime.push(doc);
  			}
  			else {
          // counter++;
  				db.close();
          res.json(minTime[0]["timestamp"]);
          startTime = minTime[0]["timestamp"];
  			}
  		});
  	});
  }
});

app.get('/savenode', function (req, res, next) {
  // console.log(req.query["switchNode"]);
  var switchNode = req.query["switchNode"];
  var settings = require('./public/settings.json');

  for(var i in switchNode) {
    // console.log(switchNode[i]);
    if(settings[switchNode[i]["id"]] != undefined) {
      if(switchNode[i]["x"] != null && switchNode[i]["y"] != null) {
        settings[switchNode[i]["id"]]["x"] = parseFloat(switchNode[i]["x"]);
        settings[switchNode[i]["id"]]["y"] = parseFloat(switchNode[i]["y"]);
      }
    }
    else {
      settings[switchNode[i]["id"]] = {};
      if(switchNode[i]["x"] != null && switchNode[i]["y"] != null) {
        settings[switchNode[i]["id"]]["x"] = parseFloat(switchNode[i]["x"]);
        settings[switchNode[i]["id"]]["y"] = parseFloat(switchNode[i]["y"]);
      }
    }
  }

  var settingJSON = JSON.stringify(settings);
  fs.writeFile('./packetMonitor/Visualization/public/settings.json', settingJSON, 'utf8', function(err) {
    // console.log(err);
    res.json({'status': 200, 'msg': 'success'});
  });
});

app.listen(3000, function () {
  console.log('OpenFlow Monitor running on port 3000!');
});
