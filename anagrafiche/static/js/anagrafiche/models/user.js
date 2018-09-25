WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  var supportStorage = Storage && sessionStorage;

  var User = Models.User = Backbone.Model.extend({
    defaults: {
      username: "guest"
    , permissions: {
        "home:read" : true
      , "*"         : false
      }
    }

  , maps: [
      { local: "username",    remote: "username"    }
    , { local: "firstName",   remote: "first_name"  }
    , { local: "lastName",    remote: "last_name"   }
    , { local: "permissions", remote:"permessi"     }
    ]

  , permissionMap: [
      { local: "article",              remote: "articolo"                  },
      { local: "movement",            remote: "movimento"                   },
      { local: "stock",               remote: "giacenza"                    },
      { local: "clientAddress",       remote: "indirizzoCliente"            },
      { local: "clientBankDatum",        remote: "contoCorrenteCliente"      },
      { local: "clientContact",        remote: "contattoCliente"           },
      { local: "clientEstimateRow",    remote: "rigaPreventivoCliente"     },
      { local: "clientEstimate",       remote: "preventivoCliente"         },
      { local: "clientOrderRow",       remote: "rigaOrdineCliente"         },
      { local: "clientOrder",          remote: "ordineCliente"             },
      { local: "clientNoteRow",        remote: "rigaBollaCliente"          },
      { local: "clientNote",           remote: "bollaCliente"              },
      { local: "clientInvoiceRow",     remote: "rigaFatturaCliente"        },
      { local: "clientInvoice",        remote: "fatturaCliente"            },
      { local: "client",               remote: "cliente"                   },
      { local: "commission",           remote: "commessa"                  },
      { local: "employee",             remote: "dipendente"                },
      { local: "sheet",                remote: "consuntivo"                },
      { local: "supplierAddress",     remote: "indirizzoFornitore"        },
      { local: "supplierContact",      remote: "contattoFornitore"         },
      { local: "supplierBankDatum",      remote: "contoCorrenteFornitore"    },
      { local: "supplierEstimateRow",  remote: "rigaPreventivoFornitore"   },
      { local: "supplierEstimate",     remote: "preventivoFornitore"       },
      { local: "supplierOrderRow",     remote: "rigaOrdineFornitore"       },
      { local: "supplierOrder",        remote: "ordineFornitore"           },
      { local: "supplierNoteRow",      remote: "rigaBollaFornitore"        },
      { local: "supplierNote",         remote: "bollaFornitore"            },
      { local: "supplierInvoiceRow",   remote: "rigaFatturaFornitore"      },
      { local: "supplierInvoice",      remote: "fatturaFornitore"          },
      { local: "supplier",             remote: "fornitore"                 },
      { local: "ownerAddress",        remote: "indirizzoProprietario"     },
      { local: "ownerContact",         remote: "contattoProprietario"      },
      { local: "ownerBankDatum",         remote: "contoCorrenteProprietario" },
      { local: "owner",                 remote: "proprietario"              },
      { local: "address",               remote: "indirizzo"                 },
      { local: "contact",               remote: "contatto"                  },
      { local: "bankData",              remote: "contoCorrente"             }
    ]

  , can: function(action) {
      if (action === undefined) return false;
      var permissions = this.get("permissions");
      if (_.contains(_.keys(permissions), action)) {
        return permissions[action];
      } else {
        if (action === "*") {
          return false;
        }
        var i = action.lastIndexOf(":");
        if (action.endsWith("*")) {
          return this.can(action.substr(0,i));
        } else {
          if (i>0) {
            return this.can(action.substr(0,i) + ":*");
          } else {
            return this.can("*");
          }
        }
      }
    }

  , constructor: function(attributes, options) {
      if (supportStorage) {
        attributes["username"] = this.get("username") || this.defaults.username;
        attributes["permissions"] = this.get("permissions") || this.defaults.permissions;
      }
      Backbone.Model.prototype.constructor.call(this, attributes, options);
    }

  , get: function(key){
      if (supportStorage) {
        return JSON.parse(sessionStorage.getItem(key));
      } else {
        return Backbone.Model.prototype.get.call(this, key);
      }
    }

  , set: function(key, value, options) {
      var attrs
        , map = this.permissionMap;
      if (typeof key === "object") {
        attrs = key;
        options = value;
      } else {
        (attrs = {})[key] = value;
      }
      var permissions = attrs["permissions"]
        , newPerm = {};
      _.each(_.keys(permissions), function(remote) {
        var local = remote;
        _.each(map, function(item){
          local = local.replace(item.remote + ":", item.local + ":");
        });
        newPerm[local] = permissions[remote];
      });
      attrs["permissions"] = newPerm;

      if (supportStorage) {
        for (attr in attrs) {
          var prev = sessionStorage.getItem(attr)
            , curr = attrs[attr];
          sessionStorage.setItem(attr, JSON.stringify(curr));
          if (prev !== curr) {
            this.trigger("change:" + attr, this, curr, options);
          }
        }
      } else {
        Backbone.Model.prototype.set.call(this, key, value);
      }
      return this;
    }

  , unset: function(key) {
      if (supportStorage) {
        sessionStorage.removeItem(key);
      } else {
        Backbone.Model.prototype.unset.call(this, key);
      }
      return this;   
    }

  , clear: function() {
      if (supportStorage) {
        sessionStorage.clear();
      } else {
        Backbone.Model.prototype.clear(this);
      }
    }

  , getPermissions: function(filter) {
      filter = (filter || "");
      var permissions = this.get("permissions");
      return _.pick(permissions, function(value, key) {
        return key.indexOf(filter) !== -1;
      });
    }
  });
  
});