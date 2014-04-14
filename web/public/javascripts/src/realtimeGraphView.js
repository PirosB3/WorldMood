define(['d3', 'marionette'], function(d3) {
  return Backbone.Marionette.ItemView.extend({
    className: 'row realtime-graph-view',
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    onRender: function() {

        // Compose metrics
        var aggregate = this.collection.aggregate({ toSeconds: 15, stepSeconds: 3 });
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

        if (!this.svg) {
          this.$el.append('<div class="col-md-10 col-md-offset-1"></div>');
          var parent = this.$('div')[0];

          // Create graph
          var width = this.$el.width() - 10;
          var height = this.$el.height() - 100;
          var halfHeight = height/2;

          this.yScale = d3.scale.linear()
            .domain([0, 1])
            .range([0, halfHeight]);
      
          this.xScale = d3.scale.linear()
            .domain([0, ratioAggregate.length])
            .range([0, width]);

          this.areas = {
            'positive': d3.svg.area()
              .interpolate('basis')
              .x(_.bind(function(d, i) {
                return this.xScale(i);
              }, this))
              //.y1(_.bind(function(d, i) {
                //return halfHeight - this.yScale(d);
              //}, this))
              //.y0(0),
              .y1(_.bind(function(d, i) {
                return this.yScale(d);
              }, this))
              .y0(halfHeight),
            'negative': d3.svg.area()
              .interpolate('basis')
              .x(_.bind(function(d, i) {
                return this.xScale(i);
              }, this))
              .y1(_.bind(function(d, i) {
                return this.yScale(d);
              }, this))
              .y0(halfHeight)
          };

          this.svg = d3.select(parent)
            .append('p')
            .append('svg')
            .attr("width", width)
            .attr("height", height)
            .append('g');

          this.svg.append("defs").append("clipPath")
            .attr("id", "clip")
          .append("rect")
            .attr("width", width)
            .attr("height", height);
        }

        var path = this.svg.selectAll('path.line')
          .data([positiveAggregates, negativeAggregates], function(d) {
              return d._type;
          });

        path.enter()
          .append("g")
          .attr("clip-path", "url(#clip)")
          .append("path")
          .attr("transform", function(a, b) {
              var translateY = a._type == 'positive' ? halfHeight : 0;
              return "translate(0 " + translateY + ")";
          })
          .attr('class', function(a, b) {
              return 'line ' + a._type;
          })

        path
          .transition()
          .attr("d", _.bind(function(a, b) {
              console.log(a._type, a);
              return this.areas[a._type](a);
          }, this));
        
    },
    render: function() {
      setInterval(_.bind(this.triggerMethod, this, "render"), 3000);
      return this.el;
    }
  });
});
