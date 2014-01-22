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

        it('should start an expire timer, if set', function() {
            jasmine.Clock.useMock();
            timerCallback = jasmine.createSpy('timerCallback');

            // New tweet view expires
            var tv = new TweetView({ doesExpire: true });
            tv.on('hasExpired', timerCallback);

            // New ticker has been started
            tv.startTicking(1000);
            expect(timerCallback).not.toHaveBeenCalled();

            jasmine.Clock.tick(1001);
            expect(timerCallback).toHaveBeenCalled();
        });

        it('should delete existing timer on swap', function() {
            jasmine.Clock.useMock();
            timerCallback = jasmine.createSpy('timerCallback');

            // New tweet view expires
            var tv = new TweetView({ doesExpire: true });
            tv.on('hasExpired', timerCallback);

            // One overrides the other
            tv.startTicking(1000);
            tv.startTicking(2000);

            jasmine.Clock.tick(1001);
            expect(timerCallback).not.toHaveBeenCalled();

            jasmine.Clock.tick(1001);
            expect(timerCallback).toHaveBeenCalled();
        });

        it('should set timer on swap, if enabled', function() {
            jasmine.Clock.useMock();
            timerCallback = jasmine.createSpy('timerCallback');

            // New tweet view expires
            var tv = new TweetView({ doesExpire: true });
            tv.on('hasExpired', timerCallback);

            // Create new tweet that expires in 3 seconds
            var t = getTerm();
            spyOn(t, 'getAccuracy').andReturn(30);

            tv.swap(t);
            expect(timerCallback).not.toHaveBeenCalled();

            jasmine.Clock.tick(3001);
            expect(timerCallback).toHaveBeenCalled();
        });

        it("should startTicking also on initialize", function() {
            jasmine.Clock.useMock();
            timerCallback = jasmine.createSpy('timerCallback');

            var t = getTerm();
            spyOn(t, 'getAccuracy').andReturn(30);

            var tv = new TweetView({ doesExpire: true, model: t });
            tv.on('hasExpired', timerCallback);

            jasmine.Clock.tick(3001);
            expect(timerCallback).toHaveBeenCalled();
        });
    });
});

