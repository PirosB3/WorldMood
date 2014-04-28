
define(['streamer', 'termCollection', 'tweetFrameView', 'pieView', 'navigationView', 'realtimeGraphView'], function(Streamer, TermCollection, TweetFrameView, PieView, NavigationView, RealtimeGraphView) {

  window.app = new Backbone.Marionette.Application();

  var AppLayout = Backbone.Marionette.Layout.extend({
      template: "#app-layout-placeholder",
      regions: {
        tweetFrameViewPlaceholder: ".tweetFrameView-placeholder",
        tweetDetailsPlaceholder: ".tweetDetails-placeholder",
        realtimeGraphViewPlaceholder: ".tweetRealtimeGraph-placeholder"
      }
  });

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
      app.container.show(new AppLayout);

      app.vent.off('streamer:newMessage:newTermClassified');

      app.queue = new TermCollection([], { nToKeep: 100 });
      app.container.currentView.tweetFrameViewPlaceholder.show(new TweetFrameView({
        queue: app.queue,
        vent: app.vent,
        numChilds: 3
      }));
      app.container.currentView.tweetDetailsPlaceholder.show(new PieView({
        queue: app.queue,
        vent: app.vent
      }));
      app.container.currentView.realtimeGraphViewPlaceholder.show(new RealtimeGraphView({
        collection: app.queue,
        vent: app.vent
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
    container: ".container"
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
