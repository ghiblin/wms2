WMS.module('Suppliers.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views, WMS.Suppliers.Forms)
    , Behaviors = WMS.Common.Behaviors;

  Views.Panel = Views.FilterPanel.extend({
    eventPrefix: 'suppliers'
  , canAdd: function() {
      return WMS.Models.Supplier.canCreate();
    }
  });

  Views.Edit = Views.EntityForm.extend({
    title         : "Aggiorna Fornitore",
    saveButtonText: "Aggiorna"
  });

  Views.New = Views.EntityForm.extend({
    title         : "Nuovo Fornitore",
    saveButtonText: "Crea Fornitore"
  });

  var Supplier = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.TableRowBehavior,
      fields        : [
        "code",
        "name",
        "vatNumber",
        "taxCode"
      ]
    }, {
      behaviorClass : Behaviors.SelectableBehavior
    }, {
      behaviorClass : Behaviors.EditableBehavior,
      insertPoint   : ".actions",
      button        : false,
      FormView      : Views.Edit
    }, {
      behaviorClass : Behaviors.DestroyableBehavior,
      insertPoint   : ".actions",
      button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });
      
  Views.Suppliers = Views.TableView.extend({
    childView           : Supplier,
    childViewEventPrefix: 'supplier',
    headers       : [
      { width: "10%", name: "code" },
      { width: "40%", name: "name" },
      { width: "20%", name: "vatNumber" },
      { width: "20%", name: "taxCode" },
      { widht: "65px" }
    ],
    modelClass    : WMS.Models.Supplier,
    behaviors           : [{
      behaviorClass : Behaviors.FilterBehavior
    }]
  });
});