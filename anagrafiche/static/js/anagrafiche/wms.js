if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

if (!String.prototype.endsWith) {
  Object.defineProperty(String.prototype, 'endsWith', {
    value: function(searchString, position) {
      var subjectString = this.toString();
      if (position === undefined || position > subjectString.length) {
        position = subjectString.length;
      }
      position -= searchString.length;
      var lastIndex = subjectString.indexOf(searchString, position);
      return lastIndex !== -1 && lastIndex === position;
    }
  });
}

if (!String.prototype.capitalize) {
  String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  }
}

if (!Number.prototype.formatMoney) {
  Number.prototype.formatMoney = function(c, d, t) {
    return numeral(this).format('0.00');
  };
}

if (!Number.prototype.formatPrice) {
  Number.prototype.formatPrice = function() {
    return numeral(this).format('0.00000');
  }
}


function coalesce() {
  var len = arguments.length;
  for (var i=0; i<len; i++) {
    if (arguments[i] !== null && arguments[i] !== undefined) {
      return arguments[i];
    }
  }
  return null;
}

window.WMS = new Marionette.Application({
  regions: {
    headerRegion: '#header-region'
  , loginRegion : '#login-region'
  , alertRegion : '#alert-region'
  , mainRegion  : new Marionette.TransitionRegion({
      el: '#main-region'
    })
  , modalRegion : new Marionette.ModalRegion({
      el: '#modal'
    })
  }
});

WMS.navigate = function(route,  options) {
  options = _.defaults({}, options, {trigger:true});
  WMS._previousRoute = Backbone.history.fragment;
  Backbone.history.navigate(route, options);
};

WMS.getCurrentRoute = function(){
  return Backbone.history.fragment
};

WMS.getSession = function() {
  return WMS.request('get:session');
};

WMS.getCurrentUser = function() {
  return WMS.request('get:session').user;
};

WMS.showModal = function(view) {
  WMS.getRegion("modalRegion").show(view);
}

var __showAlert = function(msg, type, duration) {
  var header, className;
  switch(type) {
    case 'ERROR':
      header = '<strong><span class="glyphicon glyphicon-warning-sign"></span> Errore!</strong>';
      className = 'alert-danger';
      break;
    case 'SUCCESS':
      header = '<span class="glyphicon glyphicon-thumbs-up"></span>';
      className = 'alert-success';
      break;
  }
  var view = new Backbone.Marionette.ItemView({
    template: _.template([
      '<a href="#" class="close" data-dismiss="alert">&times;</a>',
      header + '&nbsp;' + msg
    ].join('')),
    className:"alert " + className,
  });
  view.once('show', function() {
    view.$el.hide().fadeIn(500);
    setTimeout(function() {
      view.$el.fadeOut(500, function() {
        view.destroy();
      });
    }, duration || 3000);
  });

  WMS.getRegion('alertRegion').show(view);
};

WMS.showError = function(msg, duration) {
  __showAlert(msg, 'ERROR', duration);
};

WMS.showSuccess = function (msg, duration) {
  __showAlert(msg, 'SUCCESS', duration)
}

WMS.on('start', function(opts) {
  if (Backbone.history) {
    Backbone.history.start();
    if (this.getCurrentRoute() === "") {
      WMS.trigger("pages:home");
    }
  }
});

WMS.module("Models", function(Models, WMS, Backbone, Marionette, $, _) {
  Models.loading = {};
  Models.cache = {};
  
  Models.__fetchModel = function(name, Type, id, options) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(new Type({}, options));
    } else {
      if (_.isObject(id)) {
        id = id.id;
      }
      
      var model = Models.cache[name + '-' + id];
      if (model) {
        defer.resolve(model);
      } else {
        model = new Type({id: id}, options);
        Models.cache[name + '-' + id] = model;
        model.fetch()
          .success(function() {
            defer.resolve(model);
          })
          .fail(function(model) {
            defer.resolve();
          });
      }
      
    }


    return defer.promise();
  }

  Models.getAllModels = function(name) {
    return _.reduce(Models.cache, function(memo, obj, key) { 
      if (key.startsWith(name)) {
        memo.push(obj);
      }
      return memo;
    }, []);
  }

  Models.__clearCollection = function(name) {
    delete Models.cache[name];
  }

  Models.__fetchCollection = function(name, Type, options, sort) {
    options = _.defaults(options || {}, {deferred:true});
    sort = sort || "description";
    if (options.deferred) {
      var defer;
      // se ho già qualcosa cachiato, lo restituisco subito
      if (Models.cache[name]) {
        defer = $.Deferred();
        // se imposto un filtro, lo applico sulla collezione e ne creo una nuova
        if (options.where) {
          defer.resolve(new Type(Models.cache[name].data.where(options.where)));
        } else {
          defer.resolve(Models.cache[name].data);
        }
      } else {
        // verifico se ho già una richiesta di loading in corso
        if (Models.loading[name]) {
          defer = Models.loading[name];
        } else {
          defer = $.Deferred();
          Models.loading[name] = defer;

          var param = options.param !== undefined ? $.param(options.param) : null;
          var coll = new Type();
          coll.attr(options.param);
          coll.fetch({
            data: param,
            success: function(data) {
              if (sort) {
                data.sort({ sort_key:sort });
              }
              Models.cache[name] = { data:data, param:param };
            }
          }).always(function() {
            Models.loading.name = undefined;
            if (sort) {
              coll.sort({ sort_key:sort });
            }
            // se specifico l'opzione where, filtro la collezione, ma ne devo costruire una 
            // nuova perché Backbone.Collection.where restituisce un array
            if (options.where) {
              defer.resolve(new Type(coll.where(options.where)));
            } else {
              defer.resolve(coll);
            }
          });
          var modelName = Type.prototype.model.modelName;
          if (modelName) {
            console.log("NOTE: Registering handler for " + modelName + ":created");
            WMS.vent.on(modelName + ":created", function(model) {
              console.log("adding model to Models.cache['" + name + "'].data", model);
              Models.cache[name].data.add(model);
            });

            console.log("NOTE: Registering handler for " + modelName + ":updated");
            WMS.vent.on(modelName + ":updated", function(model) {
              console.log("updating model in Models.cache['" + name + "'].data", model);
              var oldModel = Models.cache[name].data.find({id: model.get("id")});
              if (oldModel) {
                //oldModel.set(model.attributes, { silent: true });
                oldModel.set(model.attributes);
              } else {
                console.log("WARNING: model not found in collection, adding it");
                Models.cache[name].data.add(model);
              }
            });

            console.log("NOTE: Registering handler for " + modelName + ":deleted");
            WMS.vent.on(modelName + ":deleted", function(model) {
              console.log("removing model from Model.cache['" + name + "'].data", model);
              var oldModel = Models.cache[name].data.find({id: model.get("id")});
              if (oldModel) {
                Models.cache[name].data.remove(oldModel);
              }
            });
          }
        }
      }
      return defer.promise();
    } else {
      var c = Models.cache[name];
      return c ? c.data : null;
    }
  };
  
  Models.__resetCollection = function(name) {
    var c = Models.cache[name];
    if (c === undefined) return;
    c.data.fetch({data: c.param});
  };
});

// Funzioni di comodo
WMS.getAddressTypes   = function() { return WMS.request("get:address:types"); }
WMS.getArticles       = function() { return WMS.request("get:article:list"); }
WMS.getClients        = function() { return WMS.request("get:client:list"); }
WMS.getCausalTransportTypes = function() { return WMS.request("get:causalTransport:types"); }
WMS.getContactTypes   = function() { return WMS.request("get:contact:types"); }
WMS.getCommissions    = function() {
  var request = "get:commission:list";
  if (_.contains(_.keys(this.defaults), "clientId")) {
    var defer = $.Deferred()
    , clientId = this.get("clientId");
    if (clientId) {
      $.when(WMS.request(request)).then(function(list) {
        defer.resolve(list.where({ clientId:clientId }));
      });
    } else {
      // Lista vuota
      defer.resolve([]);
    }
    return defer.promise();
  } else {
    return WMS.request(request);
  }
  
}
__getFilteredList = function(request, field) {
  var defer = $.Deferred()
    , value = this.get(field);
  if (value) {
    $.when(WMS.request(request)).then(function(list) {
      var filter = {};
      filter[field] = value;
      defer.resolve(list.where(filter));
    });
  } else {
    defer.resolve([]);
  }
  return defer.promise();
}
WMS.getClientDestinations   = function() {
  return __getFilteredList.call(this, "get:client:address:list", "clientId");
}
WMS.getClientNotes = function() {
  return __getFilteredList.call(this, "get:client:note:list", "commissionId");
}
WMS.getClientOrders = function() {
  return __getFilteredList.call(this, "get:client:order:list", "commissionId");
}
WMS.getEntityTypes    = function() { return WMS.request("get:entity:types"); }
WMS.getEmployees      = function() { return WMS.request("get:employee:list"); }
WMS.getIncotermTypes  = function() { return WMS.request("get:incoterm:types"); }
WMS.getMovementTypes  = function() { return WMS.request("get:movement:types"); }
WMS.getOwners         = function() { return WMS.request("get:owner:list"); }
WMS.getOwnerDestinations = function() {
  var defer = $.Deferred();
  WMS.request("get:owner").then(function(owner) {
    defer.resolve(owner ? owner.get("addresses") : []);
  });
  return defer.promise();
}
WMS.getOutwardnessTypes = function() { return WMS.request("get:outwardness:types"); }
WMS.getPaymentTypes   = function() { return WMS.request("get:payment:types"); }
WMS.getShippingTypes  = function() { return WMS.request("get:shipping:types"); }
WMS.getSuppliers      = function() { return WMS.request("get:supplier:list"); }
WMS.getSupplierCarriers = function() { return WMS.request("get:supplier:carrier:list"); }
WMS.getTechnicalTypes = function() { return WMS.request("get:technical:types"); }
WMS.getUnitTypes      = function() { return WMS.request("get:unit:types"); }
WMS.getVatRates       = function() { return WMS.request("get:vat:rates"); }
WMS.getWorkTypes      = function() { return WMS.request("get:work:types"); }