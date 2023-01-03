{
    'name': 'fields invoice SV',
    'version': '0.1',
    'category': 'sale',
    'summary': 'Modulo de campos en Facturas para compañias Salvadoreñas',
    'description': """
        Este modulo contiene campos que anteriormente fueron creados por Odoo Studio,
        Filtrando por compañias del Salvador y el tipo de factura.
    """,
    'author': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.com',
    'depends': ['account','base'],
    'data': [
        'views/view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}