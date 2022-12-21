{
    'name': 'Concatenar serie + nombre',
    'version': '13.0.1.0.0',
    'category': 'Account',
    'license': 'AGPL-3',
    'summary': 'Concatenacion de numero de serie y nombre de factura',
    'description': """
    Las compañias del salvador utilizan un numero de serie en las impresoras ricoh, entonces la contatenacion sera del
    numero de serie + el numero de la factura forzada.
    """,
    'author': 'Xetechs',
    'website': 'http://www.xetechs.com',
    'data' : ['views/view.xml'],
    'depends': ['account','base'],
    'installable': True,
}