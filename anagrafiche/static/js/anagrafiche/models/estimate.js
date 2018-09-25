WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  var Estimate = Models.Estimate = Backbone.CollectionModel.extend({
    defaults: {
      code                : "",
      date                : Date.today(),
      subject             : "",
      commissionId        : undefined,
      accepted            : false,
      destinationId       : "",
      applyTo             : "",
      vatRateId           : "",
      paymentTypeId       : "",
      total               : 0,
    }, 

    validation: {
      subject       : { required: true },
      destinationId : { required: true },
      vatRateId     : { required: true },
      paymentTypeId : { required: true }
    }, 

    maps: [
      { local: "code",                 remote: "codice"                 },
      { local: "date",                 remote: "data", type: "date"     },
      { local: "subject",              remote: "oggetto"                },
      { local: "commissionId",         remote: "commessa"               },
      { local: "commissionCode",       remote: "commessa_codice"        },
      { local: "accepted",              remote: "accettato"             },
      { local: "destinationId",        remote: "destinazione"           },
      { local: "applyTo",              remote: "persona_di_riferimento" },
      { local: "vatRateId",            remote: "aliquota_IVA"           },
      { local: "paymentTypeId",        remote: "pagamento"              },
      { local: "paymentTypeCode",      remote: "pagamento_label"        },      
      { local: "total",                remote: "totale"                 },
    ],

    isAccepted: function() {
      return this.get('accepted');
    }, 

    canUpdate: function() {
      return !this.isAccepted() && Backbone.Model.prototype.canUpdate.call(this);
    },

    canDestroy: function() {
      return !this.isAccepted() && Backbone.Model.prototype.canDestroy.call(this);
    },

    getCommissions  : WMS.getCommissions,
    getVatRates     : WMS.getVatRates,
    getPaymentTypes : WMS.getPaymentTypes,

    rowsClass       : Models.EstimateRows,
  
    toString: function() {
      return this.get('code') + ' - ' + this.get('subject');
    }
  });
  
  Models.ClientEstimate = Estimate.extend({
    urlRoot: "/api/v1/preventivoCliente/",

    defaults: _.extend({
      code                : "",
      date                : Date.today(),
      clientId            : null,
      clientCode          : ""
    }, Estimate.prototype.defaults, {
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

    validation: _.extend({
      clientId            : { required: true }
    }, Estimate.prototype.validation),

    maps: _.union([
      { local: 'clientId',             remote: 'cliente'                },
      { local: 'clientCode',           remote: 'cliente_codice'         },
      { local: 'constructionDrawings', remote: 'disegni_costruttivi'    },
      { local: 'calculationNote',      remote: 'relazione_di_calcolo'   },
      { local: 'gradeOfSteel',         remote: 'tipo_di_acciaio'        },
      { local: 'thickness',            remote: 'spessori'               },
      { local: 'galvanization',        remote: 'zincatura'              },
      { local: 'executionClass',       remote: 'classe_di_esecuzione'   },
      { local: 'wps',                  remote: 'wps'                    },
      { local: 'painting',             remote: 'verniciatura'           },
      { local: 'note',                 remote: 'note'                   },
      { local: 'printTotal',           remote: 'totale_su_stampa'       }
    ], Estimate.prototype.maps),

    initialize: function() {
      Backbone.Model.prototype.initialize.call(this);
      this.on("change:clientId", this.onChangeClientId);
    },

    /**
     * Imposto i valori:
     * - paymentTypeId
     * - applyTo
     * recuperati in base al cliente
     */
    onChangeClientId: function(model, value, options) {
      if (options.parse === true) {
        // Non è un change
        return;
      }

      WMS.request("get:client:list").then(function(list) {
        var client = list.find({id:value});
        if (client) {
          model.set({
            paymentTypeId: client.get("paymentTypeId")
          , applyTo:       client.get("applyTo")
          });
        }
      });
    },

    getDestinations: WMS.getClientDestinations,
    getClients: WMS.getClients
  }, {
    modelName: "client:estimate"
  });

  Models.SupplierEstimate = Estimate.extend({
    urlRoot: "/api/v1/preventivoFornitore/",

    defaults: _.extend({
      code                : "",
      date                : Date.today(),
      supplierId          : null,
      supplierCode        : "",
    }, Estimate.prototype.defaults, {
      commissionId        : 0,
      note                : "",
      printTotal          : true
    }),

    validation: _.extend({
      supplierId            : { required: true }
    }, Estimate.prototype.validation),

    maps: _.union([
      { local: 'supplierId',           remote: 'fornitore'              },
      { local: 'supplierCode',         remote: 'fornitore_codice'       },
      { local: 'note',                 remote: 'note'                   },
      { local: 'printTotal',           remote: 'totale_su_stampa'       }
    ], Estimate.prototype.maps),

    initialize: function() {
      Backbone.Model.prototype.initialize.call(this);
      this.on("change:supplierId", this.onChangeSupplierId);
    },

    /**
     * Imposto i valori:
     * - paymentTypeId
     * - applyTo
     * recuperati in base al fornitore
     */
    onChangeSupplierId: function(model, value, options) {
      if (options.parse === true) {
        // Non è un change
        return;
      }
      
      WMS.request("get:supplier:list").then(function(list) {
        var supplier = list.find({id:value});
        if (supplier) {
          model.set({
            paymentTypeId: supplier.get("paymentTypeId"),
            applyTo:       supplier.get("applyTo")
          });
        }
      });
    },

    getSuppliers: WMS.getSuppliers,
    getDestinations: WMS.getOwnerDestinations
  }, {
    modelName: "supplier:estimate"
  });

  Models.Estimates = Backbone.Collection.extend();
  
  Models.ClientEstimates = Models.Estimates.extend({
    url: '/api/v1/preventivoCliente/',
    model: Models.ClientEstimate
  });

  Models.SupplierEstimates = Models.Estimates.extend({
    url: '/api/v1/preventivoFornitore/',
    model: Models.SupplierEstimate
  });

  Models.EstimateRow = Backbone.Model.extend({    
    defaults: {
      articleId       : undefined,
      description     : '',
      unitTypeId      : '',
      quantity        : 0,
      price           : 0,
      discountPercent : 0,
      accepted        : false
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
    , { local: "accepted",              remote: "accettata"                       }
    , { local: "discountPercent",       remote: "sconto_percentuale"              }
    ],

    computed: {
      total: {
        depends: ['price', 'quantity', 'discountPercent'],
        get: function(fields) {
          // monkey patch: se non ho un discontPercent perché il server non me lo restituisce,
          // allora lo imposto a 0;
          if (!fields.discountPercent) fields.discountPercent = 0;
          return fields.price * (1 - fields.discountPercent/100) * fields.quantity;
        }
      }
    },

    isAccepted: function() {
      return this.get('accepted');
    },

    canUpdate: function() {
      return !this.isAccepted() && Backbone.Model.prototype.canUpdate.call(this);
    },

    canDestroy: function() {
      return !this.isAccepted() && Backbone.Model.prototype.canDestroy.call(this);
    },

    getArticles: WMS.getArticles,
    getUnitTypes: WMS.getUnitTypes,

    validation: {
      estimateId  : { required: true },
      articleId   : { required: true },
      description : { required: true },
      unitTypeId  : { required: true },
      quantity    : { min: 0 },
      discountPercent: {min:0, max:100}
    },

    toString: function() {
      return this.get('description') + ' x ' + this.get('quantity');
    }
  });
  
  Models.ClientEstimateRow = Models.EstimateRow.extend({
    urlRoot: '/api/v1/rigaPreventivoCliente/', 
    resetParent: function() {
      WMS.request('get:client:estimate', {id: this.get('estimateId') })
        .then(function(estimate) {
          estimate.fetch();
        });
    }
  }, {
    modelName: "client:estimate:row"
  });

  Models.SupplierEstimateRow = Models.EstimateRow.extend({
    urlRoot: '/api/v1/rigaPreventivoFornitore/', 
    resetParent: function() {
      WMS.request('get:supplier:estimate', {id: this.get('estimateId') })
        .then(function(estimate) {
          estimate.fetch();
        });
    }
  }, {
    modelName: "supplier:estimate:row"
  });

  Models.EstimateRows = Backbone.Collection.extend({
    getTotal: function() {
      return this.reduce(function(memo, value) { return memo + parseFloat(value.get('total')); }, 0);
    }
  });

  Models.ClientEstimateRows = Models.EstimateRows.extend({
    url: '/api/v1/rigaPreventivoCliente/'
  , model: Models.ClientEstimateRow
  });

  _.extend(Models.ClientEstimate.prototype, {
    rowsClass: Models.ClientEstimateRows
  , parentName: "preventivo"
  });

  Models.SupplierEstimateRows = Models.EstimateRows.extend({
    url: '/api/v1/rigaPreventivoFornitore/'
  , model: Models.SupplierEstimateRow
  });

  _.extend(Models.SupplierEstimate.prototype, {
    rowsClass: Models.SupplierEstimateRows
  , parentName: "preventivo"
  });
  
  WMS.reqres.setHandler('get:client:estimate:list', function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var collection = new Models.ClientEstimates();
    collection.attr(params);
    var data = {
      codice  : params.code
    , cliente : params.clientId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };
    collection.fetch({
      data: data //$.param(data)
    }).always(function() { defer.resolve(collection); });
    return defer.promise();
  });
  
  WMS.reqres.setHandler('get:client:estimate', function(id, options) {
    return Models.__fetchModel('clientEstimate', Models.ClientEstimate, id, options);
  });

  WMS.reqres.setHandler('clone:client:estimate', function(id, options) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.reject()
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      $.post("/api/v1/preventivoCliente/" + id + "/duplica/")
        .then(function(resp) {
          var estimate = new Models.ClientEstimate(Models.ClientEstimate.prototype.parse(resp));
          defer.resolve(estimate);
          WMS.vent.trigger("client:estimate:created", estimate);
        })
        .fail(function(error) {
          defer.reject(error);
        });
    }
    return defer.promise();
  });
  
  WMS.reqres.setHandler('get:client:estimate:rows', function(id) {
    var defer = $.Deferred();
    var collection = new Models.ClientEstimateRows();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(collection);
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      if(typeof id === 'object' ? !id.id : !id) {
        defer.resolve(collection);
      } else {
        collection.fetch({
          data: {preventivo: id} //$.param({ preventivo: id }),
        }).always(function() { defer.resolve(collection); });
      }
    }
    return defer.promise();
  });

  WMS.reqres.setHandler('get:client:estimate:print:url', function(id) {
    return id === undefined ? '#' : '/anagrafiche/stampa/preventivoCliente/' + id + '/';
  });

  /*********************************************************************
   * Richieste Preventivi Fornitore
   *********************************************************************/
  WMS.reqres.setHandler('get:supplier:estimate:list', function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var collection = new Models.SupplierEstimates();
    collection.attr(params);
    var data = {
      codice  : params.code
    , fornitore : params.clientId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };

    collection.fetch({
      data: data //$.param(data)
    }).always(function() { defer.resolve(collection); });
    return defer.promise();
  });
  
  WMS.reqres.setHandler('get:supplier:estimate', function(id, options) {
    return Models.__fetchModel('supplierEstimate', Models.SupplierEstimate, id, options);
  });

  WMS.reqres.setHandler('clone:supplier:estimate', function(id, options) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.reject()
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      $.post("/api/v1/preventivoFornitore/" + id + "/duplica/")
        .then(function(resp) {
          var estimate = new Models.SupplierEstimate(Models.SupplierEstimate.prototype.parse(resp));
          defer.resolve(estimate);
          WMS.vent.trigger("supplier:estimate:created", estimate);
        })
        .fail(function(error) {
          defer.reject(error);
        });
    }
    return defer.promise();
  })
  
  WMS.reqres.setHandler('get:supplier:estimate:rows', function(id) {
    var defer = $.Deferred();
    var collection = new Models.SupplierEstimateRows();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(collection);
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      if (typeof id === 'object' ? !id.id : !id) {
        defer.resolve(collection);
      } else {
        collection.fetch({
          data: { preventivo: id } //$.param({ preventivo: id }),
        }).always(function() { defer.resolve(collection); });
      }
    }
    return defer.promise();
  });

  WMS.reqres.setHandler('get:supplier:estimate:print:url', function(id) {
    return id === undefined ? '#' : '/anagrafiche/stampa/preventivoFornitore/' + id + '/';
  });

});