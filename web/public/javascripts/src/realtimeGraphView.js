define(['d3', 'marionette'], function(d3) {
  return Backbone.Marionette.ItemView.extend({
    className: 'row realtime-graph-view',
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    onRender: function() {
        var aggregate = this.collection.aggregate({ toSeconds: 35, stepSeconds: 5 });
        var ratioAggregate = aggregate.map(function(a) {
            var groups = _.groupBy(a, function(e) {
                return e.get('prediction').result;
            });
            groups = _.extend({ positive: 0, negative: 0}, groups);
            if (a.length > 0) {
                _.keys(groups).forEach(function(k) {
                    groups[k] = groups[k].length / a.length
                });
            }
            return groups;
        });
        console.log(_.pluck(ratioAggregate, 'positive'));
    },
    render: function() {
      setInterval(_.bind(this.triggerMethod, this, "render"), 1000);
      return this.el;
    }
  });
});

