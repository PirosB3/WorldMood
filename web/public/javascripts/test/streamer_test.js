define(['streamer'], function(Streamer) {
    var vent = new Backbone.Wreqr.EventAggregator();
    describe('Streamer', function() {
        it('should be able to brodcast ready', function() {
            var ws = {};
            var def = $.Deferred();
            spyOn(Streamer.prototype, '_getWebSocket').andReturn(def.promise());

            var s = new Streamer({ vent: vent });

            var spy = jasmine.createSpy();
            vent.on('streamer:ready', spy);

            expect(spy).not.toHaveBeenCalled();
            def.resolve(ws);
            expect(spy).toHaveBeenCalled();
        });

        it('should be able to receive a message', function() {
            // Mock getWebSocket and return custom object
            var ws = {};
            var def = $.Deferred();
            def.resolve(ws);
            spyOn(Streamer.prototype, '_getWebSocket').andReturn(def.promise());

            // Create new streamer
            var s = new Streamer({ vent: vent });

            // Set a spy on newTermClassified
            var spy = jasmine.createSpy();
            vent.on('streamer:newMessage:newTermClassified', spy);

            ws.onmessage({ data : JSON.stringify({ message: 'newTermClassified', hello: 'world' }) });
            expect(spy).toHaveBeenCalled();
            expect(spy.argsForCall[0][0].hello).toEqual('world');
        });

        xit('should be able to send a message', function() {
            var ws = { send: jasmine.createSpy() };
            var def = $.Deferred();
            def.resolve(ws);
            spyOn(Streamer.prototype, '_getWebSocket').andReturn(def.promise());

            // Create new streamer
            var s = new Streamer({ vent: vent });

            // Set a spy on newTermClassified
            vent.trigger('streamer:sendMessage', { message: 'changeTopic', value: 'pink floyd' });
            expect(ws.send).toHaveBeenCalled();
        });
    });
});
