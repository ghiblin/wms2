WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  Models.Address = Backbone.Model.extend({    
    defaults: {
      typeId      : null,
      line1       : "",
      line2       : "",
      city        : "",
      zip         : "",
      state       : "",
      country     : ""
    },

    maps: [
      { local: "typeId",    remote: "tipo"      },
      { local: "line1",     remote: "via1"      },
      { local: "line2",     remote: "via2"      },
      { local: "city",      remote: "citta"     },
      { local: "state",     remote: "provincia" },
      { local: "zip",       remote: "cap"       },
      { local: "country",   remote: "nazione"   }
    ],
    
    validation: {
      typeId      : { required: true },
      line1       : { required: true },
      city        : { required: true },
      zip         : { required: true },
      state       : { required: true },
      country     : { required: true }
    }, 

    getTypes: WMS.getAddressTypes, 

    toString: function() {
      var str = this.get("line1");
      if (this.get("line2")) {
        str += " " + this.get("line2");
      }
      str += " " + this.get("zip") + " " + this.get("city") + " (" + this.get("state") + ") " + this.get("country");
      return str;
    }
  });
  
  Models.Contact = Backbone.Model.extend({
    defaults: {
      typeId      : null,
      value       : "",
      note        : ""
    },

    maps: [
      { local: "typeId",    remote: "tipo"        },
      { local: "type",      remote: "tipo_label"  },
      { local: "value",     remote: "valore"      },
      { local: "note",      remote: "note"        }
    ],

    validation: {
      typeId      : { required: true },
      value       : { required: true }
    }, 

    getTypes: WMS.getContactTypes,

    toString: function() {
      return this.get("type") ? this.get("type") + ":" + this.get("value") : this.get("value");
    }
  });

  Models.BankDatum = Backbone.Model.extend({
    defaults: {
      bank        : "",
      branch      : "",
      holder      : "",
      iban        : "",
      swift       : "",
      foreigner   : false,
      main        : false
    },

    maps: [
      { local: "bank"     , remote: "nome_banca"    },
      { local: "branch"   , remote: "filiale"       },
      { local: "holder"   , remote: "intestatario"  },
      { local: "iban"     , remote: "iban"          },
      { local: "main"     , remote: "predefinito"   },
      { local: "foreigner", remote: "straniero"     }
    ],

    validation: {
      bank        : { required: true },
      holder      : { required: true },
      iban        : { required: true }
    },

    toString: function() {
      return this.get("iban");
    }
  });
  
  Models.Entity = Backbone.Model.extend({
    defaults: {
      code          : "",
      typeId        : "G",
      corporateName : "",
      firstName     : "",
      lastName      : "",
      vatNumber     : "",
      taxCode       : "",
      contacts      : [],
      addresses     : [],
      bankData      : []
    },

    maps: [
      { local: "code",          remote: "codice"                  },
      { local: "typeId",        remote: "tipo"                    },
      { local: "firstName",     remote: "nome"                    },
      { local: "lastName",      remote: "cognome"                 },
      { local: "corporateName", remote: "ragione_sociale"         },
      { local: "taxCode",       remote: "codice_fiscale"          },
      { local: "vatNumber",     remote: "partita_iva"             },
      { local: "addresses",     remote: "indirizzi"               },
      { local: "contacts",      remote: "contatti"                },
      { local: "bankData",      remote: "conti_correnti"          }
    ],

    computed: {
      name: {
        depends: ["typeId", "corporateName", "firstName", "lastName"],
        get: function(fields) {
          return fields.typeId === "G" ? 
            fields.corporateName : 
            fields.firstName + " " + fields.lastName;
        }
      }
    },
    
    validation: {
      typeId: { required: true },
      corporateName: {
        required: function(value, attr, computedState) {
          return computedState.typeId === "G";
        }
      },
      firstName: {
        required: function(value, attr, computedState) {
          return computedState.typeId === "F";
        }
      },
      lastName: {
        required: function(value, attr, computedState) {
          return computedState.typeId === "F";
        }
      },
      taxCode: {
        required: function(value, attr, computedState) {
          return computedState.typeId === "F";
        }
      }
    },

    parse: function(resp, options) {
      var resp = Backbone.Model.prototype.parse.apply(this, arguments);
      var addresses = [];
      _.each(resp.addresses, function(address) {
        addresses.push(new Models.Address(Models.Address.prototype.parse(address)));
      });
      resp.addresses = new Backbone.Collection(addresses);
      
      var contacts = [];
      _.each(resp.contacts, function(contact) {
        contacts.push(new Models.Contact(Models.Contact.prototype.parse(contact)));
      });
      resp.contacts = new Backbone.Collection(contacts);
      
      var bankData = [];
      _.each(resp.bankData, function(data) {
        bankData.push(new Models.BankDatum(Models.BankDatum.prototype.parse(data)));
      });
      resp.bankData = new Backbone.Collection(bankData);
      return resp;
    },

    getTypes: WMS.getEntityTypes,

    matchesFilter: function(filter) {
      if (!filter) return true;

      filter = filter.toLowerCase();
      if (this.get("name").toLowerCase().indexOf(filter) > -1) return true;
      if (this.get("code").toLowerCase().indexOf(filter) > -1) return true;
      if (this.get("vatNumber").toLowerCase().indexOf(filter) > -1) return true;
      if (this.get("taxCode").toLowerCase().indexOf(filter) > -1) return true;

      return false;
    },

    toString: function() {
      return this.get("name");
    }
  });
  
  Models.EntityCollection = Backbone.Collection.extend({
    model: Models.Entity,

    initialize: function() {
      _.extend(this, new Backbone.Picky.SingleSelect(this));
      Backbone.Collection.prototype.initialize.call(this);
    },

    sortByName: function() {
      return this.sort({ sort_key:'name' });
    }
  });
});