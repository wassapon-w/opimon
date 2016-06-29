var express = require('express');
var app = express();

var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';
var counter = 0;

app.get('/flowmods', function (req, res) {
  getFlowMods();

  function getFlowMods() {
  	var flowMods = [];

  	MongoClient.connect(url, function(err, db) {
  		assert.equal(null, err);

  		var cursor = db.collection('flow_mods').find();
  		cursor.each(function(err, doc) {
  			assert.equal(err, null);
  			if (doc != null) {
  				// console.dir(doc);
  				flowMods.push(doc);
  			}
  			else {
          counter++;
  				console.log(counter + " : Request FlowMod from webpage");
  				db.close();
          res.json(flowMods);
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

          for(var i = 0; i < topologyDatabase.length; i++) {
            var isNew = true;
            for(var j = 0; j < topology["node"].length; j++) {
              if(topology["node"][j]["switch_id"] == topologyDatabase[i]["switch_src"]) {
                for(var k = 0; k < topology["node"][j]["connect_to"].length; k++) {
                  if(topology["node"][j]["connect_to"][k] == topologyDatabase[i]["switch_dst"]) {
                    isNew = false;
                    break;
                  }
                }
                if(isNew) {
                  topology["node"][j]["connect_to"].push(topologyDatabase[i]["switch_dst"]);

                  topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] - 1;
                  topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] - 1;
                  topologyDatabase[i]["value"] = 1;
                  topology["link"].push(topologyDatabase[i]);
                  isNew = false;
                  break;
                }
              }
            }
            if(isNew) {
              var node = {};
              node["switch_id"] = topologyDatabase[i]["switch_src"];
              node["connect_to"] = [];
              node["connect_to"].push(topologyDatabase[i]["switch_dst"]);
              topology["node"].push(node);

              topologyDatabase[i]["source"] = topologyDatabase[i]["switch_src"] - 1;
              topologyDatabase[i]["target"] = topologyDatabase[i]["switch_dst"] - 1;
              topologyDatabase[i]["value"] = 1;
              topology["link"].push(topologyDatabase[i]);
            }
          }

          res.json(topology);
  			}
  		});
  	});
  }
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
