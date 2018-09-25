WMS.module('Commissions', function(Commissions, WMS, Backbone, Marionette, $, _) {
  Commissions.Router = Marionette.AppRouter.extend({
    appRoutes: {
      "commissions(/from::from)(/to::to)": "listCommissions",
      "commissions/:id": "showCommission"
    },

    header:'commissions',

    permissionsMap: {
      'listCommissions':'commission:list',
      'showCommission':'commission:retrieve'
    }
  });
  
  var controllers = Commissions.controllers = {}
    , API = {
    listCommissions: function(from, to) {
      if (controllers.list === undefined) {
        controllers.list = new Commissions.List.Controller();
      }
      to = to || Date.today();
      // i mesi sono nel range [0 - 11]
      from = from || new Date(to.getFullYear(), 0, 1);
      controllers.list.listCommissions(from, to);
    }

  , showCommission: function(id) {
      if (controllers.show === undefined) {
        controllers.show = new Commissions.Show.Controller();
      }
      id = _.isNaN(parseInt(id)) ? null : parseInt(id);
      controllers.show.showCommission(id);
    }
  };
  
  WMS.on('commissions:list', function() {
    WMS.navigate('commissions');
  });
  
  WMS.on('commissions:filter', function(criterion) {
    if (criterion) {
      WMS.navigate('commissions/filter/criterion:' + criterion);
    } else {
      WMS.navigate('commissions');
    }
  });
  
  WMS.on('commissions:show', function(id) {
    WMS.navigate('commissions/' + id);
  });
  
  WMS.on('before:start', function() {
    new Commissions.Router({
      controller: API
    });
  });
});