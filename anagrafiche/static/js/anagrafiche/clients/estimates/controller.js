WMS.module('Clients.Estimates', function(Estimates, WMS, Backbone, Marionette, $, _) {
  var Views = Estimates.Views;

 	Estimates.Controller = Marionette.Controller.extend({
    Layout: Estimates.Views.Layout,
    prefetchOptions: [
      { request: 'get:client:estimate:list', name: 'estimates', options: ['code', 'clientId', 'from', 'to'] },
      { request: 'get:client:estimate', name: 'estimate', options: ['id'] },
      { request: 'get:client:estimate:rows', name: 'rows', options: ['id'] },
    ],
    
    regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "Preventivi Cliente"
        }
      }, {
        name: 'filterRegion'
      , View: Views.FilterView
      , options : {
          code    : "@code"
        , clientId: "@clientId"
        , from    : "@from"
        , to      : "@to"
        }
      , events: {
          'search': 'search'
        }
      }, {
        name: 'panelRegion'
      , View: Views.Panel
      }, {
        name: 'masterRegion'
      , css: { height: '286px' }
      , className: 'scrollable'
      , stickyHeaders: true
      , viewName: '_estimates'
      , View: Views.Estimates
      , options: {
          collection: "@estimates"
        }
      , events: {
          'client:estimate:selected': 'selectEstimate'
        , 'client:estimate:unselected': 'unselectEstimate'
        }
      }, {
        name: "detailsRegion"
      , viewName: "_details"
      , View: Views.Details
      , options: {
          model: "@estimate"
        }
      , events: {
          'client:estimate:row:add': 'addEstimateRow',
          'client:estimate:clone'  : 'cloneEstimate'
        }
      }, {
        name: 'rowsRegion'
      , viewName: '_rows'
      , View: Views.Rows
      , options: {
          collection: "@rows"
        }
      }
    ]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "client:estimate:created", function(estimate) {
        var options = _.pick(self.options, "code", "clientId", "from", "to");
        options.id = estimate.get("id");
        WMS.trigger('clients:estimates:list', options);
      });

      this.listenTo(WMS.vent, "client:estimate:updated", function(estimate) {
        // Aggiorno il preventivo presente nella lista
        var model = self.options.estimates.find({ id:estimate.get("id") });
        if (model) {
          model.set(estimate.attributes);
        }

        // Aggiorno eventuale preventivo nella vista di dettaglio
        if (self.options.id === estimate.get("id")) {
          self.options.estimate.set(estimate.attributes);
        }
      });

      this.listenTo(WMS.vent, "client:estimate:row:created", function(row) {
        self.options.rows.add(row);
      });

      this.listenTo(WMS.vent, "client:estimate:row:updated", function(row) {
        var model = self.options.rows.find({ id:row.get("id") });
        if (model) {
          model.set(row.attributes);
        }
      });
    }

  , search: function(args) {
      this.options = _.omit(this.options, 'estimates');
      WMS.trigger('clients:estimates:list', args.model.attributes);
    }

  , selectEstimate: function(args) {
      var estimate = args.model;
      if (estimate.canRead()) {
        // ignora il select del preventivo se ha lo stesso id della route
        if (estimate.get('id') === this.options.id) return;
        this.options = _.omit(this.options, 'estimate', 'rows');
        WMS.trigger('clients:estimates:list', _.extend(this.options, {id: estimate.get('id')}));
      } else {
        console.log("TBD: manca rifiuto selezione");
      }
    }

    /**
     * Deseleziona un preventivo.
     */
  , unselectEstimate: function(args) {
      // se non ho un id, non ho nulla da deselezionare
      if (this.options.id === undefined) return;
      var id;
      if (args && args.model) {
        id = args.model.get('id');
      }
      // se l'id del modello è diverso da quello delle opzioni, è un event 
      // errato proveniente dalla view.
      if (id !== this.options.id) return;

      // rimuovo id dalla lista delle opzioni, assieme ai dettagli del preventivo.
      this.options = _.omit(this.options, 'id', 'estimate', 'rows');
      WMS.trigger('clients:estimates:list', this.options);
    }

  , addEstimateRow: function(args) {
      var klass = WMS.Models.ClientEstimateRow;
      if (klass.canCreate()) {
        var model = new klass({ estimateId: args.model.get('id') })
          , view = new Estimates.Views.NewRow({ model: model });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , reset:function() {
      this.options = _.omit(this.options, 'estimate', 'estimates', 'rows');
      if (this._layout && !this._layout.isDestroyed) {
        this._layout.destroy();
      }
    }

  , listEstimates: function(id, code, clientId, from, to) {
      this.options = _.extend({}, 
        _.omit((this.options || {}), 'id', 'estimate', 'rows', 'code', 'clientId', 'from', 'to'), 
        {id:id, code:code, clientId:clientId, from:from, to:to}
      );
      this.start().done(_.bind(function() {
        if (this.options.id) {
          // this.options.id è string --> converto in integer
          var id = this.options.id = parseInt(this.options.id);
        }
        // Mi assicuro che siano tutti deselezionati
        this.options.estimates.each(function(estimate) {
          if (estimate.get('id') !== id) {
            estimate.deselect();
          }
        });
          
        if (id) {
          // seleziono l'ordine dell'url
          var estimate = this.options.estimates.find({id:id});
          if (estimate) {
            estimate.select();
          }
        }

        if (this._layout !== undefined && !this._layout.isDestroyed) {
          this.setupRegions(this._layout);
        } else {
          this._layout = new this.Layout();
          this._layout.on('show', _.bind(function() {
            this.setupRegions(this._layout);
          }, this));
          WMS.getRegion('mainRegion').show(this._layout);
        }
      }, this));
    },

    cloneEstimate: function(args) {
      var self  = this
        , model = args.model;

      var cloneSuccess = function(estimate) {
        self.options.id = estimate.get("id");
        WMS.showSuccess("Preventivo Clienti " + estimate + " clonato.");
        WMS.trigger("clients:estimates:list", _.pick(self.options, "id", "code", "clientId", "from", "to"));
      }

      var cloneFail = function(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          WMS.showError(xhr.responseJSON.error);
        } else {
          WMS.showError("Errore clonando il preventivo.");
        }
      };

      if (confirm("Clonare il preventivo '" + model + "'?")) {
        WMS.request("clone:client:estimate", {id: model.get('id')})
          .then(cloneSuccess)
          .fail(cloneFail);
      }
    }
  });
});