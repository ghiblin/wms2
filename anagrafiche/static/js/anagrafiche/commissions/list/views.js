WMS.module('Commissions.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views = _.extend({}, WMS.Common.Views, WMS.Commissions.Forms)
    , Behaviors = WMS.Common.Behaviors;

  Views.Layout = Marionette.LayoutView.extend({
    template  : _.template(
      '<div id="title-region" class="page-header"></div>' +
      '<div class="row">' +
        '<div class="col-sm-12 col-md-8">' +
          '<div class="row">' +
            '<div class="col-sm-12" id="panel-region"></div>' +
            '<div class="col-sm-12" id="master-region"></div>' +
            '<div class="col-sm-12" id="paginator-region"></div>' +
          '</div>' +
        '</div>' +
        '<div id="filter-region" class="col-md-4" style="height:100%"></div>' +
      '</div>'),

    regions: {
      titleRegion   : "#title-region",
      panelRegion   : "#panel-region",
      masterRegion  : "#master-region",
      paginatorRegion: '#paginator-region',
      filterRegion  : "#filter-region"
    }
  });

  var FilterModel = Backbone.Model.extend({
    defaults: {
      clientId: null,
      from    : Date.today().addYears(-1),
      to      : Date.today()
    },

    getClients: WMS.getClients
  });

  Views.FilterView = Views.FilterView.extend({
    initialize: function(options) {
      this.model = new FilterModel(_.pick(options, _.keys(FilterModel.prototype.defaults)));
    }
  });

  Views.Panel = Marionette.ItemView.extend({
    template: _.template(""),

    behaviors: [{
      behaviorClass: Behaviors.TabPanelBehavior
    }, {
      behaviorClass: Behaviors.AddModelBehavior,
      insertPoint: ".pre.actions-bar",
      FormView: WMS.Commissions.Forms.New,
      modelClass: WMS.Models.Commission
    }]
  });
  
  /*
  Views.List = Views.TableView.extend({
    childView: Commission
  , emptyView: NoCommission
  , childViewEventPrefix: 'commission'
  , headers: [
      { width:'10%', name:'code' }
    , { width:'10%', name:'startDate' }
    , { width:'10%', name:'deliveryDate'}
    , { width:'25%', name:'clientId' }
    , { width:'35%', name:'product' }
    , { width:'65px' }
    ]
  , modelClass: WMS.Models.Commission
  , behaviors: [{
      behaviorClass : Behaviors.AddBehavior
    }],

    initialize: function(options) {
      Views.TableView.prototype.initialize.call(this, options);
      this.from = options.from;
      this.to   = options.to;
    },

    filter: function(commission, index, collection) {
      // Conservo le commesse VARIE(id = -1) e MAGAZZINO(id = 0)
      if (commission.get('id') <= 0) return true;

      if (this.clientId) {
        if (commission.get('clientId') !== this.clientId) return false;
      }

      if (this.from) {
        if (commission.get('startDate') < this.from) return false;
      }

      if (this.to) {
        if (commission.get('startDate') > this.to) return false;
      }

      return true;
    }
  });
  */
  var columns = [{
    name: 'code',
    cell: 'string',
    label: 'Codice',
    editable: false,
  }, {
    name: 'startDate',
    cell: Backgrid.Extension.MomentCell.extend({
      displayFormat: 'L',
    }),
    label: 'Data Apertura',
    editable: false,
  }, {
    name: 'deliveryDate',
    cell: Backgrid.Extension.MomentCell.extend({
      displayFormat: 'L',
    }),
    label: 'Data Consegna',
    editable: false,
  }, {
    name: 'client',
    cell: 'string',
    label: 'Cliente',
    editable: false,
  }, {
    name: 'product',
    cell: 'string',
    label: 'Prodotto',
    editable: false,
  }];

  var ListRow = Backgrid.Row.extend({
    events: {
      'click': 'onClick',
    },

    onClick: function() {
      Backbone.trigger('commission:selected', this.model);
    },
  });

  Views.List = Backgrid.Grid.extend({
    initialize: function(options) {
      let opts = Object.assign({}, options, { 
        columns: columns,
        row: ListRow,
        emptyText: 'Nessuna commessa trovata',
      });
window.commissions = options.collection;
      Backgrid.Grid.prototype.initialize.call(this, opts);
      Backbone.on('commission:selected', function(c) {
        this.trigger('commission:selected', c);
      }, this)
    },
  });

  Views.Paginator = Backgrid.Extension.Paginator.extend({});
});