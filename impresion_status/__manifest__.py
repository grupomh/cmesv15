# -*- coding: utf-8 -*-
{
    'name': 'Estado de impresion RICOH',
    'version': '1.0.1',
    'summary': 'Columna de impreso',
    'description': """
    Modulo:
    =======
    El proposito de este modulo es visualizar el estado de la factura, para 
    corroborar si la factura ya se mando a imprimir""",
    'category': 'Account',
    'author': 'Xetechs S.A.',
    'company': 'Xetechs S.A.',
    'maintainer': 'Xetechs---jrojas@xetechs.com',
    'depends': [
        'account',
        'ricoh_printers'
    ],
    'website': 'https://www.xetechs.com',
    'data': [
        'views/status_print.xml',
        'security/groups.xml'
    ],
    'qweb': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}