var ANIMATION_DURATION = 200;

_.extend(Marionette.View.prototype, {
  animateIn: function() {
    this.$el.animate(
      { opacity: 1 },
      ANIMATION_DURATION,
      _.bind(this.trigger, this, 'animateIn')
    );
  },

  // Same as above, except this time we trigger 'animateOut'
  animateOut: function() {
    this.$el.animate(
      { opacity: 0 },
      ANIMATION_DURATION,
      _.bind(this.trigger, this, 'animateOut')
    );
  },

  mixinPartials: function(target) {
    target = target || {};
    var partials = this.getOption('partials');
    partials = Marionette._getValue(partials, this);
    return _.extend(target, partials);
  },

  mixinLookups: function(target) {
    target = target || {};
    var lookups = this.getOption('lookups');
    lookups = Marionette._getValue(lookups, this);
    return _.extend(target, lookups);
  },

  getDefaultBindings: function(model) {
    return _.object(_.map(_.keys(model.prototype.defaults), function(k) {
      return ['[name=' + k + ']', k];
    }));
  }

, bindDate: function(attr) {
    return {
      observe:attr,
      onGet: function(val) {
        return val ? val.toString('yyyy-MM-dd') : '';
      }
    }
  },
  bindSelect: function(attr, collection, options) {
    options = _.defaults(options || {}, {label:'description', value:'id'});
    return {
      observe:attr,
      selectOptions: {
        collection: function() {
          return collection;
        },
        labelPath: options.label,
        valuePath: options.value,
        defaultOption: {
          label: 'Scegli...',
          value: ''
        }
      }
    }
  },
  bindLookup: function(attr, collection) {
    return {
      observe:attr,
      onGet: function(value) {
        var model = collection.find({ id:value });
        return model ? model.toString() : '';
      }
    }
  }
});

_.extend(Marionette.ItemView.prototype, {
  flash: function(cssClass) {
    var $view = this.$el;
    $view.hide().toggleClass(cssClass).fadeIn(800, function(){
      setTimeout(function(){
        $view.toggleClass(cssClass)
      }, 500);
    });
    return this;
  },

  _renderTemplate: function() {
    var template = this.getTemplate();

    if (template === false) {
      return;
    }

    if (!template) {
      throw new Marionette.Error({
        name: 'UndefinedTemplateError',
        message: 'Cannot render the template since it is null or undefined.'
      });
    }

    var data = {};
    data = this.serializeData();
    data = this.mixinTemplateHelpers(data);
    data = this.mixinPartials(data);
    data = this.mixinLookups(data);

    var html = Marionette.Renderer.render(template, data, this);
    this.attachElContent(html);

    return this;
  }
});

_.extend(Marionette.CompositeView.prototype, {
  flash: function() {
    return this;
  },

  _renderTemplate: function() {
      var data = {};
      data = this.serializeData();
      data = this.mixinTemplateHelpers(data);
      data = this.mixinPartials(data);
      data = this.mixinLookups(data);
  
      this.triggerMethod('before:render:template');
  
      var template = this.getTemplate();
      var html = Marionette.Renderer.render(template, data, this);
      this.attachElContent(html);
 
      this.bindUIElements();
      this.triggerMethod('render:template');
    },
})