WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {  
  var Session = Models.Session = Backbone.Model.extend({
    defaults: {
      authenticated: false,
      userId: ""
    }

  , url: "/api/v1"

  , initialize: function(options) {
      this.user = new Models.User({});
      this.set("authenticated", this.user.get("username") !== "guest");
    }

  , isAuthenticated: function() {
      var value = this.get("authenticated");
      return _.isString(value) ? value === "true" : value;
    }

  , login : function(credentials, callbacks) {
      var that = this;
      var login = $.ajax({
        url         : this.url + "/login"
      , contentType : "application/json"
      , dataType    : "json"
      , data        : JSON.stringify(credentials)
      , type        : "POST"
      }).done(function(userData) {
        userData = that.user.parse(userData);
        that.user.set(_.pick(userData, _.keys(that.user.defaults)));
        that.set({
          authenticated : true
        , username      : that.user.get("username")
        });
        if (callbacks && "success" in callbacks) callbacks.success(that.user);
      })
      .fail(function(error) {
        console.log("login.error", arguments);
        if (callbacks && "error" in callbacks) callbacks.error(error.responseJSON.message);
      });
    },   
    
    logout : function(callback) {
      var that = this;
      $.ajax({
        url : this.url + "/logout/",
        type : "POST"
      }).done(function(response) {
        //Clear all session data
        that.user.clear();
        that.clear();

        // Clear Models cache
        delete WMS.Models.cache;
        WMS.Models.cache = {};

        //Set the new csrf token to csrf vaiable and
        //call initialize to update the $.ajaxSetup 
        // with new csrf
        that.initialize();
        if (callback && "success" in callback) callback.success();
      }).fail(function(error) {
        if (callback && "error" in callback) callback.error(error);
      });
    }
  });
  
  _.extend(Session, {
    getInstance: function() {
      if (Session._instance === undefined) {
        Session._instance = new Session();
      }
      return Session._instance;
    }
  });
  
  WMS.reqres.setHandler("get:session", function() {
    return Session.getInstance();
  });
});