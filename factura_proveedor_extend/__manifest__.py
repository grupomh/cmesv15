# -*- coding: utf-8 -*-

{
    'name': 'Numero de comprobante, serie, resolucion',
    'version': '1.0',
    'category': 'Contabilidad',
    'description': """
	- Numero de comprobante
	- serie
    - resolucion

	""",
    'author': 'Xetechs, S.A.',
    'support': 'Justo Rivera --> justo.rivera@xetechs.com',
    'depends': ['account', 'payment'],
    'data': [
        'security/groups.xml',
        'views/account_move.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
