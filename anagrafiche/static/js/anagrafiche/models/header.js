WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  var filterPermission = function(item) {
    var permission = item.permission;
    return (permission !== undefined) 
      ? WMS.getCurrentUser().can(permission)
      : true;
  };

  Models.Header = Backbone.Model.extend({
    initialize: function(attributes) {
      var selectable = new Backbone.Picky.Selectable(this);
      _.extend(this, selectable);
      if (attributes.nested !== undefined) {
        this.set('nested', new Models.Headers(attributes.nested));
      }
    },
    hasNested: function() {
      return this.get('nested') !== undefined;
    }
  });

  Models.Headers = Backbone.Collection.extend({
    model: Models.Header,
  });

  var _headers = [];

  var initializeHeaders = function() {
    _headers = [{ 
      label: "Mr. Ferro", url: "owner", navigationTrigger: "owner",
      nested: [{ 
        label: "Home", url: "home", navigationTrigger: "pages:home" 
      }, { 
        label: "Anagrafica", url: "owner", navigationTrigger: "owner", 
        permission:'owner:retrieve' 
      }]
    }, { 
      label: "Clienti", url: "clients", navigationTrigger: "clients:list", 
      nested: [{ 
        label: "Anagrafica", url: "clients", navigationTrigger: "clients:list", 
        permission:'client:list' 
      }, { 
        label: "Preventivi", url: "clients/estimates", navigationTrigger: "clients:estimates:list", 
        permission:'clientEstimate:list' 
      }, { 
        label: "Ordini", url: "clients/orders", navigationTrigger: "clients:orders:list", 
        permission:'clientOrder:list' 
      }, {
        label: "Bolle", url: "clients/notes", navigationTrigger: "clients:notes:list", 
        permission:'clientNote:list' 
      }, {
        label: "Fatture", url: "clients/invoices", navigationTrigger: "clients:invoices:list",
        permission: "clientInvoice:list"
      }]
    }, { 
      label: "Fornitori", url: "suppliers", navigationTrigger: "suppliers:list",
      nested: [{ 
        label: "Anagrafica", url: "suppliers", navigationTrigger: "suppliers:list", 
        permission:'supplier:list' 
      }, { 
        label: "Preventivi", url: "suppliers/estimates", navigationTrigger: "suppliers:estimates:list", 
        permission:'supplierEstimate:list' 
      }, { 
        label: "Ordini", url: "suppliers/orders", navigationTrigger: "suppliers:orders:list", 
        permission:'supplierOrder:list' 
      }, {
        label: "Bolle", url: "suppliers/notes", navigationTrigger: "suppliers:notes:list", 
        permission:'supplierNote:list' 
      }, {
        label: "Fatture", url: "suppliers/invoices", navigationTrigger: "suppliers:invoices:list",
        permission: "supplierInvoice:list"
        }]
    }, { 
      label: "Dipendenti", url: "employees", navigationTrigger: "employees:list", 
      permission:'employee:list' 
    }, { 
      label: "Commesse", url: "commissions", navigationTrigger: "commissions:list", 
      permission:'commission:list' 
    }, { 
      label: "Articoli", url: "articles", navigationTrigger: "articles:list", 
      permission:'article:list' 
    }, { 
      label: "Consuntivi", url: "sheets", navigationTrigger: "sheets:list", 
      permission:'sheet:list' 
    }];
  };

  WMS.reqres.setHandler('get:headers:list', function() {
    initializeHeaders();
    var headers = _.filter(_headers, filterPermission);
    headers = _.each(headers, function(header) {
      var nested = header.nested;
      if (header.nested !== undefined) {
        header.nested = _.filter(header.nested, filterPermission);
      }
    });
    
    // scarto tutti i menù che non hanno sottomenù restanti
    headers = _.reject(headers, function(header) { 
      var nested = header.nested; 
      return nested ? nested.length === 0 : false; 
    });
    return new Models.Headers(headers).singleSelect();
  });
});