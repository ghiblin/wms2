WMS.module('Employees', function(Employees, WMS, Backbone, Marionette, $, _) {
  var EmployeeForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , insertPoint   : 'div.modal-body'
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });
  
  Employees.Forms = {
    Edit: EmployeeForm.extend({
      title: 'Aggiorna Dipendente'
    , saveButtonText: 'Aggiorna'
    })

  , New: EmployeeForm.extend({
      title: 'Nuovo Dipendente'
    , saveButtonText: 'Crea Dipendente'
    })
  }
});