var data = {
    prediction: {
        positive: 30.0,
        negative: 70.0
    },
    result: 'negative'
}

define(['term'], function(Term) {
    describe('Term', function() {
        it('should be able to return accuracy', function() {
            var t = new Term(data);
            expect(t.getAccuracy()).toEqual(40);
        });
        it('should be able to return max accuracy', function() {
            var t = new Term(data);
            expect(t.getWinningProb()).toEqual(70);
        });
    });
});
