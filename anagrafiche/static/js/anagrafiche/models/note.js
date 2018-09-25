WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {

  /***************************************************************************
   *                            GENERICO
   ***************************************************************************/
  var Note = Models.Note = Backbone.CollectionModel.extend({
    defaults: {
      code                  : '',
      date                  : Date.today(),
      commissionId          : null,
      destinationId         : null,
      subject               : '',
      applyTo               : '',
      causalTransportTypeId : 24,     // Vendita
      shippingTypeId        : 3,      // A mezzo mittente
      carrierId             : null,
      incotermTypeId        : null,   // internation commercial terms -> porto
      outwardnessTypeId     : null,   // aspetto esteriore
      netWeight             : 0,
      grossWeight           : 0,
      items                 : 0,
      note                  : ''
    },

    maps: [
      { local: "code",                 remote: "codice"                           },
      { local: "date",                 remote: "data", type: "date"               },
      { local: "subject",              remote: "oggetto"                          },
      { local: "commissionId",         remote: "commessa"                         },
      { local: "commissionCode",       remote: "commessa_codice"                  },
      { local: "destinationId",        remote: "destinazione"                     },
      { local: "paymentTypeId",        remote: "pagamento"                        },
      { local: "paymentTypeCode",      remote: "pagamento_label"                  },
      { local: "applyTo",              remote: "persona_di_riferimento"           },
      { local: "constructionDrawings", remote: "disegni_costruttivi"              },
      { local: "calculationNote",      remote: "relazione_di_calcolo"             },
      { local: "gradeOfSteel",         remote: "tipo_di_acciaio"                  },
      { local: "thickness",            remote: "spessori"                         },
      { local: "galvanization",        remote: "zincatura"                        },
      { local: "executionClass",       remote: "classe_di_esecuzione"             },
      { local: "painting",             remote: "verniciatura"                     },
      { local: "note",                 remote: "note"                             },
      { local: "outwardnessTypeId",     remote: "aspetto_esteriore"               },
      { local: "outwardnessType",       remote: "aspetto_esteriore_label"         },
      { local: "causalTransportTypeId", remote: "causale_trasporto"               },
      { local: "causalTransportType",   remote: "causale_trasporto_label"         },
      { local: "incotermTypeId",        remote: "porto"                           },
      { local: "incotermType",          remote: "porto_label"                     },
      { local: "shippingTypeId",        remote: "trasporto_a_cura"                },
      { local: "shippingType",          remote: "trasporto_a_cura_label"          },
      { local: "netWeight",             remote: "peso_netto"                      },
      { local: "grossWeight",           remote: "peso_lordo"                      },
      { local: "items",                 remote: "numero_colli"                    },
      { local: "carrierId",             remote: "vettore"                         },
      { local: "carrierCode",           remote: "vettore_codice"                  },
      { local: "carrier",               remote: "vettore_label"                   },
      { local: "invoiceIssued",         remote: "fatturata"                       }
    ],

    validation: {
      commissionId          : { required: true },
      destinationId         : { required: true },
      causalTransportTypeId : { required: true },
      shippingTypeId        : { required: true },
      netWeight             : { required: true, min: 0 },
      grossWeight           : { required: true, min: 0 },
      items                 : { required: true, min: 0 }
    },

    getCommissions          : WMS.getCommissions,
    getCausalTransportTypes : WMS.getCausalTransportTypes,
    getOutwardnessTypes     : WMS.getOutwardnessTypes,
    getIncotermTypes        : WMS.getIncotermTypes,
    getShippingTypes        : WMS.getShippingTypes,
    getCarriers             : WMS.getSupplierCarriers,
    toString: function() {
      return this.get("code") + " - " + this.get("subject");
    },
  }, {
    modelName:"note"
  });

  Models.NoteRow = Backbone.Model.extend({
    defaults: {
      articleId   : null
    , description : ""
    , unitTypeId  : null
    , quantity    : 0
    },

    maps: [
      { local: "noteId",                remote: "bolla"                           },
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
      { local: "invoiceIssued",         remote: "fatturata"                       }
    ], 

    validation: {
      noteId      : { required: true },
      articleId   : { required: true },
      description : { required: true },
      unitTypeId  : { required: true },
      quantity    : { min: 0 }
    },
    
    getArticles: WMS.getArticles,
    getUnitTypes: WMS.getUnitTypes,
    toString: function() {
        return this.get("description") + " x " + this.get("quantity");
    }
  });

  /***************************************************************************
   *                                CLIENTI
   ***************************************************************************/
  Models.ClientNote = Models.Note.extend({
    urlRoot: "/api/v1/bollaCliente/", 

    defaults: _.extend({
      code          : ""
    , date          : Date.today()
    , clientId      : null
    , clientCode    : ""
    }, Models.Note.prototype.defaults), 

    maps: _.union([
      { local: "clientId",             remote: "cliente"                          },
      { local: "clientCode",           remote: "cliente_codice"                   },
      { local: "client",               remote: "cliente_label"                    }
    ], Models.Note.prototype.maps),

    validation: _.extend({
      clientId      : { required: true }
    }, Models.Note.prototype.validation)

  , canAddRows: function() {
      if (this.isNew()) return false;
      return Models.ClientNoteRow.canCreate();
    }

  , getClients: WMS.getClients
  , getDestinations: WMS.getClientDestinations

  }, {
    modelName: "client:note"
  });

  Models.ClientNotes = Backbone.Collection.extend({
    url   : "/api/v1/bollaCliente/", 
    model : Models.ClientNote
  });
  
  Models.ClientNoteRow = Models.NoteRow.extend({
    urlRoot: "/api/v1/rigaBollaCliente/",
    resetParent: function() {
      WMS.request('get:client:note', {id: this.get('noteId') })
        .then(function(note) {
          note.fetch();
        });
    }
  }, {
    modelName: "client:note:row"
  });

  Models.ClientNoteRows = Backbone.Collection.extend({
    url: "/api/v1/rigaBollaCliente/"
  , model: Models.ClientNoteRow
  });

  _.extend(Models.ClientNote.prototype, {
    rowsClass: Models.ClientNoteRows, 
    parentName: "bolla"
  });

  WMS.reqres.setHandler("get:client:note:list", function(params) {
    params = (params || {});

    var defer = $.Deferred()
      , coll = new Models.ClientNotes();
    
    var data = {
      codice  : params.code
    , cliente : params.clientId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };
    if (params.invoiceIssued !== undefined) {
      data.fatturata = params.invoiceIssued ? "True" : "False";
    }
    if (params.withRows !== undefined) {
      data.con_righe = params.withRows ? "True" : "False";
    }
    coll.fetch({
      data: data
    }).always(function() {
        defer.resolve(coll);
      });

    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:note", function(id, options) {
    return Models.__fetchModel('clientNote', Models.ClientNote, id, options);
  });
  
  WMS.reqres.setHandler("get:client:note:rows", function(id) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(new Models.ClientNoteRows());
    } else {
      WMS.request("get:client:note", id)
        .then(function(note) {
          note.getRows().then(function(rows) {
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

  WMS.reqres.setHandler("get:client:note:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var url = (params.id !== undefined) 
      ? params.id + "/crea_righe_da_ordine/"
      : "crea_bolla_da_righe_ordine/";

    $.post("/api/v1/bollaCliente/" + url, {
      riga_ordine_cliente: params.rows
    })
      .then(function(resp) {        
        var note = new Note(Note.prototype.parse(resp));
        WMS.trigger("client:note:updated", note);
        defer.resolve(note);
      })
      .fail(function(error) {
        defer.reject(error);
      });
    return defer.promise();
  });

  WMS.reqres.setHandler("get:client:note:print:url", function(id) {
    return id ? "/anagrafiche/stampa/bollaCliente/" + id + "/" : "#";
  });
  /***************************************************************************
   *                             FORNITORI
   ***************************************************************************/
  Models.SupplierNote = Models.Note.extend({
    urlRoot: "/api/v1/bollaFornitore/",

    defaults: _.extend({
      code          : "",
      date          : Date.today(),
      supplierId    : null,
      supplierCode  : "",
      supplierDate  : Date.today(),
      supplierNote  : ""
    }, Models.Note.prototype.defaults, {
      corrosiveClass: "C3"
    }),


    maps: _.union([
      { local: "supplierId",             remote: "fornitore"                          },
      { local: "supplierCode",           remote: "fornitore_codice"                   },
      { local: "supplier",               remote: "fornitore_label"                    },
      { local: "supplierDate",           remote: "data_bolla_fornitore", type: "date" },
      { local: "supplierNote",           remote: "codice_bolla_fornitore"             },
      { local: "corrosiveClass",         remote: "classe_di_corrosivita"              }
    ], Models.Note.prototype.maps),

    validation: _.extend({
      supplierId    : { required: true },
      corrosiveClass: { required: true }
    }, Models.Note.prototype.validation),

    canAddRows: function() {
      if (this.isNew()) return false;
      return Models.SupplierNoteRow.canCreate();
    },

    getSuppliers: WMS.getSuppliers, 
    getDestinations: WMS.getOwnerDestinations

  }, {
    modelName: "supplier:note"
  });

  Models.SupplierNotes = Backbone.Collection.extend({
    url   : "/api/v1/bollaFornitore/", 
    model : Models.SupplierNote,
    maps: [
      { local: "articleId", remote: "articolo" }
    ]
  });
  
  Models.SupplierNoteRow = Models.NoteRow.extend({
    urlRoot: "/api/v1/rigaBollaFornitore/",
    resetParent: function() {
      WMS.request('get:supplier:note', {id: this.get('noteId') })
        .then(function(note) {
          note.fetch();
        });
    }
  }, {
    modelName: "supplier:note:row"
  });

  Models.SupplierNoteRows = Backbone.Collection.extend({
    url: "/api/v1/rigaBollaFornitore/", 
    model: Models.SupplierNoteRow
  });

  _.extend(Models.SupplierNote.prototype, {
    rowsClass: Models.SupplierNoteRows
  , parentName: "bolla"
  });

  WMS.reqres.setHandler("get:supplier:note:list", function(params) {
    params = (params || {});

    var defer = $.Deferred()
      , coll = new Models.SupplierNotes();
    
    var data = {
      codice  : params.code
    , fornitore : params.supplierId
    , da      : params.from && params.from.toString("yyyy-MM-dd")
    , a       : params.to && params.to.toString("yyyy-MM-dd")
    };
    if (params.invoiceIssued !== undefined) {
      data.fatturata = params.invoiceIssued ? "True" : "False";
    }
    if (params.withRows !== undefined) {
      data.con_righe = params.withRows ? "True" : "False";
    }
    coll.fetch({
      data: data
    }).always(function() {
        defer.resolve(coll);
      });

    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:note", function(id, options) {
    return Models.__fetchModel('supplierNote', Models.SupplierNote, id, options);
  });
  
  WMS.reqres.setHandler("get:supplier:note:rows", function(id) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(new Models.SupplierNoteRows());
    } else {
      WMS.request("get:supplier:note", id)
        .then(function(note) {
          note.getRows().then(function(rows) {
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

  WMS.reqres.setHandler("get:supplier:note:drop", function(params) {
    var defer = $.Deferred();
    params = (params || {});
    var url = (params.id !== undefined) 
      ? params.id + "/crea_righe_da_ordine/"
      : "crea_bolla_da_righe_ordine/";

    $.post("/api/v1/bollaFornitore/" + url, {
      riga_ordine_fornitore: params.rows
    })
      .then(function(resp) {        
        var note = new Note(Note.prototype.parse(resp));
        WMS.trigger("supplier:note:updated", note);
        defer.resolve(note);
      })
      .fail(function(error) {
        defer.reject(error);
      });
    return defer.promise();
  });

  WMS.reqres.setHandler("get:supplier:note:print:url", function(id) {
    return id ? "/anagrafiche/stampa/bollaFornitore/" + id + "/" : "#";
  });
});