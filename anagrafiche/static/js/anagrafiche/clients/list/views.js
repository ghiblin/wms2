WMS.module('Clients.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views) //, WMS.Clients.Forms)
    , Behaviors = WMS.Common.Behaviors;

  Views.Panel = Views.FilterPanel.extend({
    eventPrefix: "clients"
  , canAdd: function() {
      return WMS.Models.Client.canCreate();
    }
  });

  Views.Edit = Views.EntityForm.extend({
    title: 'Aggiorna Cliente',
    saveButtonText: 'Aggiorna'
  });
  
  Views.New = Views.EntityForm.extend({
    title: 'Nuovo Cliente',
    saveButtonText: 'Crea Cliente',
  });

  var Client = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.TableRowBehavior
    , fields        : [
        "code"
      , "name"
      , "vatNumber"
      , "taxCode"
      ]
    }, {
      behaviorClass : Behaviors.SelectableBehavior
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
    
  Views.Clients = Views.TableView.extend({
    childView           : Client,
    childViewEventPrefix: "client",
    headers       : [
      { width: "10%", name: "Codice" },
      { width: "40%", name: "Nome" },
      { width: "20%", name: "Partita IVA" },
      { width: "20%", name: "Codice Fiscale" },
      { widht: "65px" }
    ],

    modelClass    : WMS.Models.Client,

    behaviors           : [{
      behaviorClass : Behaviors.FilterBehavior
    }]
  });
});