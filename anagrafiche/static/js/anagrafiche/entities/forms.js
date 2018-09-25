WMS.module("Entities.Views", function(Views, WMS, Backbone, Marionette, $, _) {
  var form = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , insertPoint   : "div.modal-body"
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]
  });
  
  Views.Contact = {
    New: form.extend({
      modelClass    : WMS.Models.Contact
    , title         : 'Nuovo Contatto'
    , saveButtonText: 'Crea'
    })

  , Edit: form.extend({
      modelClass    : WMS.Models.Contact
    , title         : 'Modifica Contatto'
    , saveButtonText: 'Aggiorna'
    })
  };
  
  Views.Address = {
    New: form.extend({
      modelClass    : WMS.Models.Address
    , title         : 'Nuovo Indirizzo'
    , saveButtonText: 'Crea'
    })

  , Edit: form.extend({
      modelClass    : WMS.Models.Address
    , title         : 'Modifica Indirizzo'
    , saveButtonText: 'Aggiorna'
    })
  };

  Views.BankDatum = {
    New: form.extend({
      modelClass    : WMS.Models.BankDatum
    , title         : 'Nuove Coordinate Bancarie'
    , saveButtonText: 'Crea'
    })

  , Edit: form.extend({
      modelClass    : WMS.Models.BankDatum
    , title         : 'Modifica Coordinate Bancarie'
    , saveButtonText: 'Aggiorna'
    })
  };
  
  Views.Form = WMS.Common.Views.ModalFormView.extend({
    behaviors: [{
      behaviorClass : WMS.Common.Behaviors.FormBehavior
    , insertPoint   : "div.modal-body"
    , readonly      : ["code"]
    , skipFields    : ["addresses", "contacts", "bankData"]
    }, {
      behaviorClass : WMS.Common.Behaviors.ModalBehavior
    }]

  , modelEvents: {
      "change": "showHideFields"
    }

  , showHideFields: function() {
      if (this.model.get("typeId") === "G") {
        this.$el.find(".field-corporateName").removeClass("hidden");
        this.$el.find(".field-firstName").addClass("hidden");
        this.$el.find(".field-lastName").addClass("hidden");
      } else {
        this.$el.find(".field-corporateName").addClass("hidden");
        this.$el.find(".field-firstName").removeClass("hidden");
        this.$el.find(".field-lastName").removeClass("hidden");
      }
    }

  , onShow: function() {
      this.showHideFields();
    }
  });
});
