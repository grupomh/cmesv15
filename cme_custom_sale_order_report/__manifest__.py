# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Custom Report Sale Report -DEVELSECURITY-',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Custom Report Sale Report -DEVELSECURITY-',
    'description': """
Custom Report Template -DEVELSECURITY-
============================
""",
    'website': 'https://www.xetechs.odoo.com',
    'depends': ['base_setup', 'sale', 'sale_stock'],
    'data': [
        'security/groups.xml',
        'reports/reports.xml',
        'reports/cme_pedido.xml',
    ],
    'installable': True,
    'application': True,
}
