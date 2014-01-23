
define(['streamer', 'termCollection', 'tweetFrameView', 'navigationView'], function(Streamer, TermCollection, TweetFrameView, NavigationView) {

  window.app = new Backbone.Marionette.Application();

  var AppRouter = Backbone.Marionette.AppRouter.extend({
    initialize: function() {
      app.navigationPlaceholder.show(new NavigationView);

      var host = location.origin.replace(/^http/, 'ws');
      app.streamer = new Streamer({ vent: app.vent, host: host });
    },
    routes: {
      "track/:query": "start",
      '*path': 'defaultRoute'
    },
    defaultRoute: function() {
      this.navigate("/track/Plymouth", {trigger: true});
    },
    start: function(query) {
      app.vent.off('streamer:newMessage:newTermClassified');

      app.queue = new TermCollection;
      app.tweetFrameViewPlaceholder.show(new TweetFrameView({
        queue: app.queue,
        vent: app.vent,
        numChilds: 3
      }));

      app.vent.trigger('streamer:sendMessage', {trackNewTerm: query});
      app.vent.on('streamer:ready', function() {
        app.vent.trigger('streamer:sendMessage', {trackNewTerm: query});
      });

      app.vent.on('streamer:newMessage:newTermClassified', function(data) {
        app.queue.add(data);
      });
    }
  });

  window.app.addRegions({
    navigationPlaceholder: ".navigation-placeholder",
    tweetFrameViewPlaceholder: ".tweetFrameView-placeholder",
    tweetDetailsPlaceholder: ".tweetDetails-placeholder"
  });
  window.app.addInitializer(function(){
    window.app.router = new AppRouter();
    Backbone.history.start();
  });

  return {
    start: function() {
      app.start();
    }
  }
});
