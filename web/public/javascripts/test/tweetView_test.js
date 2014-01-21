define(['tweetView', 'term'], function(TweetView, Term) {
    describe('TweetView', function() {
        
        var getTerm = function() {
            return new Term({
                prediction: {
                    result: 'negative'
                },
                user: {
                    screen_name: "Dan"
                },
                text: "Hello World"
            });
        }

        it('should be able to set the color and opacity level', function() {
            var t = getTerm();
            spyOn(Term.prototype, 'getAccuracy').andReturn(60);
            var tv = new TweetView({ model: t });

            tv.render();
            tv._setColorAndOpacity();

            expect(tv.$('.panel-body').css('background')).toBeTruthy();
        });

        it('should be able to render also when empty', function() {
            var tv = new TweetView;
            tv.render();
            expect($.trim(tv.$('.panel-body').text())).toBe('');
        });

        it('should be able to swap', function() {
            var tv = new TweetView;
            tv.render();
            expect($.trim(tv.$('.panel-body').text())).toBe('');

            var t = getTerm();
            spyOn(Term.prototype, 'getAccuracy').andReturn(60);
            var tv = new TweetView({ model: t });

            tv.swap(t)
            expect($.trim(tv.$('.panel-heading').text())).toBe("Dan");

        });
    });
});

