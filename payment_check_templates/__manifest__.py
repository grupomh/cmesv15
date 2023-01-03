# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Payment Check Vourcher -Templates-',
    'version': '1.0',
    'summary': 'Custom Voucher Template',
    'sequence': 1,
    'description': """
Custom Vouche Templates
    """,
    'category': 'Account',
    'author': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.com',
    'support': 'Luis Aquino -> laquino@xetechs.com',
    'depends': ['account', 'account_accountant'],
    'data': [
        #'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'views/payment_view.xml',
        'views/reports.xml',
        'views/report_promerica_template.xml',
        'views/report_banrural_template.xml',
        'views/report_city_template.xml',
        ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
