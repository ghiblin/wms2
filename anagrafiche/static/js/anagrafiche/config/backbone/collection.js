var originalFetch = Backbone.Collection.prototype.fetch;

_.extend(Backbone.Collection.prototype, {
  initialize:function(options) {
    this._attributes = {};
    this.attr(options);
  },

  attr:function(prop, value) {
    if (prop === undefined) return;
    if (_.isObject(prop)) {
      // passo una hash di proprietà da settare
      var that = this;
      _.each(_.keys(prop), function(key) { 
        that.attr(key, prop[key]);
      });
    } else {
      // setto una proprietà singola o recupero un valore
      if (value === undefined) {
          return this._attributes[prop];
        } else {
          this._attributes[prop] = value;
          this.trigger('change:' + prop, value);
        }
    }
  },

  fetch: function(params) {
    params = params || {};
    var data = params.data || {};
    var maps = this.maps || {};
    if (this.maps) {
      _.each(this._attributes, function(value, name) {
        if (_.isObject(value) && value.format) {
          value = value.format("YYYY-MM-DD");
        }
        data[_.find(maps, {local: name}).remote] = value;
      }); 
    }
    return originalFetch.call(this, _.extend(params, {data: $.param(data)}));
  },

  comparator:function(item) {
    var value = item.get(this.sort_key || 'id');
    if (_.isString(value)) {
      value = value.toLowerCase();
    }
    return value;
  },

  sort: function(options) {
    if (!this.comparator) throw new Error('Cannot sort a set without a comparator');
    options || (options = {});
    
    if (options.sort_key) {
      this.sort_key = options.sort_key;
    }
    
    if (options.sort_dir) {
      this.sort_dir = options.sort_dir;
    }

    // Run sort based on type of `comparator`.
    if (_.isString(this.comparator) || this.comparator.length === 1) {
      this.models = this.sortBy(this.comparator, this);
    } else {
      this.models.sort(_.bind(this.comparator, this));
    }

    if (this.sort_dir === 'desc') {
      this.models.reverse();
    }

    if (!options.silent) this.trigger('sort', this, options);
    return this;
  },

  singleSelect: function() {
    _.extend(this, new Backbone.Picky.SingleSelect(this));
    return this;
  },

  multiSelect: function() {
    _.extend(this, new Backbone.Picky.MultiSelect(this));
    return this;
  },

  _initPermission: function() {
    if (this.constructor._permission) {
      this.permission = this.constructor._permission;
      return;
    }
    if (!this.model.permission) {
      this.model._initPermission();
    }
    this.permission = this.model.permission;
  },

  canRead:function() {
    //var p = this.constructor._permission; 
    if (!this.permission) {
      this._initPermission();
    }
    var p = this.permission;
    if (p === undefined) return true;
    return p.indexOf(":") > -1 
      ? WMS.getCurrentUser().can(p) 
      : WMS.getCurrentUser().can(p + ':retrieve');
  },

  canCreate:function() {   
    if (!this.permission) {
      this._initPermission();
    }
    var p = this.permission;
    return p === undefined ? true : WMS.getCurrentUser().can(p + ':create');
  },


  getTotal: function() {
    return this.reduce(function(memo, value) { return memo + parseFloat(value.get("total")); }, 0);
  }, 

  getSelected: function() {
    var selected = [];
    _.each(this.models, function(model) {
      // recupero le righe del preventivo. fetch:false impedisce il fetch dal server.
      if (model["getRows"]) {
        var rows = model.getRows({ fetch:false });
        if (rows && _.where(rows.models, {selected:true}).length > 0) {
          selected.push(model);
        }
      }
    });
    return selected;
  }, 

  getSelectedRows: function() {
    var rows = [];
    _.each(this.models, function(model) {
      if (model["getRows"]) {
        var _rows = model.getRows({fetch:false});
        if (_rows) {
          rows = rows.concat(_.where(_rows.models, {selected:true}));
        }
      }
    });
    return rows;
  }
});