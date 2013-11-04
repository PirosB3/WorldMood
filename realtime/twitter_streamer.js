var crypto = require('crypto');
var events = require("events");
var util = require("util");

var Twit = require('twit');
var _ = require("underscore");
var zmq = require('zmq');

KEYS = {
		consumer_key:         'tIPFMyYowULdaxhXAUdw'
	, consumer_secret:      '8KmoOxQfJAHCoEZ9lTdxvbTaFepat3ipH1vlUofQY'
	, access_token:         '79504968-C9PQG5G1BFCESQI4axGi6XC4AlfiddiImg2HQbhqt'
	, access_token_secret:  'm2XjR91L1iFiGfh4W8DjbgV9DkyITxHxtKUSaZM6Sw'
}

var createHash = function(text) {
	var sum = crypto.createHash('md5');
	sum.update(text);
	return sum.digest('hex');
}

function TwitterStreamer(keys) {
	this.currentStream = null;
	this.twit = new Twit(_.pick(keys, 'consumer_key', 'consumer_secret',
		'access_token', 'access_token_secret'));
	events.EventEmitter.call(this);
};

util.inherits(TwitterStreamer, events.EventEmitter);

TwitterStreamer.prototype.buildStream = function(keyword) {
	return this.twit.stream('statuses/filter', { track: keyword,
		language: 'en' });
}

TwitterStreamer.prototype.emitTweet = function(tweet) {
	var text = tweet.text;
	var textHash = createHash(text);
	if (!this.currentCache[textHash]) {
		var formattedTweet = {
			user: _.pick(tweet.user, 'profile_image_url', 'screen_name'),
			text: tweet.text,
			keyword: this.currentKeyword
		};
		this.currentCache[textHash] = true;
		this.emit('tweet', formattedTweet);
	} else {
		console.log("DUPLICATE");
	}
}

TwitterStreamer.prototype.setTrack = function(keyword) {
	if (this.currentStream) {
		this.currentStream.stop();
	}

	this.currentKeyword = keyword;
	this.currentCache = {};

	this.currentStream = this.buildStream(keyword);
	this.currentStream.on('tweet', _.bind(this.emitTweet, this));
}

function main() {
	var streamer = new TwitterStreamer(KEYS);
	streamer.setTrack('iphone');
	streamer.on('tweet', function(t) {
		console.log(t);
	});
}

main();
