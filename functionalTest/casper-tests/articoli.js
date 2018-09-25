casper.test.comment('Casper+Django integration example');
var helper = require('./djangocasper.js');
var x = require('casper').selectXPath;

casper.on('page.error', function(msg, trace) {
   this.echo('Error: ' + msg, 'ERROR');
   for(var i=0; i<trace.length; i++) {
       var step = trace[i];
       this.echo('   ' + step.file + ' (line ' + step.line + ')', 'ERROR');
   }
});

helper.scenario('/',
    function() {
        this.test.assertTitle("Mr. Ferro WMS", "Titolo della pagina è giusto.");
        this.test.assertExists('a[href="#owner"]', "bottone Mr. Ferro trovato.");
        this.click('a[href="#owner"]');
    },
    function() {
        casper.waitForSelector("form#login-form", function() {
            this.test.assertExists('form#login-form', "La form di login è trovata.");
            this.fill('form#login-form', {
                username: "admin",
                password: "nimda"
            }, false);
            this.test.assertExists('button[name="login"]', "bottone Login trovato.");
            this.click('button[name="login"]');
        });
    },
    function(){
        // casper.waitForSelector('div.panel-heading', function() {
        casper.waitForUrl('/#owner', function () {
            this.test.assertExists(x("//a[normalize-space(text())='Articoli']"),
                "Bottone 'Articoli' esiste nel menù in cima.");
            this.click(x("//a[normalize-space(text())='Articoli']"));
        });
    },
    function() {
        // casper.waitForUrl('/#articles', function () {
        this.wait(3000, function() {
            this.test.assertElementCount("div#list-region table tbody tr", 3, 
                "Trovati i 3 articoli che mi aspettavo.");
            /*this.test.assertElementCount("span.js-destroy", 3, 
                "Trovati i 3 articoli che mi aspettavo.");*/
            /*this.test.assertEval(function() {
                return __utils__.findAll("span.js-destroy").length == 3;
            }, "Trovati i 3 articoli che mi aspettavo.");*/

            this.test.assertExists("a.js-new", "bottone 'Nuovo' trovato.");
            this.click("a.js-new");
        });
    }
    , 
    function(){
        // non ho trovato altri modi di far funzionare il test se non mettere
        // un wait().
        this.wait(3000, function() {
        // casper.waitUntilVisible('div.modal-header', {
            this.fill('div.modal-content form', {
                unitTypeId: 'CM',
                description: "articolo 3",
                price: "3",
                technicalTypeId: "6"
            }, false);
            this.test.assertExists("button.js-submit", "bottone 'Crea' trovato.");
            this.click("button.js-submit");
        });
    }, 
    function(){
        this.wait(3000, function() {
            this.test.assertElementCount("div#list-region table tbody tr", 4, 
                "Trovati i 4 articoli che mi aspettavo.");
        });
    }
);
helper.run();
