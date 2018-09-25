WMS.module("Sheets", function(Sheets, WMS, Backbone, Marionette, $, _) {
  Sheets.Router = Marionette.AppRouter.extend({
    appRoutes: {
      "sheets(/employeeId::employeeId)(/from::from)(/to::to)": "listSheets",
    }

  , header:'sheets'

  , permissionsMap: {
      'listSheets':'sheet:list'
    }
  });
  
  var controllers = Sheets.controllers = {}
    , API = {
    listSheets: function(id, from, to) {
      if (controllers.list === undefined) {
        controllers.list = new Sheets.List.Controller();
      }
      id    = _.isNaN(parseInt(id)) ? null : parseInt(id);
      to    = Date.parse(to) || Date.today();
      from  = Date.parse(from) || Date.today().addMonths(-1);
      controllers.list.listSheets(id, from, to);
    }
  };
  
  WMS.on('sheets:list', function(options) {
    options = (options || {});
    _.defaults(options, {
      from:  Date.today().addMonths(-1)
    , to  : Date.today()
    });
    
    var url = ['sheets'];
    if (options.employeeId) {
      url.push('/employeeId:', options.employeeId);
    }
    url.push('/from:', options.from.toString('yyyy-MM-dd'));
    url.push('/to:', options.to.toString('yyyy-MM-dd'));
    if (Backbone.history.getFragment() === url.join("")) {
      API.listSheets(options.employeeId, options.from, options.to);
    } else {
      WMS.navigate(url.join(""));
    }
  });

  WMS.on('before:start', function() {
    new Sheets.Router({
      controller: API
    });
  });
});
