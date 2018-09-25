WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  Models.EmployeeHours = Backbone.Model.extend({
    defaults: {
      firstName : "",
      lastName  : "",
      hours     : 0
    },

    maps: [
      { local: 'firstName', remote: 'nome' },
      { local: 'lastName', remote: 'cognome' },
      { local: 'hours', remote: 'ore_totali' }
    ],

    computed: {
      name: {
        depends: ['firstName', 'lastName'],
        get: function(fields) {
          return fields.firstName + ' ' + fields.lastName;
        }
      }
    }, 

    canAddSheet: function() { 
      return !this.isNew();
    }
  }, {
    _permission: "employeeHours"
  , modelName: "employee:hours"
  });
  
  Models.EmployeeHoursCollection = Backbone.Collection.extend({
    model: Models.EmployeeHours,
    url: '/api/v1/dipendente/get_ore/',

    initialize: function() {
      _.extend(this, new Backbone.Picky.SingleSelect(this));
      Backbone.Collection.prototype.initialize.call(this);
    }
  });

  Models.Sheet = Backbone.Model.extend({
    urlRoot: '/api/v1/consuntivo/',

    defaults: {
      employeeId  : null,
      commissionId: null,
      date        : Date.today(),
      hours       : 0,
      workTypeId  : null,
      note        : ""
    },

    maps: [
      { local: 'employeeId', remote: 'dipendente' },
      { local: 'commissionId', remote: 'commessa' },
      { local: 'workTypeId', remote: 'tipo_lavoro' },
      { local: 'workType', remote: 'tipo_lavoro_label' },
      { local: 'date', remote: 'data', type:'date' },
      { local: 'hours', remote: 'ore' },
      { local: 'note', remote: 'note' }
    ], 

    validation: {
      employeeId  : { required: true },
      commissionId: { required: true },
      workTypeId  : { required: true },
      hours       : { min: 0.5 }
    },

    getCommissions: WMS.getCommissions,
    getWorkTypes: WMS.getWorkTypes,
    toString:function() {
      var date = this.get('date');
      return (date ? date.toString('dd/MM/yyyy') : '') + " - " + this.get('hours');
    }
  }, {
    _permission: "sheets"
  , modelName: "sheet"
  });
  
  Models.Sheets = Backbone.Collection.extend({
    model: Models.Sheet,

    url: function() {
      return '/api/v1/dipendente/' + this.attr('employeeId') + '/consuntivo/';
    }, 

    parse: function(resp, options) {
      if (_.isArray(resp)) {
        resp = resp[0];
      }
      this.hours = resp.tatale_ore || 0;
      return resp.consuntivi;
    },

    getHours: function() {
      return this.reduce(function(memo, value) { 
        return memo + parseFloat(value.get('hours')); 
      }, 0);
    }
  }, {
    _permission:'sheets'
  });
  
  WMS.reqres.setHandler('get:employeeHours:list', function(params) {
    params = (params || {});
    var list = new Models.EmployeeHoursCollection();
    var defer = $.Deferred();
    var data = {};
    if (params.from) {
      data.da = params.from.toString('yyyy-MM-dd');
    }
    if (params.to) {
      data.a = params.to.toString('yyyy-MM-dd');
    }
    list.attr(params);
    list.fetch({
      data: data
    }).always(function() {
      defer.resolve(list);
    });
    
    return defer.promise();
  });
  
  WMS.reqres.setHandler('get:sheet:list', function(params) {
    var defer = $.Deferred();
    var sheets = new Models.Sheets();
    if (!params.employeeId) {
      defer.resolve(sheets);
    } else {
      sheets.attr(params);
      var data = {};
      data.da = params.from && params.from.toString('yyyy-MM-dd');
      data.a = params.to && params.to.toString('yyyy-MM-dd');
      sheets.fetch({
        data: data
      }).always(function() {
        defer.resolve(sheets);
      });
    }
    return defer.promise();
  });
  
  WMS.reqres.setHandler('get:sheet', function(id) {
    var defer = $.Deferred();
    if (typeof id === 'object' ? !id.id : !id) {
      defer.resolve(undefined);      
    }
    if (_.isObject(id)) {
      id = id.id;
    }
    var sheet = new Models.Sheet({id: id});
    sheet.fetch().always(function() {
      defer.resolve(sheet);
    });
    
    return defer.promise();
  });
});