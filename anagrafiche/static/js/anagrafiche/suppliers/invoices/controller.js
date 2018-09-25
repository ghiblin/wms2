WMS.module("Suppliers.Invoices", function(Invoices, WMS, Backbone, Marionette, $, _) {
  var Views = Invoices.Views;

  Invoices.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: "get:supplier:invoice:list", name: "invoices", options: ["code", "supplierId", "from", "to"] }
    , { request: "get:supplier:note:list", name: "notes", options: ["code", "supplierId", "from", "to"] }
    , { request: "get:supplier:order:list", name: "orders", options: ["code", "supplierId", "from", "to"] }
    , { request: "get:supplier:invoice", name: "invoice", options: ["id"] }
    , { request: "get:supplier:invoice:rows", name:"rows", options:["id"] }
    ]

  , regions: [{
        name    : "titleRegion"
      , View    : Views.Title
      , options : {
          title   : "Fatture Fornitore"
        }
      }, {
        name    : "filterRegion"
      , View    : Views.FilterView
      , options : {
          code    : "@code"
        , supplierId: "@supplierId"
        , from    : "@from"
        , to      : "@to"
        }
      , events  : {
          "search": "search"
        }
      }, {
        name    : "panelRegion"
      , viewName: "_panel"
      , View    : Views.Panel
      , events  : {
          "supplier:invoice:drop" : "dropInvoice"
        , "invoices:show"       : "showInvoicesTab"
        , "notes:show"          : "showNotesTab"
        , "orders:show"         : "showOrdersTab"
        }
      }, {
        name    : "detailsRegion"
      , viewName: "_details"
      , View    : Views.Details
      , options : {
          model   : "@invoice"
        }
      , events: {
          "supplier:invoice:row:add": "addInvoiceRow"
        }
      }, {
        name:"rowsRegion"
      , viewName:"_rows"
      , View: Views.Rows
      , options: {
          collection: "@rows"
        }
      }
    ]

  , _invoicesRegion: {
      name: "masterRegion"
    , viewName: "_invoices"
    , View: Views.Invoices
    , options: {
        collection: "@invoices"
      }
    , events: {
        "invoice:selected": "selectInvoice"
      , "invoice:unselected": "unselectInvoice"
      }
    , className: "scrollable"
    , css: { height:"286px" }
    }

  , _notesRegion: {
      name: "masterRegion"
    , viewName: "_notes"
    , View: Views.Notes
    , options: {
        collection: "@notes"
      }
    }
    
  , _ordersRegion: {
      name: "masterRegion"
    , viewName: "_orders"
    , View: Views.Orders
    , options: {
        collection: "@orders"
      }
    }


  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "supplier:invoice:created", function(invoice) {
        var options = _.pick(self.options, "code", "supplierId", "from", "to");
        options.id = invoice.get("id");
        WMS.trigger("suppliers:invoices:list", options);
      });

      this.listenTo(WMS.vent, "supplier:invoice:updated", function(invoice) {
        // Aggiorno l"ordine presente nella lista
        var model = self.options.invoices.find({ id:invoice.get("id") });
        if (model) {
          model.set(invoice.attributes);
        }

        // Aggiorno eventuale ordine nella vista di dettaglio
        if (self.options.id === invoice.get("id") && self.options.invoice) {
          self.options.invoice.set(invoice.attributes);
        }
      });

      this.listenTo(WMS.vent, "supplier:invoice:row:created", function(row) {
        self.options.rows.add(row);
      });

      this.listenTo(WMS.vent, "supplier:invoice:row:updated", function(row) {
        var model = self.options.rows.find({ id:row.get("id") });
        if (model) {
          model.set(row.attributes);
        }
      });
    },

    reset: function() {
      this.options = _.omit(this.options, "invoice", "rows", "orders", "estimates");
      if (this._layout && !this._layout.isDestroyed) {
        this._layout.destroy();
      }
    }

  , listInvoices: function(id, code, supplierId, from, to) {
      supplierId = parseInt(supplierId);
      supplierId = _.isNaN(supplierId) ? null : supplierId;
      this.options = _.extend({}, 
        _.omit((this.options || {}), "id", "code", "supplierId", "from", "to", "order", "rows"), 
        {id:id, code:code, supplierId:supplierId, from:from, to:to}
      );
      var self = this;
      this.start().done(function() {
        // Mi assicuro che siano tutti deselezionati
        self.options.invoices.each(function(invoice) {
          invoice.deselect();
        });
        if (self.options.id) {
          // seleziono l"ordine dell"url
          var invoice = self.options.invoices.find({id:id});
          if (invoice) {
            invoice.select();
          }
        }

        var show = function() {
          self.setupRegions(self._layout);
          if (self.options.tab === "notes") {
            self.showNotesTab();
          } else if (self.options.tab === "orders") {
            self.showOrdersTab();
          } else {
            self.showInvoicesTab();
          }

          if (self.options.invoice && self.options.invoice.get("pending")) {
            var msg = "Fattura creata con dati di default.\nConfermarla ora?";
            if (confirm(msg)) {
              var form = new Views.EditInvoice({model:invoice});
              WMS.showModal(form);
            }
          }

        };
        if (self._layout !== undefined && !self._layout.isDestroyed) {
          show();
        } else {
          self._layout = new Views.Layout();
          self._layout.on("show", show);
          WMS.getRegion("mainRegion").show(self._layout);
        }
      });
    }

  , search: function(args) {
      this.options = _.omit(this.options, "invoices", "orders", "estimates");
      WMS.trigger("suppliers:invoices:list", args.model.attributes);
    }
    
    /**
     * Drop down dell"ordine. 
     * Se ho selezionato un ordine, aggiunge le righe selezionate a tale ordine, altrimenti
     * ne crea uno nuovo.
     */
  , dropInvoice: function() {
      var klass = WMS.Models.SupplierInvoice;
      if (klass.canCreate()) {
        var supplier = null
          , ids = [];

        // se tab = notes prento notes, se tab = orders prendo orders
        var list = this.options[this.options.tab];

        // cerco i preventivi che hanno almeno una riga selezionata
        var selected = list.getSelected();
        if (selected.length === 0) {
          WMS.showError("Selezionare almeno una riga.");
          return;
        }

        // ottengo la lista degli id dei supplieri associati ai preventivi
        var supplierIds = _.uniq(_.map(selected, function(item) { 
          return item.attributes.supplierId; 
        }));

        if (supplierIds.length > 1) {
          if (this.options.tab === "notes") {
            WMS.showError("Tutti le fatture devono essere associati allo stesso fornitore.");
          } else {
            WMS.showError("Tutti gli ordini devono essere associati allo stesso fornitore.");
          }
          return;
        }
        var supplierId = supplierIds[0];

        // ottengo la lista degli id delle commesse associate a ordini/bolle
        // NB: filtro le commissionId == null
        var commissionIds = _.without(_.uniq(_.map(selected, function(model) {
          return model.get('commissionId');
        })), null);

        if (commissionIds.length > 1) {
          var msg;
          if (tab === "notes") {
            msg = "Tutte le bolle devono essere associate alla stessa commessa.";
          } else {
            msg = "Tutti gli ordini devono essere associati alla stessa commessa.";
          }
          WMS.showError(msg);
          return;
        }
        var commissionId = commissionIds.length === 1 ? commissionIds[0] : null;

        // recupero la lista delle righe selezionate
        var rows = list.getSelectedRows();

        // tengo solo gli id delle righe
        var ids = _.map(rows, function(row) { return row.attributes.id; });

        if (this.options.id) {
          // ho una fattura selezionata
          if (supplierId !== this.options.invoice.get("supplierId")) {
            // il fornitore delle righe selezionate non corrispondono col fornitore dell"ordine
            var msg = "Attenzione! Le righe selezionate sono associate ad un fornitore diverso da quello " +
              "della fattura.\nCreo una nuova fattura con tali righe?";
            if (confirm(msg)) {
              this._createInvoiceWithRows(supplierId, commissionId, ids);
            }
          } else if (commissionId && commissionId !== this.options.invoice.get("commissionId")) {
            var msg = "Attenzione! Le righe selezionate sono associate ad una commessa diversa da quella " +
              "dell'ordine.\nCreo una nuova fattura con tali righe?";
            if (confirm(msg)) {
              this._createInvoiceWithRows(supplierId, commissionId, ids);
            }
          } else {
            var msg = "Aggiungo le righe alla fattura " + this.options.invoice + "?";
            if (confirm(msg)) {
              this._addRowsToInvoice(this.options.id, ids);
            }
          }
        } else {
          var msg = "Nessuna fattura selezionata\nCreo una nuova fattura con le righe selezionate?";
          if (confirm(msg)) {
            this._createInvoiceWithRows(supplierId, commissionId, ids);
          }
        }
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , _createInvoiceWithRows: function(supplierId, commissionId, rowIds) {
      var self = this;
      var options = {commissionId: commissionId};
      options[(self.options.tab === "notes") ? "noteRows" : "orderRows"] = rowIds;

      var dropSuccess = function(invoice) {
        self.options.id = invoice.get("id");
        WMS.showSuccess("Fattura " + invoice + " creata.");
        WMS.trigger("suppliers:invoices:list", _.pick(self.options, "id", "code", "supplierId", "from", "to"));
      };

      var dropFail = function(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          WMS.showError(xhr.responseJSON.error);
        } else {
          WMS.showError("Errore creando la fattura.");
        }
      };

      if (commissionId !== null) {
        WMS.request("get:supplier:invoice:drop", options)
          .then(dropSuccess)
          .fail(dropFail);
      } else {
        // devo recuperare la commessa
        var view = new Views.SelectCommission({
          supplierId: supplierId
        , saveHandler: function(model, view) {
            var commissionId = model.get("commissionId");
            view.trigger("close");
            options.commissionId = commissionId;    

            WMS.request("get:supplier:invoice:drop", options)
              .then(dropSuccess)
              .fail(dropFail);
          }
        });
        WMS.showModal(view);
      }
    }

  , _addRowsToInvoice: function(invoiceId, rowIds) {
      var self = this;
      var options = {id: invoiceId};
      options[(this.options.tab === "notes") ? "noteRows" : "orderRows"] = rowIds;
      WMS.request("get:supplier:invoice:drop", options)
        .then(function(invoice) {
          self.options = _.omit(self.options, "notes", "orders", "rows");
          WMS.showSuccess("Fattura " + invoice + " aggiornata.");
          self.listInvoices(
            self.options.id
          , self.options.code
          , self.options.supplierId
          , self.options.from
          , self.options.to
          );
        })
        .fail(function(xhr) {
          if (xhr.responseJSON && xhr.responseJSON.error) {
            WMS.showError(xhr.responseJSON.error);
          } else {
            WMS.showError("Errore aggiornando la fattura.");
          }
        });
    }

  , selectInvoice: function(args) {
      var invoice = args.model;
      if (invoice.canRead()) {
        if (invoice.get("id") === this.options.id) return;
        this.options = _.omit(this.options, "invoice", "rows");
        WMS.trigger("suppliers:invoices:list", _.extend(this.options, {id: invoice.get("id")}));
      }
    },

    /**
     * Deseleziono un ordine.
     */
    unselectInvoice: function() {
      if (this.options.id === undefined) return;
      // rimuovo i riferimenti all"ordine
      this.options = _.omit(this.options, "id", "invoice", "rows");
      WMS.trigger("suppliers:invoices:list", this.options);
    }

  , showInvoicesTab: function() {
      this.options.tab = "invoices";
      this._panel.setActiveTab("invoices");
      this._panel.hideDropButton();
      this.setupRegions(this._layout, [this._invoicesRegion]);
    }

  , showNotesTab: function() {
      this.options.tab = "notes";
      this._panel.setActiveTab("notes");
      this._panel.showDropButton();
      this.setupRegions(this._layout, [this._notesRegion]);
    }

  , showOrdersTab: function() {
      this.options.tab = "orders";
      this._panel.setActiveTab("orders");
      this._panel.showDropButton();
      this.setupRegions(this._layout, [this._ordersRegion]);
    }


  , addInvoiceRow: function(args) {
      var klass = WMS.Models.SupplierInvoiceRow;
      if (klass.canCreate()) {
        var model = new klass({ 
            invoiceId: args.model.get("id") 
          })
          , view = new Invoices.Views.NewRow({ model: model });
        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , editInvoiceRow: function(view, args) {
      var row = args.model;
      if (row.canUpdate()) {
        var view = new Invoices.Views.EditRow({ model: row });

        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , deleteInvoiceRow: function(childView, args) {
      var model = args.model;
      if (model.canDestroy()) {
        if (confirm("Eliminare la riga della fattura?")) {
          model.destroy();
          WMS.showSuccess("Riga della fattura '" + this.options.invoice + "' eliminata.");
        }
      }
    }
  });
});