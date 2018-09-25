WMS.module('Clients.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views = _.extend({}, WMS.Common.Views);

  Views.EntityDetails = WMS.Common.Views.EntityDetails.extend({
    FormView: Views.EntityForm.extend({
      title: 'Aggiorna Cliente',
      saveButtonText: 'Aggiorna'
    })
  });
});