WMS.module('Sheets', function(Sheets, WMS, Backbone, Marionette, $, _) {
  var SheetForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , fieldSelector : 'app-field'
    , insertPoint   : 'div.modal-body'
    , skipFields    : ["employeeId"]
    , modelClass    : WMS.Models.Sheet
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });

  
  Sheets.Forms = {
    Edit: SheetForm.extend({
      title         : 'Aggiorna Consuntivo'
    , saveButtonText: 'Aggiorna'
    })

  , New: SheetForm.extend({
      title         : 'Nuovo Consuntivo'
    , saveButtonText: 'Crea Consuntivo'
    })
  }
});