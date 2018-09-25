var nop = function() {};

_.extend(Marionette.AppRouter.prototype, {
  before: function(route, name) {
    var perm = this.authorize(name);
    if (perm !== true) {
      WMS.trigger('unauthorized', {
        path:'#' + Backbone.history.getFragment(), 
        permission:perm
      });
      return false;
    }

    var regexp = this._routeToRegExp(route);
    if (!regexp.test(WMS._previousRoute) && _.isFunction(this.reset)) {
      this.reset(route);
    }
  },

  after: function() {
    WMS.execute('set:active:header', this.header);
  },
  
  route: function(route, name, callback) {
    if (!callback) callback = this[name];

    var wrappedCallback = _.bind( function() {
      var callbackArgs = [ route, name, _.toArray(arguments) ];
      var beforeCallback;
      if ( _.isFunction(this.before) ) {
        beforeCallback = this.before;
      } else if ( typeof this.before[route] !== "undefined" ) {
        beforeCallback = this.before[route];
      } else {
        beforeCallback = nop;
      }

      if ( beforeCallback.apply(this, callbackArgs) === false ) {
        return;
      }
      
      if( callback ) {
        callback.apply( this, arguments );
      }
      
      var afterCallback;
      if ( _.isFunction(this.after) ) {
        afterCallback = this.after;
      } else if ( typeof this.after[route] !== "undefined" ) {
        afterCallback = this.after[route];
      } else {
        afterCallback = nop;
      }

      afterCallback.apply( this, callbackArgs );
    }, this);
    
    return Backbone.Router.prototype.route.call( this, route, name, wrappedCallback );
  },

  authorize: function(path) {
    var paths, match, permkey, perms;

    if (this.permissionsMap === undefined) return true;

    // find an entry for the current path
    paths = _.keys(this.permissionsMap);
    match = _.find(paths, function(p) {
      return path.indexOf(p)===0;            
    });    
    if (!match) return true;

    //check if the read permission is allowed
    permkey = this.permissionsMap[match];
    var can = WMS.request('get:session').user.can(permkey);
    return can ? true : permkey;
  },
});