define(['text!templates/navigationView.html', 'marionette'], function(tpl) {
    return Backbone.Marionette.ItemView.extend({
      tagName: 'nav',
      className: 'navbar navbar-inverse',
      template: _.template(tpl),
      events: {
        'submit form': 'triggerChange'
      },
      ui: {
        "query": "input[type='text']"
      },
      triggerChange: function(e) {
        e.preventDefault();
        var res = this.ui.query.val();
        if (res) {
          app.router.navigate("/track/" + res, {trigger: true});
        }
      }
    });
});

