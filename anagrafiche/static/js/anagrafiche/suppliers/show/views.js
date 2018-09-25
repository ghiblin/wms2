WMS.module('Suppliers.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views = {};

  Views.EntityDetails = WMS.Common.Views.EntityDetails.extend({
    FormView: WMS.Common.Views.EntityForm.extend({
      title         : "Aggiorna Fornitore",
      saveButtonText: "Aggiorna"
    })
  });
});