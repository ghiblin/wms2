WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  Models.OwnerAddress = Models.Address.extend({
    urlRoot: "/api/v1/indirizzo/", 

    maps: _.union([
      { local: "ownerId",  remote: "entita"    }
    ], Models.Address.prototype.maps),

    defaults: _.extend({
      ownerId: null
    }, Models.Address.prototype.defaults), 

    validation: _.extend({
      ownerId: { required: true }
    }, Models.Address.prototype.validation), 

    getOwners: WMS.getOwners
  }, {
    modelName: "owner:address"
  });

  Models.OwnerAddresses = Backbone.Collection.extend({
    url: "/api/v1/indirizzo/", 
    model: Models.OwnerAddress
  });

  Models.OwnerContact = Models.Contact.extend({
    urlRoot: "/api/v1/contatto/", 

    defaults: _.extend({
      ownerId: null
    }, Models.Contact.prototype.defaults), 

    maps: _.union([
      { local: "ownerId",  remote: "entita"    }
    ], Models.Contact.prototype.maps),

    validation: _.extend({
      ownerId: { required: true }
    }, Models.Contact.prototype.validation)

  , getOwners: WMS.getOwners
  }, {
    modelName: "owner:contact"
  });

  Models.OwnerContacts = Backbone.Collection.extend({
    url: "/api/v1/contatto/", 
    model: Models.OwnerContact
  });

  Models.OwnerBankDatum = Models.BankDatum.extend({
    urlRoot: "/api/v1/contoCorrente/", 

    defaults: _.extend({
      ownerId: null
    }, Models.BankDatum.prototype.defaults), 

    maps: _.union([
      { local: "ownerId",  remote: "entita"    }
    ], Models.BankDatum.prototype.maps),

    validation: _.extend({
      ownerId: { required: true }
    }, Models.BankDatum.prototype.validation), 

    getOwners: WMS.getOwners
  }, {
    modelName: "owner:bankDatum"
  });

  Models.OwnerBankData = Backbone.Collection.extend({
    url: "/api/v1/contoCorrente/", 
    model: Models.OwnerBankDatum
  });

  Models.Owner = Models.Entity.extend({
    urlRoot: '/api/v1/proprietario/', 

    defaults: _.extend({}, Models.Entity.prototype.defaults, {
      addresses     : new Models.OwnerAddresses(),
      contacts      : new Models.OwnerContacts(),
      bankData      : new Models.OwnerBankData()
    }), 

    parse: function(resp, options) {
      var resp = Backbone.Model.prototype.parse.apply(this, arguments)
        , id = resp.id;

      var addresses = [];
      _.each(resp.addresses, function(address) {
        addresses.push(new Models.OwnerAddress(Models.OwnerAddress.prototype.parse(address)));
      });
      resp.addresses = new Models.OwnerAddresses(addresses);
      resp.addresses.attr({ownerId: id});
      
      var contacts = [];
      _.each(resp.contacts, function(contact) {
        contacts.push(new Models.OwnerContact(Models.OwnerContact.prototype.parse(contact)));
      });
      resp.contacts = new Models.OwnerContacts(contacts);
      resp.contacts.attr({ownerId: id});

      var bankData = [];
      _.each(resp.bankData, function(data) {
        bankData.push(new Models.OwnerBankDatum(Models.OwnerBankDatum.prototype.parse(data)));
      });
      resp.bankData = new Models.OwnerBankData(bankData);
      resp.bankData.attr({ownerId: id});

      return resp;
    }
  }, {
    modelName: "owner"
  });

  Models.Owners = Models.EntityCollection.extend({
    url: "/api/v1/proprietario/"
  , model: Models.Owner
  });
  
  WMS.reqres.setHandler('get:owner', function() {
    return Models.__fetchModel('owner', Models.Owner, {});
  });

  WMS.reqres.setHandler("get:owner:list", function() {
    return Models.__fetchCollection('ownerList', Models.Owners);
  });
});