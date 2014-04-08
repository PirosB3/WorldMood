/*global require*/
'use strict';

require.config({
    baseUrl: 'javascripts/src',
    shim: {
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: [
                'underscore',
                'jquery'
            ],
            exports: 'Backbone'
        },
        marionette: {
            deps: [
                'backbone'
            ],
            exports: 'Backbone'
        },
        xdate: {
            exports: 'XDate'
        },
        bootstrap: {
            deps: ['jquery'],
            exports: 'jquery'
        }
    },
    paths: {
        xdate: '/javascripts/libs/xdate.dev',
        jquery: '/javascripts/libs/jquery',
        backbone: '/javascripts/libs/backbone',
        underscore: '/javascripts/libs/underscore',
        marionette: '/javascripts/libs/backbone.marionette',
        d3: '/javascripts/libs/d3',
	text: '/javascripts/libs/text'
    }
});

require(['marionette'], function (Backbone) {
    require(['main'], function (App) {
      App.start();
    });
});
