# -*- coding: utf-8 -*-

{
    'name': 'Stock Validations',
    'version': '1.0.1',
    'author': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.com', 
    'support': 'Luis Aquino --> laquino@xetechs.com', 
    'category': 'Warehouse',
    'depends': ['stock', 'sale', 'purchase', 'account', 'sale_coupon'],
    'summary': 'Stock Validations',
    'data': [
        'security/groups.xml',
        'views/res_partner_view.xml',
        'views/purchase_order_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'sequence': 1,
    'auto_install': False,
}
