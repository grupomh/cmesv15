# -*- coding: utf-8 -*-

{
    'name': "Partner Credit Limit",
    'author': "Xetechs GT",
    'website': "https://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'base_setup',
        'contacts',
        'account_followup'
                ],

    # always loaded
    'data': [
        #'data/ir_sequence.xml',
        'security/security.xml',
        'views/partner_views.xml',
        'views/company_view.xml',
    ]
}