_.extend(Backbone.Model.prototype, {
  can:function(action) {
    if (!this.constructor.permission) {
      this.constructor._initPermission();   
    }
    var p = this.constructor.permission; 
    return p === undefined ? true : WMS.getCurrentUser().can(p + ':' + action);
  },

  canRead:function() {
    return this.can('retrieve');
  }, 

  canUpdate:function() {
    return this.can('update');
  },

  canDestroy:function() {
    return this.can('destroy');
  },

  /* Converte remote to local */
  parse: function(resp, options) {
    if (!resp) return;
    if (this.maps === undefined) return resp;
    var newResp = {};
    var id = this.idAttribute || 'id';
    newResp[id] = resp[id];
    _.each(this.maps, function(map) {
      var value = resp[map.remote];
      if (map.type === 'date') {
        value = Date.parse(value);
      } 
      newResp[map.local] = value;
    });
    return newResp;
  },

  /* operazione opposta al parse: converte da local a remote */
  unparse: function() {
    var self = this
      , attributes = {}
      , id = this.idAttribute || 'id';
    attributes[id] = this.attributes[id];
    _.each(this.maps, function(map) {
      var value = self.attributes[map.local];
      if (map.type === 'date' && value) {
        value = value.toString('yyyy-MM-dd');
      }
      attributes[map.remote] = value;
    });

    return attributes;
  },

  matchesFilter: function(filter) {
    return true;
  },

  /* incapsula gli attributi in un oggetto FormData */
  _formData: function() {
    var self = this
      , formData = new FormData()
      , id = this.idAttribute || "id";
    formData.append(id, this.attributes[id]);
    _.each(this.maps, function(map) {
      var value = self.attributes[map.local];
      if (value instanceof FileList) {
        _.each(value, function(file) {
          formData.append(map.remote, file);
        });
        return;
      }

      if (map.type === "date" && value) {
        value = value.toString("yyyy-MM-dd");
      }
      formData.append(map.remote, value);
    });

    return formData;
  }, 

  sync: function(method, model, options) {
    if ((method === 'create' || method === 'update') && this.maps) {
      // se specifico fileAttribute, allora invio come FormData
      if (this.fileAttribute) {
        var formData = this._formData();
        options = _.extend(options, {
          data: formData
        , processData: false
        , contentType: false
        });

        // Apply custom XHR for processing status & listen to "progress"
        var that = this;
        options.xhr = function() {
          var xhr = $.ajaxSettings.xhr();
          xhr.upload.addEventListener('progress', that._progressHandler.bind(that), false);
          return xhr;
        }
      } 
      var attributes = this.unparse();
      // Backbone.sync usa come dati options.attrs o model.toJSON()
      options = _.extend({}, options, {attrs:attributes});  
      
    }
    var xhr = Backbone.sync.call(this, method, model, options);
    xhr.then(function() {
      var name = model.constructor.modelName;
      if (name === undefined) return;

      switch(method) {
        case "read":
          WMS.vent.trigger(name + ":fetched", model);
          break;
        case "update":
          WMS.vent.trigger(name + ":updated", model);
          break;
        case "create":
          WMS.vent.trigger(name + ":created", model);
          break;
        case "delete":
          WMS.vent.trigger(name + ":deleted", model);
          break;
      }
    });
    return xhr;
  },

  // _ Get the Progress of the uploading file
  _progressHandler: function( event ) {
    if (event.lengthComputable) {
      var percentComplete = event.loaded / event.total;
      this.trigger( 'progress', percentComplete );
    }
  },

  ajaxSave: Backbone.Model.prototype.save,
  save: function(key, val, options) {
    var xhr = this.ajaxSave(key, val, options);
    var self = this;
    if (this.resetParent) {
      xhr.then(function() {
        self.resetParent();
      });
    }
    xhr.fail(function() {
      if (self.parse) {
        self.parse(self.attributes);
      }
    });    
    return xhr;
  },
  
  initialize: function() {
    this.computedFields = new Backbone.ComputedFields(this);
    _.extend(this, new Backbone.Picky.Selectable(this));
  }
});

/**
 * Definizione metodi statici
 */
_.extend(Backbone.Model, {
  _initPermission: function() {
    if (!this.permission) {
      this.permission = this.modelName
        .replace(/(:)\w/g, function($1) { return $1.toUpperCase(); })
        .replace(/:/g, '');
    }
  },

  canCreate:function() {
    if (!this.permission) {
      this._initPermission();
    }
    var p = this.permission;
    return p === undefined ? true : WMS.getCurrentUser().can(p + ':create');
  },

  canList:function() {
    if (!this.permission) {
      this._initPermission();
    }
    var p = this.permission;
    return p === undefined ? true : WMS.getCurrentUser().can(p + ':retrieve');
  }
});

var rowsClassError = function() {
  throw new Error('A "rowsClass" property must be specified');
}

var parentNameError = function() {
  throw new Error('A "parentName" property must be specified');
}

Backbone.CollectionModel = Backbone.Model.extend({
  getRows: function(options) {
    var klass = this.rowsClass
      , parentName = this.parentName;

    if (!klass) rowsClassError();
    if (!parentName) parentNameError();

    options = _.defaults({}, options, {fetch: true, total: true});
    if (options.fetch) {
      var defer = $.Deferred();
      if (this._rows) {
        if (options.where) {
          defer.resolve(new klass(this._rows.where(options.where)));
        } else {
          defer.resolve(this._rows);
        }
      } else {
        this._rows = new klass();
        var self = this
          , params = {}
          , url = _.result(this._rows, "url");
        params[parentName] = this.get('id');
        if (!options.total) {
          url = url.substr(0, url.length - 1) + "SenzaTotale/";
        }
        this._rows.fetch({
          data: params // $.param(params)
        , url: url
        }).always(function() { 
          if (options.where) {
            defer.resolve(new klass(self._rows.where(options.where)));
          } else {
            defer.resolve(self._rows); 
          }
        });
      }
      return defer.promise();
    } else {
      return this._rows;  
    }
  }

, canAddRows: function() {
    var klass = this.rowsClass;

    if (!klass) rowsClassError();

    if (this.isNew()) return false;
    return !this.isAccepted() && this.constructor.canCreate();
  }
})