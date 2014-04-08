
/**
 * Module dependencies.
 */

var http = require('http');
var path = require('path');

var express = require('express');
var zmq = require('zmq');
var WebSocketServer = require('ws').Server;

var app = express();

var TwitterStreamer = require(__dirname + "/libs/streamer.js").TwitterStreamer;
KEYS = {
          consumer_key: process.env["TWITTER_CONSUMER_KEY"]
	, consumer_secret: process.env["TWITTER_CONSUMER_SECRET"]
	, access_token: process.env["TWITTER_ACCESS_TOKEN"]
	, access_token_secret: process.env["TWITTER_ACCESS_TOKEN_SECRET"]
};

app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// Set Realtime components
var sock = zmq.socket('req');
var streamer = new TwitterStreamer(KEYS);

sock.bindSync('tcp://127.0.0.1:9999');
console.log('ZMQ server listening on port 9999');

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

app.get('/', function(req, res) {
  res.render('index', { title: 'Express' });
});

var server = http.createServer(app);
var wsPort = process.env.PORT || 8080;
var wss = new WebSocketServer({server: server});
console.log('WebSockets server listening on port ' + wsPort);

//  WEBSOCKETS
wss.on('connection', function(ws) {
    ws.on('message', function(msg) {
	obj = JSON.parse(msg);
	console.log(obj);

	// Classify a raw phrase
	if (obj.classifyText) {
	    sock.send(JSON.stringify({ text: obj.classifyText }));

	    // Start tracking a new term
	} else if(obj.trackNewTerm) {
	    streamer.setTrack(obj.trackNewTerm);
	}
    });
});

// ZEROMQ
sock.on('message', function(msg) {
    try {
	var data = JSON.parse(msg.toString());
	data['message'] = 'newTermClassified';
        data['timestamp'] = Date.now()

	// Emit to all websockets the new data
	wss.clients.forEach(function(ws) {
	    ws.send(JSON.stringify(data));
	});

    } catch(e) {
	console.log(e);
    }
});

// TWITTER STREAMER
streamer.on('tweet', function(t) {
    text = t['text'];
    if (text) {
	console.log("Sending new term..");
	sock.send(JSON.stringify({
	    text: text,
	    user: t['user']
	}));
    }
});

server.listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
