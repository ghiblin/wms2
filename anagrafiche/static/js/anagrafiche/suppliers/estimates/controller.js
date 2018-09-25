WMS.module('Suppliers.Estimates', function(Estimates, WMS, Backbone, Marionette, $, _) {
  var Views = Estimates.Views;

 	Estimates.Controller = Marionette.Controller.extend({
    Layout: Estimates.Views.Layout,
    prefetchOptions: [
      { request: 'get:supplier:estimate:list', name: 'estimates', options: ['code', 'supplierId', 'from', 'to'] },
      { request: 'get:supplier:estimate', name: 'estimate', options: ['id'] },
      { request: 'get:supplier:estimate:rows', name: 'rows', options: ['id'] },
    ],
    
    regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "Preventivi Fornitore"
        }
      }, {
        name: 'filterRegion'
      , View: Views.FilterView
      , options : {
          code    : "@code"
        , supplierId: "@supplierId"
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
          'supplier:estimate:selected': 'selectEstimate'
        , 'supplier:estimate:unselected': 'unselectEstimate'
        }
      }, {
        name: "detailsRegion"
      , viewName: "_details"
      , View: Views.Details
      , options: {
          model: "@estimate"
        }
      , events: {
          'supplier:estimate:row:add': 'addEstimateRow',
          'supplier:estimate:clone'  : 'cloneEstimate'
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

      this.listenTo(WMS.vent, "supplier:estimate:created", function(estimate) {
        var options = _.pick(self.options, "code", "supplierId", "from", "to");
        options.id = estimate.get("id");
        WMS.trigger('suppliers:estimates:list', options);
      });

      this.listenTo(WMS.vent, "supplier:estimate:updated", function(estimate) {
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

      this.listenTo(WMS.vent, "supplier:estimate:row:created", function(row) {
        self.options.rows.add(row);
      });

      this.listenTo(WMS.vent, "supplier:estimate:row:updated", function(row) {
        var model = self.options.rows.find({ id:row.get("id") });
        if (model) {
          model.set(row.attributes);
        }
      });
    }

  , search: function(args) {
      this.options = _.omit(this.options, 'estimates');
      WMS.trigger('suppliers:estimates:list', args.model.attributes);
    }

  , selectEstimate: function(args) {
      var estimate = args.model;
      if (estimate.canRead()) {
        // ignora il select del preventivo se ha lo stesso id della route
        if (estimate.get('id') === this.options.id) return;
        this.options = _.omit(this.options, 'estimate', 'rows');
        WMS.trigger('suppliers:estimates:list', _.extend(this.options, {id: estimate.get('id')}));
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
      WMS.trigger('suppliers:estimates:list', this.options);
    }

  , addEstimateRow: function(args) {
      var klass = WMS.Models.SupplierEstimateRow;
      if (klass.canCreate()) {
        var model = new klass({ estimateId: args.model.get('id') })
          , view = new Estimates.Views.NewRow({ model: model });
        
        view.on('save', function() {
          console.log('on NewRow save', arguments);
        })

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

  , listEstimates: function(id, code, supplierId, from, to) {
      this.options = _.extend({}, 
        _.omit((this.options || {}), 'id', 'estimate', 'rows', 'code', 'supplierId', 'from', 'to'), 
        {id:id, code:code, supplierId:supplierId, from:from, to:to}
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
        WMS.showSuccess("Preventivo Fornitori " + estimate + " clonato.");
        WMS.trigger("suppliers:estimates:list", _.pick(self.options, "id", "code", "supplierId", "from", "to"));
      }

      var cloneFail = function(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          WMS.showError(xhr.responseJSON.error);
        } else {
          WMS.showError("Errore clonando il preventivo.");
        }
      };

      if (confirm("Clonare il preventivo '" + model + "'?")) {
        WMS.request("clone:supplier:estimate", {id: model.get('id')})
          .then(cloneSuccess)
          .fail(cloneFail);
      }
    }
  });
});