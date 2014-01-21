var data = {
  user: {

  },
  prediction: {
    probs: {
      positive: 30.0,
      negative: 70.0
    },
    result: 'negative'
  },
  text: ''
}

define(['tweetFrameView', 'termCollection'], function(TweetFrameView, TermCollection) {
  describe('TweetFrameView', function() {
    var vent = new Backbone.Wreqr.EventAggregator();

    it('should call pop on collection numChilds times on initialize', function() {
      var coll = new TermCollection;
      spyOn(coll, 'pop').andReturn(new Backbone.Model);

      var tfv = new TweetFrameView({ vent: vent, queue: coll, numChilds: 5 });
      tfv.render();
      expect(coll.pop.callCount).toBe(5);
    });

    it('should make a new child every time item is added until is full', function() {
      var numChilds = 5;
      var coll = new TermCollection;
      spyOn(coll, 'pop').andReturn(null);

      // Create new TFV, collection is empty so will not pull anything
      spyOn(TweetFrameView.prototype, 'addChildToDOM');
      var tfv = new TweetFrameView({ vent: vent, queue: coll, numChilds: numChilds });
      tfv.render();
      expect(tfv.addChildToDOM.callCount).toBe(0);

      // TermCollection has a new elements. Data is broadcasted
      coll.pop.andCallThrough();
      _.range(0, numChilds).forEach(function() {
        coll.add(data);
      });
      expect(tfv.addChildToDOM.callCount).toBe(5);
    });

    it('should swap if collection full but view expired', function() {
      var numChilds = 5;
      var coll = new TermCollection;
      var tfv = new TweetFrameView({ vent: vent, queue: coll, numChilds: numChilds });

      // views are full and 2 are expired
      tfv.views = { length : 5 };
      var expiredViews = _.range(0, 2).map(function(){
        return { swap: jasmine.createSpy() };
      })
      spyOn(tfv, 'getExpiredViews').andReturn(expiredViews);

      // 2 New elements are added
      _.range(0, 2).forEach(function() {
        coll.add(data, { silent: true });
      });
      coll.trigger('add');

      // both views have been swapped
      expiredViews.forEach(function(v) {
        expect(v.swap.callCount).toBe(1);
      });

    });

    it('should try to swap if collection is expired', function() {
      var numChilds = 5;
      var coll = new TermCollection;
      var tfv = new TweetFrameView({ vent: vent, queue: coll, numChilds: numChilds });

      // Child expires
      var child = tfv.addNewChild();
      spyOn(tfv, 'getExpiredViews').andReturn([ child ]);
      spyOn(child, 'swap');
    });

  });
});


