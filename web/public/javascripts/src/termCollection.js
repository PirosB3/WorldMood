define(['term'], function(Term) {
    return Backbone.Collection.extend({
        model: Term,
        comparator: function(m) {
            return m.getAccuracy();
        }
    });
});
