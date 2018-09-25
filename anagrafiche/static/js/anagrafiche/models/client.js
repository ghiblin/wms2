WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  Models.ClientAddress = Models.Address.extend({
    urlRoot: "/api/v1/indirizzo/", 

    defaults: _.extend({
      clientId: null
    }, Models.Address.prototype.defaults),

    maps: _.union([
      { local: "clientId",  remote: "entita"    }
    ], Models.Address.prototype.maps),

    validation: _.extend({
      clientId: { required: true }
    }, Models.Address.prototype.validation)

  , getClients: WMS.getClients
  }, {
    modelName: "client:address"
  });

  Models.ClientAddresses = Backbone.Collection.extend({
    url: "/api/v1/indirizzo/"
  , model: Models.ClientAddress
  });

  Models.ClientContact = Models.Contact.extend({
    urlRoot: "/api/v1/contatto/", 

    defaults: _.extend({
      clientId: null
    }, Models.Contact.prototype.defaults),

    maps: _.union([
      { local: "clientId",  remote: "entita"    }
    ], Models.Contact.prototype.maps),


    validation: _.extend({
      clientId: { required: true }
    }, Models.Contact.prototype.validation)

  , getClients: WMS.getClients
  }, {
    modelName: "client:contact"
  });

  Models.ClientContacts = Backbone.Collection.extend({
    url: "/api/v1/contatto/"
  , model: Models.ClientContact
  });

  Models.ClientBankDatum = Models.BankDatum.extend({
    urlRoot: "/api/v1/contoCorrente/",

    defaults: _.extend({
      clientId: null
    }, Models.BankDatum.prototype.defaults),

    maps: _.union([
      { local: "clientId",  remote: "entita"    }
    ], Models.BankDatum.prototype.maps),

    validation: _.extend({
      clientId: { required: true }
    }, Models.BankDatum.prototype.validation),

    getClients: WMS.getClients
  }, {
    modelName: "client:bankDatum"
  });

  Models.ClientBankData = Backbone.Collection.extend({
    url: "/api/v1/contoCorrente/",
    model: Models.ClientBankDatum,
    
    initialize: function() {
      Backbone.Collection.prototype.initialize.apply(this, arguments);
      this.on('change', this.onChange, this);
    },

    onChange: function(model) {
      if (model.get('main')) {
        this
          .without(model)
          .forEach(function(bankDatum) {
            bankDatum.set('main', false);
          });
      }
    }
  });

  Models.Client = Models.Entity.extend({
    urlRoot: '/api/v1/cliente/', 

    defaults: _.extend({}, Models.Entity.prototype.defaults, {
      addresses     : new Models.ClientAddresses(),
      contacts      : new Models.ClientContacts(),
      bankData      : new Models.ClientBankData(),
      applyTo       : "",
      paymentTypeId : null,
      cashOrder     : 0,
      foreigner     : false,
      carrier       : false
    }),

    maps: _.union([
      { local: 'paymentTypeId', remote: 'pagamento'               },
      { local: 'paymentType',   remote: 'pagamento_label'         },
      { local: "applyTo",       remote: "persona_di_riferimento"  },
      { local: 'cashOrder',     remote: 'costo_riba'              },
      { local: 'foreigner',     remote: 'straniero'               },
      { local: "carrier",       remote: "vettore"                 }
    ], Models.Entity.prototype.maps),

    validation: _.extend({}, Models.Entity.prototype.validation, {
      taxCode: {
        required: function(value, attr, computedState) {
          return computedState.typeId === 'F' && !computedState.foreigner;
        }
      },
      cashOrder     : { min: 0 },
      paymentTypeId : { required: true }
    }), 

    parse: function(resp, options) {
      var resp = Backbone.Model.prototype.parse.apply(this, arguments)
        , id = resp.id;

      var addresses = [];
      _.each(resp.addresses, function(address) {
        addresses.push(new Models.ClientAddress(Models.ClientAddress.prototype.parse(address)));
      });
      resp.addresses = new Models.ClientAddresses(addresses);
      resp.addresses.attr({clientId: id});
      
      var contacts = [];
      _.each(resp.contacts, function(contact) {
        contacts.push(new Models.ClientContact(Models.ClientContact.prototype.parse(contact)));
      });
      resp.contacts = new Models.ClientContacts(contacts);
      resp.contacts.attr({clientId: id});

      var bankData = [];
      _.each(resp.bankData, function(data) {
        bankData.push(new Models.ClientBankDatum(Models.ClientBankDatum.prototype.parse(data)));
      });
      resp.bankData = new Models.ClientBankData(bankData);
      resp.bankData.attr({clientId: id});

      return resp;
    }, 

    getPaymentTypes: WMS.getPaymentTypes, 

    isForeigner: function() {
      return this.get("foreigner");
    }
  }, {
    modelName: 'client'
  });
  
  Models.Clients = Models.EntityCollection.extend({
    url: '/api/v1/cliente/'
  , model: Models.Client
  });
  
  WMS.reqres.setHandler('get:client:list', function(options) {
    return Models.__fetchCollection('clientList', Models.Clients, options, 'name');
  });
  
  WMS.commands.setHandler('reset:client:list', function() {
    Models.__resetCollection('clientList');
    WMS.trigger('client:list:reset');
  });
  
  WMS.reqres.setHandler('get:client', function(id, options) {
    return Models.__fetchModel('client', Models.Client, id, options);
  });

  WMS.reqres.setHandler("get:client:address:list", function(options) {
    return Models.__fetchCollection("clientAddressList", Models.ClientAddresses, options);
  });

  WMS.commands.setHandler("reset:client:address:list", function() {
    Models.__resetCollection("clientAddressList");
  })
});