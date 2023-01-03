{
    "name": "Folio CME",
    "summary": "Secuencia en campo folio",
    'description': """
    La sequencia del folio se reinicia por rangos de fechas.
    Para tener una mejor segmentación en los asientos contables. 
    """,
    'author': "Palo Blanco",
    'support': "paloblancoit@gmail.com",
    "version": "1.0",
    "category": "Tools",
    "depends": ['base', 'account'],
    "data": [
        'views/view.xml',
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}