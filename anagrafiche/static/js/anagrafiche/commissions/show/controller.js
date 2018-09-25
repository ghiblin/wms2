WMS.module("Commissions.Show", function(Show, WMS, Backbone, Marionette, $, _) { 
  var Views = Show.Views;

  Show.Controller = Marionette.ShowController.extend({
    prefetchOptions: [
      { request: "get:commission", name: "commission", options: ["id"] }
    , { request: "get:commission:costs", name: "costs", options: ["id"] }
    , { request: "get:commission:files", name: "files", options: ["id"] }
    ]

  , regions : [{
      name      : "titleRegion"
    , View      : Views.Title
    , options   : {
        title     : "@commission.description"
      }
    }, { 
      name      : 'detailsRegion'
    , View      : Views.Details
    , options   : {
        model     : "@commission"
      }
    }, {
      name      : 'costsRegion'
    , View      : Show.Views.Costs
    , permission: "commission:get_costi"
    , options   : {
        collection: "@costs"
      }
    }, {
      name      : "publicFilesRegion",
      View      : Views.FileList,
      permission: "commission:get_file_pubblico",
      options   : {
        collection: "@files",
        private   : false
      },
      events: {
        "attachment:destroy": "onAttachmentDestroy"
      }
    }, {
      name      : "privateFilesRegion",
      View      : Views.FileList,
      permission: "commission:get_file_privato",
      options   : {
        collection: "@files",
        private   : true
      },
      events: {
        "attachment:destroy": "onAttachmentDestroy"
      }
    }, {
      name      : "estimatesRegion",
      View      : Views.Estimates,
      options   : {
        collection: "@commission.estimates"
      }
    }, {
      name      : "ordersRegion",
      View      : Views.Orders,
      options   : {
        collection: "@commission.orders"
      }
    }, {
      name      : "notesRegion",
      View      : Views.Notes,
      options   : {
        collection: "@commission.notes"
      }
    }, {
      name      : "invoicesRegion",
      View      : Views.Invoices,
      options   : {
        collection: "@commission.invoices"
      }
    }]

  , initialize: function() {
      var self = this;

      this.listenTo(WMS.vent, "commission:updated", function(commission) {
        if (self.options.id === commission.get("id")) {
          self.options.commission.set(commission.attributes);
        }
      });

      this.listenTo(WMS.vent, "commission:attachment:created", function(attachment) {
        if (WMS.modalRegion.currentView) WMS.modalRegion.currentView.trigger("close");
        self.options.files.fetch();
      });
    }

  , showCommission: function(id) {
      this.options.id = id;
      
      var self = this;
      this.start().then(function() {
        var commission = self.options.commission;
        if (commission) {
          var layout = self._layout = new Views.Layout();
          layout.on('show', function() {
            self.setupRegions(layout);
          });
        } else {
          self._layout = new Views.Error({ message: "Commessa non trovata." });
        }
        WMS.mainRegion.show(self._layout);
      });
    }

  , onAttachmentDestroy: function(view) {
      var model = view && view.model;
      if (model) model.destroy({wait:true});
    }
  });
});