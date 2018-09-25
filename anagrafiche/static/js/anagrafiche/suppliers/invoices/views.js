WMS.module("Suppliers.Invoices", function(Invoices, WMS, Backbone, Marionette, $, _) {
  var Views = Invoices.Views = _.extend({}, WMS.Common.Views)
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
    title: "Fatture Supplieri"
  , showFilter: true
  });
  
  Views.FilterView = Views.FilterView.extend({
    initialize: function(options) {
      this.model = new FilterModel(options);
    }
  });

  var InvoiceForm = Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : Behaviors.FormBehavior
    , insertPoint   : "div.modal-body"
    , skipFields    : ["total", "supplierCode", "pending", "fullPrice", "discounted", "totalVat"]
    , readonly      : ["code", "date"]
    , modelClass    : WMS.Models.SupplierInvoice
    }, {
      behaviorClass : Behaviors.CascadingDefaultBehavior
    , bindings      : {supplierId:["paymentTypeId", "applyTo"]}
    }, {
      behaviorClass : Behaviors.CascadingDropdownBehavior
    , bindings      : {supplierId:["commissionId","destinationId"]}
    }, {
      behaviorClass : Behaviors.ModalBehavior
    }]
  });

  Views.NewInvoice = InvoiceForm.extend({
    title         : "Nuova Fattura"
  , saveButtonText: "Crea Fattura"
  });

  Views.EditInvoice = InvoiceForm.extend({
    title: "Modifica Fattura"
  , saveButtonText: "Aggiorna"
  });

  Views.Panel = Marionette.ItemView.extend({
    template: _.template("")
  , behaviors: [{
      behaviorClass: Behaviors.TabPanelBehavior
    , tabs: ["invoices", "notes", "orders"]
    , labels: "tabs"
    }, {
      behaviorClass: Behaviors.AddModelBehavior
    , insertPoint: ".pre.actions-bar"
    , FormView: Views.NewInvoice
    , modelClass: WMS.Models.SupplierInvoice
    }, {
      behaviorClass: Behaviors.DropdownBehavior
    , insertPoint: ".post.actions-bar"
    , eventPrefix: "supplier:invoice"
    }]
  });

  var Invoice = Views.TableRowView.extend({
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
    , FormView      : Views.EditInvoice
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  Views.Invoices = Views.TableView.extend({
    childView: Invoice,
    childViewEventPrefix: "invoice",
    modelClass: WMS.Models.SupplierInvoice,
    headers: [
      { width: "10%", name:"code" },
      { width: "10%", name:"date" },
      { width: "10%", name:"supplierCode" },
      { width: "25%", name:"supplierId" },
      { width: "25%", name:"subject" },
      { width: "10%" }
    ],
    behaviors: [{
      behaviorClass: Behaviors.ResizableBehavior
    }]
  });
  
  var NoNoteRow = Views.NoListItem.extend({
    offset  : 0,
    colspan : 5,
    message : "Nessuna riga associata alla bolla."
  });
  

  var NoteRow = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.SelectableBehavior, 
      className     : 'info',
      condition     : { invoiceIssued: false },
      failureMsg    : "Fattura già emessa per questa riga della bolla."
    }, {
      behaviorClass : Behaviors.TableRowBehavior, 
      enableEdit    : false, 
      enableDestroy : false, 
      fields: ["articleCode", "description", "unitType", 
        {attr:"price", format:"price", className:"text-right"},
        {attr:"quantity", format:"money", className:"text-right"} 
      ]
    }],

    onRender: function() {
      if (this.model.get('invoiceIssued')) {
        this.$el.addClass('success');
      }
    }
  });

  var NoteRows = Marionette.CompositeView.extend({
    template: "#drilldown-table-template",
    templateHelpers: {
      cols: 5,
      headers: [
        "Cod. Art.", "Descrizione", "U.M.", "Prezzo", "Q.ta", ""
      ]
    },
    tagName             : "tr",
    className           : "drilldown",
    childView           : NoteRow,
    emptyView           : NoNoteRow,
    childViewEventPrefix: "note:row",
    childViewContainer  : "tbody"
  });
  
  var Note = Views.TableRowView.extend({
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
      condition     : { invoiceIssued: false }, 
      failureMsg    : "Bolla già fatturata."
    }, {
      behaviorClass : Behaviors.DrillDownBehavior,
      detailsView   : NoteRows
    }],

    onRender: function() {
      if (this.model.get('invoiceIssued')) {
        this.$el.addClass('success');
      }
    }
  });

  Views.Notes = Views.TableView.extend({
    childView: Note,
    childViewEventPrefix: "note",
    modelClass: WMS.Models.SupplierNote,
    headers: [
      { width: "14px" },
      { width: "20%", name: "code" },
      { width: "35%", name: "supplierId" },
      { width: "40%", name: "subject" },
      { width: "5%" }
    ]
  });

  var NoOrderRow = Views.NoListItem.extend({
    offset  : 0,
    colspan : 5,
    message : "Nessuna riga associata all'ordine."
  });
  

  var OrderRow = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.SelectableBehavior, 
      className     : 'info',
      condition     : { invoiceIssued: false },
      failureMsg    : "Riga ordine già fatturata."
    }, {
      behaviorClass : Behaviors.TableRowBehavior, 
      enableEdit    : false,
      enableDestroy : false,
      fields: ["articleCode", "description", "unitType", 
        {attr:"price", format:"price", className:"text-right"},
        {attr:"quantity", format:"money", className:"text-right"} 
      ]
    }],

    onRender: function() {
      if (this.model.get('invoiceIssued')) {
        this.$el.addClass('success');
      }
    }
  });

  var OrderRows = Marionette.CompositeView.extend({
    template: "#drilldown-table-template"
  , templateHelpers: {
      cols: 5,
      headers: [
        "Cod. Art.", "Descrizione", "U.M.", "Prezzo", "Q.ta", ""
      ]
    },
    tagName             : "tr",
    className           : "drilldown",
    childView           : OrderRow,
    emptyView           : NoOrderRow,
    childViewEventPrefix: "order:row",
    childViewContainer  : "tbody"
  });
  
  var Order = Views.TableRowView.extend({
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
      condition     : { invoiceIssued: false },
      failureMsg    : "Ordine già fatturato."
    }, {
      behaviorClass : Behaviors.DrillDownBehavior,
      detailsView   : OrderRows
    }],

    onRender: function() {
      if (this.model.get('invoiceIssued')) {
        this.$el.addClass('success');
      }
    }
  });

  Views.Orders = Views.TableView.extend({
    childView: Order,
    childViewEventPrefix: "order",
    modelClass: WMS.Models.SupplierOrder,
    headers: [
      { width: "14px" },
      { width: "20%", name: "code" },
      { width: "35%", name: "supplierId" },
      { width: "40%", name: "subject" },
      { width: "5%" }
    ]
  });

  var InvoiceRowForm = Views.ModalFormView.extend({
    triggers: {
      "click .js-cancel": "cancel",
      "click .js-submit": "save"
    },

    behaviors: [{
      behaviorClass : Behaviors.FormBehavior,
      fieldSelector : "app-field",
      insertPoint   : "div.modal-body",
      skipFields    : ["total"],
      readonly      : ['noteRowId'],
      modelClass    : WMS.Models.SupplierInvoiceRow
    }, {
      behaviorClass: Behaviors.CascadingDefaultBehavior,
      bindings: {articleId:["description", "unitTypeId", "price"]}
    }, {
      behaviorClass: Behaviors.ModalBehavior
    }]
  });

  Views.NewRow = InvoiceRowForm.extend({
    title: "Nuova riga",
    saveButtonText: "Aggiungi",
  });

  Views.EditRow = InvoiceRowForm.extend({
    title: "Aggiorna riga",
    saveButtonText: "Aggiorna"
  });

  var Row = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass: Behaviors.TableRowBehavior
    , fields: [
        "articleCode",
        "description",
        "noteCode",
        "unitType",
        { attr:"price", className:"text-right", format:"price"},
        { attr:"quantity", className:"text-right", format:"money"},
        { attr:"discountPercent", className:"text-right", format:"money"},
        { attr:"total", className:"text-right", format:"money"}
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
    title: "Righe Fattura",
    childView: Row,
    childViewEventPrefix: "supplier:invoice:row",
    modelClass    : WMS.Models.SupplierInvoiceRow,
    headers       : [
      { width: "10%", name: "articleCode" },
      { width: "30%", name: "description" },
      { widht: "10%", name: "noteCode" },
      { width: "10%", name: "unitTypeId" },
      { width: "10%", name: "price", className:"text-right" },
      { width: "10%", name: "quantity", className:"text-right" },
      { width: "10%", name: "discountPercent", className:"text-right" },
      { width: "10%", name: "total", className:"text-right" },
      { width: "10%" }
    ],
    behaviors: [{
      behaviorClass : Behaviors.CollapsableBehavior
    }, {
      behaviorClass : Behaviors.ColumnTotalBehavior,
      totals        : [,,,,,,,{attr:"total", format:"money", className:"text-right"},,]
    }, {
      behaviorClass : Behaviors.AddBehavior
    }]
  });

  Views.Details = Views.DetailsView.extend({
    behaviors: [{
      behaviorClass : Behaviors.DetailsBehavior,
      modelClass    : WMS.Models.SupplierInvoice,
      fields: [
        { name: "code" },
        { name: "date", type: "date", cols:4 },
        { type:"actions", cols:2, className:"text-right actions" },
        { name: "commissionId", cols:12, labelCols:2, fieldCols:10 },
        { name: "subject"},
        { name: "supplierInvoice" },
        { name: "supplierCode" },
        { name: "supplierId", label: false, fieldCols: 12 },
        { name: "destinationId", cols: 12, labelCols: 2, fieldCols: 10 },
        { name:"paymentTypeId" },
        { name:"vatRateId" },
        { name:"applyTo", cols:12, labelCols:2, fieldCols:10 },
        { name:"discountPercent" },
        { name:"discountValue" },
      ]
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }, {
      behaviorClass : Behaviors.AddRowBehavior
    , insertPoint   : ".actions"
    }, /*{
      behaviorClass : Behaviors.PrintableBehavior
    , insertPoint   : ".actions"
    },*/ {
      behaviorClass : Behaviors.CollapsableBehavior
    }]
  });

  Views.SelectCommission = WMS.Common.Views.ModalFormView.extend({
    initialize: function(options) {
      this.model = new WMS.Models.SupplierInvoiceCommission(_.pick(options, "supplierId"));
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
      , modelClass    : WMS.Models.SupplierInvoice
      , saveHandler   : this.options.saveHandler
      }, {
        behaviorClass : Behaviors.ModalBehavior
      }] 
    } 
  })
});