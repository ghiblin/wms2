WMS.module("Sheets.List", function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views, WMS.Sheets.Forms)
    , Behaviors = WMS.Common.Behaviors;

  List.Views.Layout = Views.MasterDetailsLayout.extend({
    title     : 'Consuntivi'
  , showFilter: true
  });

  var FilterModel = Backbone.Model.extend({
    defaults: {
      from: Date.today().addMonths(-1)
    , to  : Date.today()
    }
  });
  
  List.Views.Filter = Views.FilterView.extend({
    attributes: {},
    buttons:[
      { name: "search", label: "Cerca", icon: "filter" },
      { name: "print", label: "Stampa", icon: "print", type: "link" }
    ],
    initialize: function(options) {
      this.model = new FilterModel(_.pick(options, _.keys(FilterModel.prototype.defaults)));
      this.listenTo(this, "searc", this._setPrintURL, this);
    },

    onAttach: function() {
      this._setPrintURL();
    },

    _setPrintURL: function() {
      var $print = this.$el.find("[name=print]");
      var href = "/anagrafiche/stampa/consuntivi/?" +
        "data_inizio=" + this.options.from.toString("yyyy-MM-dd") + 
        "&data_fine=" + this.options.to.toString("yyyy-MM-dd");
      $print.attr("href", href);
    }
  });

  var Employee = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.TableRowBehavior
    , fields: [ 
        'firstName'
      , 'lastName'
      , { attr:'hours', className:'text-right', format:"money" }
      ]
    }, {
      behaviorClass: Behaviors.SelectableBehavior
    }]
  });
  
  Views.Employees = WMS.Common.Views.TableView.extend({
    childView: Employee
  , childViewEventPrefix: 'employee:hours'
  , modelClass    : WMS.Models.EmployeeHours
  , headers: [
      { width: '40%', name:'firstName' }
    , { width: '40%', name:'lastName' }
    , { width: '10%', name:'hours', className:'text-center' }
    , { width: '10%' }
    ]
  
  , initialize: function(options) {
      this.collection.sort({ sort_key:'name' });
    }
  });

  Views.EmployeeDetails = WMS.Common.Views.DetailsView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.DetailsBehavior
    , modelClass    : WMS.Models.EmployeeHours
    , fields        : [
        { name: "firstName" }
      , { name: "lastName", cols: 5 }
      , { type:'actions', cols:1, className:'actions text-right' }
      ]
    }, {
      behaviorClass : WMS.Common.Behaviors.AddRowBehavior
    , insertPoint   : ".actions"
    , eventName     : "sheet:new"
    , disableMethod : "canAddSheet"
    }]
  });

  var Sheet = WMS.Common.Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.TableRowBehavior
    , fields: [
        { attr:'date', format:'date' }
      , 'commissionId'
      , 'workTypeId'
      , { attr:'hours', className:'text-right', format:"money" }
      , 'note'
      ]
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
      behaviorClass : Behaviors.UpdateBehavior
    }]
    
  });
  
  Views.Sheets = WMS.Common.Views.TableView.extend({
    childView: Sheet
  , childViewEventPrefix: 'sheet'
  , modelClass    : WMS.Models.Sheet
  , headers: [
      { width:'10%', name: "date" }
    , { width:'30%', name: "commissionId" }
    , { width:'25%', name: "workTypeId" }
    , { width: '5%', name: "hours" }
    , { width:'25%', name: "note" }
    , { width: '5%' }
    ]
  , behaviors: [{
      behaviorClass : WMS.Common.Behaviors.ColumnTotalBehavior
    , totals: [,,,{attr:"hours", format:"money", className:"text-right"},,]
    }]

  , initialize: function(options) {
      this.collection.sort({ sort_key:'date' });
    }
  });
});