var express = require('express');
var app = express();

var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';

app.get('/', function (req, res) {
  // res.send('Hello World!');

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
  				console.log("Test");
  				flowMods.push(doc);
  			}
  			else {
  				// console.log(flowMods);
  				db.close();
          res.send(flowMods);
  			}
  		});
  	});
  }
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
