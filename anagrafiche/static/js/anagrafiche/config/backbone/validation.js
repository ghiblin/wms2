Backbone.Validation.configure({
  forceUpdate: true
, labelFormatter: "label"
});

_.extend(Backbone.Validation.callbacks, {
  valid: function(view, attr) {
    var $div = view.$el.find('form .field-' + attr);
    $div.removeClass('has-error');
    $div.find('small.help-block').remove();
  },
  invalid: function(view, attr, error) {
console.log('invalid!', attr, error);
    var $div = view.$el.find('form .field-' + attr);
    $div.addClass('has-error');
    var $msg = $div.find('small.help-block');
    if ($msg.length === 0) {
      $msg = $('<small class="help-block" />');
      $div.find('[name=' + attr + ']').after($msg);
    }
    if (_.isArray(error)) {
      error = error.join(', ');
    }
    $msg.html(error);
  }
});