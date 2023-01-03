# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

{
    'name': "Res City",
    'author': "Xetechs, S.A.",
    'support': "Luis Aquino -> laquino@xetechs.com",
    'website': "https://www.xetechs.com",
    'category': 'Accounting',
    'version': '1.01',
    'depends': ['base', 'contacts','base_address_city'],
    'data': [
            'security/ir.model.access.csv',
            'views/res_city_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
}