define(['d3', 'marionette'], function(d3) {
  return Backbone.Marionette.ItemView.extend({
    className: 'row realtime-graph-view',
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    onRender: function() {

        // Compose metrics
        var aggregate = this.collection.aggregate({ toSeconds: 5, stepSeconds: 1 });
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

        if (!this.svg) {
          this.$el.append('<div class="col-md-10 col-md-offset-1"></div>');
          var parent = this.$('div')[0];

          // Create graph
          var width = this.$el.width() - 10;
          var height = this.$el.height() - 10;
          var halfHeight = height/2;

          this.yScale = d3.scale.linear()
            .domain([0, 1])
            .range([0, halfHeight]);
      
          this.xScale = d3.scale.linear()
            .domain([0, ratioAggregate.length])
            .range([0, width]);

          this.line = d3.svg.area()
            .interpolate( 'basis' )
            .y1(_.bind(function(d, i) {
              return this.yScale(d.positive);
            }, this))
            .y0(halfHeight)
            .x(_.bind(function(d, i) {
              return this.xScale(i);
            }, this));

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

          //this.svg.append("g")
            //.attr("class", "x axis")
            //.attr("transform", "translate(0," + this.yScale(0) + ")")
            //.call(d3.svg.axis().scale(this.xScale).orient("bottom"));

          //this.svg.append("g")
            //.attr("class", "y axis")
            //.call(d3.svg.axis().scale(this.yScale).orient("right"));
        }

        var path = this.svg.selectAll('path.line')
          .data([ratioAggregate]);

        path.enter()
          .append("g")
          .attr("clip-path", "url(#clip)")
          .append("path")
          .attr('class', 'line')
          .style('fill', '#5cb85c')

        path
          .transition()
          .attr("d", this.line)
          //.ease("linear")
          //.attr("transform", "translate(" + this.xScale(-1) + ")");
        
    },
    render: function() {
      setInterval(_.bind(this.triggerMethod, this, "render"), 1000);
      return this.el;
    }
  });
});

