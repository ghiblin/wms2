WMS.module('Owner.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views = _.extend({}, WMS.Common.Views); //, WMS.Owner.Forms);

  Views.Edit = Views.EntityForm.extend({
    title         : 'Aggiorna Mr. Ferro'
  , saveButtonText: 'Aggiorna'
  });
  

  Views.EntityDetails = Views.EntityDetails.extend({
    FormView: Views.Edit
  });
});