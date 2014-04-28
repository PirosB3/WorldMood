define(['term', 'xdate'], function(Term, XDate) {
    var MAX_QUEUE_SIZE = 1000;

    var TermCollection = Backbone.Collection.extend({
        initialize: function(models, options) {
          this.c = 0;
          if (options && options.nToKeep) {
            this.nToKeep = options.nToKeep;
            this.memory = new Backbone.Collection;

            var nToKeep = this.nToKeep;
            this.memory.on('add', function() {
              while(this.length > nToKeep) {
                this.shift();
              }
            });
          }
        },
        _getSecondRange: function(args) {
          var start = new XDate();
          return _.range(0, args.toSeconds, args.stepSeconds).map(function(i) {
            return {
                start: start.clone().addSeconds(-i),
                stop: start.clone().addSeconds(-i+args.stepSeconds)
            };
          }).reverse();
        },
        _secs: function(d) {
            return d.clone().setMilliseconds(0);
        },
        _getTweetsFromRange: function(r) {
          return this.filter(_.bind(function(t) {
            var d = t.get('timestamp');
            return (r.start.getTime() <= d) && (d <= r.stop.getTime());
          }, this));
        },
        aggregate: function(args) {
          var res = this._getSecondRange(args).map(_.bind(function(range) {
            return this._getTweetsFromRange(range);
          }, this));
          return res.slice(0, res.length-1);
        },
        model: Term,
        add: function(models, options) {
          options = options || {};
          var newOptions = _.extend({ silent: true }, options);
          var res = Backbone.Collection.prototype.add.call(this, models, newOptions)

          res = _.isArray(res) ? res : [res];
          this.memory && this.memory.add(res);

          if (!options.silent) {
            var model;
            for (i = 0, l = res.length; i < l; i++) {
              (model = res[i]).trigger('add', model, this, options);
            }
          }

          if (this.length >= TermCollection.GC_TRIGGER_COUNT) {
              var sortedByTimestamp = this.sortBy(function(a) { return a.get('timestamp')});
              sortedByTimestamp.slice(0, TermCollection.GC_TRIGGER_CUTOFF).forEach(_.bind(function(e) {
                  this.remove(e.cid, { silent: true });
              }, this));
          }
        },
        comparator: function(m) {
            return m.getAccuracy();
        }
    });
    TermCollection.GC_TRIGGER_COUNT = 2000;
    TermCollection.GC_TRIGGER_CUTOFF = 1000;

    return TermCollection;

});
