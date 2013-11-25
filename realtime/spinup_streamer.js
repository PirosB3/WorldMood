var TwitterStreamer = require('./twitter_streamer').TwitterStreamer;
var zmq = require('zmq');

KEYS = {
		consumer_key:        'tIPFMyYowULdaxhXAUdw'
	, consumer_secret:     '8KmoOxQfJAHCoEZ9lTdxvbTaFepat3ipH1vlUofQY'
	, access_token:        '79504968-C9PQG5G1BFCESQI4axGi6XC4AlfiddiImg2HQbhqt'
	, access_token_secret: 'm2XjR91L1iFiGfh4W8DjbgV9DkyITxHxtKUSaZM6Sw'
}

function main() {
	var sock = zmq.socket('req');
	sock.bindSync('tcp://127.0.0.1:9999');


	var streamer = new TwitterStreamer(KEYS);
	streamer.setTrack('camels');
	streamer.on('tweet', function(t) {

		text = t['text'];
		if (text) {
			console.log(text);
			sock.send(JSON.stringify({
				text: text
			}));
		}

	});
}

main();
