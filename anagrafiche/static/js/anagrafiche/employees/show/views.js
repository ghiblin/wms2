WMS.module('Employees.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = Show.Views = _.extend({}, WMS.Employees.Forms);

  Views.EntityDetails = WMS.Common.Views.EntityDetails.extend({
    FormView: Views.Edit
  });
});