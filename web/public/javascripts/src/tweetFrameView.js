define(['tweetView'], function(TweetView) {
  return Backbone.Marionette.View.extend({
    initialize: function() {
      this.views = [];
      this.listenTo(this.options.queue, 'add', this.newElementAdded, this);
    },
    render: function() {
      var opts = this.options
      var poppedElements = _.range(0, opts['numChilds']).map(function() {
        return opts.queue.pop();
      });
      _.compact(poppedElements).forEach(_.bind(function(m) {
        var el = this.addNewChild();
      }, this));
    },
    addNewChild: function() {
      var tv = new TweetView;
      this.views.push(tv);
      this.addChildToDOM(tv);
      return tv;
    },
    newElementAdded: function() {
      if (this.views.length < this.options.numChilds) {
        var el = this.addNewChild();
        el.swap(this.options.queue.pop());
      } else {
        this.getExpiredViews().forEach(_.bind(function(e) {
          var poppedTerm = this.options.queue.pop();
          if (poppedTerm) {
            e.swap(poppedTerm);
          }
        }, this));
      }
    },
    getExpiredViews: function() {
      return _.filter(this.views, function(v) {
        return v.hasExpired();
      });
    },
    addChildToDOM: function() {
      
    }
  });
});

