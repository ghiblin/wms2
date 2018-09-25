// load a language
numeral.language('it', {
    delimiters: {
        thousands: '.',
        decimal: ','
    },
    abbreviations: {
        thousand: 'mila',
        million: 'mil',
        billion: 'b',
        trillion: 't'
    },
    ordinal : function (number) {
        return '°';
    },
    currency: {
        symbol: '€'
    }
});

// switch between languages
numeral.language('it');