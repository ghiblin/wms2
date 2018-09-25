WMS.module('Commissions', function(Commissions, WMS, Backbone, Marionette, $, _) {

  var CommissionForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , insertPoint   : 'div.modal-body'
    , readonly      : ['code']
    }, {
      behaviorClass : WMS.Common.Behaviors.CascadingDropdownBehavior
    , bindings      : {
        clientId: ["destinationId"]
      }
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });  

  Commissions.Forms = {
    New: CommissionForm.extend({
      title         : "Nuova Commessa"
    , saveButtonText: "Crea Commessa"
    })

  , Edit: CommissionForm.extend({
      title         : "Aggiorna Commessa"
    , saveButtonText: "Aggiorna"
    })
  };
});