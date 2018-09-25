WMS.labels = _.extend({}, WMS.labels, {
  filter: {
    code                : 'Codice',
    clientId            : 'Cliente',
    supplierId          : 'Fornitore',
    from                : 'Da',
    to                  : 'A'
  }

, login: {
    username            : 'Username'
  , password            : 'Password'
  }

, tabs: {
    estimates           : 'Preventivi'
  , orders              : 'Ordini'
  , notes               : 'Bolle'
  , invoices            : 'Fatture'
  }
});

_.extend(WMS.Models.Address.prototype, {
  labels: {
    typeId              : 'Tipo'
  , line1               : 'Indirizzo'
  , line2               : ' '
  , city                : 'Citt&agrave;'
  , zip                 : 'CAP'
  , state               : 'Provincia'
  , country             : 'Nazione'
  }
});

_.extend(WMS.Models.ClientAddress.prototype, {
  labels: _.extend({
    clientId            : 'Cliente'
  }, WMS.Models.Address.prototype.labels)
});

_.extend(WMS.Models.SupplierAddress.prototype, {
  labels: _.extend({
    supplierId          : 'Fornitore'
  }, WMS.Models.Address.prototype.labels)
});

_.extend(WMS.Models.OwnerAddress.prototype, {
  labels: _.extend({
    ownerId             : 'Proprietario'
  }, WMS.Models.Address.prototype.labels)
});

_.extend(WMS.Models.BankDatum.prototype, {
  labels: {
    bank                : 'Banca'
  , branch              : 'Filiale'
  , holder              : 'Intestatario'
  , iban                : 'IBAN'
  , swift               : 'SWIFT'
  , main                : 'Predefinito'
  , foreigner           : 'Straniero'
  }
});

_.extend(WMS.Models.ClientBankDatum.prototype, {
  labels: _.extend({
    clientId            : 'Cliente'
  }, WMS.Models.BankDatum.prototype.labels)
});

_.extend(WMS.Models.SupplierBankDatum.prototype, {
  labels: _.extend({
    supplierId          : 'Fornitore'
  }, WMS.Models.BankDatum.prototype.labels)
});

_.extend(WMS.Models.OwnerBankDatum.prototype, {
  labels: _.extend({
    ownerId             : 'Proprietario'
  }, WMS.Models.BankDatum.prototype.labels)
});

_.extend(WMS.Models.Contact.prototype, {
  labels: {
    typeId              : 'Tipo'
  , value               : 'Informazioni di contatto'
  , note                : 'Note'
  }
});

_.extend(WMS.Models.ClientContact.prototype, {
  labels: _.extend({
    clientId            : 'Cliente'
  }, WMS.Models.Contact.prototype.labels)
});

_.extend(WMS.Models.SupplierContact.prototype, {
  labels: _.extend({
    supplierId          : 'Fornitore'
  }, WMS.Models.Contact.prototype.labels)
});

_.extend(WMS.Models.OwnerContact.prototype, {
  labels: _.extend({
    ownerId             : 'Proprietario'
  }, WMS.Models.Contact.prototype.labels)
});

WMS.Models.Article.prototype.labels = {
  code                : 'Codice',
  technicalTypeId     : 'Tipo',
  unitTypeId          : 'Unit&agrave; Misura',
  supplierCode        : 'Codice Fornitore',
  price               : 'Prezzo',
  description         : 'Descrizione',
  leadTime            : 'Lead Time',
  safetyStock         : 'Scorta di Sicurezza',
  note                : 'Note Tecniche'
};

WMS.Models.Stock.prototype.labels = {
  articleId: "Article",
  movementTypeId: "Tipo Movimento",
  batchId: "Lotto",
  destinationId: "Destinazione",
  quantity: "Quantità"
};

WMS.Models.Movement.prototype.labels = {
  articleId           : "Articolo",
  batchId             : "Lotto",
  movementTypeId      : "Tipo Mov.",
  username            : "Utente",
  quantity            : "Q.ta",
  unitTypeId          : "U.M.",
  destinationId       : "Destinazione",
  commissionId        : "Commessa"
}

_.extend(WMS.Models.Employee.prototype, {
  labels: {
    firstName           : 'Nome'
  , lastName            : 'Cognome'
  , serialNumber        : 'Matricola'
  , costPerHour         : 'Costo orario'
  , recruitmentDate     : 'Data Assunzione'
  , cessationDate       : 'Data Cessazione'
  , medicalExpireDate   : 'Scadenza Visita Medica'
  , active              : 'Attivo'
  , taxCode             : 'Codice Fiscale'
  , bypassTaxCode       : 'Salta Validazione CF'
  , direct              : 'Diretto'
  , internal            : 'Interno',
    mobilePhone         : 'Cellulare'
  }
});

WMS.Models.Commission.prototype.labels = {
  code                : 'Codice',
  clientId            : 'Cliente',
  startDate           : 'Data Apertura',
  product             : 'Prodotto',
  destinationId       : 'Destinazione',
  deliveryDate        : 'Data Consegna'
};

_.extend(WMS.Models.CommissionCost.prototype, {
  labels: {
    date                : 'Data'
  , employee            : 'Dipendente'
  , workType            : 'Tipo Lavoro'
  , hours               : 'Ore'
  , total               : 'Totale'
  , note                : 'Note'
  }
});

_.extend(WMS.Models.CommissionAttachment.prototype, {
  labels: {
    commissionId        : 'Commessa'
  , filename            : 'Filename'
  , private             : 'Privato'
  }
})

_.each(['Client', 'Supplier', 'Owner'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: {
      code                : 'Codice',
      typeId              : 'Tipo',
      name                : 'Nome',
      firstName           : 'Nome',
      lastName            : 'Cognome',
      corporateName       : 'Ragione Sociale',
      vatNumber           : 'Partita IVA',
      taxCode             : 'Codice Fiscale',
      applyTo             : 'Persona di Riferimento',
      foreigner           : 'Straniero',
      carrier             : 'Vettore',
      paymentTypeId       : 'Tipo Pagamento',
      cashOrder           : 'Costo Ri.Ba.'
    }
  });
});

_.each(['Estimate', 'Order', 'Note', 'Invoice'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: {
      code                  : 'Codice',
      date                  : 'Data',
      clientId              : 'Cliente',
      clientCode            : 'Codice Cliente',
      supplierId            : 'Fornitore',
      supplierCode          : 'Codice Fornitore',
      supplierNote          : 'Cod. Bolla Forn.',
      supplierInvoice       : 'Cod. Fatt. Forn.',
      subject               : 'Oggetto',
      commissionId          : 'Commessa',
      orderId               : 'Ordine',
      destinationId         : 'Destinazione',
      accepted              : 'Accettato',
      applyTo               : 'Pers. Riferimento',
      vatRateId             : 'Aliquota IVA',
      paymentTypeId         : 'Pagamento',
      total                 : 'Totale',
      constructionDrawings  : 'Disegni Construttivi a carico del Cliente',
      calculationNote       : 'Note di Calcolo a carico del Cliente',
      gradeOfSteel          : 'Tipo Acciaio',
      thickness             : 'Spessori',
      galvanization         : 'Zincatura',
      executionClass        : 'Classe Esecuzione',
      wps                   : 'WPS',
      painting              : 'Verniciatura',
      causalTransportTypeId : 'Caus.Trasporto' ,
      shippingTypeId        : 'Tipo Trasporto',
      carrierId             : 'Vettore',
      incotermTypeId        : 'Incoterm',
      outwardnessTypeId     : 'Aspetto Esteriore',
      netWeight             : 'Peso Netto (kg)',
      grossWeight           : 'Peso Lordo (kg)',
      items                 : 'Numero Colli',
      discountPercent       : 'Sconto (%)',
      discountValue         : 'Sconto (€)',
      note                  : 'Note',
      printTotal            : 'Mostra totale su stampa',
      corrosiveClass        : 'Classe di Corrosività'
    }
  });
});

_.extend(WMS.Models.Estimate.prototype.labels, {
  supplierDate          : 'Data Bolla Forn.',
});

_.extend(WMS.Models.Invoice.prototype.labels, {
  supplierDate          : 'Data Fatt. Forn.',
});

_.each(['ClientEstimate', 'ClientOrder', 'ClientNote', 'ClientInvoice'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: _.extend({
      clientId            : 'Cliente'
    , clientCode          : 'Codice Cliente'
    }, WMS.Models[model].__super__.labels)
  });
});

_.each(['EstimateRow', 'OrderRow', 'NoteRow', 'InvoiceRow'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: {
      articleId           : 'Articolo'
    , articleCode         : 'Codice'
    , description         : 'Descrizione Articolo'
    , unitTypeId          : 'U. M.'
    , price               : 'Prezzo'
    , quantity            : 'Quantit&agrave;' 
    , total               : 'Totale'
    , estimateId          : 'Preventivo'
    , orderId             : 'Ordine'
    , discountPercent     : 'Sconto (%)'
    , noteId              : 'Bolla'
    , noteCode            : 'Bolla'
    }
  });
});

_.each(['ClientEstimateRow', 'ClientOrderRow', 'ClientNoteRow'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: _.extend({
      clientId            : 'Cliente'
    , clientCode          : 'Codice Cliente'
    }, WMS.Models[model].__super__.labels)
  });
});

_.each(['ClientOrderCommission', 'ClientInvoiceCommission'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: {
      clientId            : 'Cliente'
    , commissionId        : 'Commessa'
    }
  });
});

_.each(['SupplierOrderCommission', 'SupplierInvoiceCommission'], function(model) {
  _.extend(WMS.Models[model].prototype, {
    labels: {
      supplierId          : 'Fornitore'
    , commissionId        : 'Commessa'
    }
  });
});

_.extend(WMS.Models.Sheet.prototype, {
  labels: {
    employeeId          : 'Dipendente'
  , commissionId        : 'Commessa'
  , date                : 'Data'
  , hours               : 'Ore'
  , workTypeId          : 'Tipo Lavoro'
  , note                : 'Note'
  }
});

_.extend(WMS.Models.EmployeeHours.prototype, {
  labels: {
    firstName           : 'Nome'
  , lastName            : 'Cognome'
  , hours               : 'Totale Ore'
  }
});

_.extend(Backbone.Validation.messages, {
  required: '{0} è un campo obbligatorio'
, min: '{0} deve essere almeno {1}'
, max: '{0} deve essere al più {1}'
});