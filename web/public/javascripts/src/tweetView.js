define(['text!templates/tweetView.html', 'marionette'], function(tpl) {
    return Backbone.Marionette.ItemView.extend({
	className: 'tweet-view panel panel-default',
        template: _.template(tpl),
        COLORS: {
            'negative': _.template('rgba(217, 83, 79, <%= opacity %>)'),
            'positive': _.template('rgba(92, 184, 92, <%= opacity %>)')
        },
	serializeData: function(){
	    var attrs = Backbone.Marionette.ItemView.prototype.serializeData.call(this);
	    attrs.trimmedAccuracy = this.model.getAccuracy().toString().substr(0, 5);
	    return attrs;
	},
        onRender: function() {
            this.$('img').attr('src', this.model.get('user').profile_image_url);
            this._setColorAndOpacity();
        },
        _setColorAndOpacity: function() {
            var colorTemplate = this.COLORS[this.model.get('prediction').result];
            this.$('.panel-body').css('background', colorTemplate({
                opacity: this.model.getAccuracy()
            }));
        }
    });
});
