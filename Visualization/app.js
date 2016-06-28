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
          for(var i = 0; i < topologyDatabase.length; i++) {
              if(topology[topologyDatabase[i]["switch_src"]] == undefined) {
                topology[topologyDatabase[i]["switch_src"]] = {};
                topology[topologyDatabase[i]["switch_src"]][topologyDatabase[i]["switch_dst"]] = [];
                // topology[topologyDatabase[i]["switch_src"]]["switch_src"].push(topologyDatabase[i]["switch_src"]);
              }
              else {
                // topology[topologyDatabase[i]["switch_src"]]["switch_src"].push(topologyDatabase[i]["switch_src"]);
                topology[topologyDatabase[i]["switch_src"]][topologyDatabase[i]["switch_dst"]] = [];
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
