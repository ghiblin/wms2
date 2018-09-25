_.extend(Marionette.Controller.prototype, {
  _retrieveOption: function(options, tokens) {
    // Condizione d'uscita del ciclo ricorsivo
    if (tokens.length === 0) {
      return options;
    }

    // se non passo un oggetto su cui iterare, esco
    if (!options) {
      return;
    }

    // recupero la prima chiave
    var key = tokens.shift();

    if (options instanceof Backbone.Model) { 
      // è un model --> recupero l'attributo
      return this._retrieveOption(options.get(key), tokens);
    } 

    if (options instanceof Backbone.Collection) {
      var i = parseInt(key);
      if (_.isNaN(i)) {
        // la chiave è una stringa: recupero l'attributo dalla collection
        if (options[key]) {
          return this._retrieveOption(_.result(options, key), tokens);
        }
        return this._retrieveOption(options.attr(key), tokens);
      } else {
        // la ckiave è un numero: recupero il modello alla posizione i
        return this._retrieveOption(options.models[i], tokens);
      }
    }

    if (_.isObject(options)) {
      // è una hash
      return this._retrieveOption(options[key], tokens);
    }

    if (_.isArray(options)) {
      var i = parseInt(key);
      if (!_.isNaN(i)) {
        return this._retrieveOption(options[i], tokens);
      } else {
        if (key === "first") {
          return this._retrieveOption(options[0], tokens);
        }
        if (key === "last") {
          return this._retrieveOption(options[options.length-1], tokens);
        }
        return;
      }
    }

    // non so cosa sia --> probabilmente una stringa
    return options;
  }

, getOption: function(optionName) {
    if (!optionName) return;

    if (_.isString(optionName)) {
      if (optionName.startsWith("@")) {
        return this._retrieveOption(this.options, optionName.substr(1).split("."));
      } else {
        return Marionette.proxyGetOption(optionName) || optionName;
      }
    }

    if (_.isObject(optionName)) {
      var self = this;
      _.each(optionName, function(value, key, options) {
        options[key] = self.getOption(value);
      });
      return optionName;
      //options[key] = value;
    } 

    return optionName;
  }

,	start: function(list, callback) {
    var defer = new $.Deferred();
    this.options = this.options || {};
    if (!this.prefetchOptions) {
      // se non ho opzioni da caricare, bypasso il fetch
      defer.resolve(true);
    } else {
      var self		= this
      	, fetching= []
      	, options = this.options;

      _.each(this.prefetchOptions, function(item) {
        var request = item.request;
        if (request === undefined) return;

        item = _.defaults(item, {cache:true, reset:request.substr(request.indexOf(':')+1) + ':reset' });
        var fetch = false;
        if (!_.contains(_.keys(options), item.name)) {
          // Se non ho già caricato l'elemento, lo carico
          fetch = true;
        } else if (item.options !== undefined) {
          // Verifico che non siano cambiati i parametri del fetch
          var opt = options[item.name];
          if (!!opt) {
            if (_.isFunction(opt.attr)) {
              // opt è una collection
              _.each(item.options, function(key) {
                if (options[key] !== opt.attr(key)) {
                  fetch = true;
                }
              });
            } else {
              // opt è un model
              _.each(item.options, function(key) {
                if (options[key] !== opt.get(key)) {
                  fetch = true;
                }
              });
            }
          }
        }
        if (fetch || !item.cache) {
          // Conservo le opzioni presenti in option e gli aggiungo i parametri statici
          var opt = _.pick(options, item.options)
            , filters = _.filter(item.options, function(i) { 
              return _.isObject(i); 
          });
          _.each(filters, function(i) {
            _.extend(opt, i);
          });
          fetching.push({
            name    : item.name
          , request : WMS.request(item.request, opt)
          , reset   : item.reset
          , select  : item.select
          });
        }
      });

      $.when.apply($, fetching.map(function(item){return item.request;})).done(function() {
        var fetched = arguments;
        _.each(fetching, function(item, i) {
          self.options[item.name] = fetched[i];
          if (item.select !== undefined) {
            if (item.select === 'single') {
              self.options[item.name].singleSelect();
            }
            if (item.select === 'multi') {
              self.options[item.name].multiSelect();
            }
          }
        });
        defer.resolve(true);
      });
    }      
    return defer.promise();
  },

  setupRegions: function(layout, regions) {
    var regions = regions || _.result(this, "regions", []);
    var self	= this
    	, user 	= WMS.getCurrentUser();
    _.each(regions, function(region) {
      // Verifico se l'utente pu� visualizzare la regione
      if (region.permission !== undefined && !user.can(region.permission)) return;
      var view = self.setupRegion(region);
      if (region.name) {

        // Cerco la regione in cui inserire la vista. Se non esiste, non creo la vista
        var r = layout.getRegion(region.name);
        if (r === undefined) {
          console.warn("WARNING: region '" + region.name + "' not found.");
          return;
        }
        if (region.css || region.className) {
          r.once('show', function() {
            r.$el.css(region.css || {});
            r.$el.addClass(region.className);
          });
        }
        if (view) {
          r.show(view);
        } else {
          console.warn("WARNING: view not created for region '" + region.name + "'");
        }
      }
    });
  },
  
  setupRegion: function(region) {
    var self = this
      , options = {}; //_.clone(this.options);

    if (region.model) {
      var model;
      if (_.isFunction(region.model)) {
        // model è la classe con cui creare l'oggetto da usare come modello
        model = new region.model(_.pick(this.options, _.keys(region.model.prototype.defaults)));
      } else if (_.isString(region.model)) {
        model = options[region.model];
      } else {
        // model è un'istanza da usare come modello
        model = region.model;
      }
      options = _.extend(options, { model:model });
    } 

    if (region.collection) {
      options.collection = this.getOption(region.collection);
    }

    _.each(region.options, function(value, key) {
      options[key] = self.getOption(value);  
    });

    if (region.View) {
      var view = new region.View(options);
      if (!view) {
        console.warn("WARNING: View not created!", region.View);
      }
      if (region.viewName) {
        this[region.viewName] = view;
      }
      
      if (region.events) {
        _.each(_.keys(region.events), function(key) {
          view.on(key, self[region.events[key]], self);
        });
      }
      return view;
    } else {
      console.warn("WARNING: No View Class defined for region '" + region.name + "'");
    }
  },
});

Marionette.ShowController = Marionette.Controller.extend({
  showModel: function(id) {
    this.options = _.omit((this.options || {}), 'model');
    this.options.id = id;
          
    this.start().then(_.bind(function() {
      if (this.options[this.model || "model"] !== undefined) {
        this._layout = new this.Layout();
        this._layout.on('show', _.bind(function() {
          this.setupRegions(this._layout);
        }, this));
      } else {
        this._layout = new this.Missing();
      }
      WMS.mainRegion.show(this._layout);
    }, this));
  }
});
  
Marionette.FilterListController = Marionette.Controller.extend({
  filterList : function(criterion) {
    this.start().then(_.bind(function() {
      if (this.filteredCollection) {
        this.options.filtered = Backbone.FilteredCollection({
          collection: this.options[this.filteredCollection],
          filterFunction: this.filterFunction
        });
      }
      if (this._layout !== undefined && !this._layout.isDestroyed) {
        this.setupRegions(this._layout);

        if (criterion) {
          this.options.filtered.filter(criterion);
          this._panel.triggerMethod('set:filter:criterion', criterion);
        }
      } else {
        this._layout = new this.Layout();
        
        this._layout.on('show', _.bind(function() {
          this.setupRegions(this._layout);

          if (criterion) {
            this.options.filtered.filter(criterion);
            this._panel.triggerMethod('set:filter:criterion', criterion);
          }
        }, this));
        
        WMS.mainRegion.show(this._layout);
      }
    }, this));
  }
});