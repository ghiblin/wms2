WMS.module('Suppliers.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = _.extend({}, WMS.Common.Views, Show.Views);

  Show.Controller = Marionette.Controller.extend({
    regions: [{
        name: "titleRegion"
      , View: Views.Title
      , options: {
          title: "@supplier.name"
        }
      }, {
        name: 'detailsRegion'
      , View: Views.EntityDetails
      , options: {
          model: "@supplier" 
        }
      }, {
        name: "addressesRegion"
      , View: Views.Addresses
      , collection: "@supplier.addresses"
      }, {
        name: "contactsRegion"
      , View: Views.Contacts
      , options: {
          collection: "@supplier.contacts"
        }
      }, {
        name: "bankDataRegion"
      , View: Views.BankData
      , options: {
          collection: "@supplier.bankData"
        }
      }]

  , prefetchOptions: [
      { request: 'get:supplier', name: 'supplier', options: ['id'] }
    ]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "supplier:updated", function(supplier) {
        var model = self.options.supplier;
        if (model.get("id") === supplier.get("id")) {
          model.set(supplier.attributes);
          self._layout.getRegion("titleRegion").currentView.model.set({title: model.get("name") });
        }
      });

      this.listenTo(WMS.vent, "supplier:address:created", function(address) {
        self.options.supplier.get("addresses").add(address);
      });
      this.listenTo(WMS.vent, "supplier:address:updated", function(address) {
        var model = self.options.supplier.get("addresses").find({id: address.get("id")});
        model && model.set(address.attributes);
      });

      this.listenTo(WMS.vent, "supplier:contact:created", function(contact) {
        self.options.supplier.get("contacts").add(contact);
      });
      this.listenTo(WMS.vent, "supplier:contact:updated", function(contact) {
        var model = self.options.supplier.get("contacts").find({id: contact.get("id")});
        model && model.set(contact.attributes);
      });

      this.listenTo(WMS.vent, "supplier:bankDatum:created", function(bankDatum) {
        self.options.supplier.get("bankData").add(bankDatum);
      });
      this.listenTo(WMS.vent, "supplier:bankDatum:updated", function(bankDatum) {
        var model = self.options.supplier.get("bankData").find({id: bankDatum.get("id")});
        model && model.set(bankDatum.attributes);
      });
    }

  , showSupplier: function(id) {
      this.options.id = id;
      
      var self = this;
      this.start().then(function() {
        var supplier = self.options.supplier;
        if (supplier !== undefined) {
          var layout = self._layout = new Views.EntityLayout({ entity:supplier });
          layout.on('show', function() {
            self.setupRegions(layout);
          });
        } else {
          self._layout = new Views.Error({ message: "Fornitore non trovato." });
        }
        WMS.mainRegion.show(self._layout);
      });
    }
  });
});