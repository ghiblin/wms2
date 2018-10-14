WMS.module("Common", function(Common, WMS, Backbone, Marionette, $, _) {
  var Views = Common.Views = {}
    , Behaviors = Common.Behaviors;

  Views.FormView = Marionette.ItemView.extend({
    triggers: {
      "click .js-cancel": "cancel",
      "click .js-submit": "save"
    }
  });

  Views.ModalFormView = Common.Views.FormView.extend({
    template        : "#modal-form",
    className       : "modal-dialog",
    templateHelpers : function() {
      var title = this.title || ""
        , saveButtonText = this.saveButtonText || "Salva"
        , fields = this.fields || [];
      return {
        title: title,
        saveButtonText: saveButtonText,
        fields: fields,
        notes: this.getOption("notes")
      }
    },

    notes: "",

    ui: {
      cancel: ".js-cancel",
      submit: ".js-submit"
    }, 

    triggers: {
      "click @ui.cancel": "cancel",
      "click @ui.submit": "save"
    }
  });
  
  Views.DefinitionListItemView = Marionette.ItemView.extend({
    events: {
      "mouseenter" : "showActionsPanel",
      "mouseleave" : "hideActionsPanel"
    },
    modelEvents: {
      "sync": "render"
    },
    triggers: {
      "click .js-edit": "edit",
      "click .js-delete": "delete"
    },
    ui: {
      actions: "div.js-actions"
    },
    onRender: function() {
      this.ui.actions.hide();
    },
    showActionsPanel: function() { 
      this.ui.actions.fadeIn(); 
    },
    hideActionsPanel: function() {
      this.ui.actions.fadeOut();
    },
  });

  Views.MasterDetailsLayout = Marionette.LayoutView.extend({
    template: _.template(
      '<div id="title-region" class="page-header"></div>' +
      '<div class="row">' +
        '<% if (showFilter) { %>' +
          '<div class="col-sm-12 col-md-8">' +
            '<div class="row">' +
              '<div class="col-sm-12" id="panel-region"></div>' +
              '<div class="col-sm-12" id="master-region"></div>' +
              '<div class="col-sm-12" id="paginator-region"></div>' +
            '</div>' +
          '</div>' +
          '<div id="filter-region" class="col-md-4" style="height:100%"></div>' +
        '<% } else { %>' +
          '<div class="col-sm-12" id="panel-region"></div>' +
          '<div class="col-sm-12" id="master-region"></div>' +
        '<% } %>' +
      '</div>' +
      '<div class="row" id="details-region"></div>' +
      '<div class="row" id="rows-region"></div>' +
      '<div class="row" id="footer-region"></div>'
    ),
    showFilter: true,
    templateHelpers: function() {
      return {
        showFilter: this.getOption("showFilter")
      }
    },

    regions: {
      titleRegion   : "#title-region",
      panelRegion   : "#panel-region",
      masterRegion  : "#master-region",
      paginatorRegion: '#paginator-region',
      filterRegion  : "#filter-region",
      detailsRegion : "#details-region",
      rowsRegion    : "#rows-region",
      footerRegion  : "#footer-region"
    }
  });
    
  Views.FilterLayout = Marionette.LayoutView.extend({
    template: "#filter-layout",

    regions: {
      titleRegion   : "#title-region",
      panelRegion   : "#panel-region",
      listRegion    : "#list-region",
      paginatorRegion: '#paginator-region',
    },

    showPanel: true,

    onRender: function() {
      if (!this.showPanel) {
        this.panelRegion.hide();
      }
    }
  });
    
  Views.FilterPanel = Marionette.ItemView.extend({
    template: "#filter-panel"
  , fields: []
  , templateHelpers: function() {
      return {
        canAdd: _.result(this, "canAdd")
      , fields: this.getOption("fields")
      , criterion: this.getOption("criterion")
      }
    }

  , canAdd:false

  , triggers: function() {
      return {
        "click .js-new": this.eventPrefix ? this.eventPrefix + ":new" : "new",
      }
    }

  , events: {
      "submit #filter-form": "filterList"
    , "click .js-filter": "filterList"
    }

  , ui: {
      criterion: "input.js-filter-criterion"
    }

  , filterList: function(e) {
      e.preventDefault();
      var criterion = this.ui.criterion.val().replace(/\//g, "-");
      this.trigger(this.eventPrefix ? this.eventPrefix + ":filter" : "filter", criterion);
    }

  , onSetFilterCriterion: function(criterion) {
      this.ui.criterion.val(criterion);
    }
  });
  
  Views.FilterView = Marionette.ItemView.extend({
    template: _.template("")
  , tagName: "form"
  , className: "well form-horizontal"
  , buttons:[{ name: "search", label: "Cerca", icon: "filter" }]
  , behaviors:function() {
      return [{
        behaviorClass: WMS.Common.Behaviors.FormBehavior,
        buttons: this.getOption("buttons"),
        labels: "filter"
      }, {
        behaviorClass: WMS.Common.Behaviors.OffcanvasBehavior
      }];
    }

    /* Margine per allineare il filtro alle tabs */
  , attributes: {
      style: "margin-top:42px"
    }

  , triggers: {
      "click button[name=search]": "search"
    }
  });

  Views.NoListItem = Marionette.ItemView.extend({
    template: _.template([
      "<% if (offset > 0) { %>",
        "<td colspan='<%= offset %>'></td>",
      "<% } %>",
      "<td colspan='<%= colspan %>' class='text-center'>",
        "<i><%= message %></i>",
      "</td>"
      ].join(""))

  , templateHelpers: function() {
      return {
        offset  : this.getOption("offset")
      , colspan : this.getOption("colspan")
      , message : this.getOption("message")
      };
    }

  , tagName: "tr"
  , offset: 0
  , colspan: 0
  , message: ""
  });

  Views.DetailsView = Marionette.ItemView.extend({
    template  : _.template(
      "<div class='panel-heading'>Dettagli</div>"+
      "<div class='panel-body'>" +
        "<form class='form form-horizontal details'></form>" +
      "</div>"
    ),
    className : "panel panel-default"
  });

  Views.TableView = Marionette.CompositeView.extend({
    tagName   : "table",
    className : "table table-hover",
    template  : _.template("<thead></thead><tbody></tbody><tfoot></tfoot>"),
    childViewContainer: "tbody",
    headers   : [],

    onRender: function() {
      this._createHeaders();
    },

    _createHeaders: function() {
      var self  = this
        , $el = this.$el.find("thead")
        , tag   = 'th'
        , className = "header"
        , $row  = $("<tr></tr>")
        , headers = this.getOption("headers")
        , klass = this.getOption("modelClass");

      
      _.each(headers, function(header) {
        var $header = $("<" + tag + "></" + tag + ">");
        $header.addClass(className);

        if (header.width) {
          $header.attr("width", header.width);
        }
        if (header.className) {
          $header.addClass(header.className);
        }
        var name  = header.name
          , label = header.name;

        if (name) {
          $header.attr("name", name);
        }
        if (self.options.labels && WMS.labels[self.options.labels]) {
          label = WMS.labels[self.options.labels][name] || name;
        } else if (klass && klass.prototype.labels) {
          label = klass.prototype.labels[name] || name;
        }

        $header.html(label);
        $row.append($header);
      });
      $el.append($row);
    }
  });

  Views.TableRowView = Marionette.ItemView.extend({
    template  : _.template(""),
    tagName   : "tr"
  });

  Views.PanelTableView = Views.TableView.extend({
    template  : _.template(
      "<div class='panel-heading'><%= title %></div>" +
      "<table class='table table-hover'>" +
        "<thead></thead>" +
        "<tbody></tbody>" +
        "<tfoot></tfoot>" +
      "</table>"
    ),
    tagName   : "div",
    className : "panel panel-default",
    templateHelpers: function() {
      return {
        title: this.getOption("title")
      };
    }
  });

  Views.Title = Marionette.ItemView.extend({
    template  : _.template("<%= title %>")
  , tagName   : "h2"
  , className : "text-center"
  , behaviors : [{
      behaviorClass : Behaviors.UpdateBehavior
    }]
  , initialize: function(options) {
      this.model = new Backbone.Model({ title: options.title });
    }
  });

  Views.Error = Marionette.ItemView.extend({
    template: _.template("<strong>Attenzione!</strong>&nbsp;<%= message %>")
  , className: "alert alert-danger"
  , attributes: {
      role: "alert"
    }
  , initialize: function(options) {
      this.model = new Backbone.Model({ message: options.message });
    }
  });
  
  var Form = Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , fieldSelector : "app-field"
    , insertPoint   : "div.modal-body"
    , readonly      : ["clientId", "supplierId", "ownerId"]
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });

  // Address
  Views.NewAddress = Form.extend({
    title           : "Nuovo Indirizzo"
  , saveButtonText  : "Crea Indirizzo"
  });

  Views.EditAddress = Form.extend({
    title           : "Modifica Indirizzo"
  , saveButtonText  : "Aggiorna"
  });

  var Address = Marionette.ItemView.extend({
    template: _.template([
      "<dt></dt><dd>",
        "<div class='pull-right actions'></div>",
        "<address>",
          "<%= line1 %><br />",
          "<% if (line2 !== '') { %><%= line2 %><br /><% } %>",
          "<% if (zip !== '') { %><%= zip %>&nbsp; <% } %>",
          "<%= city %>",
          "<% if (state !== '') { %>&nbsp;(<%= state %>)<% } %>",
          "<br />",
          "(<%= country %>)<br />",
        "</address>",
      "</dd>"].join(""))
  , behaviors: [{
      behaviorClass: WMS.Common.Behaviors.LookupBehavior
    , field: "typeId"
    , insertPoint: "dt"
    }, {
      behaviorClass: WMS.Common.Behaviors.ItemBehavior
    , insertPoint: ".actions"
    , FormView: Views.EditAddress
    }]
  , modelEvents: {
      "change": "render"
    }
  });

  Views.Addresses = Marionette.CompositeView.extend({
    template: _.template(
      "<div class='panel-heading'>Indirizzi</div>" +
      "<div class='panel-body'>" +
        "<dl class='dl-horizontal'></dl>" +
      "</div>"
    ),
    className: "panel panel-default",
    childView: Address,
    childViewContainer: "dl",
    behaviors: [{
      behaviorClass: WMS.Common.Behaviors.CollapsableBehavior,
      collapsed: true
    }, {
      behaviorClass: WMS.Common.Behaviors.AddItemBehavior,
      insertPoint: ".panel-body",
      FormView: Views.NewAddress,
      modelOptions: ["clientId", "supplierId", "ownerId"]
    }, {
      behaviorClass: WMS.Common.Behaviors.AddBehavior
    }]
  });

  // Contatti
  Views.NewContact = Form.extend({
    title         : "Nuovo Contatto"
  , saveButtonText: "Crea Contatto"
  });
  
  Views.EditContat = Form.extend({
    title         : "Modifica Contatto"
  , saveButtonText: "Aggiorna"
  });

  var Contact = Marionette.ItemView.extend({
    template: _.template(
        "<dt></dt><dd><%= value %>" +
          "<% if (note) { %>&nbsp;<strong>(<%= note %>)</strong><% } %>" +
          "<span class='actions pull-right'></span>" +
        "</dd>")
  , behaviors: [{
      behaviorClass: WMS.Common.Behaviors.LookupBehavior
    , field: "typeId"
    , insertPoint: "dt"
    }, {
      behaviorClass: WMS.Common.Behaviors.ItemBehavior
    , insertPoint: ".actions"
    , FormView: Views.EditContat
    }]
  , modelEvents: {
      "change": "render"
    }
  });

  Views.Contacts = Marionette.CompositeView.extend({
    template: _.template(
      "<div class='panel-heading'>Contatti</div>" +
      "<div class='panel-body'>" +
        "<dl class='dl-horizontal'></dl>" +
      "</div>"
    ),
    className: "panel panel-default",
    childView: Contact,
    childViewContainer: "dl",
    behaviors: [{
      behaviorClass: WMS.Common.Behaviors.CollapsableBehavior,
      collapsed: true
    }, {
      behaviorClass: WMS.Common.Behaviors.AddItemBehavior,
      FormView: Views.NewContact,
      insertPoint: ".panel-body",
      modelOptions: ["clientId", "supplierId", "ownerId"]
    }, {
      behaviorClass: WMS.Common.Behaviors.AddBehavior
    }]
  });

  // BankDatum
  Views.NewBankDatum = Form.extend({
    title         : "Nuovo Conto Corrente"
  , saveButtonText: "Crea Conto Corrente"
  });
  
  Views.EditBankDatum = Form.extend({
    title         : "Modifica Conto Corrente"
  , saveButtonText: "Aggiorna"
  });

  var BankDatum = Marionette.ItemView.extend({
    template: _.template(
        "<dt>C/C</dt><dd>" +
          "<div class='actions pull-right'></div>" +
          "<strong><%= bank %><% if (branch != '') { %> - <%= branch %><% } %></strong><br />" +
          "<strong><%= holder %></strong><br />" +
          "<strong>IBAN:</strong><%= iban %><br />" +
          "<strong>SWIFT:</strong><%= swift %></strong>" +
        "</dd>"),

    behaviors: [{
      behaviorClass: WMS.Common.Behaviors.LookupBehavior,
      field: "typeId",
      insertPoint: "dt"
    }, {
      behaviorClass: WMS.Common.Behaviors.ItemBehavior,
      insertPoint: ".actions",
      FormView: Views.EditBankDatum
    }, {
      behaviorClass: WMS.Common.Behaviors.UpdateBehavior,
      className: 'info'
    }],
    modelEvents: {
      "change": "render"
    },

    onRender: function() {
      this.$el.removeClass('main-bank-datum');
      if (this.model.get('main')) {
        this.$el.addClass('main-bank-datum');
      }
    }
  });

  Views.BankData = Marionette.CompositeView.extend({
    template: _.template(
      "<div class='panel-heading'>Informazioni Bancarie</div>"+
      "<div class='panel-body'>" +
        "<dl class='dl-horizontal'></dl>" +
      "</div>"
    ), 
    className: "panel panel-default",
    childView: BankDatum,
    childViewContainer: "dl",
    behaviors: [{
      behaviorClass: WMS.Common.Behaviors.CollapsableBehavior,
      collapsed: true
    }, {
      behaviorClass: WMS.Common.Behaviors.AddItemBehavior,
      FormView: Views.NewBankDatum,
      insertPoint: ".panel-body",
      modelOptions: ["clientId", "supplierId", "ownerId"]
    }, {
      behaviorClass: WMS.Common.Behaviors.AddBehavior
    }]
  });

  Views.EntityLayout = Marionette.LayoutView.extend({
    template: _.template(
      '<div class="page-header" id="title-region"></div>' +
      '<div class="row" id="details-region"></div>' +
      '<div class="row" id="contacts-region"></div>' +
      '<div class="row" id="addresses-region"></div>' +
      '<div class="row" id="bankData-region"></div>'
    ),

    regions: {
      titleRegion     : "#title-region",
      detailsRegion   : "#details-region",
      contactsRegion  : "#contacts-region",
      addressesRegion : "#addresses-region",
      bankDataRegion  : "#bankData-region"
    },

    initialize: function(options) {
      this.entity = options.entity;
    }
  });


  Views.EntityDetails = Marionette.ItemView.extend({
    template: _.template(
      "<div class='panel-heading'>Dettagli</div>"+
      "<div class='panel-body'></div>"
    ),
    className: "panel panel-default",

    behaviors: function() {
      return [{
        behaviorClass: WMS.Common.Behaviors.CollapsableBehavior,
      }, {
        behaviorClass: WMS.Common.Behaviors.EditableBehavior,
        label: "Modifica",
        FormView: this.getOption('FormView'),
        insertPoint: ".panel-body",
        before: true
      }, {
        behaviorClass: WMS.Common.Behaviors.ListBehavior,
        insertPoint: ".panel-body"
      }, {
        behaviorClass: WMS.Common.Behaviors.UpdateBehavior
      }]
    },

    skipFields: function() {
      var skip = ["addresses", "contacts", "bankData"];
      if (this.model.get("typeId") === "G") {
        skip.push("firstName", "lastName");
      } else {
        skip.push("corporateName");
      }
      return skip;
    }
  });

  Views.EntityForm = Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior,
      insertPoint   : "div.modal-body",
      readonly      : ["code"],
      skipFields    : ["addresses", "contacts", "bankData"]
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }],

    modelEvents: {
      "change": "showHideFields"
    },

    showHideFields: function() {
      if (this.model.get("typeId") === "G") {
        this.$el.find(".field-corporateName").removeClass("hidden");
        this.$el.find(".field-firstName").addClass("hidden");
        this.$el.find(".field-lastName").addClass("hidden");
      } else {
        this.$el.find(".field-corporateName").addClass("hidden");
        this.$el.find(".field-firstName").removeClass("hidden");
        this.$el.find(".field-lastName").removeClass("hidden");
      }
    },

    onShow: function() {
      this.showHideFields();
    }
  });
});