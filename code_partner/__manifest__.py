# -*- coding: utf-8 -*-

{
    'name': "Code Partner",
    'author': "Xetechs GT",
    'website': "https://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',
        'stock',
        'account_accountant'
                ],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'views/partner_views.xml',
        'views/stock_views.xml'
    ]
}