
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

var _generateDataWithTimestamp = function(t, tid) {
    return {
        tid: tid,
        timestamp: t.setMilliseconds(0),
        prediction: {
            result: 'negative',
            probs: {
                positive: 0.7,
                negative: 0.3
            }
        },
    }
}

var addByRange = function(c, n) {
  _.range(0, n).forEach(function(i) {
    c.add(_generateData(i, i));
  });
};

define(['termCollection', 'xdate'], function(TermCollection, XDate) {
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

        it('should be able to aggregate by time', function() {
            var range = TermCollection.prototype._getSecondRange({
                toSeconds: 10, stepSeconds: 2
            });
            expect(range.length).toBe(5);

            var start, stop;
            var r0 = range[0];
            start = r0.start;
            stop = r0.stop;
            expect(start.diffSeconds(stop)).toBe(2);

            var r1 = range[1];
            start = r1.start;
            stop = r1.stop;
            expect(start.diffSeconds(stop)).toBe(2);

            expect(range[4].stop.diffSeconds(range[0].start)).toBe(-10);
        });

        it('should be able to pull out tweets from range', function() {
            var d = new XDate;
            var tweets = _.range(0, 30).map(function(t) {
                return _generateDataWithTimestamp(d.clone().addSeconds(-t), -t);
            });
            var coll = new TermCollection(tweets);

            var res = coll._getTweetsFromRange({
                start: d.clone().addSeconds(-15).setMilliseconds(0),
                stop: d.clone().addSeconds(-10).setMilliseconds(0)
            });
            expect(res.length).toBe(6);
        });

        it('should be able to aggregate', function() {
            var d = new XDate;
            var tweets = _.range(0, 7).map(function(t) {
                return _generateDataWithTimestamp(d.clone().addSeconds(-t), -t);
            });
            var coll = new TermCollection(tweets);
            var res = coll.aggregate({
                toSeconds: 6, stepSeconds: 2
            });
            expect(res.length).toBe(3);
        });
    });
});

