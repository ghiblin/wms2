WMS.module('Commissions.Show', function(Show, WMS, Backbone, Marionette, $, _) {  var Views = Show.Views = _.extend({}, WMS.Common.Views, WMS.Commissions.Forms)    , Behaviors = WMS.Common.Behaviors;  Views.Layout =Marionette.LayoutView.extend({    template: _.template(      "<div class='page-header' id='title-region'></div>" +      "<div class='row' id='details-region'></div>" +      "<div class='row' id='costs-region'></div>" +      "<div class='page-header'><h4 class='text-center'>Documenti Collegati</h4></div>" +      "<div class='row'>"+        "<div id='public-files-region' class='col-sm-6'></div>"+        "<div id='private-files-region' class='col-sm-6'></div>"+      "</div><div class='row'>"+        "<div id='estimates-region' class='col-sm-6'></div>"+        "<div id='orders-region' class='col-sm-6'></div>"+        "<div id='notes-region' class='col-sm-6'></div>"+        "<div id='invoices-region' class='col-sm-6'></div>"+      "</div>"    ),    regions: {      titleRegion       : '#title-region',      detailsRegion     : '#details-region',      costsRegion       : '#costs-region',      publicFilesRegion : '#public-files-region',      privateFilesRegion: '#private-files-region',      estimatesRegion   : '#estimates-region',      ordersRegion      : '#orders-region',      notesRegion       : '#notes-region',      invoicesRegion    : '#invoices-region'    }  });  Views.NotFound = Marionette.ItemView.extend({    template : _.template("<b>Errore!</b>&nbsp;Commessa non trovata")  , className: "alert alert-danger"  });  Views.AttachmentForm = Views.ModalFormView.extend({    behaviors: [{      behaviorClass : Behaviors.FormBehavior    , insertPoint   : "div.modal-body"    , readonly      : ["commissionId"]    }, {      behaviorClass : WMS.Common.Behaviors.ModalBehavior    }]  , initialize: function(options) {      this.model = new WMS.Models.CommissionAttachment({        commissionId: options.commissionId      });    }  });  Views.Details = Marionette.ItemView.extend({    template  : _.template(      "<div class='panel-heading'>Dettagli</div>"+      "<div class='panel-body'>"+        "<form class='form form-horizontal details'></form>"+      "</div>"    ),    className : "panel panel-default",    behaviors : [{      behaviorClass : Behaviors.DetailsBehavior,      modelClass    : WMS.Models.Commission,      insertPoint   : ".details",      fields        : [        { name: "code" },        { type: "actions", className: "text-right actions" },        { name: "product", cols: 12, labelCols:2, fieldCols: 10 },        { name: "clientId", cols: 12, labelCols:2, fieldCols: 10 },        { name: "destinationId", cols: 12, labelCols: 2, fieldCols: 10 },        { name: "startDate", type: "date" },        { name: "deliveryDate", type: "date" }      ]    }, {      behaviorClass: Behaviors.CollapsableBehavior    }, {      behaviorClass : Behaviors.UpdateBehavior    }, {      behaviorClass : Behaviors.EditableBehavior,      insertPoint   : ".actions",      FormView      : Views.Edit    }, {      behaviorClass : Behaviors.AttachableBehavior,      insertPoint   : ".actions",      FormView      : Views.AttachmentForm,      formOptions   : { commissionId:"id" }    }, {      behaviorClass : Behaviors.PrintableBehavior,      insertPoint   : ".actions"    }]  });  var Cost = Views.TableRowView.extend({    behaviors: [{      behaviorClass : Behaviors.TableRowBehavior    , fields        : [        { attr:'date', format:'date'},        'employee',        'workType',        {attr:'hours', className:'text-right', format:"money"},        {attr:'total', className:'text-right', format:"money"},        'note'      ]    }, {      behaviorClass : Behaviors.SelectableBehavior    }, {      behaviorClass : Behaviors.UpdateBehavior    }]  });      Views.Costs = WMS.Common.Views.TableView.extend({    template: _.template(      "<div class='panel-heading'>Costi</div>"+      "<table class='table table-hover'><thead /><tbody /><tfoot /></table>"    ),    tagName: "div",    className: "panel panel-default",    childView: Cost,    modelClass: WMS.Models.CommissionCost,    headers: [      { width: '10%', name: 'date' },      { width: '20%', name: 'employee' },      { width: '20%', name: 'workType' },      { width: '10%', name: 'hours', className: "text-right" },      { width: '10%', name: 'total', className: "text-right" },      { widht: '20%', name: 'note' },      { width: '5%'}    ],    behaviors: [      {        behaviorClass : Behaviors.CollapsableBehavior,        collapsed     : true      }, {        behaviorClass : Behaviors.ColumnTotalBehavior,        totals: [,,,,{attr: "total", className: "text-right", format: "money"},,]      }    ]  });  var FileView = Marionette.ItemView.extend({    template: _.template(      "<a href='<%= downloadUrl %>'><%= filename %></a>" +      "<span class='pull-right glyphicon glyphicon-trash js-delete'></span>" )  , templateHelpers: function() {      return {        downloadUrl: this.model.downloadUrl()      }    }  , ui: {      destroy: ".js-delete"    }  , events: {      "mouseenter": function() { this.ui.destroy.removeClass("hidden"); }    , "mouseleave": function() { this.ui.destroy.addClass("hidden"); }    }  , triggers: {      "click @ui.destroy": "attachment:destroy"    }  , tagName: "li"  , className: "list-group-item"  , onRender: function() {      this.ui.destroy.addClass("hidden");    }  });  var NoFileView = Marionette.ItemView.extend({    template: _.template("<i>Nessun file caricato.</i>")  , tagName: "li"  , className: "list-group-item"  });  var ListView = Marionette.CompositeView.extend({    template: _.template(      "<div class='panel-heading'><%= title %></div>" +      "<ul class='list-group'></ul>"    ),    templateHelpers: function() {      return {        title: this.getOption("title")      };    },    className: "panel panel-default",    childViewContainer: "ul",        behaviors: [      {        behaviorClass: Behaviors.CollapsableBehavior,        collapsed    : true      }    ]  });  var ListItemView = Marionette.ItemView.extend({    tagName: "li",    className: "list-group-item"  });  Views.FileList = ListView.extend({    childView: FileView,    emptyView: NoFileView,    filter: function(model) {      return model.get("private") === this.getOption("private");    },    private: false,    initialize: function() {      this.title = this.getOption("private") ? "File Privati" : "File Pubblici";    },    onChildviewAttachmentDestroy: function(childView) {      this.trigger("attachment:destroy", childView);    }  });  var Estimate = ListItemView.extend({    template: _.template("<a href='#clients/estimates/id:<%= id %>/code:<%= code %>'><%= code %> - <%= subject %></a>")  });  var NoEstimate = ListItemView.extend({    template: _.template("<i>Nessun preventivo associato.</i>")  });  Views.Estimates = ListView.extend({    childView: Estimate,    emptyView: NoEstimate,    title: "Preventivi Cliente"  });  var Order = ListItemView.extend({    template: _.template("<a href='#clients/orders/id:<%= id %>/code:<%= code %>'><%= code %> - <%= subject %></a>")  });  var NoOrder = ListItemView.extend({    template: _.template("<i>Nessun ordine associato.</i>")  });  Views.Orders = ListView.extend({    childView: Order,    emptyView: NoOrder,    title: "Ordini Cliente"  });  var Note = ListItemView.extend({    template: _.template("<a href='#clients/notes/id:<%= id %>/code:<%= code %>'><%= code %> - <%= subject %></a>")  });  var NoNote = ListItemView.extend({    template: _.template("<i>Nessuna bolla associata.</i>")  });  Views.Notes = ListView.extend({    childView: Note,    emptyView: NoNote,    title: "Bolle Cliente"  });  var Invoice = ListItemView.extend({    template: _.template("<a href='#clients/invoices/id:<%= id %>/code:<%= code %>'><%= code %> - <%= subject %></a>")  });  var NoInvoice = ListItemView.extend({    template: _.template("<i>Nessuna fattura associata.</i>")  });  Views.Invoices = ListView.extend({    childView: Invoice,    emptyView: NoInvoice,    title: "Fatture Cliente"  });});