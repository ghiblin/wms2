WMS.module('Suppliers.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views;

  List.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: 'get:supplier:list', name: 'suppliers' }
    ],

    regions: [{
      name: "titleRegion",
      View: Views.Title,
      options: {
        title: "Fornitori"
      }
    }, { 
      name: 'panelRegion',
      viewName: '_panel',
      View: List.Views.Panel,
      options: {
        criterion: "@criterion"
      },
      events: {
        'suppliers:new'     : 'newSupplier',
        'suppliers:filter'  : 'filterSupplier'
      }
    }, {
      name: 'listRegion',
      viewName: '_suppliers',
      View: List.Views.Suppliers,
      options: {
        collection: "@suppliers",
        criterion: "@criterion"
      },
      events: {
        'supplier:selected' : 'selectSupplier'
      }
    }],

    initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "supplier:created", function(supplier) {
        self.options.suppliers.add(supplier);
      });

      this.listenTo(WMS.vent, "supplier:updated", function(supplier) {
        var model = self.options.suppliers.find({id: supplier.get('id')});
        if (model) {
          model.set(supplier.attributes);
        }
      });
    },

    listSuppliers: function(criterion) {
      this.options.criterion = criterion;

      var self = this;
      this.start().then(function() {
        if (self._layout && !self._layout.isDestroyed) {
          self.setupRegions(self._layout);
        } else {
          self._layout = new Views.FilterLayout();
          
          self._layout.on('show', function() {
            self.setupRegions(self._layout);
          });
          
          WMS.mainRegion.show(self._layout);
        }
      });
    },

    filterSupplier: function(criterion) {
      WMS.trigger("suppliers:filter", criterion);
    },

    newSupplier: function() {
      var klass = WMS.Models.Supplier;
      if (klass.canCreate()) {
        var supplier = new klass()
          , view = new Views.New({ model: supplier });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    },

    selectSupplier: function(childView) {
      var supplier = childView.model;
      if (supplier.canRead()) {
        WMS.trigger("suppliers:show", supplier.get("id"));
      }
    }
  });
});