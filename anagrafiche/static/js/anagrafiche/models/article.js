WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  Models.Article = Backbone.Model.extend({
    urlRoot: "/api/v1/articolo/",
    defaults: {
      code            : "",
      unitTypeId      : null,
      description     : "",
      supplierCode    : "",
      technicalTypeId : null,
      price           : 0.0,
      leadTime        : 0,
      stock           : 0.0,
      safetyStock     : 0.0,
      note            : ""
    },

    maps: [
      { local: "code",            remote: "codice"                },
      { local: "unitTypeId",      remote: "unita_di_misura"       },
      { local: "unitType",        remote: "unita_di_misura_label" },
      { local: "description",     remote: "descrizione"           },
      { local: "supplierCode",    remote: "codice_fornitore"      },
      { local: "technicalTypeId", remote: "classe"                },
      { local: "technicalType",   remote: "classe_label"          },
      { local: "price",           remote: "prezzo_di_listino"     },
      { local: "leadTime",        remote: "lt"                    },
      { local: "stock",           remote: "scorta"                },
      { local: "safetyStock",     remote: "ss"                    },
      { local: "note",            remote: "note"                  }
    ],
    
    computed: {
      label: {
        depends: ["code", "description"],
        get: function(fields) {
          return fields.code + " - " + fields.description;
        }
      }
    },

    validation: {
      technicalTypeId : { required: true },
      description     : { required: true },
      unitTypeId      : { required: true },
      price           : { min: 0.01 }
    },

    getTechnicalTypes : WMS.getTechnicalTypes,
    getUnitTypes      : WMS.getUnitTypes ,
    matchesFilter: function(filter) {
      filter = filter.toLowerCase();

      if (this.get("description").toLowerCase().indexOf(filter) > -1) return true;
      if (this.get("code").toLowerCase().indexOf(filter) > -1) return true;
      if (this.get("technicalType").toLowerCase().indexOf(filter) > -1) return true;
      return false;
    }, 

    toString: function() {
      return this.get("code") + " - " + this.get("description");
    }
  }, {
    modelName: "article"
  });
  
  /*
  Models.Articles = Backbone.Collection.extend({
    model: Models.Article,
    url: "/api/v1/articolo/",
    initialize: function() {
      _.extend(this, new Backbone.Picky.SingleSelect(this));
    }
  });
  */
  Models.Articles = Backbone.PageableCollection.extend({
    model: Models.Article,
    url: "/api/v1/articolo/",
    mode: "client",
    queryParams: {
      currentPage: 'page',
      pageSize: 'custom_page_size',
      totalRecords: 'count',
    },
  });

  Models.Article.prototype.getBatches = function() {
    if (!this.batches) {
      this.batches = new Models.Batches({ articleId: this.get("id") });
      this.batches.fetch();
    }
    return this.batches;
  }

  Models.Stock = Backbone.Model.extend({
    urlRoot: "/api/v1/giacenza/",
    defaults: {
      articleId: null,
      article: "",
      batchId: null,
      batch: "",
      unitTypeId: "",
      quantity: 0,
      commissionId: "",
      commission: "",
      note: ""
    },

    maps: [
      { local: "articleId", remote: "articolo" },
      { local: "article", remote: "articolo_label" },
      { local: "batchId", remote: "lotto" },
      { local: "batch", remote: "lotto_label" },
      { local: "unitTypeId", remote: "unita_di_misura" },
      { local: "quantity", remote: "quantita" },
      { local: "commissionId", remote: "commessa" },
      { local: "commission", remote: "commessa_label" },
      { local: "note", remote: "note" }
    ],

    toString: function() {
      return this.get("batch");
    }
  }, {
    modelName: "stock"
  });

  Models.Stocks = Backbone.Collection.extend({
    url: "/api/v1/giacenza/",
    model: Models.Stock,

    maps: [
      { local: "articleId", remote: "articolo" }
    ]
  });
  WMS.reqres.setHandler("get:stocks", function(options) {
    var defer = $.Deferred();
    var coll = new WMS.Models.Stocks();
    coll.attr(options);
    coll.fetch().then(function() {
      defer.resolve(coll);
    });
    return defer.promise();
   });


  Models.Article.prototype.getStocks = function() {
    if (!this.stocks) {
      this.stocks = new Models.Stocks({ articleId: this.get("id") });
      this.stocks.fetch();
    }
    return this.stocks;
  }

  Models.Movement = Backbone.Model.extend({
    urlRoot: '/api/v1/movimento/',
    defaults: {
      articleId: null,
      article: "",
      movementTypeId: null,
      movementType: "",
      batchId: null,
      batch: "",
      quantity: 0,
      unitTypeId: null,
      commissionId: null,
      commission: "",
      userId: "",
      username: "",
      date: null
    },

    validation: {
      articleId: { required: true },
      batchId: { required: true },
      movementTypeId: { required: true }
    },

    maps: [
      { local: "articleId", remote: "articolo" },
      { local: "article", remote: "articolo_label" },
      { local: "batchId", remote: "lotto" },
      { local: "batch", remote: "lotto_codice" },
      { local: "movementTypeId", remote: "tipo_movimento" },
      { local: "movementType", remote: "tipo_movimento_label" },
      { local: "userId", remote: "autore" },
      { local: "username", remote: "autore_nome" },
      { local: "quantity", remote: "quantita" },
      { local: "unitTypeId", remote: "unita_di_misura" },
      { local: "commissionId", remote: "destinazione" },
      { local: "commission", remote: "destinazione_codice" },
      { local: "date", remote: "data", type:"date" }
    ],

    getArticles: WMS.getArticles,
    getBatchs: function() { 
      if (this.get("movementTypeId") === 1) {
        // carico
        return WMS.request("get:batches", this.get("articleId"));   
      }

      // di default lo considero uno scarico
      return WMS.request("get:stocks", { articleId: this.get("articleId")});
    },
    getMovementTypes: WMS.getMovementTypes,
    getUnitTypes: WMS.getUnitTypes,
    getCommissions: function() {
      if (this.get("movementTypeId") === 1) {
        // carico => MAGAZZINO
        return WMS.request("get:commission:list", {where: {id: 0}});
      }

      // scarico => tutto tranne magazzino
      return WMS.request("get:commission:list");
     },

     toString: function() {
      return this.get("movementType") + " " + this.get("quantity");
     }
  }, {
    modelName: "movement"
  });

  Models.Movements = Backbone.Collection.extend({
    url: function() { 
      return '/api/v1/movimento/?articolo=' + this.articleId;
    },
    model: Models.Movement,
    
    initialize: function(options) {
      this.articleId = (options || {}).articleId;
    }
  });

  Models.Article.prototype.getMovements = function() {
    if (!this.movements) {
      this.movements = new Models.Movements({ articleId: this.get("id") });
      this.movements.fetch();
    }
    return this.movements;
  }

  WMS.reqres.setHandler("get:batches", function(articleId) {
    var defer = $.Deferred();
    var batches = new WMS.Models.SupplierNotes();
    batches.attr({articleId: articleId});
    batches.fetch().then(function() {
      defer.resolve(batches);
    });
    return defer.promise();
  });
      
  WMS.reqres.setHandler("get:article:list", function() {
    return Models.__fetchCollection("articleList", Models.Articles);
  });

  WMS.commands.setHandler("reset:article:list", function() {
    Models.__resetCollection("articleList");
  });

  WMS.reqres.setHandler("get:article", function(id, options) {
    return Models.__fetchModel('article', Models.Article, id, options);
  });

  function _updateArticleStock(movement) {
    WMS.request("get:article:list")
      .then(function(articles) {
        var article = articles.find({ id: movement.get("articleId") });
        if (article) {
          article.fetch();
        }
      });
    WMS.request("get:article", movement.get("articleId"))
      .then(function(article) {
        if (article) {
          article.getStocks().fetch();
        }
      });
  }
  this.listenTo(WMS.vent, "movement:created", _updateArticleStock);
  this.listenTo(WMS.vent, "movement:updated", _updateArticleStock);
  this.listenTo(WMS.vent, "movement:deleted", _updateArticleStock);

  this.listenTo(WMS.vent, "supplier:note:deleted", function(note) {
    if (note._rows) {
      note._rows.models.forEach(_updateArticleStock);
    } else {
      // devo riaggiornare tutti gli articoli perché non so quali righe erano
      // associate alla bolla
      WMS.request("get:article:list")
        .then(function(articles) {
          articles.fetch();
        });
    }
  });

  this.listenTo(WMS.vent, "supplier:note:row:created", _updateArticleStock);
  this.listenTo(WMS.vent, "supplier:note:row:updated", _updateArticleStock);
  this.listenTo(WMS.vent, "supplier:note:row:deleted", _updateArticleStock);
});