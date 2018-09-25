WMS.module('Session', function(Session, WMS, Backbone, Marionette, $, _) {
  Session.Views = {};
  
  Session.Views.LoginView = Marionette.ItemView.extend({
    tagName: 'li',
    template: _.template([
      '<a href="#">',
        '[<span name="username"></span>] <span name="action"></action>',
      '</a>'
      ].join('')),
    templateHelpers: function() {
      return {
        authenticated: this.model.get('authenticated'),
        username: this.model.user.get('username')
      }
    },
    modelEvents: {
      'change:authenticated':'render'
    },
    onRender: function() {
      this.$('a').attr('href', this.model.isAuthenticated() ? '#logout' : '#login');
      this.$('span[name=username]').html(this.model.user.get('username'));
      this.$('span[name=action]').html(this.model.isAuthenticated() ? 'Log Out' : 'Log In');
    }
  });
  
  var LoginModel = Backbone.Model.extend({
    defaults: {
      username:'',
      password:''
    }
  });

  Session.Views.Unauthorized = Marionette.ItemView.extend({
    template: _.template('Accesso non consentito'),
    className: 'alert alert-danger'
  });
  
  Session.Views.LoginForm = Marionette.ItemView.extend({
    template: _.template(
      '<div class="col-sm-8 col-sm-offset-2">' +
        '<form id="login-form" class="form-horizontal well">' +
        '</form>' +
      '</div>')
  , className: "row"
  , behaviors: [{
      behaviorClass: WMS.Common.Behaviors.FormBehavior
    , insertPoint: "form"
    , labels: "login"
    , modelClass: LoginModel
    , buttons: [{name: "login", icon: "user", label: "Login", block: false, offset:4, large:8}]
    }]
  , initialize: function(options) {
      this.model = this.model || new LoginModel();
    }
  , ui: {
      login: ".js-login"
    }
  , triggers: {
      'click @ui.login': 'login'
    }
  });
});