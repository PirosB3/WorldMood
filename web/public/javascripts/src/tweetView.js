define(['marionette'], function() {
    return Backbone.Marionette.ItemView.extend({
        template: "#tweetViewTemplate",
        COLORS: {
            'positive': _.template('rgba(217, 83, 79, <%= opacity %>)'),
            'negative': _.template('rgba(92, 184, 92, <%= opacity %>)')
        },
        getOpacityFromAccuracy: function(n) {
            return n * 0.01;
        },
        onRender: function() {
            this.$('img').attr('src', this.model.get('user').profile_image_url);
            this._setColorAndOpacity();
        },
        _setColorAndOpacity: function() {
            var colorTemplate = this.COLORS[this.model.get('prediction').result];
            this.$el.css('background', colorTemplate({
                opacity: this.getOpacityFromAccuracy(this.model.getAccuracy())
            }));
        }
    });
});
