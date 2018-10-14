WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  var CommissionEstimate = Models.CommissionEstimate = Backbone.Model.extend({
    defaults: {
      code    : "",
      subject : ""
    },

    maps: [
      { local: "code",    remote: "codice"              },
      { local: "subject", remote: "oggetto"             }
    ]
  });

  Models.CommissionEstimates = Backbone.Collection.extend({
    model: CommissionEstimate
  });

  var CommissionOrder = Models.CommissionOrder = Backbone.Model.extend({
    defaults: {
      code: "",
      subject: ""
    },

    maps: [
      { local: "code",    remote: "codice"              },
      { local: "subject", remote: "oggetto"             }
    ]
  });

  Models.CommissionOrders = Backbone.Collection.extend({
    model: CommissionOrder
  });

  var CommissionNote = Models.CommissionNote = Backbone.Model.extend({
    defaults: {
      code: "",
      subject : "",
      date: null
    },

    maps: [
      { local: "code",    remote: "codice"              },
      { local: "subject", remote: "oggetto"             },
      { local: "date",    remote: "data", type: "date"  }
    ]
  });

  Models.CommissionNotes = Backbone.Collection.extend({
    model: CommissionNote
  });

  var CommissionInvoice = Models.CommissionInvoice = Backbone.Model.extend({
    defaults: {
      code: "",
      subject: "",
      date: null
    },

    maps: [
      { local: "code",    remote: "codice"              },
      { local: "subject", remote: "oggetto"             },
      { local: "date",    remote: "data", type: "date"  }
    ]
  });

  var CommissionInvoices = Models.CommissionInvoices = Backbone.Collection.extend({
    model: CommissionInvoice
  });

  Models.Commission = Backbone.Model.extend({
    urlRoot: "/api/v1/commessa/", 

    defaults: {
      code          : ""
    , clientId      : null
    , startDate     : Date.today()
    , product       : ""
    , destinationId : null
    , deliveryDate  : null
    }, 

    maps: [
      { local:"code",           remote:"codice"                     },
      { local:"clientId",       remote:"cliente"                    },
      //{ local:"startDate",      remote:"data_apertura", type:"date" },
      { local:"startDate",      remote:"data_apertura" },
      { local:"product",        remote:"prodotto"                   },
      { local:"destinationId",  remote:"destinazione"               },
      //{ local:"deliveryDate",   remote:"data_consegna", type:"date" },
      { local:"deliveryDate",   remote:"data_consegna" },
      { local:"estimates",      remote:"preventivi" },
      { local:"orders",         remote:"ordini" },
      { local:"notes",          remote:"bolle" },
      { local:"invoices",       remote:"fatture"}
    ],

    initialize: function(options) {
      Backbone.Model.prototype.initialize.call(this, options);
      //this.on("sync", "_updateClientCode", this);
      this._updateClientData(this, this.get("clientId"));
      this.on("change:clientId", this._updateClientData);
    }, 

    computed: {
      description: {
        depends: ["code", "product"],
        get:function(fields) {
          return fields.code + " - " + fields.product;
        }
      }
    },

    validation: {
      clientId  : { required: true },
      startDate : { required: true },
      product   : { required: true }
    }, 

    parse: function(resp, options) {
      var resp = Backbone.Model.prototype.parse.apply(this, arguments);

      var estimates = [];
      _.each(resp.estimates, function(estimate) {
        estimates.push(new CommissionEstimate(CommissionEstimate.prototype.parse(estimate)));
      });
      resp.estimates = new Models.CommissionEstimates(estimates);
      
      var orders = [];
      _.each(resp.orders, function(order) {
        orders.push(new CommissionOrder(CommissionOrder.prototype.parse(order)));
      });
      resp.orders = new Models.CommissionOrders(orders);

      var notes = [];
      _.each(resp.notes, function(note) {
        notes.push(new CommissionNote(CommissionNote.prototype.parse(note)));
      });
      resp.notes = new Models.CommissionNotes(notes);

      var invoices = [];
      _.each(resp.invoices, function(invoice) {
        invoices.push(new CommissionInvoice(CommissionInvoice.prototype.parse(invoice)));
      });
      resp.invoices = new Models.CommissionInvoices(invoices);

      return resp;
    },

    getClients      : WMS.getClients,
    getDestinations : WMS.getClientDestinations,
    getProduct: function() { return this.get("product") || ""; },
    getCode: function() { return this.get("code") || ""; },
    getClientName: function() { return this.get("clientName") || ""; },
    matchesFilter: function(filter) {
      if (!filter) return true;
      
      filter.toLowerCase();
      if (this.getProduct().toLowerCase().indexOf(filter) > -1) return true;
      if (this.getCode().replace("/","-").indexOf(filter) > -1) return true;
      if (this.getClientName().toLowerCase().indexOf(filter) > -1) return true;

      return false;
    }, 

    _updateClientData: function(model, newValue) {
      WMS.getClients().then(function(list) {
        var client = list.find({id: newValue});
        model.attributes.clientName = client ? client.get("name") : "";
        model.attributes.clientCode = client ? client.get("code") : "";
      });
    }, 

    toString: function() {
      return this.get("code") + " - " + this.get("product");
    }
  }, {
    modelName   : "commission"
  });
  
  /*
  Models.Commissions = Backbone.Collection.extend({
    model: Models.Commission,
    url: "/api/v1/commessa/",
    initialize: function() {
      _.extend(this, new Backbone.Picky.SingleSelect(this));
      Backbone.Collection.prototype.initialize.call(this);
    }
  });
  */
  Models.Commissions = Backbone.PageableCollection.extend({
    model: Models.Commission,
    url: function() {
      var da = this.attr('from') instanceof Date ? this.attr('from').toISOString().slice(0, 10) : '';
      var a = this.attr('to') instanceof Date ? this.attr('to').toISOString().slice(0, 10) : '';
      var id = this.attr('clientId') || '';
      return "/api/v1/commessa/?da=" + da + "&a=" + a + '&cliente=' + id;
    },
    mode: 'infinite',
    queryParams: {
      currentPage: 'page',
      pageSize: 'custom_page_size',
      totalRecords: 'count',
    },
    parseState: function(resp) {
      return {
        totalRecords: resp.count,
      };
    },
    parseRecords: function(resp) {
      return resp.results;
    },
    parseLinks: function(resp) {
      return {
        prev: resp.previous,
        next: resp.next,
      };
    },
  });
  
  Models.CommissionCost = Backbone.Model.extend({
    defaults: {
      date      : Date.today,
      employee  : "",
      workType  : "",
      hours     : 0.0,
      total     : 0.0
    },

    maps: [
      { local: "date",     remote: "data", type:"date"  },
      { local: "employee", remote: "nomeDipendente"     },
      { local: "workType", remote: "tipoLavoro"         },
      { local: "hours",    remote: "ore"                },
      { local: "total",    remote: "importo"            },
      { local: "note",     remote: "note"               }
    ]
  }, {
    modelName: "commission:cost"
  });
  
  Models.CommissionCosts = Backbone.Collection.extend({
    url: function() {
      return "/api/v1/commessa/" + this.commissionId + "/get_costi";
    }, 

    model: Models.CommissionCost,
    parse: function(resp, options) {
      if (resp.totali) {
        this.hours = resp.totali.totale_ore;
        this.total = resp.totali.totale_importi;
      }
      return resp.consuntivi;
    }, 

    initialize: function(options) {
      this.commissionId = (options || {}).commissionId
      _.extend(this, new Backbone.Picky.SingleSelect(this));
      Backbone.Collection.prototype.initialize.call(this, options);
    }, 

    getTotal: function() {
      return this.reduce(function(memo, value) { return memo + parseFloat(value.get("total")); }, 0);
    }
  }, {
    _permission: "commission:get_costi"
  });
  
  Models.CommissionAttachment = Backbone.Model.extend({
    fileAttribute: "filename",

    url: function() {
      return "/api/v1/commessa/" + this.get("commissionId") + "/upload_file/";
    }, 

    downloadUrl: function() {
      var path = "/get_file_" + (this.get("private") ? "privato" : "pubblico");
      return "/api/v1/commessa/" + this.get("commissionId") + path + "/?nome_file=" + this.get("filename");
    }, 

    defaults: {
      commissionId: null,
      filename    : "",
      private     : true
    },

    maps: [
      { local: "commissionId",  remote: "commessa"  },
      { local: "filename",      remote: "myfile"    },
      { local: "private",       remote: "privato"   }
    ],

    // Sovrascivo metodo destroy in quanto questo modello è "particolare"
    destroy: function(options) {
      options = options ? _.clone(options) : {};
      var model = this;
      var success = options.success;
      var error = options.error;
      var wait = options.wait;

      var destroy = function() {
        model.stopListening();
        model.trigger('destroy', model, model.collection, options);
      };

      options.success = function(resp) {
        if (wait) destroy();
        if (success) success.call(options.context, model, resp, options);
        if (!model.isNew()) model.trigger('sync', model, resp, options);
      };

      options.error = function(resp) {
        if (error) error.call(options.context, model, resp, options);
        model.trigger('error', model, resp, options);
      };

      _.extend(options, {
        method: "POST",
        url: "/api/v1/commessa/" + model.get("commissionId") + "/delete_file/",
        data: {
          privato: model.get("private"),
          nome_file: model.get("filename")
        }
      });
      var xhr = $.ajax(options);

      if (!wait) destroy();
      return xhr;
    },

    getCommissions: WMS.getCommissions
  }, {
    modelName: "commission:attachment"
  });

  Models.CommissionAttachments = Backbone.Collection.extend({
    url: function() {
      return "/api/v1/commessa/" + this.commissionId + "/get_file/";   
    }

  , model: Models.CommissionAttachment
  , parse: function(resp, options) {
      var commissionId = this.commissionId
        , files = [];
      _.each(resp.pubblici, function(item) {
        files.push({privato: false, commessa:commissionId, myfile:item});
      });
      _.each(resp.privati, function(item) {
        files.push({privato:true, commessa:commissionId, myfile:item});
      });

      return files;
    }

  , initialize: function(options) {
      this.commissionId = (options || {}).commissionId
      Backbone.Collection.prototype.initialize.call(this, options);
    }
  })

  WMS.reqres.setHandler("get:commission:list", function(params) {
    var coll = new Models.Commissions(params);
    coll.fetch();
    return coll;
  });
  
  WMS.reqres.setHandler("get:commission", function(id, options) {
    return Models.__fetchModel('commission', Models.Commission, id, options);
  });
  
  WMS.reqres.setHandler("get:commission:costs", function(id) {
    if (_.isObject(id)) {
      id = id.id;
    }
    var defer = $.Deferred()
      , list = new Models.CommissionCosts({ commissionId: id });
    if (list.canRead()) {
      list.fetch().always(function() { defer.resolve(list); });
    } else {
      defer.resolve(new Backbone.Collection());
    }
    return defer.promise();
  });

  WMS.reqres.setHandler("get:commission:files", function(id) {
    if (_.isObject(id)) {
      id = id.id;
    }
    var defer = $.Deferred()
      , list = new Models.CommissionAttachments({ commissionId: id });
    list.fetch().always(function() { defer.resolve(list); });
    return defer.promise();
  });

  WMS.reqres.setHandler("get:commission:print:url", function(id) {
    return id === undefined ? "#" : "/anagrafiche/stampa/commessa/" + id + "/";
  });
});