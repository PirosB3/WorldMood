define(['marionette'], function() {
    return Backbone.Marionette.ItemView.extend({
        COLORS: {
            'positive': _.template('rgba(54, 25, 25, <%= opacity %>)'),
            'negative': _.template('rgba(54, 25, 25, <%= opacity %>)')
        },
        getOpacityFromAccuracy: function(n) {
            return n * 0.01;
        },
        _setColorAndOpacity: function() {
            var colorTemplate = this.COLORS[this.model.get('result')];
            this.$el.css('background', colorTemplate({
                opacity: this.getOpacityFromAccuracy(this.model.getAccuracy())
            }));
        }
    });
});
