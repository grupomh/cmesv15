# -*- coding: utf-8 -*-
{
    'name': 'Custom Invoice Views',
    'version': '13.0.1.0.0',
    'summary': 'Custom Invoice Views',
    'description': 'Vistas Personalizadas de Facturas',
    'author': 'Luis Aquino -> laquino@xetechs.com',
    'company': 'Xetechs, S.A.',
    'depends': ['base', 'account',],
    'website': 'https://www.xetechs.com',
    'data': [
        'security/groups.xml',
        'views/views.xml',
    ],
    'installable': True,
    'sequence': 1,
    'auto_install': False,
    'application': True,
}