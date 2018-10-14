WMS.module("Commissions.List", function(List, WMS, Backbone, Marionette) {
  var Views = _.extend({}, WMS.Common.Views, List.Views);

  List.Controller = Marionette.Controller.extend({
    prefetchOptions: [
      { request: 'get:commission:list', name: 'commissions', options:['from', 'to'] },
    ],

    regions: [
      {
        name: "titleRegion",
        View: Views.Title,
        options: {
          title: "Commesse"
        }
      }, {
        name: 'filterRegion',
        View: Views.FilterView,
        options : {
          clientId: "@clientId",
          from    : "@from",
          to      : "@to"
        },
        events: {
          'search': 'filterCommissions'
        }
      }, { 
        name: 'panelRegion',
        viewName: '_panel',
        View: List.Views.Panel,
        options: {
          criterion: "@criterion"
        },
        events: {
          "commissions:new": 'newCommission'
        }
      }, {
        name: 'masterRegion',
        viewName: '_commissions',
        View: List.Views.List,
        options: {
          collection: "@commissions",
          from      : "@from",
          to        : "@to",
        },
        events: {
          'commission:selected': 'selectCommission',
        },
      }, {
        name: 'paginatorRegion',
        viewName: '_paginator',
        View: List.Views.Paginator,
        options: {
          collection: "@commissions",
        },
      },
    ],

    initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "commission:created", function(commission) {
        self.options.commissions.add(commission);
      });

      this.listenTo(WMS.vent, "commission:updated", function(commission) {
        var model = self.options.commissions.find({ id: commission.get("id") });
        if (model) {
          model.set(commission.attributes);
        }
      });
    },

    listCommissions: function(from, to) {
      this.options.from = from;
      this.options.to = to;

      var self = this;
      this.start().then(function() {
        if (self._layout && !self._layout.isDestroyed) {
          self.setupRegions(self._layout);
        } else {
          self._layout = new Views.Layout();
          
          self._layout.on('show', function() {
            self.setupRegions(self._layout);
          });
          
          WMS.mainRegion.show(self._layout);
        }
      });
    },

    filterCommissions: function(args) {
      var c = this._commissions.collection;
      Object.keys(args.model.attributes).forEach(function(k) {
        c.attr(k, typeof args.model.get(k) === 'undefined' ? null : args.model.get(k));
      });
      c.fetch();
    },

    newCommission: function() {
      var klass = WMS.Models.Commission;
      if (klass.canCreate()) {
        var model = new klass()
          , view = new WMS.Commissions.Forms.New({ model: model });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    },
/*
  , editCommission: function(childView, args) {
      var commission = args.model;
      if (commission.canUpdate()) {
        var view = new WMS.Commissions.Forms.Edit({ model: commission });
        
        WMS.showModal(view);
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }

  , deleteCommssion: function(childView, args) {
      var commission = args.model;
      if (commission.canDestroy()) {
        if (confirm("Eliminare commessa " + commission + "?")) {
          commission.destroy();
        }
      } else {
        WMS.showError('Operazione non consentita!');
      }
    }
*/
    selectCommission: function(childView) {
      var commission = childView.model;
      if (commission.canRead()) {
        WMS.trigger("commissions:show", commission.get("id"));
      }
    },
  });
});