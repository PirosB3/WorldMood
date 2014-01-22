define(['text!templates/tweetView.html', 'marionette'], function(tpl) {
    return Backbone.Marionette.ItemView.extend({
	className: 'tweet-view panel panel-default',
        template: _.template(tpl),
        initialize: function() {
          if (this.model && this.options.doesExpire) {
            this.startTicking(this.model.getAccuracy() * 100);
          }
        },
        COLORS: {
            'negative': _.template('rgba(217, 83, 79, <%= opacity %>)'),
            'positive': _.template('rgba(92, 184, 92, <%= opacity %>)')
        },
        startTicking: function(t) {
          if (this._currentTick) {
            clearInterval(this._currentTick);
          }
          this._currentTick = setTimeout(_.bind(function() {
            this.trigger('hasExpired');
          }, this), t);
        },
	serializeData: function(){
	    var attrs = {};
	    if (this.model) {
		attrs = Backbone.Marionette.ItemView.prototype.serializeData.call(this);
		attrs.trimmedAccuracy = this.model.getAccuracy().toString().substr(0, 5);
	    }
	    attrs.hasModel = !!this.model;
	    return attrs;
	},
        hasExpired: function() {
          return false;
        },
        onRender: function() {
	    if (this.model) {
		this.$('img').attr('src', this.model.get('user').profile_image_url);
            	this._setColorAndOpacity();
	    } else {
		this.$('.panel-body').css("background-color", "transparent");
	    }
        },
        _setColorAndOpacity: function() {
            var colorTemplate = this.COLORS[this.model.get('prediction').result];
            this.$('.panel-body').css('background', colorTemplate({
                opacity: this.model.getAccuracy()
            }));
        },
	swap: function(m) {
          this.model = m;
          if (this.options.doesExpire) {
            this.startTicking(this.model.getAccuracy() * 100);
          }
          this.render();
	}
    });
});
