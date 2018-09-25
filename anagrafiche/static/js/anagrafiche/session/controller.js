WMS.module('Session', function(Session, WMS, Backbone, Marionette, $, _) {
  var session = WMS.request('get:session');

  Session.Controller = Marionette.Controller.extend({
    showLoginView: function() {
      var view = new Session.Views.LoginView({
        model: session
      });
      WMS.getRegion('loginRegion').show(view);
    }

  , login: function() {
      var view = new Session.Views.LoginForm();
      view.on('login', function(args) {
        view.ui.login.button("loading");
        var username = args.model.get('username')
          , password = args.model.get('password');
        session.login({
          username: username
        , password: password
        }, {
          success: function(userData) {
            var fromPath = session.get('fromPath');
            session.unset('fromPath');
            WMS.navigate(fromPath !== undefined ? fromPath : '#home');
          }
        , error: function(error) {
            WMS.showError(error);
            view.ui.login.button("reset");
          }
        })          
      });
      WMS.getRegion('mainRegion').show(view);
    }

  , logout: function() {
      session.logout({
        success: function() {
          WMS.navigate('#home');
        }
      });
    }

  , unauthorized: function() {
      var view = new Session.Views.Unauthorized();
      WMS.getRegion('mainRegion').show(view);
    }
  });
});