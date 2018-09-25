WMS.module('Employees.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = _.extend({}, WMS.Common.Views, List.Views);

  List.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      //{ request: 'get:employee:list', name: 'employees' },
      { request: 'get:employee:all', name: 'employees' }
    ]

  , regions: [{
      name: "titleRegion"
    , View: Views.Title
    , options: {
        title: "Dipendenti"
      }
    }, { 
      name: 'panelRegion'
    , viewName: '_panel'
    , View: List.Views.Panel
    , options: {
        criterion : "@criterion"
      , active    : "@active"
      }
    , events: {
        'employees:new': 'newEmployee'
      , 'employees:filter': 'filterEmployee'
      , 'employees:active': 'activeEmployee'
      }
    }, {
      name: 'listRegion'
    , viewName: '_employees'
    , View: List.Views.Employees
    , options: {
        criterion : "@criterion"
      , active    : "@active"
      , collection: "@employees"
      }
    , events: {
        'employee:edit': 'editEmployee'
      , 'employee:delete': 'deleteEmployee'
      , 'employee:selected': 'selectEmployee'
      }
    }]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "employee:created", function(employee) {
        self.options.employees.add(employee);
      });

      this.listenTo(WMS.vent, "employee:updated", function(employee) {
        var model = self.options.employees.find({ id: employee.get("id") });
        if (model) {
          model.set(employee.attributes);
        }
      })
    }

  , listEmployees: function(criterion) {
      //this.options = _.omit((this.options || {}), 'employees');
      //this.filterList(criterion);
      this.options.criterion = criterion;
      _.defaults(this.options, {active:true});

      var self = this;
      this.start().then(function() {
        if (self._layout && !self._layout.isDestroyed) {
          self.setupRegions(self._layout);
        } else {
          self._layout = new Views.FilterLayout();
          
          self._layout.on('show', function() {
            self.setupRegions(self._layout);
          });
          
          WMS.mainRegion.show(self._layout);
        }
      });
    }

  , filterEmployee: function(criterion) {
      WMS.trigger("employees:filter", criterion);
    }

  , newEmployee: function() {
      var klass = WMS.Models.Employee;
      if (klass.canCreate()) {
        var employee = new klass()
          , view = new WMS.Employees.Forms.New({ model: employee });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , editEmployee: function(childView, args) {
      var employee = args.model;
      if (employee.canUpdate()) {
        var view = new WMS.Employees.Forms.Edit({ model: employee });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , activeEmployee: function(state) {
      this.options.active = state;
      this._employees.setActive(state);
    }

  , deleteEmployee: function(childView, args) {
      var employee = args.model;
      if (employee.canDestroy()) {
        if (confirm("Eliminare " + employee + "?")) {
          employee.destroy();
        }
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , selectEmployee: function(childView) {
      var employee = childView.model;
      if (employee.canRead()) {
        WMS.trigger("employees:show", employee.get("id"));
      }
    }
  });
});