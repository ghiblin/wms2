WMS.module('Session', function(Session, WMS, Backbone, Marionette, $, _) {
  var Router = Marionette.AppRouter.extend({
    appRoutes: {
      'login': 'login',
      'logout': 'logout',
      'unauthorized': 'unauthorized'
    },
    
    before: function() {
      WMS.execute('set:active:header', null);
    }
  });
  
  var controller;

  WMS.on('before:start', function() {
    if (!controller) controller = new Session.Controller();

    new Router({
      controller: controller
    });
  });
  
  WMS.on('start', function() {    
    controller.showLoginView();
  });
  
  WMS.on('unauthorized', function(opts) {
    var session = WMS.request('get:session');
    session.set('fromPath', opts.path);
    if (session.isAuthenticated()) {
      WMS.navigate('unauthorized');
    } else {
      WMS.navigate('login');
    }
  })
});