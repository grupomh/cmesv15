# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Ricoh Documents -CME-',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Richo Documents -CME-',
    'description': """
Ricoh Documents -CM-
============================
""",
    'author': 'Xetechs, S.A.',
    'support': 'Luis Aquino -> laquino@xetechs.com',
    'website': 'https://www.xetechs.odoo.com',
    'depends': ['base_setup', 'account', 'branch'],
    'data': [
        'security/groups.xml',
        'views/res_company_view.xml',
        'views/account_move_view.xml',
        'wizard/wizard_generate_file_view.xml',
    ],
    'installable': True,
    'application': True,
}
