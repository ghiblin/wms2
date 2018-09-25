WMS.module('Owner.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views;

  Show.Controller = Marionette.Controller.extend({
    regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "@owner.name"
        }
      }, {
        name: "detailsRegion"
      , View: Views.EntityDetails
      , options: {
          model: "@owner"
        }
      }, {
        name: "addressesRegion"
      , View: Views.Addresses
      , options: {
          collection: "@owner.addresses"
        }
      }, {
        name: "contactsRegion"
      , View: Views.Contacts
      , options: {
          collection: "@owner.contacts"
        }
      }, {
        name: "bankDataRegion"
      , View: Views.BankData
      , options: {
          collection: "@owner.bankData"
        }
      }]
  , prefetchOptions: [
      { request: 'get:owner', name: 'owner' }
    ]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "owner:updated", function(owner) {
        self.options.owner.set(owner.attributes);
        self._layout.getRegion("titleRegion").currentView.model.set({ title:owner.get("name") });
      });

      this.listenTo(WMS.vent, "owner:address:created", function(address) {
        self.options.owner.get("addresses").add(address);
      });
      this.listenTo(WMS.vent, "owner:address:updated", function(address) {
        var model = self.options.owner.get("addresses").find({id: address.get("id")});
        if (model) {
          model.set(address.attributes);
        }
      });

      this.listenTo(WMS.vent, "owner:contact:created", function(contact) {
        self.options.owner.get("contacts").add(contact);
      });
      this.listenTo(WMS.vent, "owner:contact:updated", function(contact) {
        var model = self.options.owner.get("contacts").find({id: contact.get("id")});
        if (model) {
          model.set(contact.attributes);
        }
      });

      this.listenTo(WMS.vent, "owner:bankDatum:created", function(bankDatum) {
        self.options.owner.get("bankData").add(bankDatum);
      });
      this.listenTo(WMS.vent, "owner:bankDatum:updated", function(bankDatum) {
        var model = self.options.owner.get("bankData").find({id: bankDatum.get("id")});
        if (model) {
          model.set(bankDatum.attributes);
        }
      });
    }

  , showOwner: function() {
      var self = this;
      this.start().then(function() {
        var owner = self.options.owner;
        if (owner !== undefined) {
          var layout = self._layout = new Views.EntityLayout({ entity:owner });
          layout.on('show', function() {
            self.setupRegions(layout);
          });
        } else {
          self._layout = new Views.Error({ message: "Proprietario non trovato." });
        }
        WMS.mainRegion.show(self._layout);
      });
    }
  });
});