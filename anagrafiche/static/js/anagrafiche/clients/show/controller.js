WMS.module('Clients.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views;

	Show.Controller = Marionette.Controller.extend({
    regions: [{
        name: "titleRegion",
        View: Views.Title,
        options: {
          title: "@client.name"
        }
      }, {
        name: "detailsRegion", 
        View: Views.EntityDetails,
        options: {
          model: "@client"
      }
      }, {
        name: "addressesRegion",
        View: Views.Addresses,
        options: {
          collection: "@client.addresses"
        }
      }, {
        name: "contactsRegion",
        View: Views.Contacts,
        options: {
          collection: "@client.contacts"
        }
      }, {
        name: "bankDataRegion",
        View: Views.BankData,
        options: {
          collection: "@client.bankData"
        }
      }],

    prefetchOptions: [
      { request: 'get:client', name: 'client', options: ['id'] }
    ],

    initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "client:updated", function(client) {
        if (client.get("id") === self.options.id) {
          self.options.client.set(client.attributes);
          var view = self._layout.getRegion("titleRegion").currentView;
          if (view) {
            view.model.set({title: client.get("name") });
            view.render();
          }
        }
      });

      this.listenTo(WMS.vent, "client:address:created", function(address) {
        if (address.get("clientId") === self.options.id) {
          self.options.client
            .get("addresses")
            .add(address);
        }
      });

      this.listenTo(WMS.vent, 'client:address:updated', function(address) {
        if (address.get('clientId') === self.options.id) {
          self.options.client
            .get('address')
            .find({id: address.get('id')})
            .set(address.attributes);
        }
      });

      this.listenTo(WMS.vent, "client:contact:created", function(contact) {
        if (contact.get("clientId") === self.options.id) {
          self.options.client
            .get("contacts")
            .add(contact);
        }
      });

      this.listenTo(WMS.vent, 'client:contact:updated', function(contact) {
        if (contact.get('clientId') === self.options.id) {
          self.options.client
            .get('contacts')
            .find({id: contact.get('id')})
            .set(contact.attributes);
        }
      });

      this.listenTo(WMS.vent, "client:bankDatum:created", function(bankDatum) {
        if (bankDatum.get("clientId") === self.options.id) {
          self.options.client
            .get("bankData")
            .add(bankDatum);
        }
      });

      this.listenTo(WMS.vent, 'client:bankDatum:updated', function(bankDatum) {
        if (bankDatum.get('clientId') === self.options.id) {
          self.options.client
            .get('bankData')
            .find({id: bankDatum.get('id')})
            .set(bankDatum.attributes);
        }
      });
    }, 

    showClient: function(id) {
      this.options.id = id;
      
      var self = this;
      this.start().then(function() {
        var client = self.options.client;
        if (client !== undefined) {
          var layout = self._layout = new Views.EntityLayout({ entity:client });
          layout.on('show', function() {
            self.setupRegions(layout);
          });
        } else {
          self._layout = new Views.Error({ message: "Cliente non trovato." });
        }
        WMS.mainRegion.show(self._layout);
      });
    }
  });
});