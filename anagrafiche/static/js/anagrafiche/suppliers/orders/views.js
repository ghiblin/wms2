WMS.module("Suppliers.Orders", function(Orders, WMS, Backbone, Marionette, $, _) {
  var Views = Orders.Views = _.extend({}, WMS.Common.Views)
    , Behaviors = WMS.Common.Behaviors;
  
  var FilterModel = Backbone.Model.extend({
    defaults: {
      code    : "",
      supplierId: null,
      from    : Date.today().addMonths(-1),
      to      : Date.today()
    },

    getSuppliers: WMS.getSuppliers
  });
  
  Views.Layout = Views.MasterDetailsLayout.extend({
    title: "Ordini Fornitori",
    showFilter: true
  });
  
  Views.FilterView = Views.FilterView.extend({
    initialize: function(options) {
      this.model = new FilterModel(options);
    }
  });

  var OrderForm = Views.ModalFormView.extend({
    notes: "N.B.: Al cambiare del fornitore, i campi Destinazione, Pagamento e Persona di Riferimento possono subire modifiche automatiche",
    behaviors: [{
      behaviorClass : Behaviors.FormBehavior,
      insertPoint   : "div.modal-body",
      skipFields    : ["total", "supplierCode"],
      readonly      : ["code", "date"],
      modelClass: WMS.Models.SupplierOrder
    }, {
      behaviorClass : Behaviors.CascadingDefaultBehavior,
      bindings      : {supplierId:["paymentTypeId", "applyTo"]}
    }, {
      behaviorClass : Behaviors.CascadingDropdownBehavior,
      bindings      : {supplierId:["destinationId"]}
    }, {
      behaviorClass : Behaviors.ModalBehavior
    }]
  });

  Views.NewOrder = OrderForm.extend({
    title         : "Nuovo Ordine",
    saveButtonText: "Crea Ordine"
  });

  Views.EditOrder = OrderForm.extend({
    title: "Modifica Ordine",
    saveButtonText: "Aggiorna"
  });

  Views.Panel = Marionette.ItemView.extend({
    template: _.template(""),
    behaviors: [{
      behaviorClass: Behaviors.TabPanelBehavior,
      tabs: ["orders", "estimates"],
      labels: "tabs"
    }, {
      behaviorClass: Behaviors.AddModelBehavior,
      insertPoint: ".pre.actions-bar",
      FormView: Views.NewOrder,
      modelClass: WMS.Models.SupplierOrder
    }, {
      behaviorClass: Behaviors.DropdownBehavior,
      insertPoint: ".post.actions-bar",
      eventPrefix: "supplier:order"
    }]
  });

  var Order = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.SelectableBehavior
    }, {
      behaviorClass: Behaviors.TableRowBehavior,
      fields: [
        "code",
        { attr:"date", format:"date" },
        "supplierCode",
        "supplierId",
        "subject"
      ]
    }, {
      behaviorClass : Behaviors.EditableBehavior
    , insertPoint   : ".actions"
    , button        : false
    , FormView      : Views.EditOrder
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  Views.Orders = Views.TableView.extend({
    childView: Order
  , childViewEventPrefix: "order"
  , modelClass: WMS.Models.SupplierOrder
  , headers: [
      { width: "10%", name:"code" }
    , { width: "10%", name:"date" }
    , { width: "10%", name:"supplierCode" }
    , { width: "25%", name:"supplierId" }
    , { width: "25%", name:"subject" }
    , { width: "10%" }
    ]
  , behaviors: [{
      behaviorClass: Behaviors.ResizableBehavior
    }]
  });
  
  var NoEstimateRow = Views.NoListItem.extend({
    offset  : 0
  , colspan : 5
  , message : "Nessuna riga associata al preventivo."
  });
  

  var EstimateRow = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.SelectableBehavior
    , className     : 'info'
    , condition     : { accepted: false }
    , failureMsg    : "Riga del preventivo già approvata."
    }, {
      behaviorClass : Behaviors.TableRowBehavior
    , enableEdit    : false
    , enableDestroy : false
    , fields: ["articleCode", "description", "unitType", 
        {attr:"price", format:"price", className:"text-right"},
        {attr:"discountPercent", format:"money", className:"text-right"},
        {attr:"quantity", format:"money", className:"text-right"} 
      ]
    }],
  });

  var EstimateRows = Marionette.CompositeView.extend({
    template: "#drilldown-table-template",
    templateHelpers: {
      cols: 6,
      headers: [
        "Cod. Art.", "Descrizione", "U.M.", "Prezzo", "Sconto %", "Q.ta", ""
      ]
    },
    tagName             : "tr",
    className           : "drilldown",
    childView           : EstimateRow,
    emptyView           : NoEstimateRow,
    childViewEventPrefix: "estimate:row",
    childViewContainer  : "tbody"
  });
  
  var Estimate = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.TableRowBehavior
    , enableEdit    : false
    , enableDestroy : false
    , fields        : [
        "code"
      , { attr:"supplierId", lookup:"suppliers" }
      , "subject"
      ]
    }, {
      behaviorClass : Behaviors.SelectableBehavior
    , className     : 'info'
    , condition     : { accepted: false }
    , failureMsg    : 'Preventivo già accettato.'
    }, {
      behaviorClass : Behaviors.DrillDownBehavior
    , detailsView   : EstimateRows
    , filter        : {accepted:false}
    }]
  , onRender: function() {
      if (this.model.get('accepted')) {
        this.$el.addClass('success');
      }
    }
  });

  Views.Estimates = Views.TableView.extend({
    childView: Estimate
  , childViewEventPrefix: "estimate"
  , modelClass: WMS.Models.Estimate
  , headers: [
      { width: "14px" }
    , { width: "20%", name: "code" }
    , { width: "35%", name: "supplierId" }
    , { width: "40%", name: "subject" }
    , { width: "5%" }
    ]
  });

  var OrderRowForm = Views.ModalFormView.extend({
    triggers: {
      "click .js-cancel": "cancel",
      "click .js-submit": "save"
    },

    behaviors: [{
      behaviorClass : Behaviors.FormBehavior
    , fieldSelector : "app-field"
    , insertPoint   : "div.modal-body"
    , skipFields    : ["total"]
    , modelClass    : WMS.Models.SupplierOrderRow
    }, {
      behaviorClass: Behaviors.CascadingDefaultBehavior,
      bindings: {articleId:["description", "unitTypeId", "price"]}
    }, {
      behaviorClass: Behaviors.ModalBehavior
    }]
  });

  Views.NewRow = OrderRowForm.extend({
    title: "Nuova riga",
    saveButtonText: "Aggiungi",
  });

  Views.EditRow = OrderRowForm.extend({
    title: "Aggiorna riga",
    saveButtonText: "Aggiorna"
  });

  var Row = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.TableRowBehavior
    , fields: [
        "articleCode"
      , "description"
      , "unitType"
      , { attr:"price", className:"text-right", format:"price"}
      , { attr:"quantity", className:"text-right", format:"money"}
      , { attr:"discountPercent", className:"text-right", format:"money"}
      , { attr:"total", className:"text-right", format:"money"}
      ]
    }, {
      behaviorClass : Behaviors.EditableBehavior
    , insertPoint   : ".actions"
    , button        : false
    , FormView      : Views.EditRow
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  Views.Rows = Views.PanelTableView.extend({
    title: "Righe Ordine",
    childView: Row,
    childViewEventPrefix: "supplier:order:row",
    modelClass    : WMS.Models.SupplierOrderRow,
    headers       : [
      { width: "10%", name: "articleCode" },
      { width: "35%", name: "description" },
      { width: "10%", name: "unitTypeId" },
      { width: "10%", name: "price", className:"text-right" },
      { width: "10%", name: "quantity", className:"text-right" },
      { width: "10%", name: "discountPercent", className:"text-right" },
      { width: "10%", name: "total", className:"text-right" },
      { width: "5%" }
    ],
    behaviors: [{
      behaviorClass : Behaviors.CollapsableBehavior
    }, {
      behaviorClass : Behaviors.ColumnTotalBehavior,
      totals        : [,,,,,,{attr:"total", format:"money", className:"text-right"},,]
    }, {
      behaviorClass : Behaviors.AddBehavior
    }]
  });

  Views.Details = Views.DetailsView.extend({
    behaviors: [{
      behaviorClass : Behaviors.DetailsBehavior,
      modelClass    : WMS.Models.SupplierOrder,
      fields: [
        { name: "code" },
        { name: "date", type: "date", cols:4 },
        { type:"actions", cols:2, className:"text-right actions" },
        { name: "commissionId", cols:12, labelCols:2, fieldCols:10 },
        { name: "subject", cols: 12, labelCols:2, fieldCols: 10 },
        { name: "supplierCode" },
        { name: "supplierId", label: false, fieldCols: 12 },
        { name: "destinationId", cols: 12, labelCols: 2, fieldCols: 10 },
        { name:"paymentTypeId" },
        { name:"vatRateId" },
        { name:"applyTo", cols:12, labelCols:2, fieldCols:10 },
        { name:"note", type: "textarea", cols:12, labelCols:2, fieldCols:10 },
        { name:"discountPercent" },
        { name:"discountValue" },
        { name:"printTotal", cols:6, type:"checkbox"}
      ]
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }, {
      behaviorClass : Behaviors.AddRowBehavior
    , insertPoint   : ".actions"
    }, {
      behaviorClass : Behaviors.PrintableBehavior,
      insertPoint   : ".actions"
    }, {
      behaviorClass : Behaviors.CollapsableBehavior
    }]
  });

  Views.SelectCommission = WMS.Common.Views.ModalFormView.extend({
    initialize: function(options) {
      this.model = new WMS.Models.SupplierOrderCommission(_.pick(options, "supplierId"));
      this.saveHandler = options.saveHandler;
    }

  , title: "Scegli commessa"
  , triggers: {
      "click .js-cancel": "cancel"
    , "click .js-submit": "save"
    }

  , behaviors: function() {
      return [{
        behaviorClass : Behaviors.FormBehavior
      , fieldSelector : "app-field"
      , insertPoint   : "div.modal-body"
      , readonly      : ["supplierId"]
      , modelClass    : WMS.Models.Order
      , saveHandler   : this.options.saveHandler
      }, {
        behaviorClass : Behaviors.ModalBehavior
      }] 
    } 
  })
});