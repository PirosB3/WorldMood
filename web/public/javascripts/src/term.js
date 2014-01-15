define(['marionette'], function() {
    return Backbone.Model.extend({
        getAccuracy: function() {
            var res = _.reduce(_.values(this.attributes.prediction), function(total, p) {
                return (total == null) ? p : total-= p;
            }, null);
            return Math.abs(res);
        },
        getWinningProb: function() {
            var attributes = this.attributes;
            return attributes.prediction[attributes.result];
        }
    });
});
