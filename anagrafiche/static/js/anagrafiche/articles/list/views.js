WMS.module('Articles.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views)
    , Behaviors = WMS.Common.Behaviors;

  var ArticleForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , insertPoint   : 'div.modal-body'
    , readonly      : ['code', 'stock']
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });  
      
  Views.New = ArticleForm.extend({
    title         : 'Nuovo Articolo'
  , saveButtonText: 'Crea'
  });

  Views.Edit = ArticleForm.extend({
    title         : 'Modifica Articolo'
  , saveButtonText: 'Aggiorna'
  });

  Views.FilterLayout = Views.FilterLayout.extend({
    title: 'Articoli'
  });

  Views.Panel = Views.FilterPanel.extend({
    eventPrefix: 'articles'
  , canAdd: function() {
      return WMS.Models.Article.canCreate();
    }
  });

  var Article = Views.TableRowView.extend({
    behaviors: [{
      behaviorClass : Behaviors.SelectableBehavior
    }, {
      behaviorClass : Behaviors.TableRowBehavior
    , fields: [
        "code"
      , "technicalTypeId"
      , "description"
      , "unitTypeId"
      , { attr: "stock", className: "text-right", format: "money" }
      , { attr: "price", className: "text-right", format: "price" }
      , { attr: "leadTime", className: "text-right", format: "money" }
      , { attr: "safetyStock", className: "text-right", format: "money" }
      ]
    }, {
      behaviorClass : Behaviors.EditableBehavior
    , insertPoint   : ".actions"
    , button        : false
    , FormView      : Views.Edit
    }, {
      behaviorClass : Behaviors.DestroyableBehavior
    , insertPoint   : ".actions"
    , button        : false
    }, {
      behaviorClass : Behaviors.UpdateBehavior
    }]
  });

  var columns = [{
    name: 'code',
    cell: 'string',
    label: 'Codice',
    editable: false,
  }, {
      name: 'technicalType',
    cell: 'string',
    label: 'Tipo',
    editable: false,
  }, {
    name: 'description',
    cell: 'string',
    label: 'Descrizione',
    editable: false,
  }, {
    name: 'unitType',
    cell: 'string',
    label: 'U.M.',
    editable: false,
  }, {
    name: 'stock',
    cell: 'number',
    label: 'Stock',
    editable: false,
  }, {
    name: 'price',
    cell: 'number',
    label: 'Prezzo',
    editable: false,
  }, {
    name: 'leadTime',
    cell: 'number',
    label: 'Lead Time',
    editable: false,
  }, {
    name: 'safetyStock',
    cell: 'number',
    label: 'Scorta di Sicurezza',
    editable: false,
  }];

  var ListRow = Backgrid.Row.extend({
    events: {
      'click': 'onClick',
    },

    onClick: function () {
      Backbone.trigger('article:selected', this.model);
    },
  });

  Views.List = Backgrid.Grid.extend({
    initialize: function (options) {
      let opts = Object.assign({}, options, {
        columns: columns,
        row: ListRow,
        emptyText: 'Nessun articolo trovato',
      });
      Backgrid.Grid.prototype.initialize.call(this, opts);
      Backbone.on('article:selected', function (c) {
        this.trigger('article:selected', c);
      }, this)
    },
  });

  Views.Paginator = Backgrid.Extension.Paginator.extend({});
  /*
  Views.List = Views.TableView.extend({
    childView: Article
  , childViewEventPrefix: 'article'
  , headers       : [
      { width: "10%", name: "code"                                  }
    , { width: "10%", name: "technicalTypeId"                       }
    , { width: "30%", name: "description"                           }
    , { width: "10%", name: "unitTypeId"                            }
    , { width: "10%", name: "stock",       className: "text-right"  }
    , { width: "10%", name: "price",       className: "text-right"  }
    , { width: "10%", name: "leadTime",    className: "text-right"  }
    , { width: "10%", name: "safetyStock", className: "text-right"  }
    , { width: "10%" }
    ]
  , modelClass    : WMS.Models.Article
  , behaviors: [{
      behaviorClass : Behaviors.AddBehavior
    }]

  , filter: function(child) {
      return child.matchesFilter(this.options.criterion);
    }
  });
  */
});