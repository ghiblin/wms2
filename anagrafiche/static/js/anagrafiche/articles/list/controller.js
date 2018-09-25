WMS.module('Articles.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views;

  List.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: 'get:article:list', name: 'articles' }
    ]

  , regions: [{ 
      name: 'panelRegion'
    , viewName: '_panel'
    , View: List.Views.Panel
    , options: {
        criterion: "@criterion"
      }
    , events: {
        "articles:new": 'newArticle',
        'articles:filter': 'filterArticle'
      }
    }, {
      name: 'listRegion'
    , viewName: '_articles'
    , View: List.Views.List
    , options: {
        criterion: "@criterion"
      , collection: "@articles"
      }
    , events: {
        'article:selected': 'selectArticle'
      }
    }]

  , initialize: function() {
      var self = this;
      WMS.vent.on("article:created", function(article) {
        self.options.articles.add(article);
      });
      WMS.vent.on("article:updated", function(article) {
        var model = self.options.articles.find({id: article.get('id')});
        if (model) {
          model.set(article.attributes);
        }
      });
    }

  , listArticles: function(criterion) {
      this.options.criterion = criterion || "";

      var self = this;
      this.start().then(function() {
        if (self._layout && !self._layout.isDestroyed) {
          self.setupRegions(self._layout);
        } else {
          self._layout = new Views.FilterLayout();
          
          self._layout.on('show', function() {
            self.setupRegions(self._layout);
          });
          
          WMS.mainRegion.show(self._layout);
        }
      });
    }

  , filterArticle: function(criterion) {
      WMS.trigger("articles:filter", criterion);
    }

  , newArticle: function() {
      var klass = WMS.Models.Article;
      if (klass.canCreate()) {
        var model = new klass()
          , view = new List.Views.New({ model: model });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , selectArticle: function(childView) {
      var article = childView.model;
      if (article.canRead()) {
        WMS.trigger("articles:show", article.get("id"));
      }
    }
  });
});