WMS.module("Header", function(Header, WMS, Backbone, Marionette, $, _) {
  var API = {
    listHeaders: function() {
      Header.List.Controller.listHeaders();
    }
  };
  
  WMS.commands.setHandler('set:active:header', function(name) {
    Header.List.Controller.setActiveHeader(name);
  });
  
  Header.on('start', function() {
    API.listHeaders();
    
    WMS.getSession().on('change:authenticated', function() {
      API.listHeaders();
    });
  });
});