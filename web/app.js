
/**
 * Module dependencies.
 */

var http = require('http');
var path = require('path');

var express = require('express');
var zmq = require('zmq');
var WebSocketServer = require('ws').Server;

var app = express();

app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// Set up ZMQ
var sock = zmq.socket('req');
sock.bindSync('tcp://127.0.0.1:9999');
console.log('ZMQ server listening on port 9999');
sock.on('message', function(msg) {
	try {
		var data = JSON.parse(msg.toString());
		wss.clients.forEach(function(ws) {
			ws.send(msg.toString());
		});
	} catch(e) {
		console.log(e);
	}
});

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

wss.on('connection', function(ws) {
	ws.on('message', function(msg) {
		obj = JSON.parse(msg);
		if (obj.classifyText) {
			sock.send(JSON.stringify({ text: obj.classifyText }));
		}
	});
});

server.listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
