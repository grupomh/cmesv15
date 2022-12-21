# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

{
    'name': "Account Invoice Rouding",
    'author': "Xetechs, S.A.",
    'support': "Luis Aquino -> laquino@xetechs.com",
    'website': "https://www.xetechs.com",
    'category': 'Accounting',
    'version': '1.01',
    'depends': ['account', 'sale_management', 'purchase'],
    'data': [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'views/account_move_view.xml',
            'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
}