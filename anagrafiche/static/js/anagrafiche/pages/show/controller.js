WMS.module('Pages.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  Show.Controller = {
    showHome: function() {
      var view = new Show.Home();
      WMS.mainRegion.show(view);
    }
  }
});