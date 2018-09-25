WMS.module('Common', function(Common, WMS, Backbone, Marionette, $, _) {
  var Behaviors = Common.Behaviors = {};

  var _getListForField = function(field, model) {
    var defer = $.Deferred()
      , method = "get" + field.substring(0, field.length - 2).capitalize() + "s";
    if (_.isFunction(model[method])) {
      $.when(model[method]()).then(function(list) {
        if (!_.isArray(list) && list.models !== undefined) {
          list = list.models;
        }
        defer.resolve(list);
      });
    } else {
      defer.resolve([]);
    }
    return defer;
  }

  var _appendOptions = function($input, list) {
    var name = $input.attr("name");
    $input.append("<option value=''>Scegli...</option>");
    _.each(list, function(model) {
      var value = model.get('id');
      if (_.has(model.attributes, name)) {
        console.log("NB: Trovato attributo '" + name + "' in " + model.constructor.modelName + "=> lo uso come ID");
        value = model.get(name);
      }
      $input.append('<option value=' + value + '>' + model + '</option>');
    });
  }

  var _setInputValue = function($input, value) {
    var type = $input.prop("type");
    switch(type) {
      case "text":
      case "number":
        $input.val(value);
        break;

      case "date":
        $input.val(value && value.toString("yyyy-MM-dd"));
        break;

      case "checkbox":
        $input.prop('checked', value);
        break;

      case "select-one":
        // per i select, la lettura delle options è asincrona
        // BUGFIX: se passo un value = "" genero una query errata per jQuery
        var option = $input.find("option[value=" + (value === "" ? undefined : value)  + "]").html();
        if (option === undefined) {
          // se non ho un elemento, aspetto che venga inserita l'opzione sul select
          $input.on("DOMNodeInserted", function (e) {
            var $el = $(e.target);

            // ignoro gli elementi che non sono un option
            if (!$el.is("option")) return;

            // verifico che il valore dell'opzione sia quella che attendo
            //if ((value || "").toString() === $el.prop("value")) {
            if (coalesce(value,"").toString() === $el.prop("value")) {
              $input.val(value);
              $input.select2("val", value);
            }
          });
        } else {
          $input.val(value);
          $input.select2("val", value);
        }

        break;
    }
  }

  var _getInputValue = function($input) {
    var type = $input.prop("type")
      , value;

    // aggiunto controllo per versioni del browser che non supportano il 
    // tipo 'date'
    if (type === 'text' && $input.prop('name') === 'date') type = 'date';
    
    switch(type) {
      case "text":
      case "password":
        value = $input.val();
        break;
      case "number":
        value = parseFloat($input.val());
        break;
      case "date":
        value = Date.parse($input.val());
        break;
      case "checkbox":
        value = $input.prop("checked");
        break;
      case "select-one":
        value = $input.find(":selected").val();
        // Verifico se l'id è numerico
        if (!isNaN(value)) {
          value = value === "" ? undefined : parseInt(value);
        }

        break;
    }
    return value;
  }

  var _renderCell = function($el, tagName, field, model) {
    var $cell = $("<" + tagName + "></" + tagName + ">");
    if (field) {
      if (!_.isObject(field)) {
        field = {attr:field};
      }
      if (field.className) {
        $cell.addClass(field.className);
      }
      if (field.format === "date") {
        var date = model.get(field.attr);
        $cell.html(date ? date.toString('dd/MM/yyyy') : '');
      } else if (field.format === "money") {
        $cell.html((model.get(field.attr) || 0).formatMoney());
      } else if (field.format === "price") {
        $cell.html((model.get(field.attr) || 0).formatPrice())
      } else if (field.attr.toLowerCase().endsWith("id")) {
        _lookupValue(model, field.attr, $cell);
      } else {
        $cell.html(model.get(field.attr));
      }
    }
    $el.append($cell);
  }

  var _renderButton = function(className, icon, label, tooltip) {
    var $a = $("<a>", {
      class: "btn btn-primary " + className
    , href: "#"
    , "data-loading-text": "Loading..."
    });
    if (tooltip) {
      $a.attr({"data-toggle":"tooltip", "data-placement":"left", "title":tooltip});
    }
    $('<span class="glyphicon glyphicon-' + icon + '"></span>').appendTo($a);
    if (label) {
      $("<span>&nbsp;" + label + "</span>").appendTo($a);
    }
    return $a;
  }

  var _renderSpanButton = function(className, icon, label) {
    var $span = $("<span class='" + className + "'></span>");
    if (icon) {
      $span.append($("<span class='glyphicon glyphicon-" + icon + "'></span>"));
    }
    if (label) {
      $span.append($("<span>&nbsp;" + label + "</span>"));
    }
    return $span;
  }

  var _lookupValue = function(model, field, $el) {
    var id = model.get(field)
      , method = "get" + field.substr(0, field.length-2).capitalize() + "s";
    if (model[method]) {
      $.when(_.result(model, method)).then(function(list) {
        var item = _.isArray(list) ? _.find(list, { id:id }) : list.find({ id:id });
        var label = (item || "").toString();
        if ($el.is("input")) {
          $el.val(label)
        } else {
          $el.html(label);
        }
      });
    } else {
      $el.html(id);
    }
  }

  Behaviors.GenerateFormBehavior = Marionette.Behavior.extend({
    defaults: {
      fieldSelector : 'app-field'
    , insertPoint   : undefined
    , skipFields    : []
    , readonly      : []
    , labels        : undefined
    , modelClass    : undefined
    , buttons       : []
    }

  , onRender: function() {
      var self = this
        , $ins = this.$el
        , model= this.view.model;

      if (model === undefined) return;

      if (this.options.insertPoint) {
        $ins = $ins.find(this.options.insertPoint);
      }

      var fields = this.options.fields || model.defaults;
      // Costruisco la form partendo dai defult del modello
      _.each(fields, function(value, field) {
        // non visualizzo i campi segnati come skip
        if (_.contains(self.options.skipFields, field)) return;

        // non visualizzo i campi array
        if (_.isArray(value)) return;

        var $div = $('<div class="form-group field-' + field + '"></div>');
        var label = field;
        if (self.options.labels && WMS.labels[self.options.labels]) {
          label = WMS.labels[self.options.labels][field] || field;
        } else if (model.labels) {
          label = model.labels[field] || field;
        } 

        if (_.isBoolean(value)) {
          // Questo è un checkbox
          $div.append(
            '<div class="col-sm-12 col-lg-offset-4 col-lg-8">' +
              '<div class="checkbox">' +
                '<label>' +
                  '<input type="checkbox" name="' + field + '">' + label +
                '</label>' +
              '</div>' +
            '</div>');
        } else {
          if (label.trim() !== "") {
            label += ":"
          }
          $div.append('<label for="' + field +'" class="control-label col-lg-4 hidden-xs hidden-sm hidden-md">' + label + '</label>');
          $field = $('<div class="col-sm-12 col-lg-8">' +
                        '<label for="' + field + '" class="control-label hidden-lg">' + label + '</label>' +
                      '</div>');
          var $input;
          if (field.toLowerCase().endsWith("id")) {
            // Questo è un id --> select
            $input = $('<select name="' + field + '" class="form-control select2-select"></select>');
            //$input.append("<option value=''>Scegli...</option>");
            _getListForField(field, self.view.model).then(function(list) {
              _appendOptions($input, list);
            });
          } else if (field.toLowerCase() === "filename") {
            $input = $("<input />", { type: "file", class: "file", "data-show-upload":false});
          } else {
            var type = "text";
            if (_.isDate(value) || field.toLowerCase().endsWith("date")) {
              type = "date";
            } else if (_.isNumber(value)) {
              type = "number";
            } else if (field.toLowerCase() === "password") {
              type = "password";
            }
            $input = $('<input type="' + type + '" name="' + field + '" class="form-control">');
          }
          $input.addClass(self.options.fieldSelector);
          if (_.contains(self.options.readonly, field)) {
            $input.prop("disabled", true);
          }
          $field.append($input);
          $div.append($field);
        }
        $ins.append($div);
      });

      // non_field_errors
      $ins.append($(
        '<div class="form-group field-non_field_errors">' +
          '<div class="col-sm-12 col-lg-offset-4 col-lg-8">' +
            '<div name="non_field_errors"></div>' +
          '</div>' +
        '</div>'
      ));
      
        //<div class="col-sm-8"><input type="date" name="medicalExpireDate" class="form-control app-field"></div></div>

      _.each(this.options.buttons, function(button) {
        button = _.defaults(button, {block:true, offset:0, large:12, type:"button"});
        var $btn;
        if (button.type === "link") {
          $btn = $("<a>", {
            class: "btn btn-primary"
          });
        } else {
          $btn = $("<button>", {
            type: "submit",
            class: "btn btn-primary",
            "data-loading-text": "Loading..."
          });
        }
        if (button.block) {
          $btn.addClass("btn-block");
        }

        if (button.name) {
          $btn
            .attr("name", button.name)
            .addClass("js-" + button.name);
        }

        //$btn.html(button.label);
        if (button.icon) {
          $btn.append($('<span class="glyphicon glyphicon-' + button.icon + '">&nbsp;</span>'));
        }
        $btn.children().after(button.label);

        $btn.appendTo('<div class="col-sm-offset-' + button.offset + ' col-sm-' + button.large + '">')
          .parent().appendTo('<div class="form-group">')
          .parent().appendTo($ins);
      });

      this.view._bindUIElements();
    }

  , onShow: function() {
      this.$('select').select2();
    },
  }),

  Behaviors.BindFieldsBehavior = Marionette.Behavior.extend({
    onRender: function() {
      var self  = this
        , $el   = this.view.$el
        , model = this.view.model;

      if (model === undefined) return;

      _.each(model.defaults, function(value, field) {
        var $input = $el.find('[name=' + field + ']')
          , value = model.get(field)
          , type;
        // ignoro se non trovo un elemento per l'attributo
        if ($input.length === 0) return;

        // initial value
        _setInputValue($input, value);

        // binding elemento --> attributo
        $input.on("change", function() {
          var value = _getInputValue($input);
          if (model.get(field) !== value) {
            model.set(field, value);
          }
        });

        // binding attributo --> elemento
        self.listenTo(model, "change:" + field, function(model, value, options) {
          _setInputValue($input, value);
        })
      })
    }
  });

  Behaviors.ValidationBehavior = Marionette.Behavior.extend({
    modelEvents: {
      'validated': 'setValidated',
      'change': "validate"
    }

  , onRender: function() {
      Backbone.Validation.bind(this.view);
      if (this.hasBeenValidated) {
        this.view.model.validate();
      }
    }

  , setValidated: function() {
      this.hasBeenValidated = true;
    }

  , validate: function() {
      if (this.hasBeenValidated) {
        this.view.model.validate();
      }
    }
  });

  Behaviors.SaveBehavior = Marionette.Behavior.extend({
    defaults: {
      fieldSelector: ":input"
    },

    onSave: function() {
      var view = this.view
        , model = this.view.model;
      console.log("SaveBehavior.onSave:" + JSON.stringify(model.attributes));
      this.$(this.options.fieldSelector).each(function() {
        var $el = $(this)
          , name = $el.attr("name");

        // ignoro gli input che non hanno un nome associato
        if (name === undefined) return;

        // ignoro gli input readonly
        if ($el.prop("readonly")) return;

        var value = _getInputValue($el);
        if (model.get(name) !== value) {
          model.set(name, value);
        }
      });

      if (model.isValid(true)) {
        var save = this.options.saveHandler;
        if (save) {
          save(model, view);
        } else {
          var callback = this.options.callback;
          view.ui.submit && view.ui.submit.button("loading");
          model.save({ wait: true })
            .then(function(updated) {
              model.set(updated.attributes);
              callback && callback(arguments);
            })
            .fail(function(resp) { 
              var errors = model.parse(resp.responseJSON);
              _.extend(errors, {non_field_errors: resp.responseJSON.non_field_errors});
              _.each(errors, function(error, name) {
                if (error) {
                  Backbone.Validation.callbacks.invalid(view, name, error);
                } else {
                  Backbone.Validation.callbacks.valid(view, name, error);
                }
              });
              view.ui.submit && view.ui.submit.button("reset");
            });
          }
      }
    }
  });

  /**
   * Compose Behavior for handling forms
   */
  Behaviors.FormBehavior = Marionette.Behavior.extend({
    defaults: {
      fieldSelector : 'app-field',
      skipFields    : [],
      readonly      : [],
      buttons       : []
    },

    behaviors: function() {
      return [{
        behaviorClass : Behaviors.GenerateFormBehavior,
        fieldSelector : this.options.fieldSelector,
        insertPoint   : this.options.insertPoint,
        fields        : this.options.fields,
        skipFields    : this.options.skipFields,
        readonly      : this.options.readonly,
        labels        : this.options.labels,
        modelClass    : this.options.modelClass,
        buttons       : this.options.buttons
      }, {
        behaviorClass : Behaviors.BindFieldsBehavior
      }, {
        behaviorClass : Behaviors.ValidationBehavior
      }, {
        behaviorClass : Behaviors.SaveBehavior,
        saveHandler   : this.options.saveHandler,
        callback      : this.options.saveCallback
      }];
    }
  });

  Behaviors.CascadingDropdownBehavior = Marionette.Behavior.extend({
    defaults: {
      bindings:{}
    }

  , onRender: function() {
      var self = this
        , model = this.view.model
        , $el = this.view.$el
        , bindings = this.options.bindings;

      _.each(_.keys(bindings), function(key) {
        self.listenTo(model, "change:" + key, function() {
          var array = bindings[key];
          if (!_.isArray(array)) {
            array = [array];
          }
          _.each(array, function(item) {
            model.set(item, model.__proto__.defaults[item]); // undefined);
            var $input = $el.find("[name=" + item + "]");
            if ($input.is("select")) {
              $input.select2("val", model.__proto__.defaults[item]); //undefined);
              $input.html("");

              _getListForField(item, model).then(function(list) {
                _appendOptions($input, list);
              });
            } else {
              $input.val("");
            }
          });
        });
      });
    }
  });

  Behaviors.CascadingDefaultBehavior = Marionette.Behavior.extend({
    defaults: {
      bindings:{}
    }

  , onRender: function() {
      var self      = this
        , model     = this.view.model
        , $el       = this.$el
        , bindings  = this.options.bindings;

      _.each(_.keys(bindings), function(key) {
        self.listenTo(model, "change:" + key, function() {
          _getListForField(key, model).then(function(list) {
            var obj   = _.find(list, { id: model.get(key) })
              , array = bindings[key];

            // Ignoro se non ho un oggetto da cui recuperare i valori di default
            if (obj === undefined) return;

            if (!_.isArray(array)) {
              array = [array];
            }
            _.each(array, function(item) {
              var def   = obj.get(item)
              , $input  = $el.find("[name=" + item + "]");

              if ($input.is("select")) {
                $input.select2("val", def);
              } else {
                $input.val(def);
              }
            });
          });
        });
      });
    }
  });

  Behaviors.ModalBehavior = Marionette.Behavior.extend({
    
    modelEvents: {
      "sync": "closeModal"
    },

    onCancel: function() {
      this.closeModal();
    },

    closeModal: function() {
      var region = WMS.getRegion("modalRegion");
      if (region) region.closeModal();
    }
  });

  Behaviors.SelectableBehavior = Marionette.Behavior.extend({
    defaults: {
      className:"active"
    , condition: null
    }

  , events: {
      'click':'onClick'
    }

  , modelEvents: {
      "selected"  : "onRender"
    , "deselected": "onRender"
    }

  , onClick: function() {
      if (this.options.condition) {
        if (!_.isMatch(this.view.model.attributes, this.options.condition)) {
          alert(this.options.failureMsg || 'Riga non selezionabile.');
          return;
        }
      } 
      if (this.view.model["toggleSelected"]) {
        this.view.model.toggleSelected();
      }
      var eventName = this.view.model.selected ? 'selected' : 'unselected';
      this.view.trigger(eventName);
    }

  , onRender: function() {
      if (this.view.model.selected) {
        this.$el.addClass(this.options.className);
      } else {
        this.$el.removeClass(this.options.className);
      }
    }
  });

  Behaviors.UpdateBehavior = Marionette.Behavior.extend({
    defaults: {
      cssClass: "info"
    }

  , modelEvents: {
      "change": "modelChanged"
    }

  , modelChanged: function(model) {
      this.view.render().flash(this.options.cssClass);
    }
  });

  Behaviors.DetailsBehavior = Marionette.Behavior.extend({
    defaults: {
      insertPoint: "form.form",
      eventPrefix: "",
      fields:[]
    },

    onRender: function() {
      var $el   = this.$el
        , model = this.view.model
        , opt   = this.options;

      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      _.each(this.options.fields, function(field) {
        if (_.isString(field)) {
          field = { name: field };
        }
        
        field = _.defaults(field, {type: 'text', cols: 6, labelCols: 4, fieldCols: 8});

        var $field = $('<div class="col-sm-' + field.cols + '"></div>');
        $field.addClass(field.className);

        var label = "";
        if (field.label !== false) {
          // Cerco label in modo gerarchico.
          if (opt.labels) {
            label = (WMS.labels[opt.labels] || {})[field.name] || field.name;
          } else if (opt.modelClass) {
            label = ((opt.modelClass.prototype || {}).labels || {})[field.name] || field.name;
          } else {
            label = field.name;
          }
        }
        if (field.type === "actions") {
          $field.addClass(field.className);
        } else if (field.type === "checkbox") {
          var $lbl = $('<label><input type="checkbox" name="' + field.name + '" disabled="disabled">' + label + '</label>');
          var $checkbox = $('<div class="checkbox"></div>')
            .append($lbl);
            
          $checkbox.appendTo($field);
          if (model && model.get(field.name)) {
            $checkbox.find("input").prop('checked', true);
          }
          
        } else {
          var $grp = $('<div class="form-group"></div>');
          if (field.label !== false) {
            var $label = $('<label class="col-sm-' + field.labelCols +' control-label"></label>');
            $label
              .attr('for', field.name)
              .append(label + ":")
              .appendTo($grp);
          }

          var $div  = $('<div class="col-sm-' + field.fieldCols + '">')
            , $input= $('<input type="' + field.type + '" name="' + field.name + '" class="form-control" readonly />');

          if (model) {
            var value = model.get(field.name)
              , name  = field.name.toLowerCase();
            if (name.endsWith("id")) {
              // recupero label 
              _lookupValue(model, field.name, $input);
            } else if(name.endsWith("date")) {
              var date = model.get(field.name);
              if (date) {
                $input.val(date.toString("yyyy-MM-dd"));
              }
            } else {
              $input.val(value);
            }
          } 
          $input.appendTo($div)
          $div.appendTo($grp);
          $grp.appendTo($field);
        }
        $field.appendTo($el);
      });
    }
  });

  Behaviors.AddRowBehavior = Marionette.Behavior.extend({
    defaults: {
      className     : "js-add",
      icon          : "plus",
      disableMethod : "canAddRows",
      tooltip       : "Nuova riga"
    }

  , triggers: function() {
      var hash = {}
        , model= this.view.model
        , name;
      if (this.options.eventName) {
        name = this.options.eventName;
      } else if (model && model.constructor.modelName) {
        name = model.constructor.modelName + ":row:add";
      } else {
        name = "row:add"
      }
      hash["click ." + this.options.className] = name;
      return hash;
    }

  , onRender: function() {
      var $el   = this.$el
        , model = this.view.model;

      if (this.options.insertPoint !== undefined) {
        $el = $el.find(this.options.insertPoint);
      }

      var $a = _renderButton(this.options.className, this.options.icon, null, this.options.tooltip);
      $a.appendTo($el);

      var method = this.options.disableMethod;
      if (!model) { 
        $a.addClass("hidden");
      } else if (_.isFunction(model[method]) && !model[method]()) {
        $a.addClass("hidden");
      }
    }
  });

  Behaviors.AddBehavior = Marionette.Behavior.extend({
    defaults: {
      cssClass: "success"
    }

  , collectionEvents: {
      "add": "modelAdded"
    }

  , initialize: function() {
    this.models = [];
  }
    // Salvo localmente il modello appena creato
  , modelAdded: function(model) {
      this.models.push(model);
    }

    // Evidenzio la view se visualizza uno dei modelli creati
  , onAddChild: function(childView) {
      var model = childView.model;
      if (_.contains(this.models, model)) {
        childView.flash(this.options.cssClass);
        this.models = _.without(this.models, model);
      }
    }
  });

  var ShowButtonBehavior = Marionette.Behavior.extend({
    defaults: {
      before: true,
      modelOptions: []
    },

    onAttach: function() {
      var collection = this.view.collection
        , $el = this.$el;

      if (!this._showButton()) return;

      var ip = this.options.insertPoint;
      if (ip) {
        $el = $el.find(ip);
      }

      var $btn = _renderButton(this.options.className, this.options.icon, this.options.label);
      if (this.options.before) {
        $el.prepend($btn);  
      } else {
        $el.append($btn);
      }
    }

  , _showButton: function() {
      return true;
    }
  });

  var ShowAddButtonBehavior = ShowButtonBehavior.extend({
    defaults: _.extend({
      className: "js-add"
    , icon: "plus"
    , label: "Nuovo"
    }, ShowButtonBehavior.prototype.defaults)

  , events: function() {
      var hash = {};
      hash["click ." + this.options.className] = "showModalForm"
      return hash;
    }

  , showModalForm: function(e) {
      e.preventDefault();

      var klass = this.options.FormView;
      if (!klass) return;

      var options = this._setupOtions();
      var model = this._createModel(options);
      if (!model) return;

      WMS.showModal(new klass({ model: model }));
    }

  , _setupOtions: function() {
      return {};
    }
  , _createModel: function() {
      return null;
    }
  });

  Behaviors.AddModelBehavior = ShowAddButtonBehavior.extend({
    _showButton: function() {
      var opt = this.options;
      return opt.modelClass && opt.modelClass.canCreate();
    }

  , _createModel: function(options) {
      var klass = this.options.modelClass;
      if(!klass) return;

      return new klass(_.pick(options, _.keys(klass.prototype.defaults)));
    }
  });

  Behaviors.AddItemBehavior = ShowAddButtonBehavior.extend({
    _showButton: function() {
      var collection = this.view.collection;
      return collection && collection.canCreate();
    }  

  , _setupOtions: function() {
      var options = {}
        , collection = this.view.collection;
      _.each(this.options.modelOptions, function(key) {
        options[key] = collection.attr(key);
      });
      return options;
    }

  , _createModel: function(options) {
      var collection = this.view.collection;
      return new collection.model(_.pick(options, _.keys(collection.model.prototype.defaults)));
    }
  });

  Behaviors.DropdownBehavior = ShowButtonBehavior.extend({
    defaults: _.extend({
      className: "js-drop"
    , icon: "download-alt"
    , label: "Drop"
    }, ShowButtonBehavior.prototype.defaults)

  , triggers: function() {
      var hash = {}
        , eventName = this.options.eventPrefix ? this.options.eventPrefix + ":drop" : "drop";
      hash["click ." + this.options.className] = eventName
      return hash;
    }

  , initialize: function() {
      var className = "." + this.options.className;

      this.view.hideDropButton = function() {
        this.$el.find(className).addClass("hidden");
      }

      this.view.showDropButton = function() {
        this.$el.find(className).removeClass("hidden");
      }
    }
  })

  Behaviors.TabPanelBehavior = Marionette.Behavior.extend({
    defaults: {
      className     : "nav nav-tabs"
    , tabs          : []
    }

  , triggers: function() {
      var hash = {};
      _.each(this.options.tabs, function(tab) {
        hash["click #" + tab] = tab + ":show";
      });
      return hash;
    }
  , initialize: function() {
      var className = this.options.className
        , tabs = "." + className.split(" ").join(".");

      this.view.setActiveTab = function(name) {
        var $tabs = this.$el.find(tabs);
        $tabs.find("li").removeClass("active");
        $tabs.find("#" + name).addClass("active");
      }
    }

  , onRender: function() {
      var $el = this.$el
        , opt = this.options;

      if (opt.insertPoint) {
        $el = $el.find(opt.insertPoint);
      }

      var $ul = $("<ul class='" + opt.className + "'></ul>");

      // Spazio per inserire i bottoni prima delle tabs
      $ul.append($(
        "<li role='presentation'>" + 
          "<p class='navbar-btn actions-bar pre'></p>" +
        "</li>"
      ));


      _.each(opt.tabs, function(tab) {
        var label = tab;
        if (opt.labels && WMS.labels[opt.labels]) {
          label = WMS.labels[opt.labels][tab] || tab;
        }
        $ul.append($(
          "<li role='presentation' id='" + tab + "' >" +
            "<a>" + label + "</a>" +
          "</li>"
        ));
      });

      $ul.append($(
        "<li role='presentation' class='pull-right'>" +
          "<p class='navbar-btn actions-bar post'></p>" +
        "</li>"
      ));
      $ul.appendTo($el);
    }
  });

  Behaviors.EditableBehavior = Marionette.Behavior.extend({
    defaults: {
      icon          : "pencil"
    , before        : false
    , button        : true
    }

  , events: {
      "click .js-edit": "editModel"
    }

  , onRender: function() {
      var $el   = this.$el
        , model = this.view.model
        , opt   = this.options;

      if (model.isNew()) return;

      if (opt.insertPoint) {
        $el = $el.find(opt.insertPoint);
      }

      var $a; 
      if (opt.button) {
        $a = _renderButton("js-edit", opt.icon, opt.label);
      } else {
        $a = _renderSpanButton("js-edit", opt.icon, opt.label);
      }
      if (opt.before) {
        $el.prepend($a);
      } else {
        $el.append($a);
      }

      if (!model.canUpdate()) {
        $a.addClass("hidden");
      }
    }

  , editModel: function(e) {
      e.preventDefault();
      e.stopPropagation();

      var model = this.view.model
        , klass = this.options.FormView;

      if (model.canUpdate()) {
        this.view.trigger(model.constructor.modelName + ":edit", model);
        if (!klass) return;

        // clono il modello per il rollback
        var view = new klass({ model: model.clone() });
        WMS.showModal(view);        
      } else {
        WMS.showError("Operazione non consentita.");
      }
    }
  });
  
  Behaviors.AttachableBehavior = Marionette.Behavior.extend({
    defaults: {
      icon: "paperclip"
    , before: false
    , button: true
    }

  , events: {
      "click .js-attach": "attachFile"
    }

  , onRender: function() {
      var $el   = this.$el
        , model = this.view.model
        , opt   = this.options;

      if (opt.insertPoint) {
        $el = $el.find(opt.insertPoint);
      }

      var $a; 
      if (opt.button) {
        $a = _renderButton("js-attach", opt.icon, opt.label);
      } else {
        $a = _renderSpanButton("js-attach", opt.icon, opt.label);
      }
      if (opt.before) {
        $el.prepend($a);
      } else {
        $el.append($a);
      }

      if (!model.canUpdate() || !this.options.FormView) {
        $a.addClass("hidden");
      }
    }

  , attachFile: function(e) {
      e.preventDefault();
      e.stopPropagation();

      var model = this.view.model
        , klass = this.options.FormView;

      if (model.canUpdate()) {
        if (!klass) return;

        var options = {};
        _.each(this.options.formOptions, function(attr, opt) {
          options[opt] = model.get(attr);
        });

        var view = new klass(options);
        view.on("attach", function() {
          this.$el.find(".file:input[type=file]").fileinput();
        });
        view.on("save", function() {
          var attr = this.model.fileAttribute;
          if (attr) {
            this.model.set(attr, this.$el.find(".file:input[type=file]")[0].files[0]);
          }
        });
        WMS.showModal(view);        
      } else {
        WMS.showError("Operazione non consentita.");
      }
    }
  });

  Behaviors.DestroyableBehavior = Marionette.Behavior.extend({
    defaults: {
      icon          : "trash"
    , before        : false
    , button        : true
    }

  , events: {
      "click .js-destroy": "destroyModel"
    }

  , onRender: function() {
      var $el   = this.$el
        , model = this.view.model
        , opt   = this.options
        , klass = opt.modelClass;

      if (opt.insertPoint) {
        $el = $el.find(opt.insertPoint);
      }

      var $a; 
      if (opt.button) {
        $a = _renderButton("js-destroy", opt.icon, opt.label);
      } else {
        $a = _renderSpanButton("js-destroy", opt.icon, opt.label);
      }
      if (this.options.before) {
        $el.prepend($a);
      } else {
        $el.append($a);
      }

      if (!model.canUpdate()) {
        $a.addClass("hidden");
      }
    }

  , destroyModel: function(e) {
      e.preventDefault();
      e.stopPropagation();

      var model = this.view.model;

      if (model.canDestroy()) {
        if (confirm("Eliminare " + model + "?")) {
          model
            .destroy({ wait: true })
            .then(function() {
              WMS.showSuccess(model + " eliminato con successo.");
            })
            .fail(function(xhr) {
              WMS.showError(xhr.responseJSON.non_field_errors);
            });
        }
      } else {
        WMS.showError("Operazione non consentita.");
      }
    }
  });

  Behaviors.ClonableBehavior = Marionette.Behavior.extend({
    defaults: {
      insertPoint : undefined,
      className   : "js-clone",
      icon        : "duplicate",
      tooltip     : "Clona"
    },

    triggers: function() {
      var hash = {};
      hash["click ." + this.options.className] = this.view.model.constructor.modelName + ":clone"
      return hash;
    },

    onRender: function() {
      var $el   = this.$el
        , model = this.view.model
        , name  = model.constructor.modelName;

      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      var $a = _renderButton(this.options.className, this.options.icon, null, this.options.tooltip);
      $a.appendTo($el);

      if (model.isNew()) {
        $a.addClass("hidden");
      }
    }
  });

  Behaviors.PrintableBehavior = Marionette.Behavior.extend({
    defaults: {
      insertPoint : undefined,
      className   : "js-print",
      icon        : "print",
      tooltip     : "Stampa"
    }

  , onRender: function() {
      var $el   = this.$el
        , model = this.view.model;

      if (this.options.insertPoint !== undefined) {
        $el = $el.find(this.options.insertPoint);
      }

      var $a = _renderButton(this.options.className, this.options.icon, null, this.options.tooltip);
      $a.appendTo($el);

      if (model.isNew()) {
        $a.addClass("hidden");
      }

      var name = model.constructor.modelName
        , url = WMS.request("get:" + name + ":print:url", model.get('id'));
      $a.prop("href", url);
    }
  });

  Behaviors.UnlinkBehavior = Marionette.Behavior.extend({
    defaults: {
      insertPoint: undefined,
      className: 'js-unlink',
      icon: 'scissors',
      tooltip: 'Dissocia'
    },

    triggers: {
      'click .js-unlink': 'unlink:invoice'
    },

    onRender: function() {
      var $el = this.$el;
      var model = this.view.model;

      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      var $a = _renderButton(this.options.className, this.options.icon, null, this.options.tooltip);
      $a.appendTo($el);

      if (model.isNew()) {
        $a.addClass("hidden");
      }
    }
  })

  Behaviors.TableRowBehavior = Marionette.Behavior.extend({
    defaults: {
      tagName: "td",
      insertPoint: undefined,
      enableEdit:true,
      enableDestroy:true,
      fields: []
    },

    events: {
      "mouseenter": "onMouseEnter",
      "mouseleave": "onMouseLeave"
    },

    onRender: function() {
      var $el = this.$el
        , tagName = this.options.tagName
        , model = this.view.model;
      if (this.options.insertPoint) {
        $el = this.$el.find(this.options.insertPoint);
      }
      _.each(this.options.fields, function(field) {
        _renderCell($el, tagName, field, model);
      });

      // aggiungo actions;
      this.$actions = $("<" + tagName + " class='actions text-right'></" + tagName + ">");
      this.$actions.addClass("hidden");
      $el.append(this.$actions);
    }

  , onMouseEnter: function() {
      this.$actions.removeClass("hidden");
    }

  , onMouseLeave: function() {
      this.$actions.addClass("hidden");
    }
  });

  Behaviors.ColumnTotalBehavior = Marionette.Behavior.extend({
    defaults: {
      rowTag      : "tr"
    , cellTag     : "th"
    , insertPoint : "tfoot"
    , totals      : []
    }

  , collectionEvents: {
      "change reset add remove": "updateTotal"
    }

  , onRender: function() {
    this.updateTotal();
  }

  , updateTotal: function () {
      var collection = this.view.collection;

      // Se non ho modelli, non mostro il totale
      if (!collection || collection.length === 0) return;

      var $el = this.$el
        , tag = this.options.cellTag
        , $row = $("<" + this.options.rowTag + "></" + this.options.rowTag + ">");

      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      $el.empty();

      _.each(this.options.totals, function(total) {
        var $cell = $("<" + tag + "></" + tag + ">");
        if (total !== undefined) {
          if (_.isString(total)) {
            total = {attr:total};
          }
          $cell.addClass(total.className);
          var result = _.result(collection, "get" + total.attr.capitalize());
          if (total.format === "money") {
            result = result.formatMoney();
          }
          if (total.format === "price") {
            result = result.formatPrice();
          }
          $cell.html(result);
        }
        $cell.appendTo($row)
      });
      $row.appendTo($el);
    }
  });

  Behaviors.DrillDownBehavior = Marionette.Behavior.extend({
    defaults: {
      total: true
    }

  , events: {
      'click .js-expand': 'expand'
    , 'click .js-contract': 'contract'
    //, "click": "onClick"
    },

    onRender: function() {
      var $cell = $("<td></td>");
      $cell.append("<span class='glyphicon glyphicon-plus js-expand'></span>");
      $cell.append("<span class='glyphicon glyphicon-minus js-contract'></span>");
      this.$el.prepend($cell).find(".js-contract").hide();
    },

    expand: function(e) {
      e.stopPropagation();
      if (this.details) {
        this.details.$el.fadeIn();
      } else {
        var self = this;
        // Nota: spostare il filtro dalla vista al controller
        this.view.model.getRows({where: this.options.filter, total: this.options.total}).then(function(collection) {
          self.details = new self.options.detailsView({
            collection: collection.multiSelect()
          });
          self.$el.after(self.details.render().$el);
          self.details.$el.fadeIn();
        });
      }
      this.$el.find(".js-expand").hide();
      this.$el.find(".js-contract").show();
    }

  , contract: function(e) {
      e.stopPropagation();
      this.details.$el.fadeOut();
      this.$el.find(".js-expand").show();
      this.$el.find(".js-contract").hide();
    }
/*
  , onClick: function() {
      var model = this.view.model
        , filter = this.options.filter
        , total = this.options.total;
      model.toggleSelected();
      if (model.selected) {
        this.$el.addClass("active");
        model.getRows({where: filter, total: total}).then(function(rows) {
          rows.multiSelect();
          rows.selectAll();
        });
      } else {
        this.$el.removeClass("active");
        model.getRows(filter).then(function(rows) {
          rows.multiSelect();
          rows.selectNone();
        });
      }
    }
  */
  });

  Behaviors.ListBehavior = Marionette.Behavior.extend({
    defaults: {
      skipFields: []
    }
  , onRender: function() {
      var model = this.view.model
        , skip = _.result(this.view, "skipFields", _.result(this.options, "skipFields", []));

      if (!model) return;
      if (model.canUpdate()) {
         _renderButton("js-edit", "pencil");
      }

      var $list = $("<dl class='dl-horizontal'></dl>");

      _.each(model.defaults, function(value, field) {
        if (_.contains(skip, field)) return;

        var label = field
          , $value = $("<dd></dd>");
        if (model.labels) {
          label = model.labels[field] || field;
        }

        var name = field.toLowerCase();
        if (name.endsWith("id")) {
          _lookupValue(model, field, $value);
        } else if (name.endsWith("date")) {
          var date = model.get(field);
          $value.html(date ? date.toString("dd/MM/yyyy") : "");
        } else if (_.isBoolean(value)) {
          var icon = model.get(field) ? "check" : "unchecked";
          $value.append($("<span class='glyphicon glyphicon-" + icon + "'></span>"));
        } else {
          $value.html(model.get(field));
        }
        $list.append($("<dt>" + label + ":</dt>"));
        $list.append($value);
      });

      var $el = this.$el;
      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }
      $el.append($list);
    }
  });

  Behaviors.ItemBehavior = Marionette.Behavior.extend({
    onRender: function() {
      var $el = this.$el
        , model = this.view.model;

      if (!model) return;
      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      if (model.canUpdate()) {
        $el.append($('<span class="js-edit"><span class="glyphicon glyphicon-pencil"></span></span>'));
      }

      if (model.canDestroy()) {
        $el.append($('<span class="js-delete"><span class="glyphicon glyphicon-trash"></span></span>'));
      }

      $el.addClass("hidden");
    }
  , events: {
        "mouseenter": "showActions"
      , "mouseleave": "hideActions"
      , "click .js-edit": "editModel"
      , "click .js-delete": "destroyModel"
    }

  , showActions: function(e) {
      var $el = this.$el;
      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }
      $el.removeClass("hidden");
    }

  , hideActions: function(e) {
      var $el = this.$el;
      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }
      $el.addClass("hidden");
    }

  , editModel: function(e) {
      e.preventDefault();
      var klass = this.options.FormView;
      if (!klass) return;

      // clono il modello attuale in modo che, se annullo le modifiche, esse non si riflettano
      // sul modello originale
      var view = new klass({model: this.view.model.clone() });
      WMS.showModal(view);
    }

  , destroyModel: function(e) {
      e.preventDefault();
      var model = this.view.model;
      if (confirm("Eliminare " + model + "?")) {
        model.destroy();
      }
    }
  });

  Behaviors.LookupBehavior = Marionette.Behavior.extend({
    defaults: {
      field: null
    , insertPoint: null
    }

  , onRender: function() {
      var model = this.view.model
        , $el = this.$el;
      if (!model) return;

      if (this.options.insertPoint) {
        $el = $el.find(this.options.insertPoint);
      }

      _lookupValue(model, this.options.field, $el);
    }
  });

  Behaviors.FilterBehavior = Marionette.Behavior.extend({
    initialize: function() {
      this.view.onSetFilterCriterion = function(criterion) {
        this.options.criterion = criterion;
        this.render();
      }

      var filter = this.options.filter;
      if (filter) {
        this.view.filter = function(child) {
          var criterion = this.getOption("criterion");
          return child.matchesFilter(criterion) 
            ? filter.call(this, child)
            : false; 
        }
      } else {
        this.view.filter = function(child) {
          var criterion = this.getOption("criterion");
          return child.matchesFilter(criterion);
        }
      }
    }
  });

  Behaviors.OffcanvasBehavior = Marionette.Behavior.extend({
    defaults: {
      parent: ".row"
    , direction: "right"
    }

  , initialize: function() {
      this.$toggler = new Marionette.ItemView({
        template: _.template(
          "<span class='glyphicon glyphicon-chevron-right'>&nbsp;</span>" +
          "<span class='glyphicon glyphicon-chevron-left'>&nbsp;</span>"
        )

      , className: "toggler hidden-md"

      , events: {
          "click": function() {
            this.trigger("toggle");
          }
        }
      });

      this.listenTo(this.$toggler, "toggle", this.toggle);
    }

  , onRender: function() {
      this.$el.addClass("hidden-sm");
    }

  , onAttach: function() {
      this.$el.parent()
        .append(this.$toggler.render().$el)
        .addClass("sidebar-offcanvas");
      this.$target = this.$el.parents(this.options.parent);
      this.$target.addClass("row-offcanvas row-offcanvas-" + this.options.direction);
    }

  , onBeforeDestroy: function() {
      this.$toggler.destroy();
      this.$target.removeClass("row-offcanvas row-offcanvas-" + this.options.direction + " active");
      this.$el.parent().removeClass("sidebar-offcanvas");
    }

  , toggle: function() {
      this.$target.toggleClass("active");
      this.$el.toggleClass("hidden-sm");
    }
  });

  Behaviors.ResizableBehavior = Marionette.Behavior.extend({
    defaults: {

    }

  , onAttach: function() {
      var self = this;
      var wrapper = this.$el.parent();

      this.$handler = new Marionette.ItemView({
        template: _.template("Click and drag me")
      
      , className: "resize-handler hidden"
      
      , events: {
          "mousedown": function(e) {
            var mouseStartY = e.pageY;
            var resizeStartHeight = wrapper.height();

            $(document)
              .on( 'mousemove.resize', function (e) {
                var height = resizeStartHeight + (e.pageY - mouseStartY);
                if ( height < 180 ) {
                  height = 180;
                }

                wrapper.height( height );
              } )
              .on( 'mouseup.resize', function (e) {
                $(document).off( 'mousemove.resize mouseup.resize' );
              } );

            return false;
          }
        }
      });
      
      wrapper.addClass("resize-wrapper")
        .on("mouseenter.resize", function() {
          self.$handler.$el.removeClass("hidden");
        })
        .on("mouseleave.resize", function() {
          self.$handler.$el.addClass("hidden");
        })
        .append(this.$handler.render().$el);
    }

  , onBeforeDestroy: function() {
      this.$handler.destroy();
      this.$el.parent().off("mouseenter.resize mouseleave.resize");
    }
  });

  Behaviors.CollapsableBehavior = Marionette.Behavior.extend({
    defaults: {
      collapsed: false
    },

    ui: {
      "header": "div.panel-heading",
      "body"  : "div.panel-body",
      "thead" : "table thead",
      "tbody" : "table tbody",
      "tfoot" : "table tfoot",
      "list"  : "ul.list-group"
    },

    events: {
      "click @ui.header": "toggleCollapse"
    },

    _collapsedIcon: "glyphicon-chevron-down",
    _expandedIcon: "glyphicon-chevron-up",

    onRender: function() {
      this._collapsed = this.options.collapsed;
      $icon = $("<i class='pull-right glyphicon'></i>");
      $icon.addClass(this._collapsed ? this._collapsedIcon : this._expandedIcon);
      this.ui.icon = $icon;
      this.ui.header.append($icon);
      var className = "collapse " + (this._collapsed ? "out" : "in");
      var showHide = this._collapsed ? "hide" : "show";

      this.ui.body && this.ui.body.addClass(className);
      
      this.ui.thead && this.ui.thead[showHide]();
      this.ui.tbody && this.ui.tbody.addClass(className);
      this.ui.tfoot && this.ui.tfoot[showHide]();

      this.ui.list && this.ui.list.addClass(className);
    },

    toggleCollapse: function() {
      if (this._collapsed) {
        this._collapsed = false;
        this.ui.icon
          .removeClass(this._collapsedIcon)
          .addClass(this._expandedIcon);
        this.ui.body && this.ui.body.collapse("show");
        this.ui.thead && this.ui.thead.show();
        this.ui.tbody && this.ui.tbody.collapse("show");
        this.ui.tfoot && this.ui.tfoot.show();
        this.ui.list && this.ui.list.collapse("show");
      } else {
        this._collapsed = true;
        this.ui.icon
          .removeClass(this._expandedIcon)
          .addClass(this._collapsedIcon);
        this.ui.body && this.ui.body.collapse("hide");
        this.ui.thead && this.ui.thead.hide();
        this.ui.tbody && this.ui.tbody.collapse("hide");
        this.ui.tfoot && this.ui.tfoot.hide();
        this.ui.list && this.ui.list.collapse("hide");
      }
    }
  });
});