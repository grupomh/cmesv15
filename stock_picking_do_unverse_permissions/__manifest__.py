{
    'name': 'Permissos para boton de anular reserva',
    'version': '13.0',
    'category': 'Reporting',
    'description': """
        En los permisos de inventario/transferencias esconder el boton de 'anular reserva' a usuarios del modulo y dejarlo solo a administradores de inventarios.
        Solo el grupo 'stock.group_stock_manager' tendra acceso
    """,
    'author': 'Justo Rivera - justo.rivera@xetechs.com',
    'website': 'https://www.xetechs.com',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking.xml',

                   ],
    'installable': True,
    'auto_install': False,
    'active': False,

}