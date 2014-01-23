define(['text!templates/navigationView.html', 'marionette'], function(tpl) {
    return Backbone.Marionette.ItemView.extend({
      tagName: 'nav',
      className: 'navbar navbar-inverse',
      template: _.template(tpl),
      events: {
        'submit form': 'triggerChange'
      },
      ui: {
        "query": "input[type='text']",
        "streamerStatus": ".streamer-status",
        "realtimeOnTemplate": "#realtime-on-tpl",
        "realtimeOffTemplate": "#realtime-off-tpl"
      },
      initialize: function() {
        this.streamerReady = false;
        this.listenTo(app.vent, 'streamer:ready', function() {
          this.streamerReady = true;
          this.render();
        });
      },
      onRender: function() {
        if(this.streamerReady) {
          this.ui.streamerStatus.html(this.ui.realtimeOnTemplate.html());
        } else {
          this.ui.streamerStatus.html(this.ui.realtimeOffTemplate.html());
        }
        this.ui.streamerStatus.removeClass(this.streamerReady ? 'off' : 'on');
        this.ui.streamerStatus.addClass(this.streamerReady ? 'on' : 'off');
      },
      triggerChange: function(e) {
        e.preventDefault();
        var res = this.ui.query.val();
        if (res) {
          app.router.navigate("/track/" + res, {trigger: true});
        }
      }
    });
});

