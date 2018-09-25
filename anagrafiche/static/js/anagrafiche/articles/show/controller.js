WMS.module('Articles.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views;

  Show.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: 'get:article', name: 'article', options: ['id'] }
    ],

    initialize: function() {
      this._initViews = this._initViews.bind(this);


      this.listenTo(WMS.vent, "movement:created", function(movement) {
        var article = this.options.article;
        if (article && article.get("id") === movement.get("articleId")) {
          article.getStocks().fetch();
          article.getMovements().fetch();
        }
      }.bind(this));

      this.listenTo(WMS.vent, "movement:updated", function(updated) {
        var movement = this.options.article.getMovements().find({ id: updated.get("id") });
        if (movement) {
          movement.set(updated.attributes);
        }
      });
    },

    showArticle: function(id) {
      var self = this;
      this.options = {
        id: id
      };
      this.start().then(this._initViews);
    },

    _initViews: function() {
      var layout = this._layout = new Views.Layout();
      var article = this.options.article;

      layout.on('show', function() {
        layout.titleRegion.show(new Views.TitleView({ model: article }));
        layout.detailsRegion.show(new Views.DetailsView({ model: article }));
        layout.stocksRegion.show(new Views.StocksView({ collection: article.getStocks() }));

        this._movementsView = new Views.MovementsView({ collection: article.getMovements() });
        layout.movementsRegion.show(this._movementsView);
        this._movementsView.on({
          "movements:download": this.onMovementsDownload,
          "movements:add": this.onMovementsAdd,
          "movements:substract": this.onMovementsSubstract,
          "movement:edit": this.onMovementEdit,
          "movement:delete": this.onMovementDelete,
          "movement:view": this.onMovementView
        }, this);
      }, this);

      WMS.mainRegion.show(layout);
    },

    // 1 => Carico
    // 2 => Scarico
    // 3 => Reso
    // 4 => Correzione positiva
    // 5 => Correzione negativa
    onMovementsDownload: function() {
      this._showMovementForm(2);
    },

    onMovementsAdd: function() {
      this._showMovementForm(4);
    },

    onMovementsSubstract: function() {
      this._showMovementForm(5);
    },

    onMovementEdit: function(movement) {
      if (movement.canUpdate()) {
        var view = new Views.EditMovement({ model: movement.clone() });
        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }
    },

    onMovementDelete: function(movement) {
      if (movement.canDestroy()) {
        if (window.confirm("Eliminare il movimento '" + movement + "'?")) {
          movement.destroy();
        }
      }
    },

    onMovementView: function(movement) {
      WMS.navigate('suppliers/notes/id:' + movement.get("batchId"));
    },

    _showMovementForm: function(movementTypeId) {
      if (WMS.Models.Movement.canCreate()) {
        var model = new WMS.Models.Movement({ 
          articleId: this.options.article.get("id"),
          userId: WMS.getCurrentUser().get("id"),
          movementTypeId: movementTypeId
        });
        var view = new Views.NewMovement({ model: model });
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }
  });
});