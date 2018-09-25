WMS.module('Models', function(Models, WMS, Backbone, Marionette, $, _) {
  var Type = Backbone.Model.extend({
    defaults: {
      description: ''
    },

    maps: [
      { local: 'description', remote: 'descrizione' }
    ],

    toString: function() {
      return this.get('description');
    }
  });

  var AddressType = Models.AddressType = Type.extend();
  var AddressTypes = Backbone.Collection.extend({
    url: '/api/v1/indirizzo/get_tipo_sede/',
    model: AddressType
  });

  var ArticleType = Models.ArticleType = Type.extend();
  var ArticleTypes = Backbone.Collection.extend({
    url: '/api/v1/classeArticolo',
    model: ArticleType
  });

  var CausalTransportType = Models.CausalTransportType = Type.extend();
  var CausalTransportTypes = Backbone.Collection.extend({
    url   : "/api/v1/tipoCausaleTrasporto/"
  , model : CausalTransportType
  });

  var ContactType = Models.ContactType = Type.extend();
  var ContactTypes = Backbone.Collection.extend({
    url: "/api/v1/contatto/get_tipo_contatto/",
    model: ContactType
  });

  var entityTypes = new Backbone.Collection([
    { id: 'F', description: 'Persona Fisica', shortDescription: 'PF' },
    { id: 'G', description: 'Persona Giuridica', shortDescription: 'PG'}
  ], {
    model: Type
  });

  var IncotermType = Models.IncotermType = Type.extend();
  var IncotermTypes = Backbone.Collection.extend({
    url   : "/api/v1/tipoPorto"
  , model : IncotermType
  });

  Models.MovementType = Type.extend();
  var MovementTypes = Backbone.Collection.extend({
    url: "/api/v1/tipoMovimento/",
    model: Models.MovementType
  });
  WMS.reqres.setHandler("get:movement:types", function() {
    return Models.__fetchCollection('movementTypes', MovementTypes);
  });

  var OutwardnessType = Models.OutwardnessType = Type.extend();
  var OutwardnessTypes =Backbone.Collection.extend({
    url   : "/api/v1/tipoAspettoEsteriore/"
  , model : OutwardnessType
  });

  var PaymentType = Models.PaymentType = Type.extend();
  var PaymentTypes = Backbone.Collection.extend({
    url: "/api/v1/tipoPagamento/",
    model: PaymentType
  });

  var ShippingType = Models.ShippingType = Type.extend();
  var ShippingTypes = Backbone.Collection.extend({
    url   : "/api/v1/tipoTrasportoACura/"
  , model : ShippingType
  });

  var TechnicalType = Models.TechnicalType = Type.extend();
  var TechnicalTypes = Backbone.Collection.extend({
    url: "/api/v1/classeArticolo/",
    model: TechnicalType
  });
  
  var UnitType = Models.UnitType = Type.extend();
  var UnitTypes = Models.UnitTypes = Backbone.Collection.extend({
    url: '/api/v1/articolo/get_unita_di_misura/',
    model: UnitType
  });
  WMS.reqres.setHandler('get:unit:types', function() {
    return Models.__fetchCollection('unitTypes', UnitTypes);
  });

  var VATRate = Models.VATRate = Type.extend({
    defaults: {
      code: '',
      description: '',
      percentage: 0.0
    },

    maps: [
      { local: 'code', remote: "codice" },
      { local: 'description', remote: "descrizione" },
      { local: 'percentage', remote: "percentuale" }
    ]
  });
  var VATRates = Backbone.Collection.extend({
    url: '/api/v1/aliquotaIVA/',
    model: VATRate
  });

  var WorkType = Models.WorkType = Type.extend();
  var WorkTypes = Backbone.Collection.extend({
    url: '/api/v1/tipoLavoro/',
    model: WorkType
  });

  WMS.reqres.setHandler('get:address:types', function() {
    return Models.__fetchCollection('addressTypes', AddressTypes);
  });

  WMS.reqres.setHandler('get:article:types', function() {
    return Models.__fetchCollection('articleTypes', ArticleTypes);
  });
  
  WMS.reqres.setHandler("get:causalTransport:types", function() {
    return Models.__fetchCollection("causalTransportTypes", CausalTransportTypes);
  });

  WMS.reqres.setHandler('get:contact:types', function() {
    return Models.__fetchCollection('contactTypes', ContactTypes);
  });

  WMS.reqres.setHandler('get:entity:types', function() {
    var defer = $.Deferred();
    defer.resolve(entityTypes);
    return defer.promise();
  });

  WMS.reqres.setHandler("get:incoterm:types", function() {
    return Models.__fetchCollection("incotermTypes", IncotermTypes);
  });

  WMS.reqres.setHandler("get:outwardness:types", function() {
    return Models.__fetchCollection("outwardnessTypes", OutwardnessTypes);
  });

  WMS.reqres.setHandler('get:payment:types', function() {
    return Models.__fetchCollection('paymentTypes', PaymentTypes);
  });
  
  WMS.reqres.setHandler("get:shipping:types", function() {
    return Models.__fetchCollection("shippingTypes", ShippingTypes);
  });

  WMS.reqres.setHandler('get:technical:types', function() {
    return Models.__fetchCollection('technicalTypes', TechnicalTypes);
  });

  WMS.reqres.setHandler('get:vat:rates', function() {
    return Models.__fetchCollection('vatRates', VATRates);
  });
  
  WMS.reqres.setHandler('get:work:types', function() {
    return Models.__fetchCollection('workTypes', WorkTypes);
  });

  WMS.on('start', function() {
    var session = WMS.getSession();
    session.on('change:authenticated', function() {
      Models.cache = {};
    });
  });
});