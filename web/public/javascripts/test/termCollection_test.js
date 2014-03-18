
var _generateData = function(pos, neg) {
    return {
        prediction: {
            result: 'negative',
            probs: {
                positive: pos,
                negative: neg
            }
        },
    }
}

define(['termCollection'], function(TermCollection) {
    describe('TermCollection', function() {
        it('should be able to return accuracy', function() {
            var coll = new TermCollection([
                _generateData(.30, .70),
                _generateData(.50, .50),
                _generateData(.87, .13),
                _generateData(.25, .75)
            ]);
            expect(coll.pop().get('prediction')).toEqual(_generateData(.87, .13).prediction);
            expect(coll.pop().get('prediction')).toEqual(_generateData(.25, .75).prediction);
        });
    });
});

