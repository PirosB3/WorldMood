define(['text!templates/pieView.html', 'd3', 'marionette'], function(tpl, d3) {
  return Backbone.Marionette.View.extend({
    className: 'row',
    template: _.template(tpl),
    COLORS: {
      'negative': 'rgb(217, 83, 79)',
      'positive': 'rgb(92, 184, 92)'
    },
    ui: {
      "piePlaceholder": "#pie-placeholder",
      "barPlaceholder": "#details-placeholder"
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
    getSvgElement: function(width, height) {
      if (!this.svg) {
        var radius = Math.min(width, height) / 2;
        this.pie = d3.layout.pie()
          .sort(null)
          .value(function(c) { return c.value; });

        this.arc = d3.svg.arc()
          .outerRadius(radius-10)
          .innerRadius(0);

        this.svg = d3.select(this.ui.piePlaceholder[0])
          .append('svg')
          .attr("width", width)
          .attr("height", height)
          .append('g')
          .attr('transform', 'translate(' + width/2 + ',' + height/2 + ')');
      }
      return {
        pie: this.pie,
        arc: this.arc,
        svg: this.svg
      };
    },
    capitaliseFirstLetter: function(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    render: function() {
      if (!this.hasRendered) {
        // Render template
        this.$el.html(this.template());
        this.bindUIElements();
        this.hasRendered = true;
      }

      //Get data
      var mappedData = this.getListFromMap();
      var totalData = mappedData.reduce(function(a, b) {
        return a + b.value;
      }, 0);

      var isattachedToDom = jQuery.contains(document, this.el);
      if (isattachedToDom && totalData > 0) {

        var percentageScale = d3.scale.linear()
          .domain([0, totalData])
          .range([0, 100]);

        var piePlaceholder = this.ui.piePlaceholder;
        var d3Els = this.getSvgElement(
            piePlaceholder.width(),
            piePlaceholder.height()
        );

        // Data bind
        var path = d3Els.svg
          .selectAll('.arc')
          .data(d3Els.pie(mappedData), function(e) {
            return e.data.label;
          });

        // On enter
        var g = path.enter()
        .append('g')
          .attr('class', 'arc')
        g.append('path')
        g.append('text')
          .attr("dy", ".35em")
          .style("text-anchor", "middle");

        path
        .select('path')
          .transition()
          .attr("d", function(d) {
            return d3Els.arc(d);
          })
          .style("fill", _.bind(function(d) {
            return this.COLORS[d.data.label];
          }, this))
        path
        .select('text')
          .transition()
          .attr("transform", function(d) { return "translate(" + d3Els.arc.centroid(d) + ")"; })
          .text(_.bind(function(d) {
            return '' + percentageScale(d.data.value).toPrecision(4) + '% ' + this.capitaliseFirstLetter(d.data.label);
          }, this));

        var barPlaceholder = this.ui.barPlaceholder;
        var barScale = d3.scale.linear()
          .domain([0, totalData])
          .range([0, barPlaceholder.width()]);

        var bars = d3.select(barPlaceholder[0])
          .selectAll('.bar')
          .data(mappedData);

        bars.enter()
          .append('div')
          .attr('class', 'bar');

        bars
          .html(_.bind(function(d) {
            // return '<h3>' +  + '</h3>';
            return '<h3>' + d.value + ' ' + this.capitaliseFirstLetter(d.label) + '</h3>';
          }, this))
          .transition()
          .style('width', function(d) {
            return barScale(d.value) + 'px';
          })
          .style('height', '50px')
          .style("background-color", _.bind(function(d) {
            return this.COLORS[d.label];
          }, this));

      }
    }
  });
});
