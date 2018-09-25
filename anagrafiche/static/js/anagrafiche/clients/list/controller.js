WMS.module('Clients.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views;

	List.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: 'get:client:list', name: 'clients' }
    ],

    regions: [{
      name    : "titleRegion",
      View    : Views.Title,
      options : {
        title: "Clienti"
      }
    }, { 
      name    : 'panelRegion',
      viewName: '_panel',
      View    : Views.Panel,
      options : {
        criterion: "@criterion"
      },
      events  : {
        "clients:new"     : 'newClient'
      , 'clients:filter'  : 'filterClient'
      }
    }, {
      name    : 'listRegion',
      viewName: '_clients',
      View    : Views.Clients,
      options: {
        criterion : "@criterion",
        collection: "@clients"
      },
      events  : {
        'client:selected' : 'selectClient'
      }
    }],

    initialize: function() {
      var self = this;
      this.listenTo(WMS.vent, "client:updated", function(client) {
        var model = self.options.clients.find({id: client.get('id')});
        if (model) {
          model.set(client.attributes);
        }
      });
    },

    listClients: function(criterion) {
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

    filterClient: function(criterion) {
      WMS.trigger("clients:filter", criterion);
    },

    newClient: function() {
      var klass = WMS.Models.Client;
      if (klass.canCreate()) {
        var client = new klass()
          , view = new Views.New({ model: client });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    },

    selectClient: function(childView, args) {
      var model = childView.model;
      if (model.canRead()) {
        WMS.trigger("clients:show", model.get("id"));
      } else {
        console.log("TBD: manca rifiuto selezione");
      }
    }
  });
});