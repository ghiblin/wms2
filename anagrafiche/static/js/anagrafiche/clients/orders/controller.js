WMS.module("Clients.Orders", function(Orders, WMS, Backbone, Marionette, $, _) {
  var Views = Orders.Views;

  Orders.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: "get:client:order:list", name: "orders", options: ["code", "clientId", "from", "to"] }
    , { request: "get:client:estimate:list", name: "estimates", options: ["code", "clientId", "from", "to"] }
    , { request: "get:client:order", name: "order", options: ["id"] }
    , { request: "get:client:order:rows", name:"rows", options:["id"] }
    ]

  , regions: [{
        name    : "titleRegion"
      , View    : Views.Title
      , options : {
          title   : "Ordini Cliente"
        }
      }, {
        name    : "filterRegion"
      , View    : Views.FilterView
      , options : {
          code    : "@code"
        , clientId: "@clientId"
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
          "client:order:drop" : "dropOrder"
        , "orders:show"       : "showOrdersTab"
        , "estimates:show"    : "showEstimatesTab"
        }
      }, {
        name    : "detailsRegion"
      , viewName: "_details"
      , View    : Views.Details
      , options : {
          model   : "@order"
        }
      , events: {
          "client:order:row:add": "addOrderRow"
        }
      }, {
        name:"rowsRegion"
      , viewName:"_rows"
      , View: Views.Rows
      , options: {
          collection: "@rows"
        }
      }
    ],
    
    _ordersRegion: {
      name: "masterRegion"
    , viewName: "_orders"
    , View: Views.Orders
    , options: {
        collection: "@orders"
      }
    , events: {
        "order:selected": "selectOrder"
      , "order:unselected": "unselectOrder"
      },
      className: "scrollable",
      css: { height:"286px" }
    },

    _estimatesRegion: {
      name: "masterRegion"
    , viewName: "_estimates"
    , View: Views.Estimates
    , options: {
        collection: "@estimates"
      }
    , events: {
        'estimate:selected': 'selectEstimate'
      , 'estimate:unselected': 'unselectEstimate'
      }
    }

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "client:order:created", function(order) {
        var options = _.pick(self.options, "code", "clientId", "from", "to");
        options.id = order.get("id");
        WMS.trigger("clients:orders:list", options);
      });

      this.listenTo(WMS.vent, "client:order:updated", function(order) {
        // Aggiorno l"ordine presente nella lista
        var model = self.options.orders.find({ id:order.get("id") });
        if (model) {
          model.set(order.attributes);
        }

        // Aggiorno eventuale ordine nella vista di dettaglio
        if (self.options.id === order.get("id") && self.options.order) {
          self.options.order.set(order.attributes);
        }
      });

      this.listenTo(WMS.vent, "client:order:row:created", function(row) {
        self.options.rows.add(row);
      });

      this.listenTo(WMS.vent, "client:order:row:updated", function(row) {
        var model = self.options.rows.find({ id:row.get("id") });
        if (model) {
          model.set(row.attributes);
        }
      });
    },

    reset: function() {
      this.options = _.omit(this.options, "order", "rows", "orders", "estimates");
      if (this._layout && !this._layout.isDestroyed) {
        this._layout.destroy();
      }
    }

  , listOrders: function(id, code, clientId, from, to) {
      clientId = parseInt(clientId);
      clientId = _.isNaN(clientId) ? null : clientId;
      this.options = _.extend({}, 
        _.omit((this.options || {}), "id", "code", "clientId", "from", "to", "order", "rows"), 
        {id:id, code:code, clientId:clientId, from:from, to:to}
      );
      var self = this;
      this.start().done(function() {
        // Mi assicuro che siano tutti deselezionati
        self.options.orders.each(function(order) {
          order.deselect();
        });
        if (self.options.id) {
          // seleziono l"ordine dell"url
          var order = self.options.orders.find({id:id});
          if (order) {
            order.select();
          }
        }

        var show = function() {
          self.setupRegions(self._layout);
          if (self.options.tab === "estimates") {
            self.showEstimatesTab();
          } else {
            self.showOrdersTab();
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
      this.options = _.omit(this.options, "orders", "estimates");
      WMS.trigger("clients:orders:list", args.model.attributes);
    }
    
    /**
     * Drop down dell"ordine. 
     * Se ho selezionato un ordine, aggiunge le righe selezionate a tale ordine, altrimenti
     * ne crea uno nuovo.
     */
  , dropOrder: function() {
      var klass = WMS.Models.ClientOrder;
      if (klass.canCreate()) {
        var client = null
          , ids = [];

        // cerco i preventivi che hanno almeno una riga selezionata
        var estimates = this.options.estimates.getSelected();
        if (estimates.length === 0) {
          WMS.showError("Selezionare almeno una riga.");
          return;
        }

        // ottengo la lista degli id dei clienti associati ai preventivi
        var clientIds = _.uniq(_.map(estimates, function(estimate) { 
          return estimate.attributes.clientId; 
        }));

        if (clientIds.length > 1) {
          WMS.showError("Tutti i preventivi devono essere associati allo stesso cliente.");
          return;
        }
        var clientId = clientIds[0];

        // ottengo la lista degli id delle commesse associate ai preventivi
        // NB: filtro le commissionId == null
        var commissionIds = _.compact(_.uniq(_.map(estimates, function(estimate) {
          return estimate.attributes.commissionId;
        })));

        if (commissionIds.length > 1) {
          WMS.showError("Tutti i preventivi devono essere associati alla stessa commessa.");
          return;
        }
        var commissionId = commissionIds.length === 1 ? commissionIds[0] : null;

        // recupero la lista delle righe selezionate
        var rows = this.options.estimates.getSelectedRows();

        // tengo solo gli id delle righe
        var ids = _.map(rows, function(row) { return row.attributes.id; });

        if (this.options.id) {
          // ho un preventivo selezionato
          if (clientId !== this.options.order.get("clientId")) {
            // il cliente delle righe selezionate non corrispondono col cliente dell"ordine
            var msg = "Attenzione! Le righe selezionate sono associate ad un cliente diverso da quello " +
              "dell'ordine.\nCreo un nuovo ordine con tali righe?";
            if (confirm(msg)) {
              this._createOrderWithRows(clientId, commissionId, ids);
            }
          } else if (commissionId && commissionId !== this.options.order.get("commissionId")) {
            var msg = "Attenzione! Le righe selezionate sono associate ad una commessa diversa da quella " +
              "dell'ordine.\nCreo un nuovo ordine con tali righe?";
            if (confirm(msg)) {
              this._createOrderWithRows(clientId, commissionId, ids);
            }
          } else {
            var msg = "Aggiungo le righe all'ordine " + this.options.order + "?";
            if (confirm(msg)) {
              this._addRowsToOrder(this.options.id, ids);
            }
          }
        } else {
          var msg = "Nessun ordine selezionato\nCreo un nuovo ordine con le righe selezionate?";
          if (confirm(msg)) {
            this._createOrderWithRows(clientId, commissionId, ids);
          }
        }
      } else {
        WMS.showError("Operazione non consentita!");
      }
    },
    
    _createOrderWithRows: function(clientId, commissionId, rowIds) {
      var self = this;
      var dropSuccess = function(order) {
        self.options.id = order.get("id");
        WMS.showSuccess("Ordine " + order + " creato.");
        WMS.trigger("clients:orders:list", _.pick(self.options, "id", "code", "clientId", "from", "to"));
      };
      var dropFail = function(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          WMS.showError(xhr.responseJSON.error);
        } else {
          WMS.showError("Errore creando l'ordine.");
        }
      };

      if (commissionId) {
        WMS.request("get:client:order:drop", {
          commissionId: commissionId
        , rows: rowIds
        }).then(dropSuccess).fail(dropFail);
      } else {
        // devo recuperare la commessa
        var view = new Views.SelectCommission({
          clientId: clientId
        , saveHandler: function(model, view) {
            var commissionId = model.get("commissionId");
            view.trigger("close");
            WMS.request("get:client:order:drop", {
              commissionId: commissionId
            , rows: rowIds
            }).then(dropSuccess).fail(dropFail);
          }
        });
        WMS.showModal(view);
      }
    }

  , _addRowsToOrder: function(orderId, rowIds) {
      var self = this;
      WMS.request("get:client:order:drop", {id:orderId, rows:rowIds})
        .then(function(order) {
          self.options = _.omit(self.options, "estimates", "rows");
          WMS.showSuccess("Ordine " + order + " aggiornato.");
          self.listOrders(
            self.options.id
          , self.options.code
          , self.options.clientId
          , self.options.from
          , self.options.to
          );
        })
        .fail(function(xhr) {
          if (xhr.responseJSON && xhr.responseJSON.error) {
            WMS.showError(xhr.responseJSON.error);
          } else {
            WMS.showError("Errore aggiornando l'ordine.");
          }
        });
    },

    selectOrder: function(args) {
      var order = args.model;
      if (order.canRead()) {
        if (order.get("id") === this.options.id) return;
        this.options = _.omit(this.options, "order", "rows");
        WMS.trigger("clients:orders:list", _.extend(this.options, {id: order.get("id")}));
      }
    },

    /**
     * Deseleziono un ordine.
     */
    unselectOrder: function() {
      if (this.options.id === undefined) return;
      // rimuovo i riferimenti all"ordine
      this.options = _.omit(this.options, "id", "order", "rows");
      WMS.trigger("clients:orders:list", this.options);
    },

    selectEstimate: function(view) {
      view.model.getRows().then(function(rows) {
        rows.multiSelect();
        // seleziono solo le righe non accettate
        rows.selectAll({accepted: false});
      });
    }

  , unselectEstimate: function(view) {
      view.model.getRows().then(function(rows) {
        rows.multiSelect();
        rows.selectNone();
      });
    }

  , showOrdersTab: function() {
      this.options.tab = "orders";
      this._panel.setActiveTab("orders");
      this._panel.hideDropButton();
      this.setupRegions(this._layout, [this._ordersRegion]);
    },
    
    showEstimatesTab: function() {
      this.options.tab = "estimates";
      this._panel.setActiveTab("estimates");
      this._panel.showDropButton();
      this.setupRegions(this._layout, [this._estimatesRegion]);
    },

    addOrderRow: function(args) {
      var klass = WMS.Models.ClientOrderRow;
      if (klass.canCreate()) {
        var model = new klass({ 
            orderId: args.model.get("id") 
          })
          , view = new Orders.Views.NewRow({ model: model });
        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    },

    editOrderRow: function(view, args) {
      var row = args.model;
      if (row.canUpdate()) {
        var view = new Orders.Views.EditRow({ model: row });

        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    },

    deleteOrderRow: function(childView, args) {
      var model = args.model;
      if (model.canDestroy()) {
        if (confirm("Eliminare la riga dell'ordine?")) {
          model.destroy();
          WMS.showSuccess("Riga dell'ordine '" + this.options.order + "' eliminata.");
        }
      }
    }
  });
});