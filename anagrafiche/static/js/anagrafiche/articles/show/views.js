WMS.module('Articles.Show', function(Show, WMS, Backbone, Marionette, $, _) {
  var Views = {}
    , Behaviors = WMS.Common.Behaviors;

  Views.Layout = Marionette.LayoutView.extend({
    template: _.template(
      "<div class='page-header' id='title-region'></div>" +
      "<div class='row' id='details-region'></div>" +
      "<div class='row' id='stocks-region'></div>" +
      "<div class='row' id='movements-region'></div>"
    ),
    regions: {
      titleRegion     : '#title-region',
      detailsRegion   : '#details-region',
      stocksRegion    : '#stocks-region', 
      movementsRegion : '#movements-region'
    }
  });

  Views.TitleView = Marionette.ItemView.extend({
    template: _.template("<%= label %>"),
    tagName: "h2"
  });

  Views.DetailsView = Marionette.ItemView.extend({
    template: _.template(
      "<div class='panel-heading'>Dettagli</div>"+
      "<div class='panel-body'>"+
        "<ul class='dl-horizontal'>"+
          "<dt>Codice:</dt><dd><%= code %></dd>"+
          "<dt>Tipo:</dt><dd><%= technicalType %></dd>"+
          "<dt>Descrizione:</dt><dd><%= description %></dd>"+
          "<dt>Prezzo:</dt><dd><%= price %></dd>"+
          "<dt>U.M.:</dt><dd><%= unitType %></dd>"+
          "<dt>Codice Fornitore:</dt><dd><%= supplierCode %></dd>"+
          "<dt>Lead Time:</dt><dd><%= leadTime %></dd>"+
          "<dt>Scorta di sicurezza:</dt><dd><%= safetyStock %></dd>"+
          "<dt>Note:</dt><dd><%= note %></dd>"+
        "</ul>"+
      "</div>"
    ),
    className: "panel panel-default",

    behaviors: [
      {
        behaviorClass: Behaviors.CollapsableBehavior
      }
    ]
  });

  var StoksItemView = Marionette.ItemView.extend({
    template: _.template(
      "<td><%= batch %></td>" +
      "<td><%= unitTypeId %></td>" +
      "<td><%= quantity %></td>" +
      "<td><%= note %></td>"
    ),

    tagName: "tr"
  });

  var StocksEmptyView = Marionette.ItemView.extend({
    template: _.template("<td colspan='4' class='text-center'><i>Nessuna giacenza trovata.</i></td>"),
    tagName: "tr"
  });

  Views.StocksView = Marionette.CompositeView.extend({
    template: _.template(
      "<div class='panel-heading'>Giacenze</div>"+
      "<div class='panel-body'>"+
      "</div>"+
      "<table class='table hover'>"+ 
        "<thead>" +
          "<tr>"+
            "<th>Lotto</th>" +
            "<th>U.M.</th>" +
            "<th>Q.ta</th>" +
            "<th>Commessa</th>" +
            "<th>Note</th>" +
          "</tr>"+
        "</thead>" +
        "<tbody></tbody>"+
      "</table>"
    ),
    className: "panel panel-default",
    childView: StoksItemView,
    emptyView: StocksEmptyView,
    childViewContainer: "tbody",

    behaviors: [
      {
        behaviorClass: Behaviors.CollapsableBehavior
      }
    ],

    collectionEvents: {
      "sync": "render"
    }
  });

  var MovementsItemView = Marionette.ItemView.extend({
    template: _.template(
      "<td><%= date && date.format('d/m/Y') %></td>" +
      "<td><%= batch %></td>" +
      "<td><%= movementType %></td>" +
      "<td><%= quantity %></td>" +
      "<td><%= unitTypeId %></td>" +
      "<td><%= commission %></td>" +
      "<td><%= username %></td>" +
      "<td><% if(movementTypeId === 1) { %>" +
      "<a class='btn btn-primary js-view'><i class='glyphicon glyphicon-eye-open' /></a>" +
      "<% } else { %>" +
      "<a class='btn btn-primary js-edit'><i class='glyphicon glyphicon-pencil' /></a>" +
      "<a class='btn btn-danger js-delete'><i class='glyphicon glyphicon-trash' /></a>" +
      "<% } %>"
    ),

    tagName: "tr",

    triggers: {
      "click .js-edit": "movement:edit",
      "click .js-delete": "movement:delete",
      "click .js-view": "movement:view"
    },

    modelEvents: {
      "change": "render"
    }
  });

  var MovementsEmptyView = Marionette.ItemView.extend({
    template: _.template("<td colspan='9' class='text-center'><i>Nessun movimento trovato.</i></td>"),
    tagName: "tr"
  });

  Views.MovementsView = Marionette.CompositeView.extend({
    template: _.template(
      "<div class='panel-heading'>Movimenti di magazzino</div>"+
      "<div class='panel-body'>"+
        "<a class='btn btn-primary js-download'><i class='glyphicon glyphicon-download' /></a>" +
        "<a class='btn btn-primary js-add'><i class='glyphicon glyphicon-plus' /></a>" +
        "<a class='btn btn-primary js-substract'><i class='glyphicon glyphicon-minus' /></a>" +
      "</div>"+
      "<table class='table hover'>"+ 
        "<thead>" +
          "<tr>"+
            "<th>Data</th>" +
            "<th>Lotto</th>" +
            "<th>Tipo Movimento</th>" +
            "<th>Q.ta</th>" +
            "<th>U.M.</th>" +
            "<th>Commessa</th>" +
            "<th>Utente</th>" +
            "<th />" +
          "</tr>"+
        "</thead>" +
        "<tbody></tbody>"+
      "</table>"
    ),
    className: "panel panel-default",
    childView: MovementsItemView,
    emptyView: MovementsEmptyView,
    childViewContainer: "tbody",

    triggers: {
      "click .js-download": "movements:download",
      "click .js-add": "movements:add",
      "click .js-substract": "movements:substract"
    },

    childEvents: {
      "movement:edit": function(view) { this.trigger("movement:edit", view.model); },
      "movement:delete": function(view) { this.trigger("movement:delete", view.model); },
      "movement:view": function(view) { this.trigger("movement:view", view.model); }
    },

    behaviors: [
      {
        behaviorClass: Behaviors.CollapsableBehavior
      }
    ]
  });

  var MovementForm = WMS.Common.Views.ModalFormView.extend({
    behaviors: [
      {
        behaviorClass : Behaviors.FormBehavior,
        fieldSelector : 'app-field',
        insertPoint   : 'div.modal-body',
        readonly      : ["articleId", "movementTypeId"],
        fields        : {
          articleId     : null,
          movementTypeId: null,
          batchId       : null,
          commissionId  : null,
          quantity      : 0
        }
      }, 
      {
        behaviorClass : Behaviors.ModalBehavior
      }
    ]
  });
  
  Views.NewMovement = MovementForm.extend({
    title         : 'Nuovo Movimento Magazzino'
  , saveButtonText: 'Crea Movimento'
  });
  
  Views.EditMovement = MovementForm.extend({
    title         : 'Modifica Movimento Magazzino'
  , saveButtonText: 'Aggiorna'
  });

  Show.Views = Views;
});