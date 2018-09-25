WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  /***************************************************************************
   * Dichiarazioni generiche
   ***************************************************************************/
  var Invoice = Models.Invoice = Backbone.CollectionModel.extend({
    
    defaults: {
      code                : "",
      date                : Date.today(),
      subject             : "",
      commissionId        : null,
      destinationId       : null,
      paymentTypeId       : null,
      vatRateId           : null,
      applyTo             : "",
      discountPercent     : 0,
      discountValue       : 0,
      fullPrice           : 0,
      discounted          : 0,
      totalVat            : 0,
      total               : 0,
      pending             : false
    }, 

    maps: [
      { local: "applyTo",              remote: "persona_di_riferimento"           },
      { local: "code",                 remote: "codice"                           },
      { local: "commissionCode",       remote: "commessa_codice"                  },
      { local: "commissionId",         remote: "commessa"                         },
      { local: "date",                 remote: "data", type: "date"               },
      { local: "destinationId",        remote: "destinazione"                     },
      { local: "discounted",           remote: "imponibile_netto"                 },
      { local: "discountPercent",      remote: "sconto_percentuale"               },
      { local: "discountValue",        remote: "sconto_euro"                      },
      { local: "fullPrice",            remote: "imponibile"                       },
      { local: "paymentTypeCode",      remote: "pagamento_label"                  },
      { local: "paymentTypeId",        remote: "pagamento"                        },
      { local: "pending",              remote: "da_confermare"                    },
      { local: "subject",              remote: "oggetto"                          },
      { local: "total",                remote: "totale"                           },
      { local: "totalVat",             remote: "totale_iva"                       },
      { local: "vatRateId",            remote: "aliquota_IVA"                     },
      { local: "wps",                  remote: "wps"                              }
    ],

    validation: {
      paymentTypeId : { required: true }
    }, 

    initialize: function(options) {
      if ((options || {}).urlRoot) {
        this.urlRoot = options.urlRoot;
      }
      Backbone.Model.prototype.initialize.call(this, options);
    },

    getCommissions  : WMS.getCommissions,
    getVatRates     : WMS.getVatRates,
    getPaymentTypes : WMS.getPaymentTypes,
    toString: function() {
      return this.get("code") + " - " + this.get("subject");
    }
  });
  

  Models.Invoices = Backbone.Collection.extend({
    /**
     * Restituisce una lista degli ordini con almeno una riga selezionata.
     * @return(array) La lista.
     */
    getSelected: function() {
      var invoices = [];
      _.each(this.models, function(invoice) {
        // recupero le righe dell'ordine. fetch:false impedisce il fetch dal server.
        var rows = invoice.getRows({ fetch:false });
        if (rows && _.where(rows.models, {selected:true}).length > 0) {
          invoices.push(invoice);
        }
      });
      return invoices;
    },

    /**
     * Restituisce la lista delle righe selezionate tra tutti gli ordini.
     * @return(array) La lista.
     */
    getSelectedRows: function() {
      var rows = [];
      _.each(this.models, function(invoice) {
        var _rows = invoice.getRows({fetch:false});
        if (_rows) {
          rows = rows.concat(_.where(_rows.models, {selected:true}));
        }
      });
      return rows;
    }
  });

  Models.InvoiceRow = Backbone.Model.extend({
    defaults: {
      articleId   : undefined,
      description : "",
      unitTypeId  : undefined,
      price       : 0,
      quantity    : 0,
      discountPercent : 0,
      total       : 0,
      noteCode : ""
    },

    maps: [
      { local: "invoiceId",             remote: "fattura"                         },
      { local: "commissionId",          remote: "commessa"                        },
      { local: "commissionCode",        remote: "commessa_codice"                 },
      { local: "estimateId",            remote: "preventivo"                      },
      { local: "estimateCode",          remote: "preventivo_codice"               },
      { local: "articleId",             remote: "articolo"                        },
      { local: "description",           remote: "articolo_descrizione"            },
      { local: "articleCode",           remote: "articolo_codice"                 },
      { local: "unitTypeId",            remote: "articolo_unita_di_misura"        },
      { local: "unitType",              remote: "articolo_unita_di_misura_label"  },
      { local: "quantity",              remote: "quantita"                        },
      { local: "price",                 remote: "articolo_prezzo"                 },
      { local: "total",                 remote: "totale"                          },
      { local: "noteRowId",             remote: "riga_bolla"                      },
      { local: "noteCreated",           remote: "bollettizzata"                   },
      { local: "discountPercent",       remote: "sconto_percentuale"              },
      { local: "noteCode",              remote: "riga_bolla_codice"               }
    ],

    computed: {
      total: {
        depends: ["quantity", "price", "discountPercent"],
        get: function(fields) {
          return fields.quantity * (1 - fields.discountPercent/100) * fields.price;
        }
      }
    }, 

    validation: {
      invoiceId   : { required: true },
      articleId   : { required: true },
      description : { required: true },
      unitTypeId  : { required: true },
      quantity    : { min: 0 },
      discountPercent: { min:0, max: 100 }
    }, 

    getArticles: WMS.getArticles, 
    getUnitTypes: WMS.getUnitTypes,

    toString: function() {
      return this.get("description") + " x " + this.get("quantity");
    }
  });

  Models.InvoiceRows = Backbone.Collection.extend({
    model: Models.InvoiceRow
  });

  /***************************************************************************
   *                                      CLIENTI
   ***************************************************************************/
  Models.ClientInvoice = Models.Invoice.extend({
    urlRoot: "/api/v1/fatturaCliente/", 

    defaults: _.extend({}, {
      code                : "",
      date                : Date.today(),
      clientId            : null,
      clientCode          : ""
    }, Models.Invoice.prototype.defaults),

    maps: _.union([
      { local: "clientId",             remote: "cliente"                          },
      { local: "clientCode",           remote: "cliente_codice"                   },
      { local: "client",               remote: "cliente_label"                    }
    ], Models.Invoice.prototype.maps),

    validation: _.extend({}, Models.Invoice.prototype.validation, {
      clientId      : { required: true }
    }),

    getClients      : WMS.getClients,
    getDestinations : WMS.getClientDestinations, 

    canAddRows: function() {
      if (this.isNew()) return false;
      return Models.ClientInvoiceRow.canCreate();
    }
  }, {
    modelName: "client:invoice"
  });

  Models.ClientInvoices = Models.Invoices.extend({
    url: "/api/v1/fatturaCliente/"
  , model: Models.ClientInvoice

  , initialize: function(options) {
      if((options || {}).url) {
        this.url = options.url;
      }
      Backbone.Collection.prototype.initialize.call(this, options);
    }
  });

  Models.ClientInvoiceRow = Models.InvoiceRow.extend({
    urlRoot: "/api/v1/rigaFatturaCliente/", 
    resetParent: function() {
      WMS.request('get:client:invoice', {id: this.get('invoiceId') })
        .then(function(invoice) {
          invoice.fetch();
        });
    }
  }, {
    modelName: "client:invoice:row"
  });

  Models.ClientInvoiceRows = Models.InvoiceRows.extend({
    url: "/api/v1/rigaFatturaCliente/"
  , model: Models.ClientInvoiceRow
  , getTotal: function() {
      return this.reduce(function(memo, value) { return memo + parseFloat(value.get("total")); }, 0);
    }
  });

  _.extend(Models.ClientInvoice.prototype, {
    rowsClass: Models.ClientInvoiceRows,
    parentName: "fattura"
  });

  /***************************************************************************
   *                                      FORNITORI
   ***************************************************************************/
  Models.SupplierInvoice = Models.Invoice.extend({
    urlRoot: "/api/v1/fatturaFornitore/",

    defaults: _.extend({}, {
      code                : "",
      date                : Date.today(),
      supplierId          : null,
      supplierCode        : "",
      supplierInvoice     : "",
      supplierDate        : Date.today()
    }, Models.Invoice.prototype.defaults), 

    maps: _.union([
      { local: "supplierId",             remote: "fornitore"                              },
      { local: "supplierCode",           remote: "fornitore_codice"                       },
      { local: "supplier",               remote: "fornitore_label"                        },
      { local: "supplierInvoice",        remote: "codice_fattura_fornitore"               },
      { local: "supplierDate",           remote: "data_fattura_fornitore", type: "date"   }
    ], Models.Invoice.prototype.maps),

    validation: _.extend({}, Models.Invoice.prototype.validation, {
      supplierId: { required: true }
    }),

    getSuppliers      : WMS.getSuppliers,
    getDestinations : WMS.getOwnerDestinations,

    canAddRows: function() {
      if (this.isNew()) return false;
      return Models.SupplierInvoiceRow.canCreate();
    }
  }, {
    modelName: "supplier:invoice"
  });

  Models.SupplierInvoices = Models.Invoices.extend({
    url: "/api/v1/fatturaFornitore/", 

    model: Models.SupplierInvoice,

    initialize: function(options) {
      if((options || {}).url) {
        this.url = options.url;
      }
      Backbone.Collection.prototype.initialize.call(this, options);
    }
  });

  Models.SupplierInvoiceRow = Models.InvoiceRow.extend({
    urlRoot: "/api/v1/rigaFatturaFornitore/", 
    resetParent: function() {
      WMS.request('get:supplier:invoice', {id: this.get('invoiceId') })
        .then(function(invoice) {
          invoice.fetch();
        });
    }
  }, {
    modelName: "supplier:invoice:row"
  });

  Models.SupplierInvoiceRows = Models.InvoiceRows.extend({
    url: "/api/v1/rigaFatturaFornitore/",
    model: Models.SupplierInvoiceRow,
    getTotal: function() {
      return this.reduce(function(memo, value) { return memo + parseFloat(value.get("total")); }, 0);
    }
  });

  _.extend(Models.SupplierInvoice.prototype, {
    rowsClass: Models.SupplierInvoiceRows
  , parentName: "fattura"
  });
  

  /***************************************************************************
   * Gestione richieste
   ***************************************************************************/
  var __getClientInvoiceList = function(params, options) {
    var defer = $.Deferred();
    params = (params || {});
    if (!!params.from && !!params.to) {
      var coll = new Models.ClientInvoices(options);
      coll.fetch({
        data: {
          codice  : params.code
        , cliente : params.clientId
        , da      : params.from && params.from.toString("yyyy-MM-dd")
        , a       : params.to && params.to.toString("yyyy-MM-dd")
        }
      }).always(function() {
          defer.resolve(coll);
        });
    } else {
      defer.reject();
    }
    return defer.promise();
  }

  WMS.reqres.setHandler("get:client:invoice:list", function(params) {
    return __getClientInvoiceList(params);
  });

  WMS.reqres.setHandler("get:client:invoice:list:nototal", function(params) {
    return __getClientInvoiceList(params, { url: "/api/v1/fatturaClienteSenzaTotale/"} );
  });

  WMS.reqres.setHandler("get:client:invoice", function(id) {
    return Models.__fetchModel('clientInvoice', Models.ClientInvoice, id);
  });

  WMS.reqres.setHandler("get:client:invoice:nototal", function(id) {
    return Models.__fetchModel('clientInvoice', Models.ClientInvoice, id, { 
      urlRoot: "/api/v1/fatturaClienteSenzaTotale/" 
    });
  });
  
  WMS.reqres.setHandler("get:client:invoice:rows", function(id) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(new Models.ClientInvoiceRows());
    } else {
      WMS.request("get:client:invoice", id)
        .then(function(invoice) {
          invoice.getRows().then(function(rows) {
            defer.resolve(rows);
          });
        })
        .fail(function(error) {
          console.error(error);
          defer.reject()
        });
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:invoice:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var path = null
      , options = null;
    if (params.noteRows) {
      path = params.id ? params.id + "/crea_righe_da_bolla/" : "crea_fattura_da_righe_bolla/";
      options = {
        riga_bolla_cliente: params.noteRows
      };
    } 
    if(params.orderRows) {
      path = params.id ? params.id + "/crea_righe_da_ordine/" : "crea_fattura_da_righe_ordine/";
      options = {
        riga_ordine_cliente: params.orderRows
      };
    } 
    if (!path) {
      defer.reject();
    } else {
      $.post("/api/v1/fatturaCliente/" + path, options)
        .then(function(resp) {
          var invoice = new Models.ClientInvoice(Models.ClientInvoice.prototype.parse(resp));
          defer.resolve(invoice);
          WMS.vent.trigger("client:invoice:updated", invoice);
        })
        .fail(function(error) {
          defer.reject(error);
        });
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:invoice:print:url", function(id) {
    return id === undefined ? "#" : "/anagrafiche/stampa/fatturaCliente/" + id + "/";
  });

  Models.ClientInvoiceCommission = Backbone.Model.extend({
    defaults: {
      clientId      : null
    , commissionId  : null
    }

  , validation: {
      commissionId: { required: true }
    }

  , initialize: function() {
      if (!this.get("clientId")) {
        throw new Error("ClientId is required.");
      }
    }

  , getClients: function() {
      return WMS.request("get:client:list");
    }

  , getCommissions: function() {
      var defer = $.Deferred()
        , clientId = this.get("clientId");
      $.when(WMS.request("get:commission:list")).then(function(list) {
        defer.resolve(list.where({clientId:clientId}));
      });
      return defer;
    }
  });

  var __getSupplierInvoiceList = function(params, options) {
    var defer = $.Deferred();
    params = (params || {});
    if (!!params.from && !!params.to) {
      var coll = new Models.SupplierInvoices(options);
      coll.fetch({
        data: {
          codice  : params.code
        , fornitore : params.supplierId
        , da      : params.from && params.from.toString("yyyy-MM-dd")
        , a       : params.to && params.to.toString("yyyy-MM-dd")
        }
      }).always(function() {
          defer.resolve(coll);
        });
    } else {
      defer.reject();
    }
    return defer.promise();
  }

  WMS.reqres.setHandler("get:supplier:invoice:list", function(params) {
    return __getSupplierInvoiceList(params);
  });

  WMS.reqres.setHandler("get:supplier:invoice:list:nototal", function(params) {
    return __getSupplierInvoiceList(params, { url: "/api/v1/fatturaFornitoreSenzaTotale/"} );
  });

  var __getSupplierInvoice = function(id, options) {
    //options = (options || {});
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve();
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      //options[id] = id;
      var model = new Models.SupplierInvoice({id: id}, options);
      model.fetch()
        .success(function() { defer.resolve(model); })
        .fail(function() { defer.resolve(); });
    }
    return defer.promise();    
  }

  WMS.reqres.setHandler("get:supplier:invoice", function(id) {
    return __getSupplierInvoice(id);
  });

  WMS.reqres.setHandler("get:supplier:invoice:nototal", function(id) {
    return __getClientInvoice(id, { urlRoot: "/api/v1/fatturaFornitoreSenzaTotale/" });
  });
  
  WMS.reqres.setHandler("get:supplier:invoice:rows", function(id) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(new Models.SupplierInvoiceRows());
    } else {
      WMS.request("get:supplier:invoice", id)
        .then(function(invoice) {
          invoice.getRows().then(function(rows) {
            defer.resolve(rows);
          });
        })
        .fail(function(error) {
          console.error(error);
          defer.reject()
        });
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:invoice:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var path = null
      , options = null;
    if (params.noteRows) {
      path = params.id ? params.id + "/crea_righe_da_bolla/" : "crea_fattura_da_righe_bolla/";
      options = {
        riga_bolla_fornitore: params.noteRows
      };
    } 
    if(params.orderRows) {
      path = params.id ? params.id + "/crea_righe_da_ordine/" : "crea_fattura_da_righe_ordine/";
      options = {
        riga_ordine_fornitore: params.orderRows
      };
    } 
    if (!path) {
      defer.reject();
    } else {
      $.post("/api/v1/fatturaFornitore/" + path, options)
        .then(function(resp) {
          var invoice = new Models.SupplierInvoice(Models.SupplierInvoice.prototype.parse(resp));
          defer.resolve(invoice);
          WMS.vent.trigger("supplier:invoice:updated", invoice);
        })
        .fail(function(error) {
          defer.reject(error);
        });
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:invoice:print:url", function(id) {
    return id === undefined ? "#" : "/anagrafiche/stampa/fatturaFornitore/" + id + "/";
  });

  Models.SupplierInvoiceCommission = Backbone.Model.extend({
    defaults: {
      supplierId      : null
    , commissionId  : null
    }

  , validation: {
      commissionId: { required: true }
    }

  , initialize: function() {
      if (!this.get("supplierId")) {
        throw new Error("SupplierId is required.");
      }
    }

  , getSuppliers: function() {
      return WMS.request("get:supplier:list");
    }

  , getCommissions: function() {
      return WMS.request("get:commission:list");
    }
  });

  WMS.commands.setHandler('unlink:invoice', function(invoice) {
    if (!invoice) return;
    if (!invoice._rows) return;

    var noteRowIds = invoice._rows
      .filter(function(row) { return !!row.get("noteCode"); })
      .map(function(row) { return row.get("noteRowId"); });
    if (noteRowIds.length === 0) return;

    $.post("/api/v1/fatturaCliente/" + invoice.get("id") + "/dissocia_bolle/")
      .then(function(resp) {
        var attrs = Models.ClientInvoice.prototype.parse(resp);
        var invoice = new Models.ClientInvoice(attrs);
        var rows = (resp.righe || []).map(function(r) { 
          return Models.ClientInvoiceRow.prototype.parse(r);
        });
        invoice._rows = new Models.ClientInvoiceRows(rows);
        WMS.vent.trigger("client:invoice:updated", invoice);

        var notes = Models.getAllModels("clientNote")
          .filter(function(note) { 
            if (!note._rows) return false;
            var rows = note._rows.filter(function(row) { 
              return _.contains(noteRowIds, row.get("id")); 
            });
            return rows.legth;
          });
        notes.forEach(function(note) {
          note.fetch();
          note._rows.fetch();
        });
      })
      .fail(function(error) {

      });
  })
});