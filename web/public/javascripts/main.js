var host = location.origin.replace(/^http/, 'ws')
var app = angular.module('main', []);

app.factory('getWebSocket', function($q) {
	var def = $q.defer();
	var ws = new WebSocket(host);
	ws.onopen = function(event) {
		def.resolve(ws);
	}
	return def.promise;
});

app.controller('MainController', function($scope, $rootScope) {
	$rootScope.$on('newSentimentClassified', function(event, data) {
		$scope.$apply(function() {
			$scope.result = data.result;
		});
		
	});

	$scope.processPhrase = function() {
		var p = $scope.phrase;
		if (p) {
			$rootScope.$emit('trackNewTerm', p);
		}
	}

	$scope.clearSentiment = function() {
		$scope.result = null;
	}
})

app.controller('RootController', function($rootScope, getWebSocket) {

	getWebSocket.then(function(ws) {
		ws.onmessage = function(msg) {
			var data = JSON.parse(msg.data)
		  console.log(data);
			//$rootScope.$emit('newSentimentClassified', data);
		}
		$rootScope.$on('trackNewTerm', function(event, text) {
			ws.send(JSON.stringify({ trackNewTerm: text }));
		});
		//ws.send(JSON.stringify({ trackNewTerm: 'ipad' }));
	});

})
