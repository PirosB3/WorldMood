var crypto = require('crypto');
var events = require("events");
var util = require("util");

var Twit = require('twit');
var _ = require("underscore");

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
		formattedTweet.user.profile_image_url = formattedTweet.user.profile_image_url.replace('_normal', '_bigger')
		this.currentCache[textHash] = true;
		this.emit('tweet', formattedTweet);
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

exports.TwitterStreamer = TwitterStreamer;
