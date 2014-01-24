define(['text!templates/pieView.html', 'd3', 'marionette'], function(tpl, d3) {
  return Backbone.Marionette.View.extend({
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    initialize: function() {
      this.resultsMap = {
        positive: 0,
        negative: 0
      }

      this.listenTo(app.vent, 'streamer:newMessage:newTermClassified', function(data) {
        this.resultsMap[data.prediction.result]++;
        this.render();
      });
    },
    getListFromMap: function() {
      return _.keys(this.resultsMap).map(_.bind(function(k) {
        return { label: k, value: this.resultsMap[k] } 
      }, this));
    },
    render: function() {
      // Get data
      var mappedData = this.getListFromMap();
      var totalData = mappedData.reduce(function(a, b) {
        return a + b.value;
      }, 0);

      // Build scale
      var widthScale = d3.scale.linear()
        .domain([0, totalData])
        .range([0, 750]);

      d3.select(this.el)
        .selectAll('div')
        .style("height", "50px")
        .style("width", function(d) {
          return widthScale(d.value) + '.px';
        })
        .data(this.getListFromMap())
        .enter()
        .append('div')
        .attr('class', 'bar')
        .style("background-color", _.bind(function(d) {
          return this.COLORS[d.label];
        }, this));
    }
  });
});
