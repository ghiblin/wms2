WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  Models.Employee = Backbone.Model.extend({
    urlRoot: '/api/v1/dipendente'

  , defaults: {
      serialNumber      : ""
    , firstName         : ""
    , lastName          : ""
    , taxCode           : ""
    , bypassTaxCode     : false
    , costPerHour       : 0
    , recruitmentDate   : null
    , cessationDate     : null
    , medicalExpireDate : null
    , mobilePhone       : ""
    , active            : true
    , direct            : true
    , internal          : true
    },

    maps: [
      { local:'firstName',          remote:'nome'                                 },
      { local:'lastName',           remote:'cognome'                              },
      { local:'serialNumber',       remote:'matricola'                            },
      { local:'costPerHour',        remote:'costo_orario'                         },
      { local:'recruitmentDate',    remote:'data_assunzione', type:'date'         },
      { local:'cessationDate',      remote:'data_cessazione', type:'date'         },
      { local:'medicalExpireDate',  remote:'scadenza_visita_medica', type:'date'  },
      { local:'taxCode',            remote:'codice_fiscale'                       },
      { local:'bypassTaxCode',      remote:'salta_validazione_cf'                 },
      { local:'active',             remote:'attivo'                               },
      { local:'direct',             remote:'diretto'                              },
      { local:'internal',           remote:'interno'                              },
      { local:'mobilePhone',        remote:'cellulare'                            }
    ], 

    computed: {
      name: {
        depends: ["firstName", "lastName"],
        get: function(fields) {
          return fields.firstName + " " + fields.lastName;
        }
      }
    },

    isActive:function() {
      return this.get('active');
    }, 

    validation: {
      firstName: { required: true },
      lastName: { required: true },
      taxCode: { 
        required: function(value, attr, computedState) {
          return !computedState.bypassTaxCode;
        }
      },
      costPerHour: { min: 0.1 }
    },

    canAddSheet: function() {
      return !this.isNew();
    }, 

    matchesFilter: function(filter) {
      if (!filter) return true;
      var name = this.get("name").toLowerCase();
      return name.indexOf(filter.toLowerCase()) > -1;
    }, 

    toString: function() {
      return this.get('firstName') + ' ' + this.get('lastName');
    }
  }, {
    modelName: "employee"
  });
  
  Models.Employees = Models.EntityCollection.extend({
    url: '/api/v1/dipendente',
    model: Models.Employee,
    
    initialize: function() {
      _.extend(this, new Backbone.Picky.SingleSelect(this));
      Backbone.Collection.prototype.initialize.call(this);
    }
  });
  
  WMS.reqres.setHandler('get:employee:all', function(options) {
    return Models.__fetchCollection('employeeAll', Models.Employees);
  })

  WMS.reqres.setHandler('get:employee:list', function(options) {
    options = _.defaults(options || {}, {param: {attivo:'True'}});
    return Models.__fetchCollection('employeeList', Models.Employees, options);
  });

  WMS.commands.setHandler('reset:employee:list', function() {
    Models.__resetCollection('employeeList');
    Models.__resetCollection('employeeAll');
  });
  
  WMS.reqres.setHandler('get:employee', function(id, options) {
    return Models.__fetchModel('employee', Models.Employee, id, options);
  });
});