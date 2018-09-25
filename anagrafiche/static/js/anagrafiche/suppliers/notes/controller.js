WMS.module("Suppliers.Notes", function(Notes, WMS, Backbone, Marionette, $, _) {
  var Views = Notes.Views;

  Notes.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: "get:supplier:note:list", name: "notes", options: ["code", "supplierId", "from", "to"] }
    , { request: "get:supplier:order:list", name: "orders", options: ["code", "supplierId", "from", "to"] }
    , { request: "get:supplier:note", name: "note", options: ["id"] }
    , { request: "get:supplier:note:rows", name:"rows", options:["id"] }
    ]

  , regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "Bolle Fornitore"
        }
      }, {
        name: "filterRegion"
      , View: Views.FilterView
      , options : {
          code    : "@code"
        , supplierId: "@supplierId"
        , from    : "@from"
        , to      : "@to"
        }
      , events: {
          "search": "search"
        }
      }, {
        name: "panelRegion"
      , viewName: "_panel"
      , View: Notes.Views.Panel
      , events: {
          "supplier:note:add"      : "addNote",
          "supplier:note:drop"     : "dropNote",
          "notes:show"    : "showNotesTab",
          "orders:show"   : "showOrdersTab",
        }
      }, {
        name    : "detailsRegion"
      , View    : Views.Details
      , options : {
          model   : "@note"
        }
      , events  : {
          "supplier:note:row:add": "addNoteRow"
        }
      }, {
        name    : "rowsRegion"
      , viewName: "_rows"
      , View    : Views.Rows
      , options : {
          collection : "@rows"
        }
      }
    ]

  , _notesRegion: {
      name: "masterRegion"
    , viewName: "_notes"
    , View: Notes.Views.Notes
    , options: {
        collection: "@notes"
      }
    , stickyHeaders:true
    , events: {
        "note:selected"   : "selectNote"
      , "note:unselected" : "unselectNote"
      }
    , className: "scrollable"
    , css: { height:"286px" }
    }

  , _ordersRegion: {
      name: "masterRegion"
    , viewName: "_orders"
    , View: Notes.Views.Orders
    , options: {
        collection: "@orders"
      }
    , stickyHeaders: true
    }

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "supplier:note:created", function(note) {
        var options = _.pick(self.options, "code", "supplierId", "from", "to");
        options.id = note.get("id");
        WMS.trigger("suppliers:notes:list", options);
      });

      this.listenTo(WMS.vent, "supplier:note:updated", function(note) {
        // Aggiorno la bolla presente nella lista
        var model = self.options.notes.find({ id:note.get("id") });
        if (model) {
          model.set(note.attributes);
        }

        // Aggiorno eventuale bolla nella vista di dettaglio
        if (self.options.id === note.get("id")) {
          self.options.note.set(note.attributes);
        }
      });

      this.listenTo(WMS.vent, "supplier:note:row:created", function(row) {
        self.options.rows.add(row);
      });

      this.listenTo(WMS.vent, "supplier:note:row:updated", function(row) {
        var model = self.options.rows.find({ id:row.get("id") });
        if (model) {
          model.set(row.attributes);
        }
      });
    }

  , listNotes: function(id, code, supplierId, from, to) {
      _.extend(this.options, {id:id, code:code, supplierId:supplierId, from:from, to:to});

      var self = this;
      this.start().done(function() {
        // Mi assicuro che siano tutti deselezionati
        self.options.notes.each(function(note) {
          note.deselect();
        });
        if (self.options.id) {
          // seleziono l'ordine dell'url
          var note = self.options.notes.find({ id:id });
          if (note) {
            note.select();
          }
        }

        var show = function() {
          self.setupRegions(self._layout);
          if (self.options.tab === "orders") {
            self.showOrdersTab();
          } else {
            self.showNotesTab();
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
      this.options = _.omit(this.options, "notes", "orders");
      WMS.trigger("suppliers:notes:list", args.model.attributes);
    }

  , addNote: function() {
      if (WMS.getCurrentUser().can("supplierNote:create")) {
        var model = new WMS.Models.Note()
          , view = new Notes.Views.NewNote(_.extend({}, this.options, {model: model}));
        
        this._showModal(view, _.bind(function() {
          this._createModel(model, view, this._notes).then(function() {
            WMS.execute("reset:note:list");
          });
        }, this));
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , selectNote: function(args) {
      if (WMS.getCurrentUser().can("supplierNote:retrive")) {
        this.options = _.omit(this.options, "note", "rows");
        WMS.trigger("suppliers:notes:list", _.extend(this.options, {id: args.model.get("id")}));
        /*this.listNotes(
          args.model.get("id")
        , this.options.code
        , this.options.supplierId
        , this.options.from
        , this.options.to);*/
      }
    }

  , unselectNote: function() {
      if (this.options.id === undefined) return;
      // rimuovo i riferimenti alla bolla
      this.options = _.omit(this.options, "id", "note", "rows");
      WMS.trigger("suppliers:notes:list", this.options);
    }

  , showNotesTab: function() {
      this.options.tab = "notes";
      this._panel.setActiveTab("notes");
      this._panel.hideDropButton();
      this.setupRegions(this._layout, [this._notesRegion]);
    },
    
    showOrdersTab: function() {
      this.options.tab = "orders";
      this._panel.setActiveTab("orders");
      this._panel.showDropButton();
      this.setupRegions(this._layout, [this._ordersRegion]);
    }

  , dropNote: function() {
      var klass = WMS.Models.SupplierNote;
      if (klass.canCreate()) {
        var supplier = null
          , ids = [];

        // cerco i preventivi che hanno almeno una riga selezionata
        var orders = this.options.orders.getSelected();
        if (orders.length === 0) {
          WMS.showError("Selezionare almeno una riga.");
          return;
        }

        // ottengo la lista degli id dei supplieri associati ai preventivi
        var supplierIds = _.uniq(_.map(orders, function(order) { 
          return order.get("supplierId"); 
        }));

        if (supplierIds.length > 1) {
          WMS.showError("Tutti gli ordini devono essere associati allo stesso fornitore.");
          return;
        }
        var supplierId = supplierIds[0];

        // recupero la lista delle righe selezionate
        var rows = this.options.orders.getSelectedRows();

        // tengo solo gli id delle righe
        var ids = _.map(rows, function(row) { return row.attributes.id; });

        if (this.options.id) {
          // ho un preventivo selezionato
          if (supplierId !== this.options.note.get("supplierId")) {
            // il fornitore delle righe selezionate non corrispondono col fornitore dell"ordine
            var msg = "Attenzione! Le righe selezionate sono associate ad un fornitore diverso da quello " +
              "della bolla.\nCreo un nuova bolla con tali righe?";
            if (confirm(msg)) {
              this._createNoteWithRows(supplierId, ids);
            }
          } else {
            var msg = "Aggiungo le righe alla bolla " + this.options.note + "?";
            if (confirm(msg)) {
              this._addRowsToNote(this.options.id, ids);
            }
          }
        } else {
          var msg = "Nessuna bolla selezionata\nCreo una nuova bolla con le righe selezionate?";
          if (confirm(msg)) {
            this._createNoteWithRows(supplierId, ids);
          }
        }
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , _createNoteWithRows: function(supplierId, rowIds) {
      var self = this;

      WMS.request("get:supplier:note:drop", {
        rows: rowIds
      }).then(function(note) {
        self.options.id = note.get("id");
        WMS.showSuccess("Bolla " + note + " creata.");
        WMS.trigger("suppliers:notes:list", _.pick(self.options, "id", "code", "supplierId", "from", "to"));
      }).fail(function(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          WMS.showError(xhr.responseJSON.error);
        } else {
          WMS.showError("Errore creando la bolla.");
        }
      });
        
    }

  , _addRowsToNote: function(orderId, rowIds) {
      var self = this;
      WMS.request("get:supplier:note:drop", {id:orderId, rows:rowIds})
        .then(function(note) {
          self.options = _.omit(self.options, "orders", "rows");
          WMS.showSuccess("Bolla " + note + " aggiornata.");
          self.listNotes(
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
            WMS.showError("Errore aggiornando la bolla.");
          }
        });
    }

  , addNoteRow: function(args) {
      var klass = WMS.Models.SupplierNoteRow;
      if (klass.canCreate()) {
        var model = new klass({
            noteId: args.model.get("id") 
          })
          , view = new Notes.Views.NewRow({ model: model });

        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  });
});