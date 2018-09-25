WMS.module("Suppliers.Notes", function(Notes, WMS, Backbone, Marionette, $, _) {
  var Views = Notes.Views = _.extend({}, WMS.Common.Views)
    , Behaviors = WMS.Common.Behaviors;
  
  var FilterModel = Backbone.Model.extend({
    defaults: {
      code    : ""
    , supplierId: null
    , from    : Date.today().addMonths(-1)
    , to      : Date.today()
    }

  , getSuppliers: WMS.getSuppliers
  });
  
  Views.Layout = Views.MasterDetailsLayout.extend({
    title     : "Ordini Fornitori"
  , showFilter: true
  });
    
  Views.FilterView = Views.FilterView.extend({    
    initialize: function(options) {
      this.model = new FilterModel(_.pick(options, _.keys(FilterModel.prototype.defaults)));
    }
  });
  
  var NoteForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : Behaviors.FormBehavior
    , insertPoint   : "div.modal-body"
    , skipFields    : ["supplierCode"]
    , readonly      : ["code", "date"]
    , modelClass: WMS.Models.SupplierNote
    }, {
      behaviorClass : Behaviors.CascadingDefaultBehavior
    , bindings      : {
        supplierId      : ["applyTo"]
      , orderId       : ["destinationId", "vatRateId"]
      }
    }, {
      behaviorClass : Behaviors.CascadingDropdownBehavior
    , bindings      : {
        supplierId      : ["commissionId", "destinationId"]
      , commissionId  : ["orderId"]
      }
    }, {
      behaviorClass : Behaviors.ModalBehavior
    }]
  });

  Notes.Views.NewNote = NoteForm.extend({
    title         : "Nuova Bolla"
  , saveButtonText: "Crea Bolla"
  });

  Notes.Views.EditNote = NoteForm.extend({
    title         : "Modifica Bolla"
  , saveButtonText: "Aggiorna"
  });

  Notes.Views.Panel = Marionette.ItemView.extend({
    template: _.template("")
  , behaviors: [{
      behaviorClass : Behaviors.TabPanelBehavior
    , tabs          : ["notes", "orders"]
    , labels        : "tabs"
    }, {
      behaviorClass : Behaviors.AddModelBehavior
    , insertPoint   : ".pre.actions-bar"
    , FormView      : Views.NewNote
    , modelClass    : WMS.Models.SupplierNote
    }, {
      behaviorClass: Behaviors.DropdownBehavior
    , insertPoint: ".post.actions-bar"
    , eventPrefix: "supplier:note"
    }]
  });

  var Note = WMS.Common.Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.SelectableBehavior
    }, {
      behaviorClass: Behaviors.TableRowBehavior,
      fields: [
        "code"
      , { attr:"date", format:"date" }
      , "supplierCode"
      , "supplierId"
      , "subject"
      ]
    }, {
      behaviorClass : Behaviors.EditableBehavior
    , insertPoint   : ".actions"
    , button        : false
    , FormView      : Views.EditNote
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  Notes.Views.Notes = Views.TableView.extend({
    childView: Note
  , childViewEventPrefix: "note"
  , modelClass    : WMS.Models.SupplierNote
  , headers       : [
      { width: "10%", name:"code" }
    , { width: "10%", name:"date" }
    , { width: "10%", name:"supplierCode" }
    , { width: "25%", name:"supplierId" }
    , { width: "25%", name:"subject" }
    , { width: "10%" }
    ]
  });
  
  var OrderRow = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.SelectableBehavior,
      className     : 'info',
      condition     : { noteIssued: false }, 
      failureMsg    : "Bolla già emessa per questa riga dell'ordine."
    }, {
      behaviorClass : Behaviors.TableRowBehavior
    , enableEdit    : false
    , enableDestroy : false
    , fields: ["articleCode", "description", "unitType", 
        {attr:"quantity", format:"money", className:"text-right"} 
      ]
    }],
    
    onRender: function() {
      if (this.model.get('noteIssued')) {
        this.$el.addClass('success');
      }
    }
  });
  
  var OrderRows = Marionette.CompositeView.extend({
    template: "#drilldown-table-template"
  , templateHelpers: {
      cols: 4,
      headers: [
        "Cod. Art.", "Descrizione", "U.M.", "Q.ta", ""
      ]
    }
  , tagName: "tr"
  , className: "drilldown"
  , childView: OrderRow
  , childViewEventPrefix: "order:row"
  , childViewContainer: "tbody"
  });
  
  var Order = WMS.Common.Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.TableRowBehavior,
      enableEdit    : false,
      enableDestroy : false,
      fields        : [
        "code",
        { attr:"supplierId", lookup:"suppliers" },
        "subject"
      ]
    }, {
      behaviorClass : Behaviors.SelectableBehavior,
      className     : 'info',
      condition     : { noteIssued: false },
      failureMsg    : "Bolla già emessa per questo ordine."
    }, {
      behaviorClass : Behaviors.DrillDownBehavior,
      detailsView   : OrderRows,
      total         : true
    }],
    onRender: function() {
      if (this.model.get('noteIssued')) {
        this.$el.addClass('success');
      }
    }
  });
  
  Views.Orders = WMS.Common.Views.TableView.extend({
    childView: Order
  , childViewEventPrefix: "order"
  , modelClass: WMS.Models.Order
  , headers: [
      { width: "14px" }
    , { width: "20%", name: "code" }
    , { width: "35%", name: "supplierId" }
    , { width: "40%", name: "subject" }
    , { width: "5%" }
    ]
  });

  var NoteRowForm = Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : Behaviors.FormBehavior,
      fieldSelector : "app-field",
      insertPoint   : "div.modal-body",
      modelClass    : WMS.Models.SupplierNoteRow
    }, {
      behaviorClass: Behaviors.CascadingDefaultBehavior,
      bindings: {articleId:["description", "unitTypeId", "price"]}
    }, {
      behaviorClass: Behaviors.ModalBehavior
    }]
  });

  Views.NewRow = NoteRowForm.extend({
    title         : "Nuova riga"
  , saveButtonText: "Aggiungi"
  });

  Views.EditRow = NoteRowForm.extend({
    title         : "Aggiorna riga"
  , saveButtonText: "Aggiorna"
  });
  
  var Row = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.TableRowBehavior
    , fields: [
        "articleCode",
        "description",
        "unitType"
      , { attr:"quantity", className:"text-right", format:"money"}
      ]
    }, {
      behaviorClass : Behaviors.EditableBehavior,
      insertPoint   : ".actions",
      button        : false,
      FormView      : Views.EditRow
    }, {
      behaviorClass : Behaviors.DestroyableBehavior,
      insertPoint   : ".actions",
      button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  Views.Rows = Views.PanelTableView.extend({
    title: "Righe Bolla",
    childView: Row,
    childViewEventPrefix: "supplier:note:row",
    modelClass    : WMS.Models.SupplierNoteRow,
    headers       : [
      { width: "20%", name: "articleCode" },
      { width: "40%", name: "description" },
      { width: "10%", name: "unitTypeId" },
      { width: "20%", name: "quantity", className:"text-right" },
      { width: "10%" }
    ], 
    behaviors: [{
      behaviorClass : Behaviors.CollapsableBehavior
    }, {
      behaviorClass : Behaviors.AddBehavior
    }]
  });

  Views.Details = Views.DetailsView.extend({
    behaviors : [{
      behaviorClass : Behaviors.DetailsBehavior,
      modelClass    : WMS.Models.SupplierNote,
      fields: [
        { name: "date", type: "date" },
        { name: "code", cols:4, labelCols:6, fieldCols:6 },
        { type: "actions", cols:2, className:"text-right actions" },
        { name: "commissionId", cols:12, labelCols: 2, fieldCols: 10 },
        { name: "supplierCode" },
        { name: "supplierId", label: false, fieldCols: 12 },
        { name: "subject", cols:12, labelCols: 2, fieldCols: 10  },
        { name: "destinationId", cols: 12, labelCols: 2, fieldCols: 10 },
        { name: "supplierDate", type: "date" },
        { name: "supplierNote" },
        { name: "applyTo" },
        { name: "causalTransportTypeId" },
        { name: "shippingTypeId" },
        { name: "carrierId" },
        { name: "incotermTypeId" },
        { name: "outwardnessTypeId" },
        { name: "netWeight" },
        { name: "grossWeight" },
        { name: "items" },
        { name: "corrosiveClass" },
        { name: "note", type: "textarea", cols:12, labelCols:2, fieldCols:10 }
      ]
    }, {
      behaviorClass : WMS.Common.Behaviors.UpdateBehavior
    }, {
      behaviorClass : Behaviors.AddRowBehavior
    , insertPoint   : ".actions"
    }, {
      behaviorClass : Behaviors.PrintableBehavior
    , insertPoint   : ".actions"
    }, {
      behaviorClass : Behaviors.CollapsableBehavior
    }]
  });
});