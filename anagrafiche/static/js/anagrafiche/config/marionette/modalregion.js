Marionette.ModalRegion = Marionette.Region.extend({
  initialize: function() {
    var self = this;
    this.$el.on('hidden.bs.modal', function() {
      self.empty();
    });
  },
  onShow: function(view) {
    var self = this;
    this.listenTo(view, 'modal:close', this.closeModal);
    this.listenTo(view, 'close', this.closeModal);
    this.$el.modal('show');
  },
    closeModal: function() {
    this.stopListening();
    this.$el.modal('hide');
  }});