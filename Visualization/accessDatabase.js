var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/test';
var topology = [];
var flowMods = [];

var getFlowMods = function(db, callback) {
	var cursor = db.collection('flow_mods').find();
	cursor.each(function(err, doc) {
		assert.equal(err, null);
		if (doc != null) {
			// console.dir(doc);	// Print data in each field
			flowMods.push(doc);
		} else {
			callback();
		}
	});
}

var getTopo = function(db, callback) {
	var cursor = db.collection('topology').find();
	// console.log(cursor);
	cursor.each(function(err, doc) {
		assert.equal(err, null);
		if (doc != null) {
			// console.dir(doc);
			topology.push(doc);
		} else {
			callback();
		}
	});
}

MongoClient.connect(url, function(err, db) {
	assert.equal(null, err);

	getFlowMods(db, function() {
		db.close();
		console.log(flowMods);
	});
});

// console.log("=============================================")

MongoClient.connect(url, function(err, db) {
	assert.equal(null, err);

	getTopo(db, function() {
		db.close();
		console.log(topology);
	});
});

