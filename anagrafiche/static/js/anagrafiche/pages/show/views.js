WMS.module('Pages.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  Show.Home = Marionette.ItemView.extend({
    template: '#home-template',
    templateHelpers: function() {
      return {
        links: WMS.request('get:headers:list').models.map(function(h) { return {label: h.get('label'), url: h.get('url') }})
      }
    }
  });
});