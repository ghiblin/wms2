WMS.module('Employees.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views, WMS.Employees.Forms)
    , Behaviors = WMS.Common.Behaviors;

  Views.Panel = Views.FilterPanel.extend({
    eventPrefix: 'employees'
  , canAdd: function() {
      return WMS.Models.Employee.canCreate();
    }

  , fields: [
      { name:'active', type:'checkbox', label:'Attivi' }
    ]

  , onRender: function() {
      this.$('input[name=active]')
        .prop("checked", this.options.active)
        .bootstrapSwitch()
        .on('switchChange.bootstrapSwitch', _.bind(function(evt, state) {
          this.trigger('employees:active', state);
        }, this));
    }
  });

  var Employee = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.SelectableBehavior
    }, {
      behaviorClass: Behaviors.TableRowBehavior
    , fields: ['serialNumber', 'firstName', 'lastName']
    }, {
      behaviorClass : Behaviors.EditableBehavior
    , insertPoint   : ".actions"
    , button        : false
    , FormView      : Views.Edit
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass: Behaviors.UpdateBehavior
    }]
    
  , onRender:function() {
      if (!this.model.isActive()) {
        this.$el.addClass('danger');
      }
    }
  });
  
  
  Views.Employees = Views.TableView.extend({
    childView: Employee
  , childViewEventPrefix: 'employee'    
  , headers       : [
      { width: "30%", name:'serialNumber' }
    , { width: "30%", name:'firstName' }
    , { width: "30%", name:'lastName' }
    , { width: "10%" }
    ]
  , modelClass    : WMS.Models.Employee
  , behaviors: [{
      behaviorClass : Behaviors.FilterBehavior
    , filter        : function(employee) {
        return this.options.active ? employee.isActive() : true;
      }
    }]
  
  , initialize: function(options) {
      this.collection.sort({ sort_key:'serialNumber' });
    }

  , setActive: function(active) {
      this.options.active = active;
      this.render();
    }
  });
});