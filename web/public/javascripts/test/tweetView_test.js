define(['tweetView', 'term'], function(TweetView, Term) {
    describe('TweetView', function() {
        it('should be able get % for accuracy', function() {
            var res = TweetView.prototype.getOpacityFromAccuracy(60);
            expect(res).toEqual(0.6);
        });
        
        it('should be able to set the color and opacity level', function() {
            var t = new Term;
            t.attributes.prediction = {
                result: 'negative'
            }
            spyOn(Term.prototype, 'getAccuracy').andReturn(60);

            var tv = new TweetView({ model: t });
            tv._setColorAndOpacity();

            expect(tv.$el.css('background')).toEqual('rgba(92, 184, 92, 0.6)');
        });
    });
});

