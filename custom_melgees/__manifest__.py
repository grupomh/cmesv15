# -*- coding: utf-8 -*-

{
    'name': "Custom Melgees",
    'author': "Xetechs GT",
    'website': "https://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale_management',
        'stock',
        'purchase',
        'account',
                ],

    # always loaded
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/sale_views.xml',
            'views/purchase_views.xml',
            'views/account_move_views.xml',
            'views/stock_views.xml'
    ]
}