var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';
var topology = [];
var flowMods = [];

// Get flow mod messages from database
function getFlowMods() {
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
				// console.log(flowMods);
				db.close();
			}
		});
	});
}

// Get topology from database
function getTopology() {
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
				console.log(topology);
				db.close();
			}
		});
	});
}

getFlowMods();
getTopology();
