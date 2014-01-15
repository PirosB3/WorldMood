define(['marionette'], function() {
    return Backbone.Model.extend({
        constructor: function(args) {
            this.vent = args.vent;
            this._getWebSocket(args.host).then(_.bind(function(ws) {
                this.vent.trigger('streamer:ready');
                ws.onmessage = _.bind(this.onMessageReceived, this);
            }, this));
        },
        onMessageReceived: function(msg) {
            var data = JSON.parse(msg)
            this.vent.trigger('streamer:newMessage:' + data.message, data);
        },
        _getWebSocket: function(host) {

        }
    });
});

