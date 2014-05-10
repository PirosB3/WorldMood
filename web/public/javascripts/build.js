{
    name: "../init",
    out: "bundle.js",
    baseUrl: './src/',
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
        xdate: '../libs/xdate.dev',
        jquery: '../libs/jquery',
        backbone: '../libs/backbone',
        underscore: '../libs/underscore',
        marionette: '../libs/backbone.marionette',
        d3: '../libs/d3',
	text: '../libs/text'
    },
    findNestedDependencies: true
}
