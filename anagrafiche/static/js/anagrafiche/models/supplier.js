WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  Models.SupplierAddress = Models.Address.extend({
    urlRoot: "/api/v1/indirizzo/",

    maps: _.union([
      { local: "supplierId",  remote: "entita"    }
    ], Models.Address.prototype.maps),

    defaults: _.extend({
      supplierId: null
    }, Models.Address.prototype.defaults), 

    validation: _.extend({
      supplierId: { required: true }
    }, Models.Address.prototype.validation),

    getSuppliers: WMS.getSuppliers
  }, {
    modelName: "supplier:address"
  });

  Models.SupplierAddresses = Backbone.Collection.extend({
    url: "/api/v1/indirizzo/"
  , model: Models.SupplierAddress
  });

  Models.SupplierContact = Models.Contact.extend({
    urlRoot: "/api/v1/contatto/", 

    maps: _.union([
      { local: "supplierId",  remote: "entita"    }
    ], Models.Contact.prototype.maps),

    defaults: _.extend({
      supplierId: null
    }, Models.Contact.prototype.defaults), 

    validation: _.extend({
      supplierId: { required: true }
    }, Models.Contact.prototype.validation), 

    getSuppliers: WMS.getSuppliers
  }, {
    modelName: "supplier:contact"
  });

  Models.SupplierContacts = Backbone.Collection.extend({
    url: "/api/v1/contatto/", 
    model: Models.SupplierContact
  });

  Models.SupplierBankDatum = Models.BankDatum.extend({
    urlRoot: "/api/v1/contoCorrente/", 

    maps: _.union([
      { local: "supplierId",  remote: "entita"    }
    ], Models.BankDatum.prototype.maps),

    defaults: _.extend({
      supplierId: null
    }, Models.BankDatum.prototype.defaults), 

    validation: _.extend({
      supplierId: { required: true }
    }, Models.BankDatum.prototype.validation), 

    getSuppliers: WMS.getSuppliers
  }, {
    modelName: "supplier:bankDatum"
  });

  Models.SupplierBankData = Backbone.Collection.extend({
    url: "/api/v1/contoCorrente/", 
    model: Models.SupplierBankDatum
  });

  Models.Supplier = Models.Entity.extend({
    urlRoot: '/api/v1/fornitore/', 

    defaults: _.extend({}, Models.Entity.prototype.defaults, {
      addresses     : new Models.SupplierAddresses(),
      contacts      : new Models.SupplierContacts(),
      bankData      : new Models.SupplierBankData(),
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
        addresses.push(new Models.SupplierAddress(Models.SupplierAddress.prototype.parse(address)));
      });
      resp.addresses = new Models.SupplierAddresses(addresses);
      resp.addresses.attr({supplierId: id});
      
      var contacts = [];
      _.each(resp.contacts, function(contact) {
        contacts.push(new Models.SupplierContact(Models.SupplierContact.prototype.parse(contact)));
      });
      resp.contacts = new Models.SupplierContacts(contacts);
      resp.contacts.attr({supplierId: id});

      var bankData = [];
      _.each(resp.bankData, function(data) {
        bankData.push(new Models.SupplierBankDatum(Models.SupplierBankDatum.prototype.parse(data)));
      });
      resp.bankData = new Models.SupplierBankData(bankData);
      resp.bankData.attr({supplierId: id});

      return resp;
    }, 

    getPaymentTypes: WMS.getPaymentTypes, 

    isForeigner: function() {
      return this.get("foreigner");
    }
  }, {
    modelName: "supplier"
  });
  
  Models.Suppliers = Models.EntityCollection.extend({
    url: '/api/v1/fornitore/', 
    model: Models.Supplier
  });

  WMS.reqres.setHandler('get:supplier:list', function(options) {
    return Models.__fetchCollection('supplierList', Models.Suppliers, options);
  });

  WMS.reqres.setHandler("get:supplier:carrier:list", function() {
    return Models.__fetchCollection("supplierList", Models.Suppliers, {where: {carrier:true}});
  });
  
  WMS.commands.setHandler('reset:supplier:list', function() {
    Models.__resetCollection('supplierList');
    WMS.trigger('supplier:list:reset');
  });
  
  WMS.reqres.setHandler('get:supplier', function(id, options) {
    return Models.__fetchModel('supplier', Models.Supplier, id, options);
  });
});