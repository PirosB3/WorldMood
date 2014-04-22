define(['d3', 'marionette'], function(d3) {
  return Backbone.Marionette.ItemView.extend({
    className: 'row realtime-graph-view',
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    initialize: function(args) {
      this.vent = args.vent;
      this.listenTo(this.vent, 'streamer:ready', function() {
          console.log("SET COLLECTION");
          this.collection = window.app.queue;
      });
    },
    getData: function() {
      // Compose metrics
      var aggregate = this.collection.aggregate({ toSeconds: 10, stepSeconds: 1 });
      var ratioAggregate = aggregate.map(function(a) {
          var groups = _.groupBy(a, function(e) {
              return e.get('prediction').result;
          });
          groups = _.extend({ positive: 0, negative: 0}, groups);
          if (a.length > 0) {
              _.keys(groups).forEach(function(k) {
                  groups[k] = groups[k].length / a.length
                  if (_.isNaN(groups[k])) {
                      groups[k] = 0;
                  }
              });
          }
          return groups;
      });

      var positiveAggregates = _.pluck(ratioAggregate, 'positive');
      positiveAggregates._type = 'positive';
      var negativeAggregates = _.pluck(ratioAggregate, 'negative');
      negativeAggregates._type = 'negative'
      return [positiveAggregates, negativeAggregates];
    },
    getAreas: function(data) {
      var halfHeight = this.height/2;

      var yScale = d3.scale.linear()
        .domain([0, 1])
        .range([0, halfHeight]);
      
      var xScale = d3.scale.linear()
        .domain([0, data[0].length])
        .range([0, this.width]);

      return {
        'positive': d3.svg.area()
          .interpolate('basis')
          .x(_.bind(function(d, i) {
            return xScale(i);
          }, this))
          .y1(_.bind(function(d, i) {
            return halfHeight - yScale(d);
          }, this))
          .y0(halfHeight),
        'negative': d3.svg.area()
          .interpolate('basis')
          .x(_.bind(function(d, i) {
            return xScale(i);
          }, this))
          .y1(_.bind(function(d, i) {
            return halfHeight - yScale(d);
          }, this))
          .y0(halfHeight)
      };
    },
    onRender: function() {

        if (!this.svg) {
          this.$el.append('<div class="col-md-10 col-md-offset-1"></div>');
          var parent = this.$('div')[0];

          // Create graph
          this.width = this.$el.width() - 10;
          this.height = this.$el.height() - 100;

          this.svg = d3.select(parent)
            .append('p')
            .append('svg')
            .attr("width", this.width)
            .attr("height", this.height)
            .append('g');

          this.svg.append("defs").append("clipPath")
            .attr("id", "clip")
          .append("rect")
            .attr("width", this.width)
            .attr("height", this.height);
        }

        var data = this.getData();
        var areas = this.getAreas(data);

        var path = this.svg.selectAll('path.line')
          .data(data);

        path.enter()
          .append("g")
          .attr("clip-path", "url(#clip)")
          .append("path")
          .attr("transform", _.bind(function(a, b) {
              var translateY = a._type == 'negative' ? this.height/2 : 0;
              return "translate(0 " + translateY + ")";
          }, this))
          .attr('class', function(a, b) {
              return 'line ' + a._type;
          })

        path
          .transition()
          .attr("d", _.bind(function(a, b) {
              return areas[a._type](a);
          }, this));
        
    },
    render: function() {
      setInterval(_.bind(this.triggerMethod, this, "render"), 1000);
      return this.el;
    }
  });
});
