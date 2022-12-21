# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Product Weight Extend',
    'version': '1.0',
    'sequence': 1,
    'category': 'Account',
    'author': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.com',
    'support': 'Justo Rivera -> justo.rivera@xetechs.com',
    'depends': ['account', 'account_accountant', 'sale', 'sale_margin'],
    'data': [
        #'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale.xml',
        'views/move.xml',
        'views/purchase.xml',
        'views/stock.xml',
        'reports/sale.xml',
        'reports/stock.xml',
        'reports/invoice.xml',
        ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
