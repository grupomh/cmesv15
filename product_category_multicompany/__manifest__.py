# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

{
    'name': "Product Category Multicompany",
    'author': "Xetechs, S.A.",
    'support': "Luis Aquino -> laquino@xetechs.com",
    'website': "https://www.xetechs.com",
    'category': 'Accounting',
    'version': '1.01',
    'depends': ['product'],
    'data': [
            'security/groups.xml',
            'views/product_category_views.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
}