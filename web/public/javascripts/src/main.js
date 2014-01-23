
define(['streamer', 'termCollection', 'tweetFrameView'], function(Streamer, TermCollection, TweetFrameView) {

  window.app = new Backbone.Marionette.Application();

  var AppRouter = Backbone.Marionette.AppRouter.extend({
    routes: {
      "track/:query": "start"
    },
    start: function(query) {
      app.queue = new TermCollection;

      var host = location.origin.replace(/^http/, 'ws');
      app.streamer = new Streamer({ vent: app.vent, host: host });

      app.tweetFrameViewPlaceholder.show(new TweetFrameView({
        queue: app.queue,
        vent: app.vent,
        numChilds: 3
      }));

      app.vent.on('streamer:ready', function() {
        app.vent.trigger('streamer:sendMessage', {
          trackNewTerm: query
        });
      });

      app.vent.on('streamer:newMessage:newTermClassified', function(data) {
        app.queue.add(data);
      });
    }
  });

  window.app.addRegions({
    tweetFrameViewPlaceholder: ".tweetFrameView-placeholder",
    tweetDetailsPlaceholder: ".tweetDetails-placeholder"
  });
  window.app.addInitializer(function(){
    new AppRouter();
    Backbone.history.start();
  });

  return {
    start: function() {
      app.start();
    }
  }
});
