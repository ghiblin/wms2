WMS.module('Articles', function(Articles, WMS, Backbone, Marionette, $, _) {
  Articles.Router = Marionette.AppRouter.extend({
    appRoutes: {
      "articles(/filter/criterion::criterion)": "listArticles",
      "articles/:id": "showArticle"
    },

    header:'articles',

    permissionsMap: {
      'listArticles':'article:list',
      'showArticle':'article:list'
    }
  });

  var controllers = Articles.controllers = {}
    , API = {
    listArticles: function(criterion) {
      if (controllers.list === undefined) {
        controllers.list = new Articles.List.Controller();
      }
      controllers.list.listArticles(criterion);
    },

    showArticle: function(id) {
      if (controllers.show === undefined) {
        controllers.show = new Articles.Show.Controller();
      }
      controllers.show.showArticle(parseInt(id));
    }
    
  };

  WMS.on('articles:list', function() {
    WMS.navigate('articles');
  });

  WMS.on('articles:filter', function(criterion) {
    if (criterion) {
      WMS.navigate('articles/filter/criterion:' + criterion);
    } else {
      WMS.navigate('articles');
    }
  });

  WMS.on('articles:show', function(id) {
    WMS.navigate('articles/' + id);
  });

  WMS.on('before:start', function() {
    new Articles.Router({
      controller: API
    });
  });
});