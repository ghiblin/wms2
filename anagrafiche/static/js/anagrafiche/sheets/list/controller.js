WMS.module("Sheets.List", function(List, WMS, Backbone, Marionette, $, _) {
  var Views = List.Views;

  List.Controller = Marionette.Controller.extend({
    Layout: Views.Layout

  , prefetchOptions: [{ 
      request   : "get:employeeHours:list"
    , name      : "hours"
    , options   : ["from", "to"]
    , cache     : false
    , select    : "single"
    }, { 
      request   : "get:sheet:list"
    , name      : "sheets"
    , options   : ["employeeId", "from", "to"]
    , cache     : false
    , select    : "multi" 
    }]

  , regions: [{
      name      : "titleRegion"
    , View      : Views.Title
    , options   : {
        title: "Consuntivi"
      }
    }, {
      name      : "filterRegion"
    , View      : Views.Filter
    , options   : {
      from: "@from",
      to: "@to"
    },
      events    : {
        "search":"search"
      }
    }, {
      name      : "masterRegion"
    , css       : { height: "188px" }
    , className : "scrollable"
    , stickyHeaders: true
    , View      : Views.Employees
    , options   : {
        collection : "@hours"
      }
    , viewName  : "_employees"
    , events    : {
        "employee:hours:selected": "selectEmployee"
      }
    }, {
      name      : "detailsRegion"
    , View      : Views.EmployeeDetails
    , options   : {
        model     : "@employeeHours"
      }
    , events    : {
        "sheet:new"   : "onSheetNew"
      }
    }, {
      name      : "rowsRegion"
    , View      : Views.Sheets
    , viewName  : "_sheets"
    , options   : {
        collection: "@sheets"
      }
    , events    : {
        "sheet:edit"  :"onSheetEdit"
      , "sheet:delete":"onSheetDelete"
      }
    }]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "sheet:created", function(sheet) {
        WMS.trigger("sheets:list", _.extend(self.options, {employeeId: sheet.get("employeeId") }));
      });

      this.listenTo(WMS.vent, "sheet:updated", function(sheet) {
        WMS.trigger("sheets:list", _.extend(self.options, {employeeId: sheet.get("employeeId") }));
      });
    }

  , listSheets: function(employeeId, from, to) {
      _.extend(this.options, {
        employeeId: employeeId
      , from      : from
      , to        : to
      });

      this.start().done(_.bind(function() {
        if (this.options.employeeId && this.options.hours) {
          this.options.employeeHours = this.options.hours.find({id: this.options.employeeId});
        } else {
          this.options.employeeHours = new WMS.Models.EmployeeHours();
        }
        if (this._layout && !this._layout.isDestroyed) {
          this.setupRegions(this._layout);
        } else {
          this._layout = new this.Layout();
          this._layout.on("show", _.bind(function() {
            this.setupRegions(this._layout);
          }, this));
          WMS.getRegion("mainRegion").show(this._layout);
        }
      }, this));
    }

  , search: function(args) {
      this.options = _.omit(this.options, "hours", "employee", "sheets");
      WMS.trigger("sheets:list", args.model.attributes);
    }

  , selectEmployee: function(args) {
      this.options = _.omit(this.options, "employee", "sheets");
      WMS.trigger("sheets:list", _.extend(this.options, {employeeId: args.model.get("id")}));
    }

  , onSheetNew: function(args) {
      var klass = WMS.Models.Sheet;
      if (klass.canCreate()) {
        var sheet = new klass({employeeId: this.options.employeeId})
        , view = new WMS.Sheets.Forms.New({ model: sheet });

        WMS.showModal(view)
      } else {
        WMS.showError("Operazione non consentita!");
      }
    }

  , onSheetEdit: function(view, args) {
      var sheet = args.model;

      if (sheet.canUpdate()) {
        var view = new WMS.Sheets.Forms.Edit({ model: sheet });

        WMS.showModal(view);
      } else {
        WMS.showError("Operazione non consentita!");
      }        
    }

  , onSheetDelete: function(view, args) {
      var sheet = args.model;
      if (sheet.canDestroy()) {
        if (confirm("Eliminare consuntivo " + sheet + "?")) {
          sheet.destroy();
        }
      } else {
        WMS.showError("Operazione non consentita!");
      }
      
    }
  });
});