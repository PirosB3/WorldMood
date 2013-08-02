var Twit = require('twit'),
		redis = require('redis');

ARGS = {
	positive: {
		filter: ':)',
		key: 'positive'
	},
	negative: {
		filter: ':(',
		key: 'negative'
	}
}

var target = ARGS[process.argv[2]];
if (!target) {
	console.log("Not a valid sentiment");
	process.exit(1);
}

var twit = new Twit({
    consumer_key:         'tIPFMyYowULdaxhXAUdw'
  , consumer_secret:      '8KmoOxQfJAHCoEZ9lTdxvbTaFepat3ipH1vlUofQY'
  , access_token:         '79504968-C9PQG5G1BFCESQI4axGi6XC4AlfiddiImg2HQbhqt'
  , access_token_secret:  'm2XjR91L1iFiGfh4W8DjbgV9DkyITxHxtKUSaZM6Sw'
});
client = redis.createClient();
client.on("error", function (err) {
		console.log("Error " + err);
});

var stream = twit.stream('statuses/filter', { track: target.filter, language: 'en' })
stream.on('tweet', function (tweet) {
	var text = tweet['text'];

	client.sadd('sentiment-analysis:' + target.key, text)
	console.log(text);
})
