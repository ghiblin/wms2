WMS.module("Pages", function(Pages, WMS, Backbone, Marionette, $, _) {
  Pages.Router = Marionette.AppRouter.extend({
    appRoutes: {
      'home' : 'showHome'
    },    
  });
  
  var API = {
    showHome: function() {
      Pages.Show.Controller.showHome();
      WMS.execute('set:active:header', 'owner');
    }
  };
  
  WMS.on('pages:home', function() {
    WMS.navigate('home');
    API.showHome();
  });
  
  WMS.on('before:start', function() {
    new Pages.Router({
      controller: API
    });
  });
});