WMS.module('Header.List', function(List, WMS, Backbone, Marionette, $, _) {
  var Header = Marionette.CompositeView.extend({
    template: '#header-template',
    templateHelpers: function() {
      return {
        hasNested: this.model.hasNested()
      };
    },
    tagName: 'li',
    className: function() {
      return this.model.hasNested() ? "dropdown" : undefined;
    },
    childView: List.Header,
    childViewContainer: 'ul',
    
    events: function() {
      if (!this.model.hasNested()) {
        return { 'click a': 'navigate' }
      }
    },
    childEvents: {
      navigate: function(childView, model) {
        this.trigger('navigate', model);
      }
    },
    
    navigate: function(e) {
      e.preventDefault();
      this.trigger('navigate', this.model);
    },
    
    initialize: function(options) {
      this.collection = this.model.get('nested');
    },
    
    onRender: function() {
      if (this.model.selected) {
        this.$el.addClass('active');
      }
    }
  });
  
  List.Views = {};

  List.Views.Headers = Marionette.CollectionView.extend({
    tagName: 'ul',
    className: 'nav navbar-nav',
    
    childView: Header,
  });
});