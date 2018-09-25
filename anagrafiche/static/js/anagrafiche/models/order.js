WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {

  /***************************************************************************
   * Dichiarazione classi generiche
   ***************************************************************************/
  var Order = Models.Order = Backbone.CollectionModel.extend({
    
    defaults: {
      subject             : ""
    , commissionId        : null
    , destinationId       : null
    , paymentTypeId       : null
    , vatRateId           : null
    , applyTo             : ""
    , total               : 0
    , discountPercent     : 0
    , discountValue       : 0
    , note                : ""
    , printTotal          : true
    }, 

    maps: [
      { local: "code",                 remote: "codice"                           }
    , { local: "date",                 remote: "data", type: "date"               }
    , { local: "subject",              remote: "oggetto"                          }
    , { local: "commissionId",         remote: "commessa"                         }
    , { local: "commissionCode",       remote: "commessa_codice"                  }
    , { local: "destinationId",        remote: "destinazione"                     }
    , { local: "paymentTypeId",        remote: "pagamento"                        }
    , { local: "paymentTypeCode",      remote: "pagamento_label"                  }
    , { local: "applyTo",              remote: "persona_di_riferimento"           }
    , { local: "constructionDrawings", remote: "disegni_costruttivi"              }
    , { local: "calculationNote",      remote: "relazione_di_calcolo"             }
    , { local: "gradeOfSteel",         remote: "tipo_di_acciaio"                  }
    , { local: "thickness",            remote: "spessori"                         }
    , { local: "galvanization",        remote: "zincatura"                        }
    , { local: "executionClass",       remote: "classe_di_esecuzione"             }
    , { local: "painting",             remote: "verniciatura"                     }
    , { local: "note",                 remote: "note"                             }
    , { local: "vatRateId",            remote: "aliquota_IVA"                     }
    , { local: "total",                remote: "totale"                           }
    , { local: "wps",                  remote: "wps"                              }
    , { local: "printTotal",           remote: "totale_su_stampa"                 }
    , { local: "discountPercent",       remote: "sconto_percentuale"              }
    , { local: "discountValue",         remote: "sconto_euro"                     }
    , { local: "noteIssued",            remote: "bollettato"                      }
    , { local: "invoiceIssued",         remote: "fatturato"                       }
    ],

    validation: {
      destinationId : { required: true }
    }, 

    initialize: function(options) {
      if ((options || {}).urlRoot) {
        this.urlRoot = options.urlRoot;
      }
      Backbone.Model.prototype.initialize.call(this, options);
    }

  , getCommissions  : WMS.getCommissions
  , getVatRates     : WMS.getVatRates
  , getPaymentTypes : WMS.getPaymentTypes

  , toString: function() {
      return this.get("code") + " - " + this.get("subject");
    }
  });

  Models.Orders = Backbone.Collection.extend();
  
  Models.OrderRow = Backbone.Model.extend({
    defaults: {
      articleId   : undefined
    , description : ""
    , unitTypeId  : undefined
    , price       : 0
    , quantity    : 0
    , discountPercent : 0
    , total       : 0
    }, 

    maps: [
      { local: "orderId",               remote: "ordine"                          }
    , { local: "commissionId",          remote: "commessa"                        }
    , { local: "commissionCode",        remote: "commessa_codice"                 }
    , { local: "estimateId",            remote: "preventivo"                      }
    , { local: "estimateCode",          remote: "preventivo_codice"               }
    , { local: "articleId",             remote: "articolo"                        }
    , { local: "description",           remote: "articolo_descrizione"            }
    , { local: "articleCode",           remote: "articolo_codice"                 }
    , { local: "unitTypeId",            remote: "articolo_unita_di_misura"        }
    , { local: "unitType",              remote: "articolo_unita_di_misura_label"  }
    , { local: "quantity",              remote: "quantita"                        }
    , { local: "price",                 remote: "articolo_prezzo"                 }
    , { local: "total",                 remote: "totale"                          }
    , { local: "noteRowId",             remote: "riga_bolla"                      }
    , { local: "noteIssued",            remote: "bollettata"                      }
    , { local: "invoiceIssued",         remote: "fatturata"                       }
    , { local: "discountPercent",       remote: "sconto_percentuale"              }
    ],

    computed: {
      total: {
        depends: ["quantity", "price", "discountPercent"],
        get: function(fields) {
          // monkey patch: se non ho un discontPercent perché il server non me lo restituisce,
          // allora lo imposto a 0;
          if (!fields.discountPercent) fields.discountPercent = 0;
          return fields.quantity * fields.price * (1 - fields.discountPercent/100);
        }
      }
    }

  , validation: {
      orderId     : { required: true }
    , articleId   : { required: true }
    , description : { required: true }
    , unitTypeId  : { required: true }
    , quantity    : { min: 0 }
    , discountPercent: {min: 0, max: 100 }
    }

  , getArticles: WMS.getArticles
  , getUnitTypes: WMS.getUnitTypes

  , toString: function() {
      return this.get("description") + " x " + this.get("quantity");
    }
  });

  Models.OrderRows = Backbone.Collection.extend({});

  /***************************************************************************
   *                                CLIENTI
   ***************************************************************************/
  Models.ClientOrder = Models.Order.extend({
    urlRoot: "/api/v1/ordineCliente/"
  , defaults: _.extend({
      code                : ""
    , date                : Date.today()
    , clientId            : null
    , clientCode          : ""
    }, Models.Order.prototype.defaults, {
      constructionDrawings: true,
      calculationNote     : true,
      gradeOfSteel        : "",
      thickness           : "",
      galvanization       : "",
      executionClass      : "",
      wps                 : "",
      painting            : "",
      note                : "",
      printTotal          : true
    }),

    maps: _.union([
      { local: "clientId",             remote: "cliente"                          }
    , { local: "clientCode",           remote: "cliente_codice"                   }
    , { local: "client",               remote: "cliente_label"                    }
    ], Models.Order.prototype.maps),

    validation: _.extend({
      clientId      : { required: true }
    , subject       : { required: true }
    , commissionId  : { required: true }
    }, Models.Order.prototype.validation)

  , getClients      : WMS.getClients
  , getDestinations : WMS.getClientDestinations

  , canAddRows: function() {
      if (this.isNew()) return false;
      return Models.ClientOrderRow.canCreate();
    }
  }, {
    modelName: "client:order"
  });

  Models.ClientOrders = Models.Orders.extend({
    url: "/api/v1/ordineCliente/"
  , model: Models.ClientOrder

  , initialize: function(options) {
      if((options || {}).url) {
        this.url = options.url;
      }
      Backbone.Collection.prototype.initialize.call(this, options);
    }
  });

  Models.ClientOrderRow = Models.OrderRow.extend({
    urlRoot: "/api/v1/rigaOrdineCliente/"
  }, {
    modelName: "client:order:row"
  });

  Models.ClientOrderRows = Models.OrderRows.extend({
    url: "/api/v1/rigaOrdineCliente/"
  , model: Models.ClientOrderRow
  });

  _.extend(Models.ClientOrder.prototype, {
    rowsClass: Models.ClientOrderRows
  , parentName: "ordine"
  });

  /***************************************************************************
   *                               FORNITORI
   ***************************************************************************/
  Models.SupplierOrder = Models.Order.extend({
    urlRoot: "/api/v1/ordineFornitore/"
  , defaults: _.extend({
      code                : ""
    , date                : Date.today()
    , supplierId          : null
    , supplierCode        : ""
    }, Models.Order.prototype.defaults, {
      commissionId        : 0
    }), 

    maps: _.union([
      { local: "supplierId",             remote: "fornitore"                          },
      { local: "supplierCode",           remote: "fornitore_codice"                   },
      { local: "supplier",               remote: "fornitore_label"                    }
    ], Models.Order.prototype.maps),

    getSuppliers      : WMS.getSuppliers,
    getDestinations : WMS.getOwnerDestinations, 

    canAddRows: function() {
      if (this.isNew()) return false;
      return Models.SupplierOrderRow.canCreate();
    }
  }, {
    modelName: "supplier:order"
  });

  Models.SupplierOrders = Models.Orders.extend({
    url: "/api/v1/ordineFornitore/"
  , model: Models.SupplierOrder

  , initialize: function(options) {
      if((options || {}).url) {
        this.url = options.url;
      }
      Backbone.Collection.prototype.initialize.call(this, options);
    }
  });
  
  Models.SupplierOrderRow = Models.OrderRow.extend({
    urlRoot: "/api/v1/rigaOrdineFornitore/"
  }, {
    modelName: "supplier:order:row"
  });

  Models.SupplierOrderRows = Models.OrderRows.extend({
    url: "/api/v1/rigaOrdineFornitore/"
  , model: Models.SupplierOrderRow
  });

  _.extend(Models.SupplierOrder.prototype, {
    rowsClass: Models.SupplierOrderRows
  , parentName: "ordine"
  });

  /***************************************************************************
   * Gestione richiesta CLIENTI
   ***************************************************************************/  
  var __getClientOrderList = function(params, options) {
    var defer = $.Deferred();
    params = (params || {});
    var coll = new Models.ClientOrders(options);

    var data = {
      codice  : params.code
    , cliente : params.clientId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };

    coll.fetch({
      data: data
    }).always(function() {
        defer.resolve(coll);
      });
    return defer.promise();
  }

  WMS.reqres.setHandler("get:client:order:list", function(params) {
    return __getClientOrderList(params);
  });

  WMS.reqres.setHandler("get:client:order:list:nototal", function(params) {
    return __getClientOrderList(params, { url: "/api/v1/ordineClienteSenzaTotale/"} );
  });

  WMS.reqres.setHandler("get:client:order", function(id, options) {
    return Models.__fetchModel('clientOrder', Models.ClientOrder, id, options);
  });

  WMS.reqres.setHandler("get:client:order:nototal", function(id) {
    return Models.__fetchModel('clientOrder', Models.ClientOrder, id, { 
      urlRoot: "/api/v1/ordineClienteSenzaTotale/" 
    });
  });
  
  WMS.reqres.setHandler("get:client:order:rows", function(id) {
    var defer = $.Deferred();
    var collection = new Models.ClientOrderRows();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(collection);
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      if (typeof id === 'object' ? !id.id : !id) {
        defer.resolve(collection);
      } else {
        collection.attr("orderId", id);
        collection.fetch({
          data: { ordine: id },
        }).always(function() { defer.resolve(collection) });
      }
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:order:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var url = (params.id !== undefined) 
      ? params.id + "/crea_righe_da_preventivo/"
      : "crea_ordine_da_righe_preventivo/";

    $.post("/api/v1/ordineCliente/" + url, {
      commessa: params.commissionId
    , riga_preventivo_cliente: params.rows
    })
      .then(function(resp) {
        var order = new Models.ClientOrder(Models.ClientOrder.prototype.parse(resp));
        defer.resolve(order);
        WMS.vent.trigger("client:order:updated", order);
      })
      .fail(function(error) {
        defer.reject(error);
      });
    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:order:print:url", function(id) {
    return id === undefined ? "#" : "/anagrafiche/stampa/ordineCliente/" + id + "/";
  });

  Models.ClientOrderCommission = Backbone.Model.extend({
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

  /***************************************************************************
   * Gestione richiesta FORNITORI
   ***************************************************************************/  
  var __getSupplierOrderList = function(params, options) {
    var defer = $.Deferred();
    params = (params || {});
    var coll = new Models.SupplierOrders(options);

    var data = {
      codice  : params.code
    , fornitore : params.supplierId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };

    coll.fetch({
      data: data
    }).always(function() {
        defer.resolve(coll);
      });
    return defer.promise();
  }

  WMS.reqres.setHandler("get:supplier:order:list", function(params) {
    return __getSupplierOrderList(params);
  });

  var __getSupplierOrder = function(id, options) {
    //options = (options || {});
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve();
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      //options[id] = id;
      var model = new Models.SupplierOrder({id: id}, options);
      model.fetch()
        .success(function() { defer.resolve(model); })
        .fail(function() { defer.resolve(); });
    }
    return defer.promise();    
  }

  WMS.reqres.setHandler("get:supplier:order", function(id, options) {
    return Models.__fetchModel('supplierOrder', Models.SupplierOrder, id, options);
  });

  WMS.reqres.setHandler("get:supplier:order:nototal", function(id) {
    return Models.__fetchModel('supplierOrder', Models.SupplierOrder, id, { 
      urlRoot: "/api/v1/ordineFornitoreSenzaTotale/" 
    });
  });
  
  WMS.reqres.setHandler("get:supplier:order:rows", function(id) {
    var defer = $.Deferred();
    var collection = new Models.SupplierOrderRows();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(collection);
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      if (typeof id === 'object' ? !id.id : !id) {
        defer.resolve(collection);
      } else {
        collection.attr("orderId", id);
        collection.fetch({
          data: { ordine: id },
        }).always(function() { defer.resolve(collection) });
      }
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:order:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var url = (params.id !== undefined) 
      ? params.id + "/crea_righe_da_preventivo/"
      : "crea_ordine_da_righe_preventivo/";

    $.post("/api/v1/ordineFornitore/" + url, {
      commessa: params.commissionId
    , riga_preventivo_fornitore: params.rows
    })
      .then(function(resp) {
        var order = new Models.SupplierOrder(Models.SupplierOrder.prototype.parse(resp));
        defer.resolve(order);
        WMS.vent.trigger("supplier:order:updated", order);
      })
      .fail(function(error) {
        defer.reject(error);
      });
    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:order:print:url", function(id) {
    return id === undefined ? "#" : "/anagrafiche/stampa/ordineFornitore/" + id + "/";
  });

  Models.SupplierOrderCommission = Backbone.Model.extend({
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

  , getCommissions: WMS.getCommissions
  });
});