# -*- coding: utf-8 -*-

{
    'name': "MRP Scrap Extends",
    'author': "Luis Aquino --> laquino@xetechs.com",
    'website': "https://www.xetechs.com",
    'category': 'Operations/Inventory',
    'version': '1.0.1',
    'sequence': 1,
    'description': "MRP Scrap Extends",
    'depends': ['mrp', 'stock'],
    'data': [
        'views/mrp_production_view.xml',
        'views/mrp_scrap_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
