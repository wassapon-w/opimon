var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';

// Get flow mod messages from database
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
			}
		});
	});
}

// Get topology from database
function getTopology() {
	var topology = [];

	MongoClient.connect(url, function(err, db) {
		assert.equal(null, err);

		var cursor = db.collection('topology').find();
		cursor.each(function(err, doc) {
			assert.equal(err, null);
			if (doc != null) {
				// console.dir(doc);
				topology.push(doc);
			}
			else {
				// console.log(topology);
				db.close();
			}
		});
	});
}

getTopology();
getFlowMods();
