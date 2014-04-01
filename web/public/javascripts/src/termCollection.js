define(['term'], function(Term) {
    return Backbone.Collection.extend({
        initialize: function(models, options) {
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
        },
        comparator: function(m) {
            return m.getAccuracy();
        }
    });
});
