define(['d3', 'marionette'], function(d3) {
  return Backbone.Marionette.ItemView.extend({
    className: 'row realtime-graph-view',
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    collectionEvents: {
      add: 'memoryUpdatedHandler'
    },
    memoryUpdatedHandler: function() {
      this.drawGraph();
    },
    onRender: function() {
      // Item has rendered, prepare all interpolates
      var width = this.$el.width() - 10;
      var height = this.$el.height() - 10;
      var halfHeight = height/2;

      this.yScale = d3.scale.linear()
        .domain([0, 1])
        .range([0, halfHeight]);

      this.xScale = d3.scale.linear()
        .domain([0, 100])
        .range([0, width]);

      this.line = d3.svg.line()
        .interpolate("basis")
        .x(_.bind(function(d, i) {
          return this.xScale(i);
        }, this))
        .y(_.bind(function(d, i) {
          var scaledValue = this.yScale(d.getAccuracy());
          return scaledValue;
          //if (d.get('prediction').result === 'negative') {
            //scaledValue *= -1;
          //}
          //return halfHeight - scaledValue;
        }, this));

      // Create SVG Element
      this.svg = d3.select(this.el)
        .append('p')
        .append('svg')
        .attr("width", width)
        .attr("height", height)
        .append('g');
    },
    drawGraph: function() {
      var path = this.svg.selectAll('path')
        .data([this.collection.models]);

      path
        .enter()
        .append("path");

      path
        .attr("class", "line")
        .attr("d", _.bind(function(a, b) {
          return this.line(a);
        }, this));
    },
    render: function() {
      _.defer(_.bind(this.triggerMethod, this, "render"));
      return this.el;
    }
  });
});

