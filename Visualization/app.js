var express = require('express');
var path =  require("path");
var app = express();

var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';
var counter = 0;

app.get('/', function(req, res){
    res.setHeader('Content-Type', 'text/html');
    res.sendFile(path.join(__dirname, './public', 'index.html'));
});

app.get('/d3.v4.min.js', function(req, res){
    res.sendFile(path.join(__dirname, './public', 'd3.v4.min.js'));
});

app.get('/visualize.js', function(req, res){
    res.sendFile(path.join(__dirname, './public', 'visualize.js'));
});

app.get('/flowmods', function (req, res) {
  getFlowMods();

  function getFlowMods() {
  	var flowModsDatabase = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('flow_mods').find();
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
              var flow = {};
              flow["switch_id"] = flowModsDatabase[i]["switch"];
              flow["match"] = flowModsDatabase[i]["message"]["match"];
              flow["actions"] = flowModsDatabase[i]["message"]["actions"];
              flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
              flow["timestamp"] = flowModsDatabase[i]["timestamp"];
              flowTable[flowModsDatabase[i]["switch"]].push(flow);
            }
            else {
              flowTable[flowModsDatabase[i]["switch"]] = [];
              switchFlowTable.push(flowModsDatabase[i]["switch"]);

              var flow = {};
              flow["switch_id"] = flowModsDatabase[i]["switch"];
              flow["match"] = flowModsDatabase[i]["message"]["match"];
              flow["actions"] = flowModsDatabase[i]["message"]["actions"];
              flow["hard_timeout"] = flowModsDatabase[i]["message"]["hard_timeout"];
              flow["timestamp"] = flowModsDatabase[i]["timestamp"];
              flowTable[flowModsDatabase[i]["switch"]].push(flow);
            }
          }
          flowTable["switchFlowTable"] = switchFlowTable.sort();

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

  		var cursor = db.collection('topology').find();
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

          var nodeCounter = 0;
          for(var i = 0; i < topologyDatabase.length; i++) {
            var isNew = true;
            for(var j = 0; j < topology["node"].length; j++) {
              if(topology["node"][j]["id"] == topologyDatabase[i]["switch_src"]) {
                for(var k = 0; k < topology["node"][j]["connect_to"].length; k++) {
                  if(topology["node"][j]["connect_to"][k] == topologyDatabase[i]["switch_dst"]) {
                    isNew = false;
                    break;
                  }
                }
                if(isNew) {
                  topology["node"][j]["connect_to"].push(topologyDatabase[i]["switch_dst"]);

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
              node["id"] = topologyDatabase[i]["switch_src"] + '';
              node["group"] = 1;
              node["connect_to"] = [];
              node["connect_to"].push(topologyDatabase[i]["switch_dst"]);
              topology["node"].push(node);

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

app.listen(3000, function () {
  console.log('OpenFlow Monitor running on port 3000!');
});
