
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

var addByRange = function(c, n) {
  _.range(0, n).forEach(function(i) {
    c.add(_generateData(i, i));
  });
};

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

        it('should always contain a sub-collection of the last N', function() {
            var coll = new TermCollection([], { nToKeep: 20 });
            expect(coll.memory).toBeTruthy();

            addByRange(coll, 40);
            expect(coll.memory.length).toEqual(20);
            expect(coll.memory.pop().attributes.prediction.probs.positive).toEqual(39);
            expect(coll.memory.shift().attributes.prediction.probs.positive).toEqual(20);
        });

        it('should first trigger events on memory, then broadcast', function() {
            var coll = new TermCollection([], { nToKeep: 20 });

            var aSpy = jasmine.createSpy();
            coll.on('add', aSpy);
            coll.memory.on('add', aSpy);

            coll.add(_generateData(.30, .70))

            // First memory should be called, then trigger "change" to the open
            expect(aSpy.callCount).toEqual(2);
            expect(aSpy.calls[0].object).toBe(coll.memory);
            expect(aSpy.calls[1].object).toBe(coll);
        });
    });
});

