WMS.module('Employees.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = _.extend({}, WMS.Common.Views, Show.Views);

  Show.Controller = Marionette.Controller.extend({
    regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "@employee.name"
        }
      }, {
        name: "detailsRegion"
      , View: Views.EntityDetails
      , options: {
          model: "@employee"
        }
      }
    ]
  , prefetchOptions: [{
      request: "get:employee", name: "employee", options: ["id"]
    }]
   
  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "employee:updated", function(employee) {
        var model = self.options.employee;
        if (model.get("id") === employee.get("id")) {
          model.set(employee.attributes);
          self._layout.getRegion("titleRegion").currentView.model.set("title", employee.get("name"));
        }
      });
    } 

  , showEmployee: function(id) {  
      this.options.id = id;

      var self = this;
      this.start().then(function() {
        var employee = self.options.employee;
        if (employee) {
          var layout = self._layout = new Views.EntityLayout({ entity:employee });
          layout.on("show", function() {
            self.setupRegions(layout);
          })
        } else {
          self._layout = new Views.Error({ message: "Dipendente non trovato. "});
        }
        WMS.getRegion("mainRegion").show(self._layout);
      });
    }
  });
});